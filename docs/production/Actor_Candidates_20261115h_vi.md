# Huyền Bút: sửa chạy N/E và tương tác NE — ứng viên H

**Ghi chép ứng viên trước bản E v4; giữ làm lịch sử.** Bản v4 đã sửa đầu bút pha12 và ba nguồn H đã được kiểm/áp ledger. Trạng thái cuối xem [báo cáo H](Actor_Batch_20261115h_vi.md). Các quan sát và việc còn chờ bên dưới là mốc trước nghiệm thu nguồn, không phải trạng thái hiện hành.

H có ba sheet chọn/48 tư thế, năm phiên bản PNG nguyên gốc được lưu bằng công cụ tạo ảnh tích hợp. Ảnh, prompt và lịch sử ở `Art_Source/Actor_Library_20261107/Candidates_20261115h`. Có ba video native hiện hành, hai video E thử trước lưu riêng; mỗi video hiện hành giải mã đủ 180 frame. Trace xác nhận đã xem đủ 16 pha thật; hai dải nối 14/15/0/1 lấy từ vòng lặp thực, không xếp ảnh tùy ý để giả lập đường nối.

- Chạy N: bản mới phân biệt chân thấp ở contact0/8 rõ hơn; đã xem đủ 16 pha và đường nối. Còn cần so với các hướng còn lại, chuyển action và di chuyển thực.
- Tương tác NE: đã bỏ bàn tay idle dư trong các pha đưa lòng bàn tay ra. Đã xem đủ 16 pha; còn kiểm NW lật và chuyển action.
- Chạy E v1: hai nửa còn lặp nhịp tay/chân. V2 đổi được nhịp tay nhưng bút bật vị trí ở 15→0. V3 sửa bốn pha cuối, đường nối bút đã tốt hơn; **pha12 vẫn thiếu silhouette đầu bút/ferrule rõ ràng nên cần vẽ tiếp**, chưa duyệt từ việc nối vòng tốt hơn.

`Tools/ArtProduction/prepare_actor_candidate_review.py` tạo portable project Studio riêng với PNG byte giống nguồn, 16 vùng ảnh và pivot/timing đo từ nguồn. Các project ở `Implementation/Reports/Evidence/Actor_Batch_20261115h/Candidate_Studio`; mở `project.json` bằng chức năng mở project của Studio để chỉnh tay. Công cụ chỉ dùng cho whole-body Huyền Bút hiện tại; không tự chấp nhận actor khác. Catalogue và 362 pin G không đổi khi chuẩn bị bundle.

`review_actor_candidates_20261115h.ps1` ghi từng project bằng Godot; `finalize_actor_candidates_20261115h.py` kiểm trace/giải mã và xuất ảnh bằng chứng từ video. `manual_review_working.json` chứa ghi chú cùng hash nguồn/bằng chứng, mang `manualReviewComplete=false`. Không dùng tệp này làm ledger approval hoặc thay asset gameplay. PNG nguồn không bị vẽ lại, ghép ô hoặc chỉnh alpha bằng script.

Việc tiếp theo: sửa đầu bút pha12 E, kiểm lại toàn bộ pha có thay đổi và đường nối; so hướng W/NW, chuyển đứng→chạy→tương tác trước migration và ledger chính thức. Sau đó kiểm/vẽ lại năm action kế thừa idle/walk/basic_attack/hurt/death và ghép VFX hỗ trợ Huyền Bút với sự kiện xác nhận. Các class khác, quái/boss/NPC, biến thể, map/UI và gameplay vẫn thuộc mục tiêu tiếp tục.
