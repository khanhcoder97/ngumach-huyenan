# ClientGodot — Ngũ Mạch: Huyền Ấn, Godot .NET client

The official game client per the owner's decision (DEC-024, approved
2026-11-03) and `docs/production/Godot_Client_Execution_Decision_20261103_vi.md`.
Delivered by Muse under Work Order 24, package **MUSE-GODOT-ALPHA** (M-A
checkpoint: reproducible source handover). PR target:
`codex/story-gameplay-integration-20261031`. Production gates OFF; Codex
reviews and merges.

This is a **partial handover** in the sense of Work Order 24: the full
client source is here, but several runtime assets are still DRAFT-grade —
see `ASSET_MANIFEST.md` (per-group status) and `HANDOVER_CHECKLIST.md`
(what is missing, split into missing-source vs missing-asset).

## Toolchain (pinned)

| Component | Version |
|---|---|
| Godot editor | **4.7.2 stable, mono build** (4.8 is beta and needs .NET 10 — excluded) |
| Export templates | 4.7.2.stable.mono |
| .NET SDK | 8.0.x official Microsoft tarball (apt/Ubuntu SDK breaks publish — do not use) |
| Client target | net8.0, `Godot.NET.Sdk/4.7.2` |
| NuGet | local folder feed only: `../nuget-local` (see its PACKAGES.md) |

## Build / test / export

```bash
# one time: fetch the vendored NuGet feed (offline afterwards)
../nuget-local/fetch_feed.sh

export DOTNET_ROOT=/path/to/dotnet8            # SDK 8 root
export GODOT_BIN=/path/to/Godot_v4.7.2-stable_mono_linux.x86_64

./build.sh           # restore (lockfile) + dotnet build
./test.sh            # 8 offline headless suites; +2 online suites when
                     # NGUMACH_P1_SERVER_DIR points at Qoder's P1 slice
./export_windows.sh  # cold import with timeout+log, then Windows export
```

Android is built **only via CI** (the Muse VM host cannot run the Gradle
daemon — measured CommitLimit ≈ 4 GB, recorded as blocked, never as PASS):
see `.github/workflows/build-android.yml`, manual `workflow_dispatch`.

## Layout

- `project.godot`, `NgumachPrototype.csproj/.sln`, `packages.lock.json`
- `scripts/` — all C# (player, directional animator, tilemap builder,
  HUD, class select, online client, test harnesses)
- `*.tscn` — Main + dedicated test scenes
- `assets/` — runtime art (per-group status in `ASSET_MANIFEST.md`)
- `tools/` — Python pipeline that produced the runtime art data
  (tiledata converters, detail-layer builder, portrait builder)
- `export_presets.cfg` — Linux / Windows Desktop / Android presets.
  Keystore paths are intentionally empty: set them locally or let CI
  generate a debug keystore. A production signing key is the owner's.

## Evidence convention

Every test/export claim for this client must cite: exact source SHA,
toolchain (above), command, and log. Current verified state and its
limits are in `HANDOVER_CHECKLIST.md`.
