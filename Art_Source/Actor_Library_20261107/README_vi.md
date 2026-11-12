# Thư viện actor/VFX — đợt sản xuất07/11/2026

> Quyết định hiện hành 12/11: quay lại sprite sheet chibi nguyên khối. Hủy hướng nhân vật paper-doll mới; studio giữ để chỉnh tay. Nguồn cũ giữ nguyên, các HOLD chất lượng vẫn giữ. Xem [Sprite Studio](../../docs/production/Sprite_Studio_20261112_vi.md).

**Đang sản xuất; chưa hoàn thành toàn bộ thư viện.** Chuẩn16–20pose thực/clip/hướng, renderer60FPS. PNG mới là ứng viên review, chưa tự thay asset gameplay.

Đợt mới nhất: [20261113b — ba pha Chồi Đất và VFX rễ](../../docs/production/Actor_Batch_20261113b_vi.md), **18 sheet /288 ô nguồn**. Rễ Nước12/12 action đủ nguồn và kiểm source; còn tinh chỉnh nối pha, tích hợp gameplay/AI/hitbox. Thêm chiều cao đứng tường minh cho clip bắt đầu thấp, review biến thể2 và Studio phát sau fit. Catalogue còn949/1008 job thiếu; mục tiêu toàn thư viện tiếp tục.

Đợt trước: [20261113a — vận động Rễ Nước, Phản Quang và chèn component](../../docs/production/Actor_Batch_20261113a_vi.md), 20 sheet chọn / 320 ô nguồn mới. Rễ Nước có chín action đủ nguồn tám hướng xem, còn ba pha chồi đất; Minh Kiếm thêm động tác thủ skill_01. [Đợt f](../../docs/production/Actor_Batch_20261112f_vi.md) có hurt/death và VFX năm lớp; [đợt e](../../docs/production/Actor_Batch_20261112e_vi.md) giữ roi rễ/vòng gợn; [đợt d](../../docs/production/Actor_Batch_20261112d_vi.md) có Người Giữ Thuyền, walk E/NE còn HOLD. Inventory các đợt phản ánh lựa chọn hiện hành; báo cáo từng đợt giữ số giao lịch sử.

## Phạm vi và nguồn

Catalogue130actor:5class,30quái (21gốc+9tinh anh),12boss,83NPC; thêm30kỹ năng. Nguồn là NPC_Actor_Production_Registry_vi.csv, Art Bible, World_Spawn_Gathering_Manifest_vi.csv và Combat_Skills_VFX_Animation_Spec_vi.md. BOSS_WEEKLY_ROTATION trỏ các boss thật.

Hàng đợi1008page bắt buộc chỉ bao phủ base actor animation và timeline VFX. Chưa gồm biến thể trang bị/ngoại trang/cơ thể, portrait/icon tĩnh, thú cưỡi/pet, map/UI hoặc VFX thành phần tách thêm theo cơ chế. Đây là công việc cần làm, không phải1008ảnh đã sinh. production_catalog.json/generation_jobs.json là kế hoạch. generation_jobs.json chứa prompt dự kiến; **Prompts + generation_records/history** ghi prompt thực đã dùng. Lịch sử và Rejections giữ bản bị thay/loại.

coverage.json báo số page qua cấu trúc, pending và approval. Có3clip Minh Kiếm kế thừa Motion16; nguồn mới được duyệt riêng theo PNG/binding sau kiểm native. Duyệt source/clip không phải nghiệm thu toàn actor. Pilot một hướng/page sửa riêng không được cộng thành actor hoàn chỉnh. Còn thiếu phần lớn class/skill/quái/boss/NPC và chuỗi VFX nhiều thành phần.

## Tạo ảnh và kiểm tra

Dùng imagegen tích hợp, không CLI/API. PNG gốc giữ nguyên. Sửa bằng lần sinh/edit mới, có prompt và bản cũ. Python chỉ đọc alpha/grid/bounds/hash, xuất metadata và copy PNG nguyên byte sang runtime. Frame hash khác nhau chưa chứng minh pose/chuyển động đúng.

Atlas80pose:8cột×10hàng, mỗi hướng N/NE/E/SE/S chiếm2hàng8frame. Manifest8direction references ghi rõ SW/W/NW lật khi được phép. Băng tay/sừng gãy/mặt nạ bất đối xứng cần góc riêng. Trang16pose4×4 có thể sửa một hướng; hướng đối xứng được phép dùng bản sửa. Không gọi hướng lật là hướng vẽ riêng.

## Xem trong Godot

Từ repo:

```powershell
python Tools/ArtProduction/build_actor_library_plan.py --check
python Tools/ArtProduction/inspect_actor_library.py --export --check
ClientGodot/Run_Actor_Library.ps1 -Test
ClientGodot/Run_Actor_Library.ps1
ClientGodot/Run_Actor_Library.ps1 -SkipBuild -CombatReview -Actor MOB_WATERROOT -Direction NE
```

Hoặc nhấp ClientGodot/Xem_Thu_Vien_Asset.cmd. ActorLibrary.tscn chạy offline, không HTTP/damage/loot/credit. Chọn nhóm/actor/clip; xem8hướng, tạm dừng, tua từng khung, kéo timeline, F5 reload, Escape thoát. Clip thiếu hiện CHƯA CÓ, không mượn sprite. Scene review phát lặp cả death; ActorLibrarySprite có Loop=false để production one-shot giữ khung cuối.

`--require-complete` là cổng hoàn tất và hiện **phải thất bại**. `--check` chỉ kiểm đồng bộ batch hiện hữu. visual_review.json ghi HOLD. ActorLibraryData mặc định chặn ảnh chưa production-approved; browser bật reviewMode để xem ứng viên.

referenceHeight thường hiệu chỉnh theo từng page/hướng từ pose đầu; không lấy pose nằm làm chuẩn đứng. Cá Linh đăng ký tâm thân bạc. Idle/báo/đánh/hồi roi Rễ Nước dùng lõi rêu, chiều cao thân trung tính và offset chân idle chung theo góc; hurt/death dùng FOOT để giữ chuyển động oằn/sụp của tán. Recovery roi lấy chiều cao từ pose cuối đã thu rễ. VFX dùng tâm ô cố định hoặc FOOT nếu là bụi sát đất. Profile preview component xuất thời lượng/chế độ vòng vào metadata, được Studio đọc và pin binding kiểm lại khi đổi. Tất cả là trình bày phải kiểm native, không sửa collider hoặc PNG.

Walk/run/turn Rễ Nước cũng dùng FOOT. Turn chỉ chuẩn bị đổi hướng, không xoay sang block khác; walk/run không đổi quyền di chuyển AI. Studio có `+ Component 16 khung nguồn` và launcher `-Component`: chèn texture/regions gốc để chỉnh layer/timing/vị trí thủ công; ban đầu trải 16 nguồn trên timeline host, không tự gắn sự kiện gameplay hoặc bảo toàn thời lượng component độc lập. Host dưới16 ô bị từ chối.

## Bằng chứng và giới hạn

Implementation/Reports/Evidence/Actor_Library_20261107 có ảnh native tĩnh và benchmark. GeForce820M/1280×720, cảnh8hướng Ảnh Đao walk: khoảng60FPS,721mẫu/12giây, median16,648ms/p9518,365ms. Chỉ cảnh art review, chưa chứng nhận gameplay/crowd/combat.

Component cung Kiếm Trận 16 khung đã nối vào SkillVfxPlayer với ba nhịp trình bày; vòng gợn Rễ Nước mới chỉ ghép ở cảnh review. Actor mới trong thư viện chưa được nghiệm thu thay renderer gameplay hoặc đóng gói PCK. Một atlas full_timeline chưa chứng minh đủ cast/projectile/impact/loop/end. Tiếp tục các action thiếu, transitions/class/VFX, thư viện môi trường/UI/icon/audio và tích hợp backend theo hợp đồng thật; chưa được tuyên bố game/full art hoàn thiện.
