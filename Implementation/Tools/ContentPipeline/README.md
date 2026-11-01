# Content pipeline — Bến Mưa candidates (OPC-11)

Công cụ Python standard library đọc nguồn thiết kế canonical, sinh **candidate
bundle** cho Bến Mưa, kiểm tra provenance/reference và so sánh theo từng field.
Đây là proposal tooling trước migration: compiler **không** ghi `Server/**`,
không sửa `Implementation/Content/Examples/**`, không bật runtime data và không
thay thế review của Qoder/Codex.

## Chạy nhanh

Từ thư mục gốc repo:

```powershell
# Sinh bundle ứng viên
python Implementation/Tools/ContentPipeline/content_pipeline.py build

# Xác nhận bundle đã commit khớp byte-for-byte với build mới
python Implementation/Tools/ContentPipeline/content_pipeline.py build --check

# Kiểm tra schema, provenance, reference, digest, source hash
python Implementation/Tools/ContentPipeline/content_pipeline.py check

# Gate dành cho migration: fail nếu còn field unresolved
python Implementation/Tools/ContentPipeline/content_pipeline.py check --require-resolved

# So sánh hai bundle theo JSON pointer
python Implementation/Tools/ContentPipeline/content_pipeline.py diff old.json new.json

# Chạy test
python -m unittest discover -s Implementation/Tools/ContentPipeline/tests -v
```

`build --check` không ghi file. `check --require-resolved` hiện trả exit code 1
vì dữ liệu nguồn còn 57 field unresolved; đây là hành vi đúng, không phải lỗi
của tool.

## Đầu ra

`Implementation/Content/BuildCandidates/BEN_MUA/candidates.json`

- Canonical JSON: key sắp xếp, UTF-8, LF, không timestamp, `ensure_ascii=False`.
- `bundleDigest` = SHA-256 của bundle không gồm chính nó.
- Mỗi candidate có `candidateDigest` = SHA-256 của candidate không gồm chính nó.
- `summary` đếm candidate/ready/blocked/unresolved.
- `activation.eligible` chỉ `true` khi không còn blocking unresolved; hiện là
  `false`. `activation.requiresReview` luôn `true`.
- `sources` chứa path/version/SHA-256 của mọi nguồn đã đọc.

Cùng input → cùng bytes và digest. Test `test_build_is_deterministic` và
`test_golden_output_is_current` khóa hành vi này.

## Candidate hiện có (21)

| Kind | Số lượng | Ghi chú |
|---|---:|---|
| `QUEST` | 5 | P00-01 copy canonical; P00-02..05 proposal một phần |
| `OBJECTIVE_MAP` | 5 | vị trí, spawn, checkpoint, availability từ Atlas/manifest |
| `ACTOR_PROFILE` | 1 | level 1, không gear, Minh Kiếm |
| `MOB_PROFILE` | 3 | Cá Linh, Rễ Nước, Kẻ Rình Bờ ở reference level 5 |
| `BOSS_REFERENCE` | 1 | Mãng Cốt, reference level 10 |
| `ITEM_REFERENCE` | 6 | 1 resolved, 5 unresolved |

Kết quả hiện tại: **3 ready / 18 blocked / 57 unresolved**. Ba candidate ready
là `QUEST-P00-01`, `OBJMAP-P00-01`, `ITEM-REF-P00-01-CHEST`.

## Source map

Mọi field có provenance gồm `sourceId`, `sourceRef`, `sourceVersion`, `units`,
`transform`. Compiler đọc:

- `docs/production/P1_Design_Resolution_20261029_vi.md` — actor/mob/boss
  reference numbers và các nút chưa chốt.
- `docs/production/Production_Rules_Complete_v1_vi.md` §1–5 — công thức,
  combat order, boss Mãng Cốt, quest graph.
- `docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md` §12 — mob
  archetype, telegraph, boss table.
- `docs/production/Quest_and_Narrative_Production_Spec_vi.md`,
  `Quest_Dialogue_Production_Data_vi.csv` — quest bước, NPC, graph.
- `docs/production/Map_Production_Atlas_vi.md`,
  `World_Spawn_Gathering_Manifest_vi.csv` — vị trí, spawn, respawn, ring.
- `NPC_Actor_Production_Registry_vi.csv`, `Item_Master_Catalog_vi.csv`,
  `Item_Rarity_Variant_Catalog_vi.csv` — NPC/skill/item reference.
- `Implementation/Content/Schemas/**` và examples canonical — schema/version.
- `Production_Content_Audit_20261030_vi.md` — coverage gap của 5 class.

`sourceRef` dạng `path#fragment`; `sourceVersion` là version khai báo trong
`SOURCE_SPECS` (compiler_core). Đổi nguồn làm SHA-256 đổi, nên `check` fail cho
tới khi build lại.

## Quy tắc unresolved

- Field không có nguồn **không được mặc định 0**. Field bị bỏ khỏi definition
  và ghi một entry `unresolved` với `valueState: MISSING`.
- Field có giá trị nhưng ngữ nghĩa còn tranh chấp dùng
  `valueState: PRESENT_UNRESOLVED`; path phải tồn tại và có provenance.
- Mọi entry hiện `blocking: true`. Một candidate có bất kỳ entry blocking nào
  thì `status = BLOCKED_UNRESOLVED`; bundle `activation.eligible = false`.
- Schema target vẫn được kiểm tra. Required field bị thiếu chỉ được suppress
  nếu có đúng unresolved `MISSING` bao phủ path đó; thiếu mà không có
  unresolved là lỗi cứng.

## Các blocker đang mở

- **Quest reward/unlock thiếu ID hoặc XP token**: P00-02, P00-03, P00-04,
  P00-05. Generic “thuốc” không chọn được `POT-HP-01` hay `POT-MP-01`; không có
  footwear T1; `EQ-[CLASS]-WEAPON-T1-R-COMMON` cần class substitution.
- **Objective chưa có type canonical**: P00-03 “né một đợt sóng”; P00-05 “vào
  boss ring”. P00-03 Rễ Nước còn tranh chấp KILL vs INTERACT.
- **Range/share policy**: ripple, root, seal thiếu interaction radius; nhiều
  objective thiếu share policy theo Rules §5.
- **Spawn level/quantization**: manifest chỉ cho band 1–10; P1 level 5/10 là
  reference calculation, chưa chọn encounter level; runtime integer
  quantization chưa chốt.
- **Telegraph conflict**: Art Bible cho Cá Linh leap 0.45s và Kẻ Rình Bờ charge
  0.6s, thấp hơn minimum heavy attack 0.7s. Giá trị được giữ nguyên và đánh dấu
  `PRESENT_UNRESOLVED`, không tự sửa.
- **Boss descriptors**: thiếu base attack, defense, phase guard, interruptible,
  damage type, hit window, rounding party HP, vị trí hai safe pad.
- **Actor gear**: `ItemDefinition` v1 không có stat vector; chưa thể compile
  equipped profile.
- **Class coverage**: chỉ Minh Kiếm có ClassDefinition/SkillDefinition example;
  bốn class còn lại chưa có candidate.
- **Availability conflict**: manifest đặt NPC rescue ở P00-04 trong khi quest
  P00-03 yêu cầu cứu; `NPC_CLASS_TRIAL` xuất hiện sau P00-05 nhưng P00-05 lại
  cần xác nhận class tại NPC đó.

## Validation

`validation.py` kiểm tra:

- JSON Schema cho bundle và từng target definition.
- Digest bundle/candidate; source metadata và SHA-256 hiện tại.
- Provenance phủ đúng **mọi leaf** của definition, không thừa/thiếu, path sắp
  xếp, source/version/ref hợp lệ.
- Unresolved path sorted/unique; `MISSING` phải vắng, `PRESENT_UNRESOLVED` phải
  có mặt và có provenance.
- Quest/NPC/map/item/skill/currency/loot/spawn reference; duplicate ID;
  prerequisite cycle; quest unlock quan hệ.
- Objective map phủ mọi objective, count khớp quest, sourceId thuộc targetIds,
  spawn record đúng map/entity/respawn, vị trí trong map bounds.
- Actor formula oracle; mob base/multiplier oracle; boss HP/party/attack/phase
  oracle; item catalog resolution.
- Summary/status/activation nhất quán.

## CI

`.github/workflows/content-pipeline.yml` chạy unit tests, `build --check`,
`check`, và một bước chứng minh `check --require-resolved` fail khi còn
blocking unresolved. CI không tuyên bố Unity/runtime PASS.

## Giới hạn

- Không có Unity trong môi trường này; không có bằng chứng import/playback.
- Không sửa `Server/**`, `Tools/PlayablePreview/**`, P1 contracts, runtime C#,
  Muse art/manifest.
- Không tự merge PR; Qoder/Codex review rồi mới migration/activation.
- Compiler chỉ ghi `Implementation/Content/BuildCandidates/**`; không có hai
  compiler cùng ghi một file.
