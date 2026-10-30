# NGUMACHHUYENAN - Original MMORPG Project

## Bản Bến Mưa có thể chơi ngay trên máy yếu

Nhấp đúp **CHOI_THU.cmd** hoặc chạy `python Tools/PlayablePreview/server.py --open`, rồi mở http://127.0.0.1:8090. Cần Python3.10+, không cần Unity/.NET/npm. Có sprite8hướng Minh Kiếm ứng viên Muse, bản đồ pixel blockout,5nhiệm vụ mở đầu, đánh quái/guard/dodge/skill, boss3đòn, nhạc/SFX, hành trang, hồi sinh và save trong trình duyệt.

Đây là **bản chơi thử một người cục bộ**, dùng Canvas để kiểm gameplay ngay; dự án production vẫn dùng Unity và server Qoder. Map/quái procedural và một số số liệu là fixture có nhãn, không đồng nghĩa asset/topology/balance được duyệt hoặc MMO đã hoàn tất. Hướng dẫn/nguồn/giới hạn: [Bến Mưa playtest](Tools/PlayablePreview/README_vi.md).

## Project Overview

A new original MMORPG project with design documents stored in `docs/production` as the source of truth.

## Graphics Direction

The project uses original 2D pixel art. Follow [`docs/production/Pixel_Art_Production_Standard_vi.md`](docs/production/Pixel_Art_Production_Standard_vi.md): 640×360 logical render, 20 PPU, integer scaling, point filtering, lossless sprite assets, frame-based animation, tilemaps and pixel-art UI. Previous vector concepts are archived outside Unity Assets and are not runtime art.

The Unity client uses URP's built-in Pixel Perfect Camera (URP 17.3); do not add the separate Built-in Render Pipeline `com.unity.2d.pixel-perfect` package. Source sprites placed under `Client/Assets/Art/` or `Client/Assets/UI/Art/` receive the point-filter, lossless, no-mipmap 20 PPU import defaults from the editor asset postprocessor.

## Current Code Layout

### Client (Unity)
- Unity Editor 6000.3.17f1 (Unity 6.3 LTS) project with URP 17.3.0
- Title bootstrap implementation
- **Start button stays disabled until P1 implementation; server status is informational only**

### Server (ASP.NET Core)
- `Server/Health/Health.csproj` - Health endpoint implementation
- Net10.0 runtime
- Provides `/health` GET endpoint

### Content Definitions
- `Implementation/Content/Schemas/` - Seven JSON schemas: Class, Skill, Item, Map, Spawn, GatheringNode, Quest
- `Implementation/Content/Examples/` - Valid examples linked to production IDs
- `Implementation/Content/map_bounds.json` - 46-map bounds registry (standard 360x72 WU; `MAP_THANG_LONG` 900x96)

### P1 Contracts
- `Implementation/Contracts/P1/` - Eight transport-independent JSON schemas: envelope, move intent, combat input, world snapshot, combat event, quest state, inventory snapshot, teleport request
- `Implementation/Contracts/P1/Examples/` - Valid examples linked to P1 content IDs and map bounds

### Implementation Tools
- `Implementation/Tools/validate_content.py` - Content validation tool
- Checks manifest row count, required fields, IDs, foreign keys, map bounds, definition schemas and example references
- `--report PATH` writes a machine-readable JSON report for content-owner review
- Last saved report: `Implementation/Reports/P0_content_validation.json` (generated before the 2026-10-26 P00-01 turn-in NPC correction; rerun before content lock)
- `Implementation/Tools/validate_contracts.py` - P1 contract/example validation tool
- Checks schema shape, ID references, map bounds, combat/quest/inventory semantics
- Saved report: `Implementation/Reports/P1_contract_validation.json`
- `Implementation/Tools/json_schema.py` - Shared minimal JSON Schema subset validator

## Local Development Setup

### Prerequisites
- **Note**: Unity and .NET are not available in this environment, so builds/imports are not verified

### Startup Commands
1. **Validate content**:
   ```bash
   python Implementation/Tools/validate_content.py
   ```

2. **Validate P1 contracts**:
   ```bash
   python Implementation/Tools/validate_contracts.py
   ```

3. **Run server health check**:
   ```bash
   dotnet run --project Server/Health/Health.csproj
   ```

4. **Open Unity client**:
   - Open `Client` folder in Unity Hub
   - After Unity finishes importing packages, run `Tools > Ngũ Mạch > Initialize Pixel Art Project` once. This creates a URP 2D asset and a startup scene without replacing an existing scene.
   - Run `Tools > Ngũ Mạch > Create Pixel Art Smoke Scene` to create a disabled calibration scene with a 16×16 tilemap and a generated placeholder sprite; this is technical test art, not production art.
   - Set `Client/Assets/Resources/client-config.json` `healthUrl` to the reachable `/health` endpoint for your local server. For an Android emulator or phone, use the host address reachable from that device instead of `127.0.0.1`.

## Status Notes

- Server status is local development only
- Unity MMO gameplay still requires engine/integration evidence; the standalone Bến Mưa local playtest above is playable without Unity/.NET.
- Title start button stays disabled until P1; its server status display is informational
- P0 content foundation is in place: seven definition schemas, examples, map bounds and cross-reference validation
- `validate_content.py` passes with 349 manifest rows, resolved IDs/references and map bounds
- `TOOL-ROD-01` was added to `Item_Master_Catalog_vi.csv` with owner approval to close the canonical item gap
- P1 transport contracts and examples validate against current content IDs and map bounds
- No gameplay or economy code changes implemented yet; project-wide pixel-art direction is documented in `docs/production/Pixel_Art_Production_Standard_vi.md`
- No Unity/.NET builds or runtime tests performed

## Documentation

For detailed design and implementation information, refer to `docs/production` folder.
