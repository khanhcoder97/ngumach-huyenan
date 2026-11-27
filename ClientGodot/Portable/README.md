# Native P1 source bridge

Codex-owned Godot integration dependency for the real P00-01 native slice. This is a portable net8.0 library, with no Godot or Unity runtime dependency.

- Links the existing tracked Client/Assets/Scripts/Online/Core/*.cs without copying or editing them. From this project the path is ../../Client/... .
- Newtonsoft.Json is pinned13.0.1; packages.lock.json is generated and must be tracked.
- vendor/HttpClientTransport.cs is copied unchanged from Git blob at OpenCode PR109 head685b888ae1ac42a314569602e1a4370a783f250c, path Shared/ClientCore/Transport/HttpClientTransport.cs. Its original ownership/provenance header is retained. No unreviewed ClientSession/TimeoutTransport/dispatcher implementation is imported.
- NativeOnlineSession owns one serial worker,8second HTTP timeout, lifetime epoch, command queue and main-thread detached frame publication. It never grants damage/items/quest progress locally.
- Start(baseUrl,scenario:false), SetMove(canonicalDirection), Command(kind,targetId,questId,skillId,aimX,aimY) are called on the Godot main thread. Server positiveY is up. Host code owns world-pixel conversion and map navigation compatibility.
- Command kinds: ACCEPT / INTERACT / TURNIN / RETRY / REFRESH / BASIC_ATTACK / CAST. ACCEPT/TURNIN targetId is NPC_*; INTERACT targetId is the ENT_* entity ID. Combat supports only the portable source's real capabilities, not arbitrary six-skill mock grants.
- FrameReady, ScenarioPassed and ScenarioFailed run via Godot CallDeferred on the main thread. Every frame DTO graph is detached. AcceptedAction/AcceptedSkill are one-publication edges; polls clear them. Events come only from the validated server event stream.
- Scenario mode exclusively owns the movement/command flow and rejects manual commands. It uses public HTTP client API, actual movement and real server rewards. It drops the first successfully committed turn-in reply, verifies pending state, retries the identical body/key, checks exactly-once20COIN+onechest and a separate character's unchanged state. No teleport, private store reflection, fixture grant or server-side seed.
- Parent Godot project must ProjectReference this csproj and remove Portable/**/*.cs from its default Compile set, to prevent compiling linked Core/vendor/generated obj twice.
- Build this library with dotnet build Portable/P1NativeCore.csproj -p:RestoreLockedMode=true after the initial lockfile restore. A native scene test is still required; this dependency alone is not gameplay acceptance.
