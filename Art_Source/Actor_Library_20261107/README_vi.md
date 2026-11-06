# Thư viện actor/VFX — đợt sản xuất07/11/2026

**Đang sản xuất; chưa hoàn thành toàn bộ thư viện.** Chuẩn16–20pose thực/clip/hướng, renderer60FPS. PNG mới là ứng viên review, chưa tự thay asset gameplay.

## Phạm vi và nguồn

Catalogue130actor:5class,30quái (21gốc+9tinh anh),12boss,83NPC; thêm30kỹ năng. Nguồn là NPC_Actor_Production_Registry_vi.csv, Art Bible, World_Spawn_Gathering_Manifest_vi.csv và Combat_Skills_VFX_Animation_Spec_vi.md. BOSS_WEEKLY_ROTATION trỏ các boss thật.

Hàng đợi1008page bắt buộc chỉ bao phủ base actor animation và timeline VFX. Chưa gồm biến thể trang bị/ngoại trang/cơ thể, portrait/icon tĩnh, thú cưỡi/pet, map/UI hoặc VFX thành phần tách thêm theo cơ chế. Đây là công việc cần làm, không phải1008ảnh đã sinh. production_catalog.json/generation_jobs.json là kế hoạch. generation_jobs.json chứa prompt dự kiến; **Prompts + generation_records/history** ghi prompt thực đã dùng. Lịch sử và Rejections giữ bản bị thay/loại.

coverage.json báo số page qua cấu trúc, pending và approval. Có3clip Minh Kiếm kế thừa Motion16 đã nghiệm thu; ảnh mới chưa production-approved. Pilot một hướng/page sửa riêng không được cộng thành actor hoàn chỉnh. Còn thiếu phần lớn class/skill/quái/boss/NPC và chuỗi VFX nhiều thành phần.

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
```

Hoặc nhấp ClientGodot/Xem_Thu_Vien_Asset.cmd. ActorLibrary.tscn chạy offline, không HTTP/damage/loot/credit. Chọn nhóm/actor/clip; xem8hướng, tạm dừng, tua từng khung, kéo timeline, F5 reload, Escape thoát. Clip thiếu hiện CHƯA CÓ, không mượn sprite. Scene review phát lặp cả death; ActorLibrarySprite có Loop=false để production one-shot giữ khung cuối.

`--require-complete` là cổng hoàn tất và hiện **phải thất bại**. `--check` chỉ kiểm đồng bộ batch hiện hữu. visual_review.json ghi HOLD. ActorLibraryData mặc định chặn ảnh chưa production-approved; browser bật reviewMode để xem ứng viên.

referenceHeight hiệu chỉnh theo từng page/hướng từ pose đầu; không lấy pose nằm làm chuẩn đứng. VFX lấy chiều cao lớn nhất làm chuẩn preview. Metadata này còn cần kiểm native; không sửa collider.

## Bằng chứng và giới hạn

Implementation/Reports/Evidence/Actor_Library_20261107 có ảnh native tĩnh và benchmark. GeForce820M/1280×720, cảnh8hướng Ảnh Đao walk: khoảng60FPS,721mẫu/12giây, median16,648ms/p9518,365ms. Chỉ cảnh art review, chưa chứng nhận gameplay/crowd/combat.

Asset mới chưa nối HeroAnimator/NativeActorsView/SkillVfxPlayer. Game online vẫn dùng baseline3skill Minh Kiếm có backend; không mở khóa class chưa hỗ trợ. Một atlas full_timeline chưa hoàn thành cast/projectile/impact/loop/end. Tiếp theo cần sửa atlas bị chặn, review transitions5class, đủ bộ Bến Mưa rồi các roster khác và bind từng actor đủ clip.
