# ClientCore — adoption matrix & source dependency closure (2026-11-12)

Gói39 O39-D. Tài liệu ghi nhận mức độ áp dụng theo từng module của client portable
(`Shared/ClientCore`), closure source-level (file nào phụ thuộc file nào), và những
hạng mục chưa được chứng minh. Đây không phải là capability change, không đặt
production budget, không tuyên bố low-device performance; license first-party giữ
**UNSPECIFIED** (thêm LICENSE thuộc quyết định chủ dự án, không chặn sửa source
hay đo đạc). Production OFF; không sửa compiler pipeline/Godot/server/media assets;
host engine VFX/HUD/widget thuộc Codex.

## 1. Adoption matrix theo module

Acceptance evidence (2026-11-12): unit Release 336/336; paired gates-off local
**102 assertions exit 0** (1 UNVERIFIED: encounter route unmapped) và private-alpha
local **272 assertions exit 0** tại head `b98b3ee`+`7644591` (UNVERIFIED: encounter
live/DEFEATED typed reads với raw body evidence, portal-positive shape, consume
405 / map-viewed 405 / escort 404 — tất cả route từ pin server `4cada354` chưa map,
+ B-C wire finding ở Q39-B). Branch: `opencode/opc-15-godot-client-core-20261103`.
CI xanh cho từng block theo báo cáo handoff tương ứng (#85, PR #109).

| Module | Source (portable) | Dependency | Owner | Trạng thái adoption | Coverage |
|---|---|---|---|---|---|
| P1 wire client + models | `Client/Assets/Scripts/Online/Core/P1Client*.cs`, `P1Models*.cs`, `P1Wire.cs`, `P1Narrative.cs`, `P1Audio*.cs`, `P1GameplayInputGate.cs`, `CombatTraceFactory.cs` (compiled in via explicit includes) | net8.0, Newtonsoft.Json 13.0.1 | OpenCode | **Adopted** (core); engine transport binding = host | Unit 336; runner paired journey; Sample |
| Composition (session, epoch, carry) | `Shared/ClientCore/Composition/*` | P1 wire client | OpenCode | **Adopted**; relogin monotonic epoch + pending carry qua relogin | Unit + runner A/B relogin legs |
| Encounter read model (snapshot/validator/state/view) | `Shared/ClientCore/Encounter/*` | Guards, net8.0 | OpenCode | **Adopted at view layer** (parse strict, apply/commit, event gate); **runtime UNVERIFIED** — live typed read bị chặn bởi server wire off-contract (moveCooldownRemainingTicks camelCase `{"a","b","c"}` vs contract bắt buộc `["A","B","C"]`, schema `EncounterSnapshotV1.schema.json` pin `4cada354`); foreign-owner negative PASS; DEFEATED read UNVERIFIED cùng lý do | Unit (parse/apply/stale), runner active-window probe (UNVERIFIED + raw body) |
| Encounter VFX binder | `Shared/ClientCore/Encounter/EncounterVfxBinder.cs` | Encounter view | OpenCode | **Renderer-neutral only**; engine VFX/timing = Codex | Unit (reducedMotion, deadline); Sample stub flow |
| Guards (stale response, receipt replay) | `Shared/ClientCore/Guards/*` | net8.0 | OpenCode | **Adopted**; cross-session replay rejected, replay after commit rejected | Unit + runner A/B replay legs |
| Handshake / capability | `Shared/ClientCore/Handshake/*` | net8.0 | OpenCode | **Adopted**; production-off default, no route advertised by default | Unit + runner availability checks |
| Tutorial progress | `Shared/ClientCore/Tutorial/TutorialProgress.cs` | net8.0 | OpenCode | **Adopted**; server-authoritative unlock (no client-side unlock) | Unit + runner P00-01..05 legs |
| Dispatch | `Shared/ClientCore/Dispatch/MainThreadDispatcher.cs` | net8.0 | OpenCode | **Interface adopted**; SynchronousDispatcher (headless); Godot dispatcher = Codex | Unit via SynchronousDispatcher |
| Catalog | `Shared/ClientCore/Catalog/FileProvider.cs` | net8.0 | OpenCode | **Present in core**; not separately benchmarked; coverage gián tiếp qua suite | Suite (where used) |
| Transport (HTTP) | `Shared/ClientCore/Transport/HttpClientTransport.cs`, `TimeoutTransport.cs` | net8.0, System.Net.Http | OpenCode | **Adopted** cho HTTP host binding; host Godot có thể dùng assembly này hoặc bind transport riêng qua `IP1Transport` | Sample stub; runner `Http` |
| Media playback metadata bridge | `Client/.../Presentation/MediaPlaybackMetadata.cs`, `MediaPlaybackPresenter.cs` | Newtonsoft.Json 13.0.1 | OpenCode | **Adopted** (strict PLAYBACK_METADATA_v1 parser, canonical containment, embedded/alternate/review-only typed rules, real Muse fixtures b1472f2); host player/widget binding = Codex | Unit (8 fixture-backed) + Sample real-metadata run |
| Presenters khác (Inventory V2, NpcDialogue, Talk, Portal, QuestJournal, Map, MapViewed, Escape, DeathReturn, Character, Cinema, HUD*, Settings, …) | `Client/.../Presentation/*` | P1 wire client; một số `IP1UIAdapter` host-boundary interfaces | OpenCode (typed/read-model + boundary) | **Adopted at typed layer**; VFX/HUD/UX/camera = Codex | Unit (subsets) + runner FT legs (inventory v2, talk, portal far/locked, escort audience) |
| Escort (provenance gate) | `Client/.../Presentation/EscortPresenter.cs` | v2 read model | OpenCode | **Adopted with provenance gate (O39-A)**: owner chỉ bind từ EscortPacket đã duyệt (`BindEscortPacket`), không substring/coordinate inference; giữ unsupported/not-served khi thiếu provenance; route escort-current chưa pin → UNVERIFIED | Unit (6 escort provenance tests) + runner AOI/escort legs |
| ClientCore.Tests | `Shared/ClientCore.Tests/*` | xUnit (test-time only) | OpenCode | **Adopted**: 336 tests | — |
| ClientCore.HttpRunner | `Shared/ClientCore.HttpRunner/*` | ClientCore, System.Net.Http, Python 3 | OpenCode | **Adopted**: gates-off + private-alpha acceptance, fingerprint fail-closed (5 runtime bundles + alpha baseline), negative controls | Local run output; CI matrix 2 modes |
| ClientCore.Sample | `Shared/ClientCore.Sample/*` | ClientCore | OpenCode | **Adopted**: stub-transport flow + real Muse metadata/provenance section (script runs, output committed to handoff) | Runs clean (see below) |
| ClientCore.Bench | `Shared/ClientCore.Bench/*` | ClientCore | OpenCode | **Adopted (measurement only)**: env/SDK report, fixture sha256 provenance, parse/event-gate/lane-poll distributions | Runs clean (see below) |

## 2. Source dependency closure (client portable)

- **Language/runtime**: net8.0 for portable assemblies (ClientCore, Tests, Runner,
  Sample, Bench). No Godot SDK, no Unity, no native dependencies, no platform-specific
  code paths. Deterministic builds (`Deterministic=true`, symbols off for pack).
- **Compile closure**: `ClientCore.csproj` uses `EnableDefaultCompileItems=false` and
  explicit includes — `Encounter/*.cs`, `Guards/*.cs`, `Handshake/*.cs`, `Dispatch/*.cs`,
  `Tutorial/*.cs`, `Composition/*.cs`, `Catalog/*.cs`, `Transport/*.cs`, plus
  `Client/Assets/Scripts/Online/Core/*.cs` and `.../Presentation/*.cs` **by file**, so a
  change anywhere in the closure is a build/test change — there is no hidden re-compile
  of engine assets. The Godot tree keeps its sources; the portable assembly consumes them.
- **External packages**: Newtonsoft.Json 13.0.1 (core/presenters; covered in
  `THIRD-PARTY-NOTICES.md`), xUnit (tests only), nothing else. No licenses were added.
- **Closure boundary**: Godot scenes/widgets/graphics/VFX assets, server code, Muse
  media, pipeline/compiler — explicitly out of scope (owner lanes noted above).

## 3. Evidence produced this round (2026-11-12)

Sample (stub transport, no P1_BASE_URL) — real Muse delivery, pin b1472f2:

```
document: manifest=NGM_PLAYBACK_METADATA_V1 scenes=21 embeddedSoundtrack=21 silent=0
provenance: sha256:91d1c55182d6aa3cc0389a4262e914090363097f25db7a9bef9a502a3fc0c133 manifest=PLAYBACK_METADATA_v1.json
srt CIN_000_vi.srt: cues=6 success=True
srt CIN_001_vi.srt: cues=1 success=True
policy: real delivery canonical in-root=True traversal refused=True
sample OK
```

Bench (fixed workload, warm-up, distribution, provenance), excerpt:

```
framework: .NET 10.0.14 os: Windows 10.0.19045 (X64) cores=4 gc: serverGC=False
may provide different numbers on any other machine — measurement-only run:
encounter-parse n=2000  p50/p90/p99/mean alloc/op=28357 B
media-parse     n=200    p50/p90/p99          alloc/op≈734847 B
srt-parse       n=2000   p50/p90/p99          alloc/op=26638 B
apply+commit    n=500    new-cast delivered=500 (exactly once), duplicate re-apply ×1000 → 0 re-deliveries
encounter lane/poll burst=4 delayMs=2 rounds=100: reads=400, peak in-flight (backlog)=4, updates=400, new-cast=400
```

## 4. Not proven / not ours

- Encounter live typed read (owner and DEFEATED): off-contract server wire (Q39-B);
  foreign 404 negatives PASS; client parser frozen by design.
- Portal wire (Qoder Q39-B), consume/MAP_VIEWED/escort routes (Qoder work35/Q39-C).
- License: first-party UNSPECIFIED; not blocking source or measurement.
- Low-device performance: not claimed by this document or the bench; requires Codex
  native/device measurement. Bench = portable proxy evidence only.
- Relogin/queued-owner regressions remain green at the paired acceptance level
  (B expiry on mutation rejected, B relogin monotonic epoch, pending carried across
  relogin, retry same key after relogin, replay after commit rejected, A/B
  cross-session replay rejected).
