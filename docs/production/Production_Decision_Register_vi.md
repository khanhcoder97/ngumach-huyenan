# SỔ QUYẾT ĐỊNH PRODUCTION
## Ngũ Mạch: Huyền Ấn — nguồn chuẩn cho các tài liệu v1.1

Mỗi quyết định dưới đây được áp dụng đồng nhất cho GDD, đặc tả domain, manifest, data import và nghiệm thu. Thay đổi sau khi code/data đã dùng phải có decision ID, owner, phạm vi ảnh hưởng và migration note. Quyết định này khóa baseline để bắt đầu production; nó không thay playtest/balance tuning.

| ID | Quyết định chuẩn | Lý do / áp dụng |
|---|---|---|
| DEC-001 | Engine baseline: Unity 6.3 LTS, C#, URP 2D, Pixel Perfect Camera và Tilemap; actor art dùng frame-based spritesheets. | Cụ thể hóa dòng “Unity 6 LTS” và pixel-art migration; chỉ nâng package qua change review. |
| DEC-002 | Hai raid 10 người, mỗi raid có **3 encounter**, gồm 2 encounter objective/add và 1 encounter boss cuối; hiện có 1 canonical raid boss mỗi raid. | “3 boss” ở GDD được sửa thành “3 encounter”; khớp Activity spec, art roster và 12 boss canonical. Thêm boss canonical cần quyết định scope mới. |
| DEC-003 | Giữ mode PvP **Chiến Trường Trấn Sơn 10v10**. Đây là queue/instance riêng, dùng geometry và asset của `MAP_TRAN_SON_SIEGE`, không chung rating, roster hay reward với công thành 20v20. | Hoàn thiện mode đã hứa ở GDD/AI plan mà không nhân đôi map art; cấp data/zone riêng `BG10`. |
| DEC-004 | Session reconnect grace là **120 giây**. Match tournament reconnect là **một lần trong 90 giây**; đây là luật trận, không thay session recovery. | Tách reconnect phiên khỏi reconnect bracket; dungeon/raid slot còn giữ 120 giây nếu encounter chưa đóng. |
| DEC-005 | Reset daily lúc **05:00 Asia/Ho_Chi_Minh**; weekly reset thứ Hai lúc **05:00 Asia/Ho_Chi_Minh**. Scheduler lưu timestamp UTC tương ứng và mọi UI hiển thị timezone. | Chuẩn hóa giờ bản Việt Nam đã dùng trong Content Bible; thay giá trị 04:00 không ghi timezone. Lịch tournament riêng không tự reset ledger. |
| DEC-006 | Escort C2-03 kéo dài **90 giây**, checkpoint tại từng van; nếu wipe/đứt tuyến thì trả về van gần nhất và resume objective. | Quest Production Spec là nguồn chi tiết; sửa dòng 120 giây cũ trong Content Bible. |
| DEC-007 | Mỗi lớp có **8 passive nodes**, hai nhánh × bốn node ở cấp 20/40/60/80. Người chơi equip tối đa **2 passive** cùng lúc; “2 nội tại đặc trưng” là số slot đang dùng, không phải số node toàn cây. | Phân biệt số node với loadout; tree và stat đều có ID/runtime data. |
| DEC-008 | Boss Tháp tuần là một biến thể lịch của 6 world-boss canonical; schedule luôn lưu `sourceBossId` thật. `BOSS_WEEKLY_ROTATION` chỉ là slot cấu hình, không phải entity/art ID runtime. | Không tạo boss chưa có model; tránh placeholder đi vào compendium/scene build. |
| DEC-009 | Regional time/season/ledger dùng config có timezone rõ; lịch reward không được ghi một số giờ trần trong code client. | Cho phép mở region mới mà không lệch reset. |
| DEC-010 | Tên `Ngũ Mạch: Huyền Ấn` là working title. Chỉ phát hành sau trademark/title clearance; font, nhạc, voice và artwork phải có license/chain-of-title. | Chặn sử dụng thương hiệu/asset chưa được cấp quyền. |

| DEC-011 | Passive nodes tự mở ở cấp 20/40/60/80 sau node trước trong cùng nhánh; không tiêu điểm nội tại. Equip tối đa 2 node, đổi miễn phí tại hub/rest point; khóa khi combat, queue hoặc instance đang chạy. | Khóa state/economy cho cây 40 node và bỏ nhu cầu suy diễn phí reset. |
| DEC-012 | BG10 mở ở cấp 36 sau C3-01; session reconnect giữ slot 120 giây. Mode dùng PvP template skill/passive đồng nhất, chuẩn hóa stat quanh profile cấp 40; reward chỉ cosmetic, tối đa 3 cache và 60 CURRENCY_TSS_MERIT/account/ngày. | Tách level PvE/progression khỏi fairness 10v10; khớp reconnect chuẩn DEC-004. |
| DEC-013 | Farm là pocket riêng 5 luống/account, tổng yield cap 12/ngày; câu cá có 6 anchors trong world manifest, cap 20 catches/account/ngày. Quota reset 05:00 Asia/Ho_Chi_Minh. | Không đặt farm collision lên map thế giới; chống reset quota bằng đổi nhân vật/shard. |
| DEC-014 | Toàn dự án dùng pixel-art 2D cho gameplay, environment, VFX và UI; logical 640×360, 20 PPU, integer scale, point filtering, lossless textures, không blur/anti-aliasing/bone-warp. | Chủ dự án đổi art direction ngày 2026-10-26 theo ảnh tham chiếu chibi kiếm sĩ. Giữ nguyên WU, gameplay/network/data IDs; migration theo `Pixel_Art_Production_Standard_vi.md`. |
| DEC-015 | Sheet nhân vật dùng **8 hướng (N, NE, E, SE, S, SW, W, NW), cell 48×64, walk 6 frame/hướng ở 8 fps, pivot bottom-center** (Mẫu A), thay dòng side-on của bản 2026-10-26. Tạo hình Minh Kiếm chốt: tóc xanh gai, kiếm vàng bản lớn guard gắn ngọc lục giác, áo choàng đỏ, áo teal viền trắng, khóa thắt lưng lục giác vàng, giáp thép đen (gunmetal) viền vàng ấm. Sản xuất sprite theo quy trình strip từng hướng → ghép bằng code → audit đếm pixel. | Chủ dự án chốt với Muse ngày 2026-10-27 sau khi chọn Mẫu A và duyệt sheet đi bộ Minh Kiếm v2 qua audit. Giữ nguyên 640×360, 20 PPU, bounds/capsule và mọi thông số gameplay của DEC-014. Đã cập nhật `Pixel_Art_Production_Standard_vi.md` và `Art_Brief_P1_Minh_Kiem_vi.md`. |

### Quy tắc phân xử tài liệu

1. Sổ này thắng các giá trị cũ đang mâu thuẫn, cho đến khi có decision mới.
2. GDD giữ scope; đặc tả domain giữ hành vi/chi tiết triển khai; data files giữ giá trị import; runtime server config là source cuối sau khi được version và duyệt.
3. Khi tài liệu chưa nêu dữ liệu cụ thể, agent mở một decision/change request thay vì tự tạo luật runtime.

### Các quyết định sản phẩm còn cần người sở hữu chấp thuận trước phát hành

Đây không chặn local prototype nhưng cần owner của sản phẩm/nhà phát hành: region hosting và số CCU/shard; privacy/data-retention theo thị trường; moderation staffing; monetization/store/payment; localization/voice scope; trademark và license media. Đến khi có người ký, dùng baseline không bán power, không dùng asset chưa clearance, chỉ tiếng Việt cho prototype và không thu thông tin account nhạy cảm vào telemetry.




## DEC-016 — Góc nhìn từ trên (2026-10-28)

Chủ dự án xác nhận gameplay 2D nhìn từ trên, di chuyển XY 8 hướng. `Top_Down_Gameplay_World_Spec_vi.md` thay mọi luật side-scroll/jump, Y-height và capsule cũ. Giữ 640×360, 20 PPU và sheet 48×64 theo DEC-015; footprint hero 1,2×0,6 WU. 349 anchors cần review topology theo hồ sơ migration, không đổi ID/coordinate silently. `Production_Completion_Addendum_vi.md` khóa bổ sung hành vi giao nhận quest/transaction/UI; không coi đây là bằng chứng đã implementation.

## DEC-017 — Gói luật hoàn thiện thiết kế v1 (2026-10-28)

Theo yêu cầu chủ dự án bổ sung toàn bộ các miền còn thiếu, khóa baseline thiết kế trong Production_Rules_Complete_v1_vi.md, Online_Persistence_Release_Complete_vi.md và Content_Export_and_Asset_Completion_vi.md. Gói xác định progression/stat/damage/status/AI/quest/economy/UI/network/persistence/ops, thay các câu mâu thuẫn lớp cố định/đổi lớp và farm6/5. Bảng số mới là tuning v1 do agent thiết kế, cần playtest; không tự bật trên runtime P1. Thay loader/schema cần migration PR riêng, giữ tương thích và IDs. Quyết định này không thay phê duyệt thị trường/pháp lý/CCU hoặc nghiệm thu map/device.

## DEC-018 — Fantasy kể qua khám phá và cinema (2026-10-28)

Theo yêu cầu chủ dự án, narrative v2 bổ sung chiều sâu cho nhân vật/lore và beat khám phá đủ76 quest hiện hữu, kèm20 cảnh video/63 shot giao Muse. Mở đầu chỉ gợi chuông/thư, không spoil Cơ/thí nghiệm; mốc300 năm là vỡ Huyền Ấn,30 năm là thí nghiệm thế hệ hiện tại. Giữ ending chung, avatar đa lớp/diện mạo và runtime quest/reward IDs. Video chỉ presentation có skip/fallback/replay, authority trên server. Tài liệu và prompt chưa chứng minh video đã tạo; dialogue CSV cũ vẫn cần line-edit trước voice production.

## DEC-019 — HUD vòng cung (2026-10-29)

Chủ dự án yêu cầu6ô kỹ năng tạo vòng cung quanh nút tấn công lớn góc phải dưới theo ảnh layout tham khảo. Dùng HUD_Skill_Arc_Layout_vi.md và concept06; thay bố cục grid của board04 và công thức bán cung cũ. Giữ skill IDs, mechanics, số slot và input authority; ảnh mẫu chỉ tham chiếu layout. Các concept khác trong reference v1 vẫn là direction candidates, chưa đồng nghĩa owner phê duyệt toàn bộ art.

## DEC-020 — Kinh thành rộng và pixel art giản lược (2026-10-29)

Chủ dự án yêu cầu Thăng Long có quy mô kinh thành lớn và pixel game dễ làm nhưng sắc nét. Thiết kế mục tiêu2048×1536WU/12phường, chunk64WU, sản xuất một chunk service street trước; dimension2048×1536 là phương án quy hoạch cụ thể do Codex đề xuất để đáp ứng yêu cầu, cần xác nhận bằng blockout/playtest, chưa active runtime. Giữ pipeline pixel top-down, giảm chi tiết/tái dùng module, không đổi engine. Layout v1/runtime bounds được giữ cho đến migration đồng bộ theo Capital_Scale_and_Simple_Pixel_v2_vi.md. HUD vòng cung DEC-019 giữ hiệu lực. Concept macro không phải screenshot một màn gameplay hoặc topology approved.
