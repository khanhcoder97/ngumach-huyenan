# Bến Mưa local — bằng chứng chơi thử 2026-10-30

Codex triển khai `Tools/PlayablePreview`, không sửa Server/Qoder, OpenCode tooling, Muse source art/Animator hoặc Unity engine baseline. Mục tiêu có vòng chơi ngay trên máy chưa cài Unity/.NET. Đây là local single-player playtest, không là production server hoặc MMO đã hoàn thiện.

## Đã chạy

- `node Tools/PlayablePreview/tests/engine_checks.mjs`: **68 assertions PASS**. Scenario chính đi bằng move/interact/attack/step qua5quest, boss, mảnhấn, class confirmation và cổng348; không teleport/chỉnh HP/flags để vượt tuyến. Các regression guard/save/death/collision riêng dùng fixture được phân biệt trong source.
- `python -m unittest discover -s Tools/PlayablePreview/tests -p 'test_*.py' -v`: **4 test PASS**, có11ảnh PNG thực,15dòng thoại, MIME JavaScript và path/root/source-file guards. Không suy từ HTTP tests ra nghe audio hoặc touch đã đạt.
- Browser thực ở localhost: title tải thành công; vào game thấy hero pixel/sprite, HUD vòng cung, minimap, quest; nút Tới mục tiêu đi từ18 tới39,9; mở Ly An và nhậnP00-01 hiện0/3kiện; nút kỹ năng disabled trong dialogue. Không console error ở phiên QA lúc kiểm. PhiênQA dùng namespace save riêng để giữ nguyên bản đang chơi.
- Có ảnh gameplay đã chụp từ browser, local export `Art_Source/Exports/Playtest_Evidence/BenMua_Gameplay_20261030.jpg` trên checkout người dùng. Không claim ảnh này là Unity screenshot hoặc full-campaign visual proof.
- ZIP standalone có11PNGứng viên Muse và19clip cần dùng; manifest SHA256. Chạy Python launcher mở browser; không cần npm/Unity/.NET.

## Lỗi tìm và sửa trong kiểm thử

Ly An dừng cách checkpoint2WU nên không kích wave: sửa NPC tiến tới checkpoint khi người chơi đã tới gần. Quái thường chồng quest wave: vô hiệu ordinary spawns trong encounter local. Save/death phải giữ checkpoint80/120 và READY, không bắt đánh lại wave đã commit. NPC gần kiện không được lấy mất ưu tiên tương tác mục tiêu quest. Guard/whiff theo tick, chết không emit death nhiều lần; sweep không xuyên nhà. Input giữ qua modal không tự chạy lại; game chỉ arm khi input mới/thả phím hoặc gesture mới. Boss warning path dùng3clip đã có, không tên phỏng đoán.

## Phạm vi chưa chứng minh

Chưa có browser playthrough đủ5quest hoặc test touch/device dài hạn; full route hiện được kiểm bằng cùng engine local ở Node. Chưa audition/mix sign-off hoặc FPS/RAM benchmark; sốFPS HUD trong một phiên không là nghiệm thu thiết bị. Terrain/NPC/mobs/UI skin là procedural blockout, hero là candidate PR22; chưa duyệt art/topology. Có fixture cấp/tuning/thuốc/weapon đã nêu trong README, không export sang production. Chưa có multiplayer, authentication, persistence server, nền kinh tế, cinema/video/VO hoặc các map/chương khác. Unity client #51 và server Qoder tiếp tục theo ownership cũ.
