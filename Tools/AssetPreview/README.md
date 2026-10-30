# OPC-08 Asset Preview Tool

Local, read-only sprite preview server (Python stdlib only, no Unity required).

## Quick start

```bash
# 1. Regenerate the deterministic 288x512 / 6-column x 8-row fixture
python Tools/AssetPreview/create_fixtures.py

# 2. Start the preview server confined to the repository root
python Tools/AssetPreview/server.py --root .

# 3. Open http://127.0.0.1:8080
```

The default manifest is `Client/Assets/ArtManifests/muse_delivery_manifest.json`.
Use `--manifest Tools/AssetPreview/fixtures/preview_manifest.json` for the
synthetic fixture.

## URL parameters

The UI also accepts a reproducible deep link:

```
http://127.0.0.1:8080/?assetId=CHR_MINH_KIEM_WALK\
&path=Client/Assets/Art/Characters/MinhKiem/minh_kiem_walk.png\
&direction=SW&play=1
```

* `assetId` loads `/api/layout/<assetId>` and then the manifest image.
* `path` loads a sheet directly when no `assetId` is supplied.
* `direction` must be one of `N, NE, E, SE, S, SW, W, NW`.
* `play=1` starts the selected animation after a supported layout loads.

## Features

### Server (`server.py`)

* Binds to the requested host (default `127.0.0.1`) and confines every path to
  `--root`; there is no working-directory fallback.
* Percent-decodes each API path exactly once, rejects NUL, absolute/drive/UNC
  paths and `..`/symlink escapes, and serves only PNG/JPEG/GIF/WebP.
* No wildcard CORS header.
* Endpoints:
  * `GET /` → preview UI
  * `GET /styles.css`, `GET /app.js` → static UI files
  * `GET /api/sprites/<encoded path>` → image bytes
  * `GET /api/layout/<assetId>` → truthful layout JSON

### Layout semantics

* Legacy v1 manifests (no `manifestVersion`) derive frame width from
  `pixelWidth / framesPerDirection` and frame height from
  `pixelHeight / directionCount`.
* Real Muse asset `CHR_MINH_KIEM_WALK` therefore reports
  **6 columns × 8 rows**, `48×64` per frame, `288×512` total.
* v2 manifests must declare `frameSize`; a missing/inconsistent field returns
  `supported: false` with explicit `unsupportedReasons`. The server never
  invents an 8×6 or 6×8 grid.
* `columnStart`/`columnEnd` animation ranges are honoured by the selection
  rectangle, frame preview and playback.
* Lookup prefers the canonical `assetId`; the legacy `id` field still works but
  emits a warning.

### UI (`index.html`, `styles.css`, `app.js`)

* Fixed **720×560** canvas viewport with nearest-neighbour rendering.
* Grid overlay, zoom, direction rows and per-frame preview.
* Animation list and real interval playback (`fps`, `columnStart`).
* Avoids stale state: manually loading a new sheet clears the previous layout,
  animations and direction selection.
* Publishes machine-readable state on `<body>` for browser smoke checks:
  `data-layout-supported`, `data-layout-cols`, `data-layout-rows`,
  `data-frame-width`, `data-frame-height`, `data-current-direction`,
  `data-current-frame`, `data-animation`.

## Verification

```bash
# Unit + HTTP integration tests
python -m unittest discover -s Tools/AssetPreview/tests -v

# Real headless browser check (DOM state + screenshot evidence)
python Tools/AssetPreview/browser_smoke.py \
  --manifest Client/Assets/ArtManifests/muse_delivery_manifest.json \
  --asset-id CHR_MINH_KIEM_WALK \
  --path Client/Assets/Art/Characters/MinhKiem/minh_kiem_walk.png \
  --direction SW \
  --screenshot preview-evidence.png
```

The browser check verifies six columns, eight rows, `48×64` frames, the selected
direction and `walk` playback, then saves a screenshot. It is a UI smoke test,
**not** Unity import or runtime playback proof.

## File structure

```
Tools/AssetPreview/
├── server.py              # HTTP server + layout logic
├── index.html             # Preview UI
├── styles.css             # Dark theme
├── app.js                 # Plain JS (no frameworks)
├── create_fixtures.py     # Deterministic 6x8 fixture generator
├── browser_smoke.py       # Optional headless Chrome/Edge evidence
├── fixtures/              # Generated PNG/.meta/manifest
├── tests/                 # unittest + HTTP integration tests
└── README.md
```

## Limits

* The preview is a static/visual tool; it does not prove Unity compile,
  animation import or in-game playback.
* Layout support covers `direction_rows` and `strip` sheets. Other layouts are
  reported unsupported rather than guessed.
* JPEG/GIF/WebP are served read-only but layout maths assumes atlas geometry
  declared by the manifest.

---

**OPC-08 Implementation** | No Unity | Python stdlib | Localhost only
Refs: #40, OPC-08
