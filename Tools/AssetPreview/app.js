// OPC-08: sprite-sheet preview UI.
// The browser encodes the whole asset path once; the server decodes it once.

(() => {
    'use strict';

    const VIEW_WIDTH = 720;
    const VIEW_HEIGHT = 560;
    const FRAME_PREVIEW_SIZE = 160;
    const DIRECTIONS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];

    document.addEventListener('DOMContentLoaded', () => {
        const canvas = document.getElementById('spriteCanvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        canvas.width = VIEW_WIDTH;
        canvas.height = VIEW_HEIGHT;

        const elements = {
            status: document.getElementById('statusMessage'),
            layoutInfo: document.getElementById('layoutInfo'),
            directionsPanel: document.getElementById('directionsPanel'),
            animList: document.getElementById('animList'),
            framePreview: document.getElementById('framePreview'),
            playBtn: document.getElementById('playBtn'),
            toggleGrid: document.getElementById('toggleGrid'),
            zoom: document.getElementById('zoomLevel'),
            spritePath: document.getElementById('spritePath'),
            assetId: document.getElementById('assetId'),
            loadBtn: document.getElementById('loadBtn'),
            layoutBtn: document.getElementById('layoutBtn')
        };

        let currentImage = null;
        let currentObjectUrl = null;
        let spriteLayout = null;
        let currentDirection = 'N';
        let currentFrameIndex = 0;
        let currentAnimationIndex = 0;
        let animationTimer = null;
        let gridVisible = true;
        let framePreviewCanvas = null;
        let view = { scale: 1, offsetX: 0, offsetY: 0 };
        const params = new URLSearchParams(window.location.search);

        function updateDatasets() {
            document.body.dataset.layoutSupported = spriteLayout ? String(spriteLayout.supported) : '';
            document.body.dataset.layoutCols = spriteLayout && spriteLayout.grid ? String(spriteLayout.grid.cols) : '';
            document.body.dataset.layoutRows = spriteLayout && spriteLayout.grid ? String(spriteLayout.grid.rows) : '';
            document.body.dataset.frameWidth = spriteLayout && spriteLayout.frameSize ? String(spriteLayout.frameSize.width) : '';
            document.body.dataset.frameHeight = spriteLayout && spriteLayout.frameSize ? String(spriteLayout.frameSize.height) : '';
            document.body.dataset.currentDirection = currentDirection;
            document.body.dataset.currentFrame = String(currentFrameIndex);
            const animation = currentAnimation();
            document.body.dataset.animation = animation ? animation.name : '';
        }

        function setStatus(message, type = 'info') {
            elements.status.textContent = message;
            elements.status.style.borderLeftColor = {
                success: 'var(--success)',
                error: 'var(--error)',
                warning: 'var(--warning)'
            }[type] || 'var(--accent)';
        }

        function loadImage(blob) {
            return new Promise((resolve, reject) => {
                const image = new Image();
                image.onload = () => resolve(image);
                image.onerror = () => reject(new Error('browser could not decode the image'));
                image.src = URL.createObjectURL(blob);
            });
        }

        function resetFramePreview() {
            elements.framePreview.textContent = '';
            const hint = document.createElement('p');
            hint.className = 'hint';
            hint.textContent = 'No frame selected';
            elements.framePreview.appendChild(hint);
            framePreviewCanvas = null;
        }

        function clearLayout() {
            spriteLayout = null;
            currentAnimationIndex = 0;
            currentFrameIndex = 0;
            stopAnimation();
            elements.layoutInfo.classList.add('hidden');
            elements.layoutInfo.textContent = '';
            elements.animList.textContent = '';
            const hint = document.createElement('p');
            hint.className = 'hint';
            hint.textContent = 'Load a layout to see animations';
            elements.animList.appendChild(hint);
            elements.playBtn.disabled = true;
            showDirectionsPanel(false);
            resetFramePreview();
        }

        async function loadSpritePath(path, options = {}) {
            const keepLayout = Boolean(options.keepLayout);
            const value = String(path || '').trim();
            if (!value) {
                setStatus('Error: sprite path is required', 'error');
                return null;
            }
            if (!keepLayout) {
                // A manually loaded sheet must not keep the previous sheet's
                // grid, directions, animation list or selection.
                clearLayout();
            }
            setStatus(`Loading sprite: ${value}...`);
            try {
                // Encode the entire path; the server's single decode produces the
                // filesystem-relative path before confinement checks.
                const response = await fetch(`/api/sprites/${encodeURIComponent(value)}`, {
                    cache: 'no-store'
                });
                if (!response.ok) {
                    let detail = `HTTP ${response.status}`;
                    try {
                        const payload = await response.json();
                        if (payload && payload.error) detail = payload.error;
                    } catch (_ignored) {
                        // Keep the HTTP status when the body is not JSON.
                    }
                    throw new Error(detail);
                }
                const blob = await response.blob();
                const image = await loadImage(blob);
                if (currentObjectUrl) URL.revokeObjectURL(currentObjectUrl);
                currentObjectUrl = image.src;
                currentImage = image;
                stopAnimation();
                currentFrameIndex = 0;
                render();
                setStatus(`Loaded ${value} (${image.width}×${image.height})`, 'success');
                return image;
            } catch (error) {
                console.error(error);
                setStatus(`Failed to load sprite: ${error.message}`, 'error');
                return null;
            }
        }

        async function fetchLayout() {
            const assetId = String(elements.assetId.value || '').trim();
            if (!assetId) {
                setStatus('Error: assetId is required', 'error');
                return;
            }
            setStatus(`Fetching layout for ${assetId}...`);
            let warning = null;
            try {
                const response = await fetch(`/api/layout/${encodeURIComponent(assetId)}`, {
                    cache: 'no-store'
                });
                let payload = null;
                try {
                    payload = await response.json();
                } catch (_ignored) {
                    payload = null;
                }
                if (!response.ok) {
                    throw new Error((payload && payload.error) || `HTTP ${response.status}`);
                }
                spriteLayout = payload;
                showLayoutInfo(payload);
                stopAnimation();
                currentFrameIndex = 0;
                currentAnimationIndex = 0;

                if (!payload.supported) {
                    setStatus(
                        `Unsupported layout: ${(payload.unsupportedReasons || []).join('; ')}`,
                        'error'
                    );
                    showDirectionsPanel(false);
                    resetFramePreview();
                    render();
                    return;
                }

                if (!currentImage && payload.path) {
                    const loaded = await loadSpritePath(payload.path, { keepLayout: true });
                    if (!loaded) {
                        updateDatasets();
                        return;
                    }
                }
                if (payload.image && currentImage &&
                    (currentImage.width !== payload.image.width ||
                     currentImage.height !== payload.image.height)) {
                    warning =
                        `Layout says ${payload.image.width}×${payload.image.height} but the loaded image is ` +
                        `${currentImage.width}×${currentImage.height}`;
                    setStatus(warning, 'warning');
                }

                const directions = payload.directions || [];
                if (payload.directional && directions.length) {
                    if (!directions.includes(currentDirection)) currentDirection = directions[0];
                } else {
                    currentDirection = 'N';
                }
                setupAnimations();
                showDirectionsPanel(Boolean(payload.directional));
                render();
                if (!warning) {
                    setStatus(
                        `Layout loaded: ${payload.grid.cols} frame columns × ${payload.grid.rows} rows ` +
                        `(${payload.frameSize.width}×${payload.frameSize.height}px per frame)`,
                        'success'
                    );
                }
            } catch (error) {
                console.error(error);
                spriteLayout = null;
                setStatus(`Failed to fetch layout: ${error.message}`, 'error');
                render();
            }
        }

        function showLayoutInfo(layout) {
            elements.layoutInfo.classList.remove('hidden');
            elements.layoutInfo.textContent = '';
            const badge = document.createElement('div');
            badge.className = layout.supported ? 'layout-badge supported' : 'layout-badge unsupported';
            badge.textContent = layout.supported
                ? `SUPPORTED — ${layout.grid.cols} columns × ${layout.grid.rows} rows`
                : `UNSUPPORTED — ${(layout.unsupportedReasons || []).join('; ')}`;
            const details = document.createElement('pre');
            details.textContent = JSON.stringify(layout, null, 2);
            elements.layoutInfo.append(badge, details);
        }

        function currentAnimation() {
            if (!spriteLayout || !spriteLayout.animations) return null;
            return spriteLayout.animations[currentAnimationIndex] || spriteLayout.animations[0] || null;
        }

        function currentRow() {
            if (!spriteLayout || !spriteLayout.directional) return 0;
            const row = spriteLayout.directionRows[currentDirection];
            return Number.isInteger(row) ? row : 0;
        }

        function computeView() {
            if (!currentImage) return;
            const zoom = Math.max(0.25, Number(elements.zoom.value) || 1);
            const fitScale = Math.min(
                (VIEW_WIDTH - 40) / currentImage.width,
                (VIEW_HEIGHT - 40) / currentImage.height
            );
            view.scale = Math.max(0.1, fitScale * zoom);
            view.offsetX = (VIEW_WIDTH - currentImage.width * view.scale) / 2;
            view.offsetY = (VIEW_HEIGHT - currentImage.height * view.scale) / 2;
        }

        function render() {
            ctx.imageSmoothingEnabled = false;
            ctx.fillStyle = '#161616';
            ctx.fillRect(0, 0, VIEW_WIDTH, VIEW_HEIGHT);
            if (!currentImage) {
                ctx.fillStyle = '#7c8fbf';
                ctx.font = '16px Segoe UI, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('Load a sprite sheet to begin', VIEW_WIDTH / 2, VIEW_HEIGHT / 2);
                updateDatasets();
                return;
            }
            computeView();
            ctx.drawImage(
                currentImage,
                view.offsetX, view.offsetY,
                currentImage.width * view.scale,
                currentImage.height * view.scale
            );
            if (spriteLayout && spriteLayout.supported) {
                if (gridVisible) drawGrid();
                drawSelection();
                drawFramePreview();
            }
            updateDatasets();
        }

        function drawGrid() {
            const grid = spriteLayout.grid;
            const frame = spriteLayout.frameSize;
            if (!grid || !frame) return;
            ctx.save();
            ctx.strokeStyle = 'rgba(124, 143, 191, 0.55)';
            ctx.lineWidth = 1;
            for (let col = 0; col <= grid.cols; col += 1) {
                const x = Math.round(view.offsetX + col * frame.width * view.scale) + 0.5;
                ctx.beginPath();
                ctx.moveTo(x, view.offsetY);
                ctx.lineTo(x, view.offsetY + grid.rows * frame.height * view.scale);
                ctx.stroke();
            }
            for (let row = 0; row <= grid.rows; row += 1) {
                const y = Math.round(view.offsetY + row * frame.height * view.scale) + 0.5;
                ctx.beginPath();
                ctx.moveTo(view.offsetX, y);
                ctx.lineTo(view.offsetX + grid.cols * frame.width * view.scale, y);
                ctx.stroke();
            }
            ctx.restore();
        }

        function drawSelection() {
            const animation = currentAnimation();
            const frame = spriteLayout.frameSize;
            if (!animation || !frame) return;
            const column = animation.columnStart + currentFrameIndex;
            const row = currentRow();
            const x = view.offsetX + column * frame.width * view.scale;
            const y = view.offsetY + row * frame.height * view.scale;
            ctx.save();
            ctx.strokeStyle = '#fc913e';
            ctx.lineWidth = Math.max(2, Math.round(view.scale));
            ctx.strokeRect(
                x, y,
                frame.width * view.scale,
                frame.height * view.scale
            );
            ctx.restore();
        }

        function drawFramePreview() {
            const animation = currentAnimation();
            const frame = spriteLayout.frameSize;
            if (!animation || !frame) return;
            if (!framePreviewCanvas) {
                framePreviewCanvas = document.createElement('canvas');
                framePreviewCanvas.width = FRAME_PREVIEW_SIZE;
                framePreviewCanvas.height = FRAME_PREVIEW_SIZE;
                framePreviewCanvas.className = 'frame-preview-canvas';
                elements.framePreview.textContent = '';
                elements.framePreview.appendChild(framePreviewCanvas);
            }
            const previewCtx = framePreviewCanvas.getContext('2d');
            previewCtx.imageSmoothingEnabled = false;
            previewCtx.clearRect(0, 0, FRAME_PREVIEW_SIZE, FRAME_PREVIEW_SIZE);
            const scale = Math.min(
                (FRAME_PREVIEW_SIZE - 12) / frame.width,
                (FRAME_PREVIEW_SIZE - 12) / frame.height
            );
            const drawWidth = frame.width * scale;
            const drawHeight = frame.height * scale;
            previewCtx.drawImage(
                currentImage,
                (animation.columnStart + currentFrameIndex) * frame.width,
                currentRow() * frame.height,
                frame.width, frame.height,
                (FRAME_PREVIEW_SIZE - drawWidth) / 2,
                (FRAME_PREVIEW_SIZE - drawHeight) / 2,
                drawWidth, drawHeight
            );
        }

        function setupAnimations() {
            elements.animList.textContent = '';
            const animations = (spriteLayout && spriteLayout.animations) || [];
            if (!animations.length) {
                const hint = document.createElement('p');
                hint.className = 'hint';
                hint.textContent = 'No animations in this layout';
                elements.animList.appendChild(hint);
                elements.playBtn.disabled = true;
                return;
            }
            animations.forEach((animation, index) => {
                const item = document.createElement('button');
                item.type = 'button';
                item.className = 'anim-item';
                item.dataset.animationIndex = String(index);
                item.textContent = `${animation.name} (${animation.frames} frames @ ${animation.fps}fps, col ${animation.columnStart})`;
                item.addEventListener('click', () => selectAnimation(index));
                elements.animList.appendChild(item);
            });
            elements.playBtn.disabled = false;
            markActiveAnimation(0);
        }

        function markActiveAnimation(index) {
            elements.animList.querySelectorAll('.anim-item').forEach((item, itemIndex) => {
                item.classList.toggle('active', itemIndex === index);
            });
        }

        function selectAnimation(index) {
            if (!spriteLayout || !spriteLayout.animations || !spriteLayout.animations[index]) return;
            stopAnimation();
            currentAnimationIndex = index;
            currentFrameIndex = 0;
            markActiveAnimation(index);
            const animation = currentAnimation();
            setStatus(
                `Animation: ${animation.name} (${animation.frames} frames, ${animation.fps}fps)`,
                'info'
            );
            playAnimation();
        }

        function playAnimation() {
            const animation = currentAnimation();
            if (!animation) {
                setStatus('No animation selected', 'warning');
                return;
            }
            stopAnimation();
            currentFrameIndex = 0;
            animationTimer = window.setInterval(() => {
                currentFrameIndex = (currentFrameIndex + 1) % animation.frames;
                render();
            }, Math.max(16, 1000 / (animation.fps || 8)));
            elements.playBtn.textContent = '⏸ Stop';
            elements.playBtn.classList.add('playing');
            render();
        }

        function stopAnimation() {
            if (animationTimer) {
                window.clearInterval(animationTimer);
                animationTimer = null;
            }
            elements.playBtn.textContent = '▶ Play Animation';
            elements.playBtn.classList.remove('playing');
        }

        function resetAnimation() {
            stopAnimation();
            currentFrameIndex = 0;
        }

        function showDirectionsPanel(show) {
            elements.directionsPanel.classList.toggle('hidden', !show);
            if (show) attachDirectionListeners();
        }

        function attachDirectionListeners() {
            const buttons = elements.directionsPanel.querySelectorAll('.dir-btn');
            buttons.forEach((button) => {
                button.classList.toggle('active', button.dataset.dir === currentDirection);
                button.onclick = () => {
                    currentDirection = button.dataset.dir || 'N';
                    currentFrameIndex = 0;
                    buttons.forEach((item) => item.classList.remove('active'));
                    button.classList.add('active');
                    render();
                    setStatus(`Direction: ${currentDirection}`, 'success');
                };
            });
        }

        async function initialiseFromQuery() {
            const requestedDirection = String(params.get('direction') || '').toUpperCase();
            if (DIRECTIONS.includes(requestedDirection)) {
                currentDirection = requestedDirection;
            }
            const pathParam = params.get('path');
            const assetParam = params.get('assetId');
            if (pathParam) elements.spritePath.value = pathParam;
            if (assetParam) elements.assetId.value = assetParam;
            if (assetParam) {
                await fetchLayout();
            } else if (pathParam) {
                await loadSpritePath(pathParam);
            }
            const play = String(params.get('play') || '').toLowerCase();
            if (play === '1' || play === 'true') {
                if (spriteLayout && spriteLayout.supported) {
                    playAnimation();
                } else if (pathParam && !spriteLayout) {
                    setStatus(
                        'Loaded sheet only; playback requires ?assetId= with a supported layout',
                        'warning'
                    );
                }
            }
        }

        elements.toggleGrid.onclick = () => {
            gridVisible = !gridVisible;
            elements.toggleGrid.classList.toggle('active', gridVisible);
            render();
        };

        elements.zoom.onchange = render;
        elements.loadBtn.onclick = () => loadSpritePath(elements.spritePath.value);
        elements.layoutBtn.onclick = fetchLayout;
        elements.playBtn.onclick = () => {
            if (animationTimer) {
                stopAnimation();
                render();
            } else {
                playAnimation();
            }
        };

        setStatus('Ready — load a sheet, then fetch layout by assetId', 'info');
        render();
        updateDatasets();
        initialiseFromQuery();
    });
})();
