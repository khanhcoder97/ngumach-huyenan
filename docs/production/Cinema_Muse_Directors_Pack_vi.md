# Bộ đạo diễn và prompt video cho Muse — v1

Owner Muse. Dữ liệu từng shot ở `Implementation/Content/Narrative/Cinema_Production_Pack_v1.json`: 20 cảnh,63 shot6giây, tổng378giây. Mỗi prompt đã gồm style lock và hành động riêng; không yêu cầu công cụ tạo một đoạn phim dài nhiều biến cố. Bộ này là kịch bản sản xuất, chưa có video được tạo hoặc duyệt.

## 1. Kết quả cần giao

Với từng CIN_xxx: storyboard/contact sheet, ảnh keyframe đã duyệt của mỗi shot, clip từng shot, sequence dựng, video silent, video mixed, audio stems, subtitles WebVTT/SRT, transcript UTF-8, poster/recap still và manifest. Các cảnh mô tả glyph/tên trên giấy phải để vùng trống cho typeset hậu kỳ; không dùng chữ sinh tự động như bằng chứng truyện.

Mỗi shot có seed/model/version nếu tool hỗ trợ, prompt nguyên văn, reference hashes và notes lỗi. Không đưa token/quyền tài khoản vào manifest. Không bịa trường seed khi provider không trả; ghi unsupported. Nếu tool không giữ pixel grid/nhân dạng thì gọi là animatic draft, dùng keyframe dựng lại; không chuyển dự án thành phim3D để giải quyết lỗi công cụ.

Ưu tiên P0: CIN_001/002/004; P1: 006/008/015/018/019; các scene còn lại P2 nội dung. Draft 3 cảnh đầu trước, không render trọn63 shot khi character/environment lock chưa được kiểm.

## 2. Chuẩn hình và nhân vật

- Master composition640×360 logical, 16:9; export1280×720 scale2 hoặc1920×1080 scale3 nearest-neighbor. Master editing30fps, giữ pose8–12fps theo cadence đã chọn và không optical-flow. Dùng PNG lossless keyframes và master lossless nếu công cụ cho phép; delivery H.264 MP4 yuv420p, audio AAC48kHz, giữ master/source. Codec có thể làm cạnh màu sai, phải xem bản encode thật.
- Giữ pixel art đã chốt, cluster/palette/outline có chủ ý. Camera cinematic được cận/trung/toàn theo shot, nhưng shot thoát phải về top-down XY như gameplay. Không suy cinematic close-up thành đổi góc gameplay.
- Ly An tóc buộc lệch, áo khoác mưa xanh/viền vàng đất, túi chéo; Tạ áo xanh đen/tay băng/kiếm gãy; Hạ Mặc áo xám giấy-lam mực, kính lúp; Sầm áo đỏ nâu/cân gỗ; Tống giáp ghép/vai lệch/cờ rách; Cơ hiện tại lõi đồng/khung lưng/mặt nạ sứ nứt. Dùng ảnh chuẩn trong Art Bible và reference của Muse, không dùng chiều cao WU cũ làm scale cinema.
- Cơ30 năm trước là người trưởng thành, chưa có khung máy/mặt nạ hiện tại; Tạ thời ký lệnh là người trẻ trưởng thành. Không làm Ly An xuất hiện30 năm trước hoặc người chơi đứng trong lịch sử đó.
- Avatar người chơi không hardcode thành Minh Kiếm nam. Các video chung ưu tiên POV/offscreen/không mặt; câu người chơi dùng subtitle, không tự chọn voice. Nếu cần avatar có hình, game compositing lớp sprite đã chọn hoặc Muse giao đủ variant được duyệt. Chưa có variant thì dùng master không avatar, không khóa người chơi vào trang phục khác.

## 3. Quy trình dùng prompt

1. Đọc purpose/trigger/revealTier và Narrative_Depth_and_Discovery_vi.md trước khi tạo reference. Dựng location/character contact sheet, palette, props và screen direction.
2. Chọn record scene, đọc từng shotId. `prompt` trong JSON là câu lệnh hoàn chỉnh; gắn approved reference tương ứng. Không nối3 prompt thành một request18giây.
3. Generate keyframe trước, kiểm tay/đạo cụ/hướng ánh sáng và thông tin spoiler. Sau đó tạo video6giây từ keyframe, giữ camera theo `camera` và đúng một hành động.
4. Check first/last frame: nhân vật/đạo cụ không mọc thêm, background không bơi, nước không đổi hướng giữa shot vô cớ, mưa/giọt nước có pattern ổn định, không parallax đổi map topology.
5. Dựng hard cuts hoặc match cuts; dissolve chỉ cho memory transitions có chủ ý, không dùng blur trộn cụm pixel. Dành1giây cuối shot cuối để handoff ổn định.
6. Lồng tiếng/âm nhạc tách khỏi clip hình. Thêm dialogue từ `dialogueLines`, nhưng timing cần cue sheet thủ công; không gán toàn bộ lời vào6giây nếu đọc không kịp. Có thể đặt lời trên khoảng hold/recap sau scene, không đổi số shot chính mà không cập nhật duration/manifest.
7. Giao PR draft kèm preview và thông số. Duyệt story→visual continuity→audio/subtitles→engine playback→device. ART_APPROVED không tự thành ENGINE_INTEGRATED.

## 4. Kịch bản mở đầu chi tiết — CIN_001 (36s)

Mục tiêu: người chơi muốn giúp Ly An và muốn biết tiếng chuông từ đâu. Chưa hiện tên Cơ, không kể lịch sử300 năm, không đánh boss trước khi người chơi được điều khiển.

| Timecode | Shot | Hình/nhịp | Âm thanh/thoại | Handoff |
|---|---|---|---|---|
| 00–06 | S01 | toàn Bến Mưa, một vòng nước đi ngược mưa rồi bình thường | mưa mỏng, gỗ kẽo kẹt, chưa nhạc | tò mò, không dọa bằng jump scare |
| 06–12 | S02 | dây kiện trượt và mắc chốt, không rơi mất | dây cọ gỗ, giọt rơi tách riêng | cho thấy việc nhỏ có thể giúp |
| 12–18 | S03 | bóng chuông dưới mặt nước nhưng phía trên trống | một âm đồng thiếu đuôi, không tiếng nói ma | bí ẩn cảm giác |
| 18–24 | S04 | sáp năm vạch trên thư còn niêm trong túi | tiếng mưa thấp đi0,5s, không chữ tiên tri | thư chưa vỡ, không lộ nội dung |
| 24–30 | S05 | Ly An giữ kiện, nhìn người ngoài khung | 25–29s: “Giữ giúp tôi đầu dây. Đừng để kiện ấy trôi.” | không gọi tên/giới tính avatar |
| 30–36 | S06 | về top-down bến; kiện đã tựa chốt, Ly An hướng chỗ đứng người chơi | tiếng làng trở lại, nhạc hai nốt rất nhỏ | fade0,25s vào vị trí server spawn; sau khi quay lại gameplay Ly An mới trao thư/accept |

Câu thoại nhận thư sau video vẫn thuộc dialogue tương tác: “Nếu họ hỏi, cô chưa từng giữ lá thư này.” Skip video trả recap “Một người đưa thư cần giúp ở Bến Mưa. Tiếng chuông chỉ vang trọn khi nhìn xuống nước.” Không tự ACCEPT_QUEST vì clip đã hết.

## 5. Cue âm thanh theo chương

| Vùng | Motif | Hành vi cụ thể |
|---|---|---|
| Bến Mưa | chuông thiếu âm cuối, mưa/gỗ | CIN002 phần âm cuối nghe dưới nước; không tiếng gọi tiên tri |
| Thanh Lạc/Thăng Long | búa nhỏ/tiếng chợ, nhạc gảy thưa | CIN006 để tiếng cân và giấy dẫn nhịp, không nhạc điều tra giật gân kết tội Sầm |
| Lâm Triều | lá/rễ/nước/giọng xa không rõ chữ | CIN008 hạ ambient để câu Tạ được nghe rõ, không choir tha tội |
| Sa Hỏa | nhịp kẹp lò, bình nước, gió bụi | CIN011 chuyển nhịp lao động sang khoảng lặng tại vết sửa quota |
| Trấn Sơn | bước chân/gate/kèn sơ tán | CIN014 sau con dấu đặt xuống dừng trống chiến, chừa im lặng |
| Bạch Uyên | áp suất/giọt/âm trầm dịu | CIN016 không ép cảm xúc bằng nhạc bi lụy; ưu tiên hơi thở và bút |
| Vực/ending | motif năm vùng đan nhau | CIN019 từng motif còn nhận ra, không tất cả hòa thành một âm duy nhất |
| Hậu truyện | âm bút và làng | CIN020 kết bằng trang giấy, không âm đe dọa teaser |

Master mix mục tiêu -16 LUFS integrated cho video hoàn chỉnh, true peak<=-1dBTP; đo khi có audio, không ghi PASS giả. Reduced audio/flash option; tiếng lớn không là cue duy nhất. Voice phải có quyền sử dụng và diễn viên/model được phép; không bắt chước giọng người thật.

## 6. Subtitle, localization và accessibility

Phụ đề tách track, tối đa2dòng, gợi ý<=38ký tự/dòng nhưng ưu tiên tiếng Việt không vỡ từ, 12–17ký tự/giây; đọc thử trên720p. Không đè vùng nguy hiểm vì scene chỉ phát trong safe narrative mode. Tên speaker ngoài thoại, sound caption khi thông tin quan trọng như [Chuông vang từ dưới nước]. Tắt âm vẫn hiểu manh mối; tắt video vẫn có recap.

Không dùng flash toàn màn hình, shake mạnh hay motion blur. Ký ức dùng palette/border/caption “Ký ức • khoảng30 năm trước” hậu kỳ; không chỉ dựa hue để phân biệt lịch sử. Không cần lip-sync ở shot xa; ở close-up người đang nói phải có keyframes miệng được duyệt hoặc dùng offscreen VO.

## 7. Trigger, skip, replay và multiplayer

`triggerDescription` là contract thiết kế, chưa là predicate code. Qoder chuyển thành guard quest/objective server; không đoán tên flag từ lời mô tả. `revealTier` giới hạn journal/replay, không phải độ hiếm vật phẩm. Receiver chỉ phát scene khi server cấp narrative permission và player ở safe/private layer.

Video không cấp reward, không tự set quest COMPLETE, không pause shared simulation. Skip hold0,7s, watchdog load3s→fallback still+recap. Reconnect giữa cảnh: nhận state server, hiện tùy chọn xem lại; không phát cảnh boss intro trong combat đã ACTIVE. Raid ending chỉ sau victory transaction, phát cá nhân tại lobby; không bắt vote skip toàn party. Replay từ journal luôn không có reward.

## 8. File paths và manifest video

Source ngoài Unity: `Art_Source/Cinematics/CIN_xxx/` (cần bổ sung quyền sở hữu vào work order). Delivery MP4: `Client/Assets/Cinematics/CIN_xxx/`; subtitles/manifest: `Implementation/Content/Narrative/Deliveries/CIN_xxx/`. Preview qua GitHub release artifact hoặc PR link khi dung lượng quá lớn; không ép người review tải mọi master. MP4/WAV/PNG theo Git LFS; không commit cache/model weights.

Manifest video sidecar tách schema manifest sprite hiện có: sceneId/questId/packVersion/status/duration/fps/width/height/codec/videoPath/posterPath/subtitlePaths/audioStems/sourceCommit/referenceHashes/modelInfo/licenseEvidence/continuityNotes/reviewer/evidenceUrls. Video chưa có thì delivery manifest không tạo path giả. Trạng thái REQUESTED→STORYBOARD→ANIMATIC→VISUAL_APPROVED→AUDIO_APPROVED→ENGINE_TESTED→DEVICE_QA.

## 9. Checklist nghiệm thu Muse

- Đúng nhân vật/đạo cụ, đồng nhất shot trước-sau, không đổi tay băng/vị trí mặt nạ hoặc trang phục avatar.
- Đúng reveal guard: không lộ lịch sử của Tạ trướcC2-04, người sống sót trướcC5-03, lựa chọn cơ chế trướcC6-05.
- Thời lượng shot/cảnh khớp manifest; hình không sinh chữ vô nghĩa, watermark hay pixel bị nội suy.
- Tiếp gameplay đúng top-down, không tự đổi tọa độ/quest state, fallback/skip/replay chạy được.
- Có master/preview/stems/subtitle/provenance, kiểm export sau encode trên thiết bị; video là tư liệu thật mới được đánh dấu đã bàn giao.

## 10. Danh mục sản xuất

| Scene | Quest | Tên | Giây | Reveal gate |
|---|---|---|---:|---|
| CIN_001 | P00-01 | Nước không soi bóng | 36 | OPENING |
| CIN_002 | P00-02 | Âm cuối dưới nước | 18 | OPENING |
| CIN_003 | P00-03 | Hai người, hai bóng | 18 | OPENING |
| CIN_004 | P00-05 | Vết đau của linh thú | 18 | OPENING |
| CIN_005 | C1-01 | Một thành phố vẫn sống | 18 | CHAPTER_1 |
| CIN_006 | C1-06 | Con dấu qua phố | 18 | CHAPTER_1 |
| CIN_007 | C2-02 | Tên trong vỏ cây | 18 | CHAPTER_2 |
| CIN_008 | C2-04 | Bàn tay đã ký | 18 | CHAPTER_2 |
| CIN_009 | C2-05 | Tiếng rừng được đáp | 18 | CHAPTER_2 |
| CIN_010 | C3-01 | Bình nước cuối xe | 18 | CHAPTER_3 |
| CIN_011 | C3-03 | Chữ khắc bị sửa | 18 | CHAPTER_3 |
| CIN_012 | C3-05 | Giữ tên người sống | 18 | CHAPTER_3 |
| CIN_013 | C4-01 | Qua cổng, còn người đợi | 18 | CHAPTER_4 |
| CIN_014 | C4-05 | Dấu lệnh đặt xuống | 18 | CHAPTER_4 |
| CIN_015 | C5-01 | Thành phố dưới nước | 18 | CHAPTER_5 |
| CIN_016 | C5-03 | Quyền được kể lại | 18 | CHAPTER_5 |
| CIN_017 | C5-05 | Lõi và dòng triều | 18 | CHAPTER_5 |
| CIN_018 | C6-04 | Điều ông không cho ai từ chối | 18 | CHAPTER_6 |
| CIN_019 | C6-05 | Năm mạch, không một chủ nhân | 18 | ENDING |
| CIN_020 | SQ-DM-05 | Thư có hồi âm | 18 | EPILOGUE |
