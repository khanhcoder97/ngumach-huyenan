# Biên tập tiếp Bến Mưa và Con dấu qua phố

Source tại branch `codex/narrative-workshop-20261031`, PR95. Ngày2026-10-31. Bản sửa này tiếp workshop có sẵn, không thay CSV230dòng/76quests, spawn manifest, quest/reward/closedAPI hoặc cinema production source.

## Kết quả thực tế

Sửa BM04 để mọi nhánh đã giữ túi đều trao lại trước checkpoint kế; lời hỏi phụ thuộc việc người chơi thật sự đã cầm. BM05 bớt lặp nút dây, kết bằng người chèo đò thử sợi neo. Nhánh hỏi Tạ có câu trả lời cụ thể hơn và yêu cầu từ Ly An; chi tiết “bản chép” là claim ứng viên, chưa là collectible/canon fact hay đáp án quá khứ.

Viết mới toàn C1-06 “Con dấu qua phố”:10cảnh+2checkpoint reading-room, năm bước nguồn hóa đơn/dấu lò/lưu trữ/đối chiếu/báo cáo. Có lựa chọn hỏi sai, chép bằng chứng bất lợi, mô tả thay hình nhỏ và sửa kết luận. Giữ nghi vấn theo chứng cứ, không chấm điểm đạo đức hoặc tạo Trust flag. Bốn giọng Hạ Mặc/Sầm/thợ phụ/quan thư lầu được phân biệt bằng việc họ làm và điều họ biết.

Packet Muse bổ sung CIN_006,3shot×6s, giữID/duration/trigger nguồn, prompt hình và diễn xuất/âm thanh/fallback. Chưa tạo video/voice. Những vị trí Hạ Mặc/Sầm chưa thống nhất giữa quest/cinema và registry được ghi thành integration requirement, không tự dịch chuyển actor hoặc sửa tọa độ.

## Kiểm tra đã chạy

- inkjs2.4.0 compile:0warning,39records (28SCENE+10CHECKPOINT+reading room). `npm run check` PASS:38node truyện/checkpoint đều tới được,2398choiceedges,992decisionstates,31explicitends; replay/gate tên Huyền Ấn/thứ tự evidence/reset Thăng Long/cinema source+timing đều đạt.
- Compiler C# officialInk1.2.1 compile cùng main.ink ra file tạm ngoài repo; chạy cùng verifier trên output này, cùng38nodes/2398edges/992states PASS. Đây là hai compiler cho bản đọc, không là engine/game acceptance.
- BrowserChrome headless mở server riêng cổng động: cả entryBếnMưa vàThăngLong load/actualbuttonadvance PASS, route không biết/traversal404. Chỉ dừng process của smoke; reader người dùng tại8126 được giữ.
- Đã nhìn screenshot Thăng Long: sidebar có mụcC1-06, chữ Việt đọc được, speaker styles/choices/header hoạt động, annotation mặc định ẩn. Screenshot sau bấm lựa chọn nên main có scroll; không là layout nativeHUD hoặc mobile acceptance.
- Canonical/runtime source không sửa; kiểm generated drift và git diff whitespace trước commit. SourceDigest `3b3e04a6a5c4bf093804c6a3e228faaee2531ce4a07eff29525562faf3b86658`.

## Giới hạn

Authoring candidate/runtimeOFF. C1-01..05 và chương sau chưa có scene-level draft trong workshop này. Chưa có người đọc độc lập xác nhận văn hay, VO/video/native/livequest chưa nghiệm thu. Đọc EDITORIAL_REVIEW_20261031_vi.md để biết lựa chọn biên tập và điểm cần đánh giá tiếp; compile không chứng nhận chất lượng truyện. Phạm vi report workshop cũ vẫn là snapshot lần đầu, không sửa lịch sử để đổi count.
