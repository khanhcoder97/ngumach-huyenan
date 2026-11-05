# QOD-24 - the pet and mount table, read for the first time (2026-11-06)

Work order: the owner's standing instruction while decisions are pending is "make
progress against the spec, keep production off, do not invent numbers". This is the
fourth pass of that method: enumerate `docs/production/*.{csv,md}` against what the
server and the tools actually read, then read what is missing.

`docs/production/Pet_Mount_Production_Data_vi.csv` was the last table no loader read.
Earlier passes covered `Elite_Variant_Data_vi.csv` + `NPC_Actor_Production_Registry_vi.csv`,
`Loot_Recipe_Reward_Production_Data_vi.csv`, `Class_Passive_Production_Data_vi.csv`,
`Currency_Production_Data_vi.csv`, `Life_Sim_Content_Data_vi.csv` and
`Weekly_Boss_Rotation_Data_vi.csv`, and `Map_Production_Atlas_vi.md` through
`Implementation/Tools/reconcile_map_atlas.py`. After this commit the unread list is empty.

## 1. What shipped

- `Server/Health/Gameplay/Pets/CompanionCatalog.cs` - a strict reader for the 23 columns
  and 10 rows. Closed sets, not prefixes: the two combat rules, the two slot strings, the
  two leash strings, the companion XP rule, the five elements (plus the literal `COSMETIC`
  that only mounts may use) and the rarity vocabulary. Type-correctness rules: a companion
  must carry a `PET_SKILL_*`/`PET_PASSIVE_*` pair with effects, a level list, a positive
  leash range and a feed item with a positive cooldown; a mount must carry none of those,
  range 0 and empty feed columns. `feed_stat` must contain "cosmetic", so a row that makes
  feeding grant a stat fails startup.
- Registered in the composition root (`Server/Health/Program.cs:150` area) and logged at
  boot. Seven `companion.*` self-checks pin the cross-file facts.
- **No route, no gate, no wire field, no `docs/production/**` edit, no topology
  `reviewState` change.** `appsettings.json` is untouched.

Measured at this head: `--self-check` **563 passed, 0 failed** (was 556 before this
commit); the boot line reads `Loaded pet and mount table: 5 companions (leash 8 WU, fed
every 12h for cosmetics only) and 5 cosmetic mounts (no combat)`.

## 1b. A measurement I have to correct the same day

While verifying this boot line I ran `smoke_p1.py` against the same Release build with the
same five CI gates, twice from different start-up directories:

- ContentRoot `Server/Health` (what CI uses): **358** checks.
- ContentRoot = repository root: **453** checks, twice (453, 453; one earlier run said 454).

Nothing else differed: same binary, same `P1__QuestAccept/Interact/QuestTurnIn/CombatV2/
CombatDamage=true`, same worktree. So `appsettings.json` not being the configuration
source changes roughly ninety smoke assertions. I had started from the assumption that a
gate must be defaulting ON; the two candidates I checked say otherwise and I am recording
that instead of a story:

- `Server/Health/Gameplay/Alpha/AlphaProfile.cs:19` - `AlphaProfileOptions.Enabled` has no
  initializer, so it defaults to `false`. The startup line `Loaded alpha profile
  DESIGN-BM-ALPHA-20261103` prints whether or not the gate is on (the profile is validated
  at startup by design), so it is **not** evidence that the alpha profile was enabled.
- No `P1:*` gate in the server code carries a `= true` default.

What is still true, and is the reason this is in the report: **the published smoke total
is only meaningful together with the start-up directory.** CI pins it by using
`working-directory: Server/Health`; a local run from the repo root measures a different
suite. My README claim ("smoke 358, measured twice on a fresh server") should be read as
"358 with the CI start-up directory". The follow-up I have not done yet is to enumerate
which `appsettings.json` keys change route mapping or fixture state between those two
boots, and to make the suite report one number regardless of the directory it is run from.


## 2. What the two approved sources say about the same ids

Every `item_template_id` in the pet table exists in `Item_Master_Catalog_vi.csv`. Both
files name a **different creature** for all 10 shared ids:

| id | pet table | item catalogue |
| --- | --- | --- |
| `PET-01` | Moc Linh | Cao Tro |
| `PET-02` | Mua Ngau | Rua Rey |
| `PET-03` | Thach Cau | Chim Suong |
| `PET-04` | Hoa Ho | Meo Mua |
| `PET-05` | Tuyet Yen | Thon Lan Da |
| `MOUNT-01` | Bach Ma | Ca Chep Mua |
| `MOUNT-02` | Linh Huou | Huu Re Non |
| `MOUNT-03` | Hoa Loan | Thon Lan Sa Hoa |
| `MOUNT-04` | Thuy Long | Son Thu Tran Thanh |
| `MOUNT-05` | Thach Tuong | Ca Duoi Lam |

(The table above is written without diacritics on purpose: the names are printed by the
check from the source files, and the check's detail line carries the exact text.)

The species differ, not just the label: `PET-01` is a fox in one file and a plant-spirit
name in the other, `MOUNT-01` is a horse versus a fish. This is not a rounding
disagreement - two approved files describe different content under one id.

Four further cross-file facts, each now a CI check:

1. The catalogue's `element` column is blank for all 10 rows; only the pet table states an
   element (five elements for companions, `COSMETIC` for mounts).
2. No item in either catalogue occupies a `PET_HEAD`/`PET_ARMOR`/`PET_COLLAR`/
   `PET_SADDLE`/`MOUNT_SADDLE` slot - the catalogue's own slot cells are `Pet summon` /
   `Mount summon`, and the pet table itself says the four pet slots are "appearance slots
   only; no stat item in baseline". So the slots exist in the source and nothing fills
   them: 0 rows.
3. All five mount rows are impossible as written: `level_cap 1` in the pet table against
   `required_level 10` in the catalogue. There is no level at which the item is usable and
   the mount is under cap.
4. The two sources agree on exactly one rule: mount travel `+10%` out of combat, disabled
   in combat/PvP/instance. For the five companions the catalogue value column carries the
   placeholder `Pet passive` - no number at all - while the pet table states a concrete
   effect (`+3% gather speed`, `+2% water resistance`, `+2% PvE damage reduction`, `+2%
   forge material yield; non-stack`, `+3% minimap reveal radius`).

And a gap rather than a conflict: the ten `PET_SKILL_*`/`PET_PASSIVE_*` ids appear in no
other `.csv`/`.md` under `docs/production/`. They are named in one table and defined
nowhere - same shape as the elite-variant and gear-stat gaps.

## 3. Decisions I need before any companion can be implemented

Nothing here is a route, and I am not asking for one. To make a pet or mount exist over
HTTP I need the owner/Codex to state:

1. **Which file owns the display name** for the 10 shared ids, and whether the other file
   gets corrected (that is a `docs/production/**` edit, which I do not own).
2. **Which level column wins for mounts** (`level_cap` or `required_level`), and what
   `level_cap` even means for a mount that has no XP (`xp_source: none`).
3. **Whether the four pet slots enter the wire slot vocabulary.** The frozen v1 enum has
   five tokens and the approved v2 has twelve player slots; `PET_*`/`MOUNT_*` are neither.
   Adding them is a contract change, not a server choice.
4. **Definitions for the ten skill ids** (coefficients, targets, ICD semantics). The pet
   table states `45s ICD`, `0.35x owner attack water`, `taunt one normal mob 2s; no boss`
   etc. in prose. "0.35x owner attack" needs a place in the Production_Rules section 2
   formula, which currently has no pet term - the same unsourced-application problem as
   the DEC-023 gear stats.
5. **The XP/level subsystem for a companion.** `xp_source` states daily-activity XP with
   `cap 1 level/day to L20, 2/day after`; no daily reset exists in this server, which is
   the same gap already recorded for the currency daily caps and for the pet feed cooldown
   (12h). A cooldown of hours needs a clock and persistence, not an in-memory ledger.
6. **Leash authority.** `owner_range_wu 8` with "teleport to owner after 5s out of range"
   is a server-side behaviour on the tick; whether a companion is a world entity, an AOI
   audience member, or client-only art is not stated anywhere.

Until (1)-(6) are answered, the table stays loaded as data and the checks stay as pins:
if someone edits either source to make these numbers agree, the corresponding check goes
red and the fix has to be a deliberate edit of the pin, not a silent drift.
