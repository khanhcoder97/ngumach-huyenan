# DEC-024 — Proposed patch (Muse draft for Codex to apply)

Status: **draft proposal**. The project owner approved DEC-024 (Godot .NET
as the official client) on 2026-11-03; the decision text lives in
`docs/production/Godot_Client_Execution_Decision_20261103_vi.md`. Per Work
Order 24 M-A, Muse submits the proposed register patch and line edits;
Codex applies them. Historical documents are NOT bulk-rewritten — old
Unity text stays as history, per the Execution Decision.

## Proposed register entry (append to Production_Decision_Register_vi.md)

| DEC-024 | Client engine: **Godot .NET 4.7.2 stable (mono)** is the sole official client, Windows first, Compatibility renderer. The Unity client line is closed; Unity sources and PR #22 are kept as historical reference only, not deleted or closed by agents. Server and contracts remain engine-independent and unchanged by this decision. Client source is delivered in `ClientGodot/`; asset production continues under the locked pixel standard (640×360 logical, 20 PPU, Point filter). | Owner decision 2026-10-31 (final) + version lock 4.7.2 (2026-10-31); execution detail in `Godot_Client_Execution_Decision_20261103_vi.md`; delivery per Work Order 24 (MUSE-GODOT-ALPHA). Supersedes the client-runtime part of DEC-001. |

## Line edits (surgical, not bulk)

1. `Production_Decision_Register_vi.md`, DEC-001 row: append to its status
   — "Phần client runtime được thay thế bởi DEC-024 (Godot .NET); các phần
   còn lại giữ làm lịch sử." (The 6.3 LTS/URP/Pixel Perfect wording itself
   is left untouched as the historical record.)
2. Any *current* (non-historical) runtime instruction that names Unity as
   the client to build must point to DEC-024 instead. Known candidates
   for Codex to confirm: `AI_Agent_Implementation_Plan_vi.md` (active-plan
   sections only). Handoff/review documents dated ≤ 2026-10-31 are
   historical and stay as-is.
3. No change to: server stack (ASP.NET Core), contracts/schemas, canonical
   IDs, the alpha design baseline
   (`Implementation/Content/DesignBaselines/ben_mua_alpha_20261103.json`),
   or the pixel-art production standard.

## Notes for the reviewer

- The 4.7.2 lock is deliberate: 4.8 is beta and requires .NET 10; the
  client targets net8.0 / SDK 8.0.x. Do not "upgrade" the lock as part of
  applying this patch.
- Android/iOS C# support in Godot 4 is experimental (Execution Decision);
  DEC-024 commits the alpha to Windows first, Android via CI with a real
  APK artifact as the only PASS evidence. No web build is promised.
