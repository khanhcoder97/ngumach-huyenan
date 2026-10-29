# OPC-08 Asset Preview Tool

Static HTML/CSS/JS preview server (Python stdlib only, no Unity required).

## Quick Start

1. **Create fixtures** (if needed):
   ```bash
   python Tools/AssetPreview/create_fixtures.py
   ```

2. **Start preview server**:
   ```bash
   python Tools/AssetPreview/server.py --root . --port 8080
   ```

3. **Open browser**: http://localhost:8080

4. **Load sprite**: `Client/Assets/Art/Fixtures/synthetics/actor_8dir_test.png`

5. **Fetch layout**: Use asset ID from manifest (e.g., `FIX_ACTOR_8DIR_TEST`)

## Features

### Server (`server.py`)
- Binds to localhost only (path traversal protected)
- API endpoints:
  - `GET /` → preview UI
  - `GET /api/sprites/<path>` → serve PNG images
  - `GET /api/layout/<asset_id>` → calculate grid layout from v2 manifest schema
- Standard library only: `http.server`, `socketserver`, `json`, `pathlib`, `urllib`
- No external dependencies

### UI (`index.html`, `styles.css`, `app.js`)
- Canvas-based sprite sheet viewer
- Nearest-neighbor zoom (1x–8x)
- Grid overlay toggle
- Directional navigation buttons (N, NE, E, SE, S, SW, W, NW)
- Animation playback timeline
- VFX frame-by-frame inspection

## File Structure

```
Tools/AssetPreview/
├── server.py          # HTTP server with API
├── index.html         # Preview UI template
├── styles.css         # Dark theme styling
├── app.js             # Plain JS logic (no frameworks)
├── create_fixtures.py # Generate synthetic PNGs for testing
└── README.md          # This file
```

## Testing Checklist

- [x] Server starts on localhost:8080
- [x] Serve static files without CORS errors
- [x] `/api/sprites/` proxies image requests
- [x] `/api/layout/` returns calculated geometry
- [x] Path traversal blocked (../ rejected)
- [x] Fixtures created: `actor_8dir_test.png` (48×64 × 48 sprites)
- [x] Unity `.meta` format validated
- [x] Zoom and grid rendering functional

## Review Questions

1. Should support URL-based sprites (serve from remote origin)?
2. Add metadata validation warnings in UI?
3. Support multiple viewports for overlap checking?

---

**OPC-08 Implementation** | No Unity | Python stdlib | Localhost only
Refs: #40, OPC-08
