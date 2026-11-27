# Bến Mưa: biên kịch, canon và tích hợp

Status AUTHORING_CANDIDATE; runtimeActivationAllowed=false. Nguồn văn bản mới là bảy file `.ink` (main, năm Bến Mưa, C1-06); hai bản screenplay Markdown và JSON preview được build từ đó. Không dùng chúng thay CSV hoặc compiler gameplay. Guard trong tags mô tả yêu cầu tương lai, không là expression đã được runtime xác minh.

## Người giữ thư

| Cảnh | Người giữ trong bản thảo | Điều người chơi thấy |
|---|---|---|
| BM01_LETTER | Ly An → người chơi | Vải dầu, niêm nguyên; không đọc thư |
| BM01_RECEIPT | Người chơi → Tạ | Chuyển thư theo objective hiện có |
| BM01_SEAL | Tạ trên khay dưới mái kho | Ông nhận ra điều gì đó nhưng không mở/giải thích |
| BM02_REPORT | Tạ → Ly An | Ông yêu cầu mang theo khi ra đầm |
| BM03_SHORE | Ly An | Túi ướt, cô kiểm lớp che niêm |
| BM04_CRACK | Ly An | Rạn tại checkpoint, không do người chơi lựa chọn đúng/sai |
| BM05_NAME | Ly An giữ thư; mảnh ấn dùng prop theo interaction | Hai vật cùng phản ứng, chưa kết luận nguồn gốc |

Việc trả thư cho Ly An và những động tác tay/túi là **staging mới cần consumer review**, chưa là ownership transaction. Không tạo thêm instance item hoặc cho phép dùng preview gây duplication. Canon chưa chốt người gửi/nội dung thư; không tự giải bằng huyết thống avatar hoặc lời thú tội Tạ.

## Điều đã thấy, giả thuyết và bí mật người viết

| Mốc | Quan sát có thể kể lại | Chưa được ghi thành sự thật |
|---|---|---|
| P00-01 | Ba dấu dây, niêm năm vạch, Tạ kiểm mặt niêm | Ai gửi thư, vì sao Tạ nhận ra |
| P00-02 | Ripples co vào, bóng chuông, âm thay theo vị trí | Có chuông vật lý thật, ai đánh chuông |
| P00-03 | Hai người được cứu kể khác nhau | Ai nói dối, avatar từng có mặt, ký ức là video toàn tri |
| P00-04 | Sáp rạn khi túi đứng yên; đường ra đầm nguy hiểm | Cơ gây ra việc này, thư tự mở hoặc nội dung thư |
| P00-05 trước seal | Nước trở lại, một vệt kim chưa đổi theo mây | Tên Huyền Ấn chưa được NPC nói ở đoạn trước interaction |
| P00-05 sau seal | Tên Huyền Ấn, Tạ đã nghe tên, chưa kể ở đâu | Trách nhiệm Tạ, sự kiện 30 năm, Bạch Uyên/Cơ, avatar được chọn do huyết thống |

Nguồn canon dài hạn: Narrative_Depth_and_Discovery_vi.md. C2-04 mới mở chữ ký phong tỏa của Tạ. Khái niệm hai mốc 300 năm/30 năm không trộn. Kịch bản mở đầu không giảng hai mốc này. Ngày sau, biên tập chương tiếp dựa trên tri thức từng nhân vật tại thời điểm đó.

## Những chi tiết mới chưa thành runtime

- Nút dây/dấu vải, khay thư, cử chỉ, nội dung hội thoại và quan hệ được diễn rõ hơn là candidate trình bày. Dùng existing packages/actors; không thêm tracked item/node hoặc tọa độ mới.
- Hai người được cứu giữ canonical IDs NPC_BM_RESCUE_01/02. Muốn đổi pose hoặc đứng sau giải cứu cần phase/visibility adapter; không tự chuyển 349 placements. Mâu thuẫn source rescue P00-03/P00-04 còn mở ở báo cáo content candidates.
- Cảnh nghỉ ở hai escort checkpoints chỉ khi server đã clear wave và vùng an toàn; không pause world hoặc dùng ended video để tiến quest. Lời cảnh báo boss không thêm threat/taunt mechanic.
- Mảnh ấn sau boss chỉ xuất hiện khi interaction được xác nhận. Không tự chọn lại lớp; NPC_CLASS_TRIAL còn cần availability review. Không sửa reward IDs/counts/XP, drop hoặc balance bằng việc đổi lời thoại.
- Choices trong bản đọc chỉ đổi câu đáp/local reading-room variables. Chưa có Trust hoặc persistent story flags tương ứng. Nhánh khác nhau vẫn hội tụ ở các mốc nguồn.

## Packet cho người phát triển và Muse

Consumer chỉ nhận các scene cần thiết sau khi guard/IDs được đối chiếu với contract. Đề xuất sơ đồ mở rộng: OFFER → accepted/explore/checkpoint → READY → request turn-in → pending/error/fullbag hoặc committed receipt → after-commit scene. Không nhét mọi đoạn mới vào OFFER/CLUE/TURN_IN và không cho lời khen của NPC thay receipt.

Mỗi line live cần localization key/line ID riêng khi migration được thực hiện. scene_manifest.json cung cấp scene ID/knot/source line/digest để biên tập và mapping; **chưa là runtime DialogueDefinition**. Cutscene triggers là dữ liệu thiết kế, chưa phải message contract. Không auto-play CIN_001 khi COMPLETED P00-01: nguồn đặt opening trước accept trong safe layer.

Video đã có trong source: CIN_001 trước accept 36s; CIN_002 sau ba ripple 18s; CIN_003 sau rescue trong chỗ nghỉ 18s; CIN_004 trước combat P00-05 trong private ready-check 18s. Không gán CIN_004 cho cảnh gọi tên mảnh ấn sau boss. BM05_NAME hiện dùng in-engine/text staging; cần proposal riêng nếu muốn thêm video. Đọc MUSE_CINEMA_DIRECTION_vi.md để dựng storyboard/performance. Chưa yêu cầu Muse render toàn bộ trước khi khóa keyframe.

## Bổ sung ngày 2026-10-31: continuity và C1-06

Bến Mưa: mọi nhánh giữ túi ở BM04 đều hoàn trả trước khi đi chặng hai. Khi người chơi không giữ túi, Ly An tự tìm chỗ va thay vì hỏi như họ đã cầm. BM05 giảm lặp nút dây, trả cảnh cuối về chiếc đò của người vừa cứu. Lời Tạ về một bản chép là **phát biểu ứng viên của nhân vật**, không chứng minh bản chép đúng, không đặt thêm collectible hoặc xác nhận nguồn gốc Huyền Ấn. Nếu giữ take này, chương sau cần trả được lời hẹn cho Ly An/người chơi xem; không được thay bằng một lần trì hoãn chung chung nữa. Chưa phát sinh quest tìm sách.

C1-06 được viết đủ năm bước nhưng vẫn là authoring candidate. `tl_step`0..4, `tl_margin_seen`, `tl_report_style` chỉ điều khiển reading room. Các câu mô phỏng không chấp nhận quest/consume/award hoặc chứng nhận checkpoint live. Không có Trust score hay phạt lựa chọn. Nhánh kết tội sớm dẫn tới yêu cầu chỉ chứng cứ, cho sửa hoặc giữ giả thuyết có nhãn; mọi nhánh dùng cùng reward nguồn sau receipt.

| Quan sát trong bản thảo | Suy luận cho phép | Chưa chứng minh |
|---|---|---|
| Hóa đơn ghi giấy; có khoản ứng nước bị tranh chấp | Sầm tham gia đường cung cấp giấy; sổ có phần bất lợi | Ông vô tội hoặc chỉ huy phù giả |
| Vòng dấu tương tự, một gờ kéo khác hai vết ép | Không dùng vòng ngoài để xác nhận cùng công cụ | Thợ phụ biết người làm giả |
| Ngày giao có sửa và phần nộp bổ sung còn lưu | Phải giữ cả trước/sau và đọc đúng cột | Đó là vụ xóa hồ sơ tháp hoặc phong tỏa ba mươi năm |
| Mẫu nhựa và trang mô tả đối được sau ba nguồn | Tuyến vật liệu dẫn về Lâm Triều | Ai ra lệnh, ai viết thư, vai trò Cơ |

Chi tiết sổ/khoản nước/vết dấu/mẫu giấy là văn cảnh mới cần content review trước migration; không được xuất chúng thành item/node/stat sản xuất bằng suy đoán. Mô tả nhựa trước đối chiếu chưa nói địa danh; chỉ ở COMPARE sau đủ nguồn mới nêu Lâm Triều. Cinema phải sau xác nhận đối chiếu và trước report, tên của nó không là completion event.

### Actor và placement cần nối, chưa tự chuyển map

Nguồn Quest Spec và CIN_006 đặt Hạ Mặc/Sầm tại đoạn truyện Thăng Long; Actor Registry/World Manifest hiện giữ NPC_HA_MAC ở Thanh Lạc và NPC_SAM_CHU_QUY ở Sa Hỏa. Đây là **mâu thuẫn tích hợp có thật**. Chọn phase-specific appearance/remote service hoặc migration anchor qua producer review; không dùng vị trí (0,0), không clone ID global, không tự dời XY canonical. Bản đọc mô tả cuộc gặp thiết kế, không chứng nhận actor đã spawn.

Thợ phụ dùng NPC_TL_CIVILIAN_06, thư lầu dùng NPC_COURT_ARCHIVIST, người chở hàng dùng NPC_TL_CIVILIAN_01, đều có registry/manifest Thăng Long. Bàn dấu/giấy và ghế là set dressing; tương tác quest riêng cần source ID/binding rõ. Không lấy NPC_BLACKSMITH Thanh Lạc làm thợ Thăng Long. Toàn bộ vị trí/nav/camera-path phải theo top-down và phạm vi map đã duyệt, không shrink kinh thành để ba quầy chung một màn hình.

### Giữ năm bước thành hành động

LIVE: ledger-interact-confirmed → forge-clue-confirmed → archive-clue-confirmed → comparison-confirmed → turn-in committed. Chỉ là semantic proposal, chưa là event contract. Cho xem lại evidence không nhân progress. Thiếu evidence dẫn về bước còn thiếu, không tự bù bằng đoạn recap. Trong reading room, recap phần bên lề chỉ phục vụ đọc tiếp; không được copy logic đó làm bypass server. Reward giữ300Đồng/EXP chưa tự điền/Huy hiệu Thanh Lạc và C2-01/route theo nguồn.

Đọc `MUSE_THANG_LONG_CIN006_DIRECTION_vi.md` và packet cinema đã bổ sung CIN_006 (3shot×6s). Không render C1-01/02/03/04/05 thành đã viết trong workshop: các quest đó mới có canonical outline/thoại nguồn, chưa có bản cảnh sâu như C1-06.

## Ghi nhận tự biên tập đợt trước

Đã đọc liền năm quest và sửa lần hai: bỏ người áp tải mất tích chưa có payoff; thay một câu giải thích quan sát bằng câu hỏi vị trí; thay lời cảm ơn ẩn dụ bằng lời nói về tay trơn. Chọn giữ việc Tạ trì hoãn lời giải vì reveal schedule đã chốt, nhưng kết cảnh bằng công việc đưa người về bến thay một lời hứa bí mật to tát.

Đây là ghi nhận tự biên tập của Codex, không là phản biện độc lập hoặc người chơi đã duyệt. Còn cần người đọc đánh giá giọng Ly An/Tạ có phân biệt, đoạn cứu dân có đủ khoảng thở, và lời né của Tạ có bị lặp. Công cụ chỉ kiểm nhánh và invariants; không có điểm tự động chứng nhận văn hay hoặc xác định AI/human.
