# ĐẶC TẢ BANG HỘI, XÃ HỘI VÀ CÔNG THÀNH
## Ngũ Mạch: Huyền Ấn — bản sản xuất v1.0

### 1. Mục tiêu hệ thống

Bang hội tạo nơi chơi chung lâu dài: nhận mục tiêu tuần, cùng giúp thành viên mới, mở mỹ phẩm/sảnh, và tham gia công thành 20v20. Tiến trình bang không khóa cốt truyện chính, không tạo độc quyền vật liệu cấp cao, không tăng sát thương PvP vô hạn. Tài liệu này bổ sung chi tiết cho mục 7.2 GDD.

Trung tâm guild đặt tại `MAP_THANG_LONG`, Phường Bang Hội, `NPC_GUILD_CLERK=(636,0)`; counter dịch vụ cơ bản ở `MAP_THANH_LAC=(309,0)` vẫn dùng cùng canonical NPC ID và một guild ledger. Guild Hall mở panel bang, kho, nhiệm vụ, sự kiện, quyền và lịch sử; đi vào đây không đưa người chơi tự động vào siege instance.

### 2. Tạo bang và vòng đời

**Điều kiện tạo:** nhân vật cấp 10+, chưa thuộc bang, trả 20.000 Đồng và 10 Huy hiệu Thanh Lạc. Tên 3–20 ký tự; tag 2–4 ký tự ASCII; kiểm duyệt từ cấm, trùng tên và ký tự vô hình. Khẩu hiệu tối đa 80 ký tự, có kiểm duyệt chat. Creator trở thành Bang chủ. Có thể có tối đa 4 bang trên một tài khoản nhưng chỉ một nhân vật tham gia bang tại một thời điểm.

**Vòng đời trạng thái**
- CREATED: tạo xong, có 24h để mời ít nhất 3 người; nếu không bang vẫn tồn tại, không bị xóa tự động.
- ACTIVE: hoạt động bình thường.
- DORMANT: 45 ngày không có đăng nhập của bang chủ/phó; hệ thống nhắc thành viên, có quy trình chuyển quyền.
- DISSOLVING: bang chủ xác nhận giải tán 2 lần trong 24h; khóa đóng góp, chợ, công thành; sau 7 ngày giải tán hoàn toàn.
- MERGED: không gộp tự động. Khi giải tán, quỹ chia vào hòm thư theo quy tắc và kho chung trả về người đóng góp nếu log còn; item nghiên cứu/mỹ phẩm không chuyển.

**Giới hạn ban đầu:** 40 thành viên; mở cấp bang theo bảng tiến trình tới tối đa 60. Bang không thể vượt cap; lời mời hết hạn sau 72h. Người rời bang có cooldown 24h trước khi vào bang khác; kick không tạo cooldown dài hơn 12h trừ vi phạm hệ thống.

### 3. Vai trò, quyền và nhật ký

| Vai trò | Số lượng tối đa | Quyền mặc định |
|---|---:|---|
| Bang chủ | 1 | toàn quyền, đổi tên một lần/năm, giải tán, chuyển chủ |
| Phó bang chủ | 2 | mời/kick thành viên thường, mở sự kiện, xem kho, đề xuất chi tiêu |
| Trưởng lão | 5 | mời, duyệt đơn, tạo nhóm nhiệm vụ, xem đóng góp |
| Thành viên | theo cap | chat, đóng góp, đăng ký sự kiện, rút vật phẩm cá nhân được gửi vào kho nếu policy cho phép |
| Tân binh | tối đa 10 | chat guild, nhiệm vụ hướng dẫn; không rút kho |

Mỗi quyền tắt/bật riêng: invite, approve, kick, edit bulletin, start guild quest, access treasury, withdraw item, set siege roster, promote, demote, transfer ownership. Quyền mặc định không thể rút tiền/quý vật khỏi kho bởi bất kỳ ai ngoài Bang chủ và Phó. Rút đồ kho yêu cầu 2 người phê duyệt nếu item được gắn tag HI_VALUE. Mọi thao tác ghi Actor, item/currency, lượng, thời điểm, requestId, lý do. Log hiển thị 30 ngày; audit đầy đủ lưu nội bộ 180 ngày.

**Chuyển bang chủ:** xác nhận của chủ hiện tại + người nhận online; nếu chủ không đăng nhập 30 ngày, phó có thể mở biểu quyết 72h, cần 60% thành viên active tham gia và đa số phiếu. Không thể chuyển khi siege/treasury transaction đang mở.

### 4. Cấp bang, XP và mở khóa

| Cấp | Thành viên | Công trình/sảnh | Mở khóa |
|---:|---:|---|---|
| 1 | 40 | Sảnh gỗ 1 | bảng tin, chat, quest bang 3 loại |
| 2 | 44 | nâng sảnh 1 | kho bang 40 ô, 1 nhóm nghiên cứu |
| 3 | 48 | sảnh 2 | đoàn xe tuần, 2 nhóm nghiên cứu |
| 4 | 52 | sảnh 2 | công thành, trang phục bang |
| 5 | 56 | sảnh 3 | kho 80 ô, banner tùy chỉnh |
| 6 | 60 | sảnh 3 | chiến tích, emote, sân luyện |
| 7+ | tối đa 60 | trang trí | mỹ phẩm/tiện ích xã hội, không tăng damage |

XP bang tới từ quest tuần, sự kiện, tuyển thành viên mới được xác minh, boss group contribution. Cấp 2–6 mỗi lần yêu cầu Đồng + vật liệu bang và XP; số tiền/cost phải hiện trong UI. Không mua XP bằng tiền thật. Cấp 7+ dùng XP để đổi cosmetic và cải thiện xã hội, không tăng combat stats. Mỗi thành viên đóng góp tối đa 5.000 Đồng/ngày và 30 đơn vị vật liệu bang/ngày tính XP, chặn alt-farm.

### 5. Kho bang, quỹ và công trình

**Kho vật phẩm:** 80 ô tối đa; chỉ vật phẩm tradeable, không quest-bound, không item đang mặc. Gửi không mất phí; rút có permission, cooldown 10s chống double click. Có log deposit/withdraw; item vừa gửi bởi người mới chưa duyệt có thể có hold 24h nếu high value.

**Quỹ bang:** hai sổ cái tách: Đồng thường và Điểm Công Trình. Mọi giao dịch atomic; không dùng quỹ bang cho trade cá nhân, không chuyển quỹ khi giải tán trừ khoản đã ghi trong quy chế server. Màn hình hiển thị thu/chi 14 ngày và limit theo role. Phó chủ cần Bang chủ duyệt mọi chi trên 100.000 Đồng.

**Công trình**
- Sảnh: thay backdrop, bàn họp, vật phẩm trang trí, điểm tập hợp; không cộng chỉ số.
- Bảng tin: nhận quest nhóm, chọn giờ hoạt động.
- Sân luyện: dummy, DPS log cá nhân; không cấp XP/loot.
- Trạm hậu cần: sửa đồ/đổi thuốc ở hub guild với giá NPC bình thường.
- Tủ chiến tích: trưng bày cúp công thành và bảng thành viên.
Vật liệu bang có nguồn từ quest, boss vùng và nghề, giới hạn weekly pool; công trình không tiêu vật phẩm Di vật/Cổ Vật.

### 6. Nhiệm vụ bang hội

Mỗi tuần bang chọn 3 nhiệm vụ từ pool; mỗi nhiệm vụ cần contribution của tối thiểu 5 thành viên hoặc 2 nhóm. Cấp 1 có pool 3, cap 3 hoạt động; cấp cao mở thêm lựa chọn nhưng không tăng phần thưởng cá nhân không giới hạn.

| Mã quest | Mục tiêu | Contribution | Thưởng cá nhân / bang |
|---|---|---|---|
| GQ-01 Đoàn xe Mưa | bảo vệ 3 xe qua 2 checkpoint, 5 người | damage/repair/escort đều tính điểm | 250 XP nhân vật, Đồng, 1–3 vật liệu bang |
| GQ-02 Truy quét Rễ Mộng | hạ 20 quái trong 3 vùng, 5 người | tối đa 10 kill contribution mỗi người | XP, gỗ/dược, XP bang |
| GQ-03 Gác mạch nước | giữ 3 van mỗi van 30s, 2 nhóm | giữ van, hồi máu, xử lý wave | nguyên liệu, điểm công trình |
| GQ-04 Săn tinh anh tuần | hạ một elite có telegraph, 5 người | damage/heal/interrupt/avoid | token tuần, không có item độc quyền |
| GQ-05 Bàn giao vật tư | nộp nguyên liệu tự thu thập, 8 người | cap theo loại/ngày | Đồng, XP bang, cosmetic progress |
| GQ-06 Hướng dẫn tân binh | hoàn tất quest cấp thấp cùng 3 thành viên mới | cần group session ≥10 phút | điểm mentoring, không tăng power |

Contribution được tính theo hỗ trợ thật: damage hiệu lực, hồi phục, khiên, giải debuff, sửa vật thể, giữ objective. AFK nhận không quá 5% điểm nếu không nhập input/không ở vùng. Phần thưởng cá nhân có giới hạn tuần; người chơi có thể nhận “đã giúp” kể cả bang đã chạm cap nhưng không nhận thêm token.

### 7. Công thành bang 20v20

**Định dạng:** mỗi trận 20 người mỗi phe; người đăng ký tối đa 30 để tạo danh sách dự bị. Một bang có thể tham dự tối đa một siege/tuần; đội hình được khóa 30 phút trước trận. Matchmaking ưu tiên rating, sau đó số người/cấp bang; không ghép bằng tổng chiến lực hiển thị đơn thuần.

**Lịch:** vòng loại thứ Bảy 19:00 giờ server; chung kết Chủ Nhật 19:00. Mỗi trận 18 phút + tối đa 3 phút overtime. Lịch có thể điều chỉnh theo vùng nhưng cố định trong chu kỳ season 8 tuần.

**Sơ đồ mục tiêu trên biến thể MAP_TRAN_SON_SIEGE:**
- Phe A spawn x=18; Phe B x=342.
- Cổng Tây (A) x=94; cổng Đông (B) x=266.
- Trạm tiếp tế trung tâm x=180, vùng radius 8.
- Hai ụ nỏ x=132 và x=228.
- Cờ ấn trên tháp x=180, y=12; đường platform hai bên y=5 và y=9.
- Đường ngang dưới luôn mở; hai đường trên cần phá cổng/đi cầu, không được spawn camp.

**Pha trận**
1. 0:00–2:00: cổng khóa, chọn đường và thiết lập đội.
2. 2:00–7:00: phá cổng hoặc chiếm 2 ụ nỏ. Mỗi ụ giữ 45s cho một điểm chiến thuật.
3. 7:00–14:00: mở trạm tiếp tế; đứng trong vùng để cộng điểm theo số người tới ngưỡng 5; đông hơn không tăng tốc vô hạn.
4. 14:00–18:00: cờ ấn mở; giữ 90s tổng để thắng ngay hoặc tích 100 điểm cuối trận.
5. Overtime 3 phút nếu hòa; điểm tăng nhanh hơn, không hồi sinh sau 30s cuối.

**Điểm số:** phá cổng 10, ụ nỏ 15 mỗi ụ, supply 1 điểm/5s, cờ 1 điểm/3s; hạ người chơi không cho điểm trực tiếp để tránh farm. Thắng bằng cờ giữ đủ 90s hoặc điểm cao hơn ở phút 18. Nếu hòa sau overtime, tie-break theo thời gian giữ trạm/cờ, rồi shared draw.

**Combat rules:** sát thương PvP profile, potion có cooldown 12s, không dùng vật phẩm raid heal vượt limit; revive đồng đội 4s và có thể bị ngắt; spawn protection 4s chỉ khi rời spawn và mất khi tấn công. Không tàng hình/teleport vào vùng spawn địch. Telegraphed siege hazard có viền/pattern rõ. Disconnect có 90s để reconnect vào slot; AFK trên 2 phút bị đánh dấu, trên 3 phút tự kick, dự bị được gọi vào.

**Thưởng:** huy hiệu season, cờ, title/cosmetic, token đổi vật liệu phổ thông. Không có vũ khí độc quyền mạnh hơn; không có thuế bắt buộc từ người chơi không tham gia. Thua nhận participation reward nếu đạt 5 phút hoạt động. Phần thưởng bang có cap tuần, chia đều cho tối đa 20 roster active.

### 8. Nhóm, bạn bè và tìm đội

Party tối đa 5, raid 10 chia 2 đội. Leader có thể đặt loot mode cá nhân hoặc luân phiên; mọi người nhìn thấy mode trước khi vào dungeon. Loot boss raid ưu tiên token và reward cache cá nhân; roll vật phẩm chỉ cho cosmetic/đồ tradeable với xác nhận. XP chia theo contribution, hỗ trợ không bị thiệt. Mời có thể tắt theo người chơi, chặn spam 10 invites/10 phút.

Danh sách bạn hiển thị trạng thái online, khu vực nếu đã bật chia sẻ, lớp/cấp, hoạt động đang tìm. Người chơi có thể ẩn trạng thái, không tiết lộ vị trí. Tìm đội lọc level band, hoạt động, ngôn ngữ, role mong muốn; role là sở thích không bắt buộc. Queue không kick người chơi vì lớp.

### 9. Chat, an toàn và chống spam

Kênh: Khu vực, Nhóm, Bang, Thì thầm, Hệ thống. Chat thế giới toàn server mở theo level hoặc quest, có giới hạn 1 tin/8s; người chơi mới có quota thấp hơn để chống bot. Bang/guild 1 tin/1.5s. Có mute cá nhân, block, report spam/lừa đảo/quấy rối, filter lời nói; dữ liệu báo cáo lưu theo policy máy chủ. Người gửi không biết ai report. Tin hệ thống và cảnh báo giao dịch không thể bị lọc mất.

### 10. Trường hợp quản trị và khai thác lỗi

- Bang chủ bị khóa tài khoản: chỉ moderator chuyển quyền sau quy trình xác minh; không tự trao cho người có hoạt động cao.
- Giao dịch kho thất bại/mất mạng: requestId và ledger bảo đảm không nhân đôi item/currency.
- Bang rời trước khi reward settle: vẫn nhận phần thưởng đã earned nếu đã vượt contribution threshold; không nhận reward bang nếu rời trước snapshot trừ trường hợp reconnect.
- Siege match disconnect/abuse: server lưu log combat, AFK, reconnect, không phạt người bị crash; moderator có thể void trận khi server outage.
- Không cho thành viên tự mời alt liên tục để tăng XP; new member contribution chỉ ghi khi tài khoản qua tuổi tối thiểu/đạt cấp xác minh.
- Mọi kick, promote, đổi quyền, chi quỹ, giải tán ghi log và có reason field.
- Nút report không mở cửa sổ chat mở; report xử lý im lặng.

### 11. Checklist bàn giao

- Quyền được enforce trên server; UI ẩn nút không thay thế permission check.
- Cap thành viên, contribution, kho, treasury, lịch siege đặt trong config và version hóa.
- Thử trường hợp rớt mạng trong deposit/withdraw, hai request đồng thời, Bang chủ offline, roster full, member rời trong siege.
- Match 20v20 đạt mục tiêu 60 FPS client mid-range và giữ telegraph rõ khi 40 người dùng VFX.
- Có log kiểm toán, công cụ moderator và chính sách lưu dữ liệu chat/báo cáo được xác định trước khi phát hành.
