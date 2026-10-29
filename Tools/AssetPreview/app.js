// OPC-08: Sprite Sheet Preview - Plain JavaScript (no frameworks)

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('spriteCanvas');
    const ctx = canvas.getContext('2d');
    const statusMsg = document.getElementById('statusMessage');
    const layoutInfo = document.getElementById('layoutInfo');
    const directionsPanel = document.getElementById('directionsPanel');
    const animList = document.getElementById('animList');
    const framePreview = document.getElementById('framePreview');
    const playBtn = document.getElementById('playBtn');
    const toggleGridBtn = document.getElementById('toggleGrid');
    const gridOverlay = document.getElementById('gridOverlay');
    const zoomSelect = document.getElementById('zoomLevel');

    let currentImage = null;
    let spriteLayout = null; // v2 layout from API
    let gridSize = { rows: 1, cols: 1, pixelWidth: 64, pixelHeight: 64 };
    let currentDirection = 'N';
    let currentFrameIndex = 0;
    let animationInterval = null;
    let isGridVisible = true;
    let frameScale = 2;

    // Load sprite sheet
    async function loadSpriteSheet() {
        const pathInput = document.getElementById('spritePath').value.trim();
        if (!pathInput) {
            setStatus('Error: Please enter a sprite sheet path', 'error');
            return;
        }

        setStatus(`Loading sprite: ${pathInput}...`);
        
        try {
            const response = await fetch(`/api/sprites/${encodeURIComponent(pathInput)}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const blob = await response.blob();
            currentImage = await loadImage(blob);
            
            ctx.drawImage(currentImage, 0, 0);
            updateDisplaySize();
            setStatus(`Loaded: ${pathInput}`, 'success');
            showDirectionsPanel(false);
            showAnimList([]);
            resetAnimation();
            
        } catch (err) {
            console.error(err);
            setStatus(`Failed to load: ${err.message}`, 'error');
        }
    }

    function loadImage(blob) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = URL.createObjectURL(blob);
        });
    }

    function updateDisplaySize() {
        const zoom = parseInt(zoomSelect.value);
        frameScale = zoom * 2; // Scale by zoom + base scale
        
        if (currentImage) {
            canvas.width = currentImage.width * zoom;
            canvas.height = currentImage.height * zoom;
            drawCurrentFrame(zoom);
        }
    }

    // Fetch layout from manifest metadata
    async function fetchLayout() {
        const assetId = document.getElementById('assetId').value.trim();
        if (!assetId) {
            setStatus('Error: Asset ID required', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/layout/${encodeURIComponent(assetId)}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            spriteLayout = await response.json();
            
            displayLayoutInfo(spriteLayout);
            calculateGridSize();
            setupAnimations();
            showDirectionsPanel(spriteLayout.directional);
            setStatus(`Layout loaded for ${assetId}`, 'success');
            
        } catch (err) {
            console.error(err);
            setStatus(`Failed to fetch layout: ${err.message}`, 'error');
        }
    }

    function displayLayoutInfo(layout) {
        layoutInfo.classList.remove('hidden');
        layoutInfo.innerHTML = JSON.stringify(layout, null, 2);
        
        gridSize = layout.grid;
        ctx.drawImage(currentImage, 0, 0);
        drawGrid();
    }

    function calculateGridSize() {
        const zoom = parseInt(zoomSelect.value);
        canvas.width = gridSize.pixelWidth * zoom;
        canvas.height = gridSize.pixelHeight * zoom;
        drawCurrentFrame(zoom);
    }

    function drawCurrentFrame(zoom = 1) {
        if (!currentImage || !spriteLayout) return;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw full sprite sheet scaled
        ctx.drawImage(currentImage, 
            0, 0, currentImage.width, currentImage.height,
            0, 0, canvas.width, canvas.height
        );
        
        // Highlight current direction frame
        if (spriteLayout.directional) {
            drawDirectionHighlight(zoom);
        }
    }

    function drawDirectionHighlight(zoom) {
        if (!spriteLayout.animations) return;
        
        const dirIndex = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'].indexOf(currentDirection);
        if (dirIndex === -1) return;
        
        const colsPerDir = 8;
        const frameY = dirIndex * spriteLayout.animations[0].frames;
        const x = 0;
        const y = frameY * (gridSize.pixelHeight / colsPerDir);
        
        ctx.strokeStyle = '#fc913e';
        ctx.lineWidth = 2 * zoom;
        ctx.strokeRect(x * zoom, y * zoom, 
            gridSize.pixelWidth * zoom, 
            (gridSize.pixelHeight / colsPerDir) * zoom
        );
    }

    function drawGrid() {
        const zoom = parseInt(zoomSelect.value);
        
        ctx.strokeStyle = 'rgba(124, 143, 191, 0.5)';
        ctx.lineWidth = 1;
        
        // Vertical lines
        for (let col = 0; col <= gridSize.cols; col++) {
            const x = col * (gridSize.pixelWidth / gridSize.cols) * zoom;
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        }
        
        // Horizontal lines
        for (let row = 0; row <= gridSize.rows; row++) {
            const y = row * (gridSize.pixelHeight / gridSize.rows) * zoom;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        }
    }

    function setupAnimations() {
        animList.innerHTML = '';
        
        if (spriteLayout.animations) {
            spriteLayout.animations.forEach((anim, index) => {
                const item = document.createElement('div');
                item.className = 'anim-item';
                item.textContent = `${anim.name} (${anim.frames} frames @ ${anim.fps}fps)`;
                item.onclick = () => selectAnimation(index);
                animList.appendChild(item);
            });
        }
        
        playBtn.disabled = false;
    }

    function selectAnimation(index) {
        resetAnimation();
        
        if (!spriteLayout.animations) return;
        
        const anim = spriteLayout.animations[index];
        
        playBtn.textContent = `⏸ Stop`;
        
        // Play animation loop
        animationInterval = setInterval(() => {
            if (spriteLayout.directional) {
                // Directional: each animation is one direction
                // Frame cycles through frames in that direction
            } else {
                // Strip: single animation across all frames
                const totalFrames = spriteLayout.grid.cols;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                const frameWidth = (spriteLayout.grid.pixelWidth / totalFrames);
                const frameX = (currentFrameIndex * frameWidth) * (parseInt(zoomSelect.value));
                
                // Draw only current frame
                const zoom = parseInt(zoomSelect.value);
                ctx.drawImage(currentImage,
                    currentFrameIndex * (gridSize.pixelWidth / gridSize.cols), 0,
                    gridSize.pixelWidth / gridSize.cols, gridSize.pixelHeight,
                    frameX, 0,
                    frameWidth * zoom, gridSize.pixelHeight * zoom
                );
                
                currentFrameIndex = (currentFrameIndex + 1) % totalFrames;
            }
        }, 1000 / (anim.fps || 8));
    }

    function resetAnimation() {
        if (animationInterval) {
            clearInterval(animationInterval);
            animationInterval = null;
        }
        currentFrameIndex = 0;
        playBtn.textContent = '▶ Play Animation';
    }

    function showDirectionsPanel(show) {
        if (show) {
            directionsPanel.classList.remove('hidden');
            attachDirectionListeners();
        } else {
            directionsPanel.classList.add('hidden');
        }
    }

    function attachDirectionListeners() {
        const buttons = directionsPanel.querySelectorAll('.dir-btn');
        buttons.forEach(btn => {
            btn.onclick = () => {
                currentDirection = btn.dataset.dir;
                
                // Update UI
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Redraw with highlight
                const zoom = parseInt(zoomSelect.value);
                drawCurrentFrame(zoom);
                
                setStatus(`Selected direction: ${currentDirection}`, 'success');
            };
        });
    }

    function showDirectionsPanel(show) {
        const panel = document.getElementById('directionsPanel');
        if (show) {
            panel.classList.remove('hidden');
        } else {
            panel.classList.add('hidden');
        }
    }

    function showAnimList(items) {
        const list = document.getElementById('animList');
        if (items.length === 0) {
            list.innerHTML = '<p class="hint">Load a layout to see animations</p>';
        }
    }

    function setStatus(message, type = 'info') {
        const el = document.getElementById('statusMessage');
        el.textContent = message;
        
        el.style.borderLeftColor = {
            success: 'var(--success)',
            error: 'var(--error)',
            warning: 'var(--warning)'
        }[type] || 'var(--accent)';
    }

    // Toggle grid overlay
    toggleGridBtn.onclick = () => {
        isGridVisible = !isGridVisible;
        gridOverlay.classList.toggle('show', isGridVisible);
        toggleGridBtn.classList.toggle('active', isGridVisible);
    };

    // Zoom change
    zoomSelect.onchange = updateDisplaySize;

    // Event bindings
    document.getElementById('loadBtn').onclick = loadSpriteSheet;
    document.getElementById('layoutBtn').onclick = fetchLayout;
    playBtn.onclick = () => {
        if (animationInterval) {
            resetAnimation();
        } else {
            const items = animList.querySelectorAll('.anim-item');
            if (items.length > 0) {
                items[currentFrameIndex].click();
            }
        }
    };

    // Initialize with default values
    setStatus('Ready - Press "Load" then "Fetch Layout"', 'info');
    
    // Prevent default form submissions
    document.querySelectorAll('form').forEach(f => f.preventDefault());
});
