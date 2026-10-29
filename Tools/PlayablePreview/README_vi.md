# Bến Mưa — bản chơi thử cục bộ v1

Mục tiêu: có một hành trình để chơi ngay trên máy yếu khi Unity/.NET chưa sẵn sàng. Đây là nhánh playtest **một người, Canvas/JavaScript + Python**, không thay engine Unity của dự án hoặc giao thức/server Qoder. Không có tài khoản online, multiplayer, giao dịch hay đồng bộ thưởng vào server thật.

## Chơi ngay

Giải nén toàn bộ gói nếu dùng ZIP, rồi nhấp đúp `CHOI_THU.cmd` ở thư mục gốc. Máy cần Python3.10+; không cần Unity, .NET hoặc npm. Cửa sổ server cần tiếp tục chạy trong lúc chơi.

Hoặc chạy từ root dự án:

```powershell
python Tools/PlayablePreview/server.py --port 8090 --open
```

Mở `http://127.0.0.1:8090`. Nếu cổng đang được dùng, giữ server cũ nếu đó là game đang chơi hoặc chọn `--port 8091`. Server chỉ nghe127.0.0.1. Không mở port ra Internet để gọi đây là MMO.

## Điều khiển

- Nhấp đất hoặc WASD/phím mũi tên để đi; nút **Tới mục tiêu** dẫn tới điểm nhiệm vụ, chưa tự chiến đấu/nhận thưởng. Nếu một đoạn bị vật cản chặn, nhấp đất hoặc điều khiển tay để đi vòng.
- E hoặc nút Tương tác khi gần NPC/vật thể; Space/nút lớn đánh thường; 1 Phản Quang; 2 Tầm Long; 3 Kiếm Trận.
- Shift né, Q dùng thuốc, B túi đồ, J nhật ký, Esc đóng/mở cài đặt. Cần ảo hỗ trợ touch. Click kỹ năng rồi quay lại WASD vẫn điều khiển được.
- Có nhạc Bến Mưa/đánh boss, mưa và SFX từ audio pack gốc. Chỉnh hoặc tắt trong cài đặt. Boss có telegraph hình học để đọc dù tắt âm.
- Tiến độ tự lưu trong localStorage của trình duyệt/origin này; không xóa dữ liệu trang nếu muốn giữ. Tải lại để tiếp tục. Đổi cổng/trình duyệt là save khác. Cài đặt có xác nhận trước chơi lại.
- Khi đọc thoại/mở bảng/rời tab, bản một người tạm dừng. Đây là UX playtest riêng; production MMORPG không được pause world khi mở modal.

## Tuyến thực sự triển khai

P00-01: Ly An→3kiện riêng→Tạ Vân Khanh. P00-02:3gợn nước+4Cá Linh→báo cáo. P00-03:3Rễ Nước+2dân+tránh sóng→báo cáo. P00-04:Ly An đi qua80/120, mỗi điểm3quái, không chồng spawn thường; checkpoint giữ qua save/death. P00-05:boss3đòn/3pha→mảnhấn→quan sát viên xác nhận Minh Kiếm→vũ khí thưởng→cổng Đông348. Sau đó có thể khám phá/hái thuốc/đánh quái bờ Đông, các map/chương khác chưa chơi trong gói này.

Quest accept/turn-in kiểm khoảng cách; nhặt/reward không cộng lặp; chết hồi Bến Gỗ và giữ objective; mob có aggro/telegraph/return/group respawn. Damage/scheduled hit, guard/counter/dodge và boss warnings dùng fixed step20Hz trong client local, không phải authoritative network combat. Boss A cone120°/8WU/0,9s; B circle4WU/1,2s chốt vị trí; C annulus3..7WU/1s. Pha60%/30%; hai bệ biểu tượng ở pha3 là geometry candidate local.

## Nguồn và các fixture phải giữ nhãn

15dòng thoại mở đầu lấy nguyên bản từ CSV đã biên tập; tên/ID/tuyến chính dựa Quest Spec và Atlas. Hero dùng11sheet ứng viên Muse tại commit497702ec0e7d3f9167466007b90877e901a4c95c (PR22), provenance/hash trong content.json. Đọc được/được chơi thử chưa là duyệt artwork/import Unity. Không sửa source art, Animator hoặc builder Muse.

Terrain, cây, nhà, NPC, quái là **original procedural pixel blockout** do code vẽ, chưa là bộ asset final của Muse hoặc349placement đã REVIEWED. Chọn hành lang playable Y=-11..9 ở Bến Mưa; giữ các anchor quest X nguồn. Collision chân nhà là geometry local; không export sang nav production.

Tuning local: quái thường chọn profile cấp1 theo base144HP/12ATK/2,8DEF và archetype, HPceil một lần; HP cá116/rễ159/stalker130. Đây là lựa chọn onboarding của bản thử, không đổi spawn level canonical hay REFERENCE_L5 của Qoder. EXP quái12; boss local cấp1 dùng HPoverride640/ATK20/DEF6 và120EXP để có encounter ngắn; chưa phải balance boss production12600HP minh họa. Giới hạn cấp10, chưa có phân bổ điểm/gear stat vector/rank/PvP. Thuốc100HP/50MP/CD10s, mua3/10Đồng; weapon thưởng đặt tổngattack26 và hồi phục khi trả quest là fixture playtest. Không đưa những số này vào ItemDefinition/server thay nguồn đã review.

Phản Quang dùng precision DEC-022 cho cửa8tick, một counter tick kế tiếp, +2resource và whiff20tick. Bản local chưa kiểm mọi interaction status/PvP/LOS; engine guard tests không chứng minh runtime Qoder đã tích hợp. Không có cinematic video/voice thực trong gói, chỉ thoại và nhạc.

## Kiểm tra và tái tạo

```powershell
node Tools/PlayablePreview/tests/engine_checks.mjs
python -m unittest discover -s Tools/PlayablePreview/tests -p "test_*.py" -v
```

Full-run check đi bằng movement/interact/attack thật qua cả5quest/boss/cổng, không đặt teleport/HP/questflags để vượt tuyến; test guard/save/death/collision riêng có fixture. Browser UI/audio/touch cần kiểm riêng, không suy từ Node PASS.

Tái đóng gói hero/dialogue trong repo có Git/LFS: `python Tools/PlayablePreview/prepare_content.py`. Script đọc đúng commit Muse, smudge LFS khi cần; fetch ref/object trước nếu clone mới chưa có. Chạy lại giữ nguyên text/art gốc. Trong ZIP runtime không cần bước này.

Đóng ZIP runtime: `python Tools/PlayablePreview/package_playable.py --output D:/duong-dan/BenMua.zip`. Gói chỉ lấy11heroPNG và audio thực sự dùng; manifest SHA256 cho từng file. Không gộp master, audio không dùng, .git, personal files hoặc test save.
