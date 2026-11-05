# QOD-24 — Skill catalogue coverage (work order 29, Q4)

**Ngày:** 2026-11-05. **Issue:** #87, #41. **PR:** #106 (OPEN, không self-merge).
**Nguồn kỹ năng:** `docs/production/Combat_Skills_VFX_Animation_Spec_vi.md:33-135` (30 skill / 5 class), `Implementation/Content/Schemas/SkillDefinition.schema.json` (frozen), `docs/production/Content_Bible_Ngu_Mach_Huyen_An_vi.md:258-271` (status), `:124,139,154,169` (passive), `docs/production/GDD_Ngu_Mach_Huyen_An_vi.md:155` (PvP 0,65), `docs/production/Character_Equipment_Inventory_Spec_vi.md:14-18` (class id).

Không đổi schema, không đổi wire vocabulary, không bật gate. Số đo ở head này: `--self-check` **499/0**, smoke **358**, `validate_contracts.py` OK (31 schema / 31 example, reference set `skill=7`).

## 1. Điều đã ship

Bốn row mới, mỗi giá trị lấy từ đúng một dòng spec, `sourceRef` trỏ về dòng đó:

| skillId | classId | CD | MP | targeting | hệ số | telegraph | source |
|---|---|---|---|---|---|---|---|
| `SK-HB-02` | CLASS_HUYEN_BUT | 12 | 18 | ENEMY, 1 target, **không** `rangeWu` | 1,10 | 0,18s | `spec:82-83` |
| `SK-HB-04` | CLASS_HUYEN_BUT | 18 | 28 | AREA, bán kính 3 m → `rangeWu` 6, 5 target | 0 (hồi máu, không phải damage) | 0,45s | `spec:88-89` |
| `SK-TC-01` | CLASS_THACH_CHUY | 8 | 14 | CONE 60°, sâu 2,6 m → `rangeWu` 5,2, 1 target | 1,70 | 0,25s | `spec:99-100` |
| `SK-TC-05` | CLASS_THACH_CHUY | 10 | 12 | DASH 4 m → `rangeWu` 8, 1 target | 1,00 | 0,22s | `spec:111-112` |

Quy ước đổi đơn vị: `1 WU = 0,5 m` (`Top_Down_Gameplay_World_Spec_vi.md:7`, `Pixel_Art_Production_Standard_vi.md:20`) nên mét × 2. `coefficients.pvp = 0,65` cho mọi row, theo `GDD:155` — không phải giá trị tôi tự chọn. `boss = pve` theo đúng tiền lệ ba row MK đã merge.

**`SK-TC-05` dùng convention, không dùng số:** spec không nói giới hạn mục tiêu của cú lao; tôi lấy 1 theo tiền lệ `SK-MK-02` (cùng hình DASH, cùng im lặng) và ghi lại ở đây để Codex phủ quyết nếu muốn khác.

## 2. Vì sao chỉ bốn row, không phải 27

Ba ràng buộc kỹ thuật, đều kiểm được trong repo:

1. **`telegraphSeconds` là bắt buộc và không cho phép null** (`SkillDefinition.schema.json`, loader `CombatSkillCatalogLoader.cs:166-173`). 19 trong 23 skill còn lại **không có thời gian chuẩn bị riêng**; nguồn chỉ cho dải theo nhóm (`spec:28-30`: nhanh 0,12–0,22s / có báo trước 0,35–0,75s / tuyệt kỹ 0,50–0,90s). Chọn một điểm trong dải là bịa số → tôi không làm.
2. **Loader dùng cùng predicate cho nội dung và cho wire.** `P1Validation.IsSkillId` là `^SK-MK-0[1-3]$` (`P1Validation.cs:49-50`) trong khi schema publish `^SK-[A-Z0-9]{2}-[0-9]{2}$`. Hệ quả: server **không nạp nổi** bất kỳ row nào ngoài subset MK. Đã tách thành hai vocabulary:
   - `CombatSkillCatalogLoader.ContentSkillIdPattern` = pattern của schema, chỉ dùng để kiểm file content;
   - `P1Validation.IsSkillId` **giữ nguyên** `^SK-MK-0[1-3]$`, vẫn là cổng duy nhất cho input client.
   Bằng chứng giữ nguyên: self-check `contracts.skill_id_wire_vocabulary_still_alpha_only` + hai smoke check từ chối `SK-TC-01`/`SK-HB-02` ở tầng HTTP với `invalid_payload / payload.skillId`.
3. **Nhiều skill cần subsystem server chưa có.** `CombatTargetingTypes` chỉ định nghĩa `SELF/DASH/CONE` (`CombatSkillDefinition.cs:3-9`); chưa có resource per-class (Kiếm Ý/Nhiệt/Thủy Ấn/Thế/Mộc Tiêu), chưa có status window (khiên, DoT, chậm, dấu, nổ muộn, khiêu chiến, hất, tốc chạy), chưa có party/guild route.

`SK-MK-04..06` **cố ý không nạp**: class Minh Kiếm là class alpha đang bật, nên một row MK là skill client gọi được ngay. `SK-MK-06` còn "tiêu Kiếm Ý khi server chấp nhận" (`spec:55`) mà server không model Kiếm Ý → nạp vào sẽ tạo một skill chạy sai chính nguồn của nó.

## 3. Bảng 30 skill — row nào thiếu gì

| skill | dòng | row | field/chặn | loại |
|---|---|---|---|---|
| SK-MK-01/02/03 | 40/43/46 | có | — | shipped |
| SK-MK-04 | 49 | chưa | telegraph; khiên hấp thụ | A+B |
| SK-MK-05 | 52 | chưa | telegraph | A |
| SK-MK-06 | 55 | chưa | telegraph 0,70 **đã có**, nhưng class đang bật + tiêu Kiếm Ý | B+C |
| SK-AD-01 | 60 | chưa | telegraph; DoT tick | A+B |
| SK-AD-02 | 63 | chưa | telegraph; dấu 5s + kích nổ muộn | A+B |
| SK-AD-03 | 66 | chưa | telegraph (0,10s là cửa hitbox, không phải chuẩn bị); thưởng đánh sau lưng | A+B |
| SK-AD-04 | 69 | chưa | telegraph; status chậm | A+B |
| SK-AD-05 | 72 | chưa | telegraph | A |
| SK-AD-06 | 75 | chưa | `maxTargets` vùng không có trong nguồn; tiêu Nhiệt | C+B |
| SK-HB-01 | 80 | chưa | telegraph (0,25s là bay đạn); xuyên 3 mục tiêu | A+C |
| SK-HB-02 | 83 | **có** | — | shipped |
| SK-HB-03 | 86 | chưa | telegraph; target đồng minh; "bảng nội tại" Tĩnh Thủy | A+B+D |
| SK-HB-04 | 89 | **có** | (khai báo pve 0 vì bản chất là hồi máu) | shipped |
| SK-HB-05 | 92 | chưa | telegraph; buff tốc chạy | A+B |
| SK-HB-06 | 95 | chưa | telegraph; party trong cùng encounter; hệ số raid | A+B+D |
| SK-TC-01 | 100 | **có** | — | shipped |
| SK-TC-02 | 103 | chưa | telegraph; hất 0,5s; giới hạn mục tiêu vùng | A+B+C |
| SK-TC-03 | 106 | chưa | telegraph; cửa giảm sát thương; tiêu Thế | A+B |
| SK-TC-04 | 109 | chưa | telegraph; khiêu chiến + miễn nhiễm boss; giới hạn mục tiêu 6 m | A+B+D |
| SK-TC-05 | 112 | **có** | (maxTargets theo convention, xem §1) | shipped |
| SK-TC-06 | 115 | chưa | telegraph; vùng tồn tại 5s; tiêu Thế | A+B+C |
| SK-LC-01 | 120 | chưa | telegraph; dấu tăng sát thương nhóm | A+B |
| SK-LC-02 | 123 | chưa | có telegraph 0,45s; bẫy có vòng đời 4s, schema không có field duration; giới hạn mục tiêu vùng | C+B |
| SK-LC-03 | 126 | chưa | telegraph; 5 mũi ×45% không biểu diễn được (một skill một hệ số) | A+C |
| SK-LC-04 | 129 | chưa | telegraph; giảm 30% trong 0,8 m (falloff theo khoảng cách) | A+C |
| SK-LC-05 | 132 | chưa | telegraph; lùi + bắn trong một lệnh | A+C |
| SK-LC-06 | 135 | chưa | `rangeWu` duy nhất không chứa cả tầm chọn điểm 12 m và bán kính 6 m; tiêu Mộc Tiêu | C+B |

Loại: **A** = thiếu telegraph điểm; **B** = server chưa có subsystem; **C** = schema hiện tại không biểu diễn được; **D** = thiếu bảng số trong nguồn.

## 4. Câu hỏi cần Codex/owner chốt (kèm options, tôi không tự chọn)

1. **`telegraphSeconds` cho 19 skill A.** Options: (i) cho phép `null` nghĩa là "chưa duyệt" (đổi schema → cần approval, có packet); (ii) chốt một điểm trong dải `spec:28-30` per nhóm skill; (iii) owner/Codex ghi số per skill. Mặc định của tôi: để skill đó **không có row**.
2. **Bảng kháng boss/quái.** `spec:83` ("tùy bảng kháng"), `spec:123` ("nếu có kháng"), `spec:109` ("boss không bị ép đổi mục tiêu"). Repo chưa có bảng `mob/boss × hiệu ứng` nào. Options: Codex thêm cột vào `combat_mob_stats_v1.json`, hoặc một `status_immunity_v1.json` mới (tôi làm được, cần duyệt).
3. **"Bảng nội tại" Tĩnh Thủy** (`spec:86`): thiếu % khiên thêm và ngưỡng HP. Bible chỉ nêu tên nội tại (`:139`).
4. **Set bonus còn là biến chữ:** `Item_Catalog_and_Set_Bible_vi.md:97` ghi "tăng **n%** damage" và "tăng **m%** damage". Cần giá trị, hoặc cho phép ghi `null` trong catalog.
5. **Party/guild.** `spec:89` ("không hồi mục tiêu ngoài party/guild"), `spec:95` ("chỉ party trong cùng encounter") chặn HB-03/HB-04/HB-06 ở phía *điều kiện*, không chặn row. Server chưa có route party nào (Q7) → tôi để nguyên, không giả danh sách party.
6. **Schema không biểu diễn được hình học.** Options cho `rangeWu` đơn: thêm `effectRadiusWu` + `castRangeWu`, thêm `durationSeconds` cho trap/zone, thêm mảng `hits[]` cho multi-hit. Đây là đổi schema đã đóng băng → chỉ làm khi được duyệt, và tôi sẽ viết packet trước khi động vào file.

## 5. Việc kế tiếp trong Q4, không cần chờ ai

Thứ tự tôi sẽ đi nếu không có trả lời mới: (a) tách vocabulary loader/wire thành hai contract test có tên rõ (đã xong một phần); (b) nạp tiếp các row **chỉ thiếu** telegraph khi câu 1 có trả lời; (c) `status_immunity_v1.json` + loader + validator nếu câu 2 được duyệt, vì nó mở khoá cả TC-04/HB-02/AD-04; (d) phần combat/AI còn lại của Q4 không phụ thuộc số: respawn, group credit, loot authoritative đã có đường đi và đang đo được.
