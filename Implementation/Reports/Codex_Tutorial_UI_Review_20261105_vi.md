# Nhật ký, art khám phá và nghiệm thu nhân sự — 05/11/2026

Baseline f383233, nhánh codex/tutorial-expansion-20261105. Không nhận toàn bộ PR106/109/119 khi còn các lỗi đã tái hiện. Báo cáo review có source SHA cụ thể tại Review_20261105; gói sửa lớn và phần việc tiếp tục tại Work_Orders/30_REVIEW_REPAIRS_AND_NATIVE_TUTORIAL_20261105.md.

## Phần đã triển khai trong Godot

Nhật ký mở bằng J hoặc bảng nhiệm vụ, dùng title, thoại và mục tiêu từ source; state/counter lấy từ server. Năm nhiệm vụ P00 có metadata; locked không lộ tên/nội dung về sau. Nhiệm vụ hoàn thành lưu phần thoại đã xác nhận giao nhận, thay vì lặp lời nhắc còn thiếu kiện hàng. Không cắt đoạn truyện giữa chừng. Tracker ưu tiên ready/active/available, theo tiến độ được server công bố. Hội thoại NPC có thể chọn nhiệm vụ kế tiếp đã AVAILABLE, thay vì khóa cứng P00-01; lật trang, hỏi thêm và xem nhật ký không grant.

Giao diện đã sẵn sàng đọc thêm quest; backend hiện tại vẫn chỉ nghiệm thu native tuyến P00-01. Không gọi đây là tutorial năm nhiệm vụ đã chơi xong. Source Alpha definition được giữ riêng, không sửa canonical activation BLOCKED.

Art mới bằng image_gen: atlas 1536×1024, tám cell384×512 gồm bốn pha gợn nước và hai dân mắc kẹt với pose chờ/đứng. Giữ alpha nguyên gốc; inspect_combat chỉ đọc bitmap và ghi metadata. Runtime nhận exact alpha IDs trong world rồi mới vẽ marker; không dựng actor hoặc tiến độ giả. Gợn nước có loop presentation; dân dùng pose chờ, chưa suy ra pose cứu thành công. Fragment dùng sprite có sẵn. Gallery native chỉ kiểm hình, không phải tọa độ spawn hoặc chứng nhận backend đã chạy.

Launcher chơi tay tạo thư mục log riêng theo timestamp + ID ở tools/play-sessions. Các log Playable_Alpha cũ đã bị lần chơi tay trước đó thay đổi được giữ nguyên trong worktree, không stage/ghi đè. Build dùng một MSBuild node để giảm tải máy.

## Kiểm chứng

- Godot 4.7.2 .NET/OpenGL GeForce820M: P00-01 nhận/làm/trả, J mở nhật ký, counter3/3, committed story và inventory đúng20COIN+1áo: **125 assertion PASS**, exit0. Bằng chứng mới riêng tại Evidence/Tutorial_UI_20261105/; không ghi đè log chơi tay.
- QuestPresentationSelfTest: **12 assertion PASS**, source/DTO UI only. Kiểm AVAILABLE P00-02 được chọn thay completed P00-01, final action bind đúng quest/NPC, đọc trang không nhận quest, pending không gửi trùng, ACTIVE chuyển sang clue, tracker theo quest kế tiếp và locked không lộ title. Đây không phải HTTP/tutorial completion.
- Camera48, input/physics9, animation/VFX15 PASS sau thay đổi. Locked build client0 warning/0 error. Inspector combat8 source/runtime byte pairs, 64 body frames,36VFXframes,6questsprites/6mobposes/6nodes/6icons và8markerframes PASS; catalog source check PASS.
- Screenshot nhật ký, world, inventory và gallery được render trực tiếp trong Godot. Chưa nghe thử audio Muse, chưa nghiệm thu native video.

## Nghiệm thu và công việc đã giao

OpenCode c3c8a12 có221unitPASS, timeout/alphaID fix tốt, nhưng còn death-return/callback sauDispose và UI Dispose đứng khoảng2giây. Qoder cb4f475 có556self-check/17deathHTTPPASS nhưng đời nhân vật bị evict sau256nhân vật khác chết; fullalphaHTTP thất bại ởP00-04, escort chưa ra world, P00-05 thiếuTALK. Muse3f34f0d có timing20scene,72sreel storyboard và3VOdraft; 541audio là port pack Codex cũ. Đã xác nhận sai4cuecount,40hash Windows doCRLF và5picturedefects. Các PR giữ ngoài baseline cho tới khi sửa và review lại.

Work30 đã gửi qua issues85/87/116/79, review chi tiết trên PR109/106/119; OpenCode được gọi trực tiếp CLI với cùng session/model/auth. Không tuyên bố agent đã sửa khi chưa có checkpoint mới. Muse được duyệt21cửa sổ để làmVO nháp theo decision JSON mới; câu thoại đối chiếu canon, thời gian trong shot. CIN020 có voice role cinematic-only cho Người nhận thư, không sinh NPC gameplay. Đây không duyệt final picture/mix/autoplay. LF/LFS policy mới hỗ trợ sửa gói media, không nhận cả reel làm opening.

## Phần còn thiếu

Full tutorial/boss/death/equip12/campaign/persistence, world projection cho escort, map migration và các lớp/asset còn lại chưa được native nghiệm thu. Không dùng sprite/VFX/video callback để vượt các khoảng trống đó. Codex tiếp nhận từng checkpoint đã kiểm, giữ production OFF.
