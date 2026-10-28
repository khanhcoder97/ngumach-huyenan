# Rà soát đặc tả và bàn giao agent — 2026-10-28

Baseline GitHub: `4fbf95a10e7b7c9193e65d25c09ca935649f3bc2`. Đợt này rà cấu trúc toàn bộ thư mục production (Markdown/CSV/media), đối chiếu các hợp đồng trọng yếu với code và chạy lại các validator. Không chứng nhận mọi câu thoại, mọi encounter hoặc mọi thiết bị đã được playtest.

## Kết luận

Chưa đủ để sản xuất game hoàn chỉnh chỉ bằng gói tài liệu hiện có. Scope/GDD, UI và catalogue đã rộng nhưng dữ liệu runtime mới là ví dụ: 7 schemas/9 examples, 8 P1 contracts/8 examples. Có 76 quest ID nhưng chỉ 1 QuestDefinition; 5 môn phái trong thiết kế nhưng 1 ClassDefinition, 30 active skills nhưng mới 3 SkillDefinition. Cần data conversion và field coverage, không coi ID resolve là full implementation.

Chủ dự án chốt top-down trong lượt audit này: DEC-016. Đã bổ sung hợp đồng tọa độ, footprint, input, camera, combat ranges, floor/nav, migration maps và nghiệm thu. Đã bổ sung quest accept/reward, economy transaction, UI failure states, persistence và release evidence. Các numeric chưa có nguồn không được bịa thành nội dung đã khóa.

## Mâu thuẫn và gap có bằng chứng

| Mức | Phát hiện | Xử lý / điều kiện đóng |
|---|---|---|
| P0 | Atlas cũ Y=độ cao/platform nhưng controller Muse dùng gravity=0, XY 8 hướng | DEC-016 thay model; review 349 placement qua migration registry, dựng nav/collision trước content lock |
| P0 | Hero cell 64px /20 PPU=3,2 WU nhưng văn bản cũ ghi 5 WU, capsule 3,6 | Chốt cell 48×64 và footprint 1,2×0,6 WU; các kích thước nhân vật cũ là concept history |
| P0 | SK-MK-01/02 JSON rangeWu=2,2/5,5 trong khi mô tả 2,2/5,5 mét; 1WU=0,5m | Quy định export 4,4/11 WU; Qoder cần PR sửa data và kiểm tra semantic, không đổi API client âm thầm |
| P0 | SK-MK-03 chưa có range; damage/stat/XP config chưa đủ bảng cấp | Cần numeric contract và migration trước damage rollout; hiện chỉ gating/effect |
| P0 | Quest accept chưa có contract hoàn chỉnh, thiếu NPC world/proximity và level runtime | Addendum khóa guard/retry; issue #20 thực hiện schema trước, endpoint feature off khi thiếu guard |
| P0 | Runtime state in-memory; client chọn characterId | Chưa persistence/auth production; không đủ điều kiện lưu tiến trình hay mở public game server |
| P1 | Sheet actor là draft; topology, UI, VFX, audio chưa đầy đủ | Hoàn từng asset pack có manifest, preview, exact build evidence và runtime acceptance |
| P1 | Unit tests/CI xanh nhưng không có hai client chơi quest→boss→reward→save | P1 end-to-end chưa đạt; nghiệm thu theo completion addendum |
| P1 | WORK ORDER Muse còn hero_vanguard/tóc nâu, branch/client work cũ | DEC-015/016 và giao việc mới thắng; Minh Kiếm đã được chốt và có sheet |

## Bàn giao thực tế

### Qoder

PR #6–#14, #19 đã merge: session/move/world, domain skeletons, combat HTTP, đọc quest/inventory; có server build, HTTP smoke và service self-check trong CI. Không có damage resolution đầy đủ, mob world populated, quest accept/turn-in/reward persistence hay login production. Issue #20 đề xuất QuestAcceptRequest vẫn mở. Kết luận: phần API prototype đã giao; full MMORPG backend chưa hoàn tất.

### OpenCode

PR #16 đã merge: validator asset, README, 63 unit tests, GitHub Actions. Chạy lại 63 tests đạt; manifest thật Muse đạt. Kiểm header PNG, paths, metadata hợp lệ; chưa chứng minh PNG decode đầy đủ, palette, pixel duplicates, .meta slicing hay Unity runtime. Khóa 8 hướng cho mọi sprite_sheet sẽ cần phân loại khi VFX/UI có sheet. Kết luận: OPC-05 đã đạt phạm vi hiện tại, còn hardening và coverage cần issue tiếp.

### Muse

PR #15 chốt DEC-015; PR #17 bàn giao PNG LFS 288×512, 8×6 cell, preview, .meta, script animator/controller và builder scene. Đã xem trực tiếp sheet và kiểm file bằng validator. Manifest còn `draft`; chưa có idle/attack/death, tileset Bến Mưa/Thăng Long, UI pack/VFX toàn game.

PR #17 báo cáo Unity 6000.3.17f1 headless BuildAll exit 0 trên máy ảo. Đây là bằng chứng do agent báo cáo; chưa có log/artifact exact commit để người review tái kiểm, máy local audit không có Unity/.NET. Controller hiện di chuyển local, chưa kết nối authoritative API. Muse đã thay C# ngoài art boundary để dựng demo; lần tiếp theo cho phép chỉ demo/builder đã nêu, không tự nhận server/network authority.

## Bằng chứng kiểm tra

- `python Implementation/Tools/validate_content.py`: PASS, 7 schema/9 example.
- `python Implementation/Tools/validate_contracts.py`: PASS, 8 schema/8 example.
- `python Implementation/Asset_Handoff/validate_asset_delivery.py`: PASS, pack p1_minh_kiem_walk, 1 asset, 0 warnings.
- `python -m unittest discover -s Implementation/Asset_Handoff/tests`: PASS, 63 tests.
- GitHub main baseline: content-validation, contract-validation, asset-handoff-validation, server-build, server-smoke đều success.
- Không chạy Unity/.NET local; kết quả build/smoke backend dựa vào GitHub CI trên baseline, không suy thành device acceptance.

## Thứ tự đóng thiếu sót

1. Muse xác nhận và dựng blockout Bến Mưa top-down, giao geometry/placement review và log Unity của sheet hiện tại.
2. OpenCode thêm báo cáo coverage spec→definition→asset và kiểm .meta/frame geometry; không cần cài Unity local.
3. Qoder sửa unit conversion theo DEC-016, hoàn proposal #20 có guards/dedupe; chuẩn bị runtime content và persistence theo gate riêng.
4. Khi có schema/data mới, chạy validators và review PR; sau đó mới combat/quest/boss/save end-to-end. Không đổi thiết kế cả game để coi prototype đã xong.
5. Phát hành chỉ sau đầy đủ runtime records, device QA, economy/load/recovery và sign-off sản phẩm. CCU/hosting/store/legal còn cần quyết định thực tế.
