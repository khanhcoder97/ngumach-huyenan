# ĐẶC TẢ SẢN XUẤT MAP THĂNG LONG THÀNH
## Ngũ Mạch: Huyền Ấn — trung tâm đô hội và cửa ngõ liên vùng v1.0

> DEC-020 (2026-10-29): quy hoạch mục tiêu thành phố2048×1536WU/12phường theo Capital_Scale_and_Simple_Pixel_v2_vi.md. Các bảng900×96/3cell/x-only bên dưới là layout v1 đang chờ migration, không còn là mục tiêu quy mô toàn thành. Registry/runtime giữv1 cho đến khi bundle geometry/placement/quest/route đồng bộ; không chuyển tọa độ bằng ảnh concept.


> DEC-016 (2026-10-28): áp dụng `Top_Down_Gameplay_World_Spec_vi.md`. Các bảng kích thước/placement cũ là blockout chưa nghiệm thu top-down. Y luôn là Bắc–Nam trên mặt đất. “Platform” là bệ/cầu/vùng an toàn có đường đi hoặc floor link, không yêu cầu nhảy; chiều cao silhouette/capsule cũ không dùng làm collider. ID được giữ; không tự chuyển tọa độ cũ thành độ cao.


### 1. Vai trò trong game

**Thăng Long Thành** (`MAP_THANG_LONG`) là thủ phủ, chợ lớn và điểm tập trung xã hội của Ngũ Mạch. Đây là map an toàn, lớn nhất game; người chơi gặp nhau, mua/bán, gửi đồ, nhận truy nã, rèn/nâng cấp, quản lý bang, tìm nhóm hoạt động và tham gia Giải Đấu Trường Long Môn hàng tuần. Thành cũng là điểm điều phối dịch chuyển đến các vùng đã mở.

Map mở bằng cốt truyện sau C1-05. Người chơi vào lần đầu để hoàn thành C1-06; sau đó cổng tuyến và bảng dịch chuyển hiển thị mọi vùng đã được mở bằng quest. Thành không mở tắt chương, không cho đi vào khu vực vượt tiến trình. Thanh Lạc vẫn là thành nhập môn/học viện; Thăng Long Thành là trung tâm toàn game và có đủ dịch vụ endgame.

Ngôn ngữ hình ảnh là pixel art fantasy Việt cổ nguyên bản: tường đất nung, gạch xám, mái ngói cong, gỗ sơn son, bến sông, phường nghề, cờ Ngũ Mạch và đèn lồng được dựng bằng tile/module pixel theo `Pixel_Art_Production_Standard_vi.md`. Không tái dựng nguyên trạng một di tích có thật, không dùng asset lịch sử hoặc KPAH. Placement vẫn theo WU; tile nền theo lưới 16×16 source px.

### 2. Kích thước, camera và chia vùng tải

- Kích thước graybox: **900×96 WU** (450×48m), rộng gấp 2,5 lần vùng 360 WU thường và là map lớn nhất.
- Hệ trục dùng chuẩn Atlas: `Y=0` là đường tham chiếu trên mặt đất, player/NPC đặt theo pivot chân; camera 32 WU ngang, 18 WU cao ở 16:9.
- Chia streaming thành 3 cell liền mạch: `THANG_LONG_CELL_WEST x=0..299`, `THANG_LONG_CELL_CENTER x=300..599`, `THANG_LONG_CELL_EAST x=600..899`. Tải trước cell kế tiếp khi người chơi cách biên 40 WU; seamless, không có màn chờ hoặc chặn camera.
- Mọi tương tác dùng khoảng cách tối đa 5 WU; lối chính rộng tối thiểu 10 WU, tuyến xe hàng rộng 14 WU. Cầu chồng đường dùng floorId; mái nhà có chế độ che khuất để luôn thấy actor và telegraph.
- Entry lần đầu tại `(24,0)`; điểm hồi sinh an toàn `(520,0)` ở quảng trường trung tâm. Không spawn quái ngoài instance.
- Để giữ độ rộng mà không buộc người chơi chạy qua 28 màn camera mỗi lần đổi dịch vụ, bản đồ có xe điện/cổng dẫn lộ an toàn miễn phí tại `CITYROUTE_THANG_LONG_WEST=(24,0)`, `CITYROUTE_THANG_LONG_MARKET=(237,0)`, `CITYROUTE_THANG_LONG_EXCHANGE=(316,0)`, `CITYROUTE_THANG_LONG_FORGE=(409,0)`, `CITYROUTE_THANG_LONG_PLAZA=(520,0)`, `CITYROUTE_THANG_LONG_GUILD=(636,0)`, `CITYROUTE_THANG_LONG_ARCHIVE=(758,0)`, `CITYROUTE_THANG_LONG_EAST=(876,0)`. Mini-map chọn một điểm đã khám phá, fade 0,4s; không hoạt động trong PvP/instance/escort. Đây là route nội thành, không mở map ngoài hay bỏ quest.

### 3. Bố cục tổng thể và blockout theo tọa độ

Đường chính chạy Tây → Đông dọc trục `Y=0`. Mỗi phố có biển tên, màu mái và cổng nhìn thấy từ xa; đường phụ là hốc tương tác ngắn, không tạo ngõ cụt che NPC. Khu phố không dùng cùng một texture lặp liên tục.

| Khu | Tọa độ X | Graybox/đạo cụ cố định | Chức năng và landmark |
|---|---:|---|---|
| Cửa Tây và cầu thành | 0–99 | Tường gạch cao 18 WU; cổng 20×18 tâm x=22; 2 lầu canh (x=8/42); cầu qua hào rộng 14; 6 cờ; 8 đèn lồng | Cửa vào từ Thanh Lạc/Bến Mưa; landmark mái cổng hình song long cách điệu |
| Bến Sông Ngự | 100–199 | Sông trang trí 54×10 tâm x=147, Y=-4; 2 cầu đá x=118–132 và 166–180; 3 thuyền hàng; 8 kho nhỏ; 10 thùng hàng | Tuyến vận chuyển và chợ vật phẩm thường; nước không có hazard |
| Đại Chợ Ngũ Mạch | 200–299 | 16 quầy modular (mỗi 8×5), 4 mái vải lớn, 2 biển giá, 12 đèn treo, 6 xe hàng | Người chơi tập trung; quầy bán trang bị/phụ liệu theo band; không bán đồ cuối game có stat độc quyền |
| Phường Giao Dịch | 300–399 | Nhà ký gửi 30×18 tâm x=319; kho tài khoản 26×16 x=352; 8 bảng rao; sân cân hàng 20×12; 2 bốt thu ngân | Chợ người chơi, mua/bán trực tiếp qua sàn, ngân khố và thư |
| Phố Bách Công | 400–499 | Lò rèn 28×20 tâm x=410, 3 ống khói, 2 máng nước, 6 đe; sạp nhuộm 12×8 x=455; 8 cửa hàng nghề | Rèn, nâng cấp, khảm, tinh luyện, sửa chữa, phân giải; chỉnh diện mạo và nhuộm |
| Quảng trường Ngũ Mạch | 500–599 | Sân đá 52×34 tâm x=527; cột mốc Ngũ Mạch cao 16 x=522; đài phun tròn Ø10 x=500; bảng hoạt động 12×8 x=548; tiền sảnh đấu trường 42×26 x=577 | Landmark trung tâm, điểm hồi sinh, bảng xếp hạng, ghép nhóm hoạt động và lối vào PvP |
| Phường Bang Hội | 600–699 | Hội quán 36×24 x=624; 5 cột cờ bang; sảnh thú 24×14 x=658; 2 sân lễ; 12 đèn cờ | Quản lý guild, nhiệm vụ/đóng góp, kho bang, điểm thú và chợ vanity bang |
| Phường Công Văn | 700–799 | Lưu trữ thư tịch 42×26 x=746; 3 mái hiên; kho lệnh 18×12 x=712; bảng truy nã 10×6 x=730; sân chứng cứ 18×12 x=770 | Cốt truyện C1-06, nhiệm vụ ngày/tuần, truy nã và tra cứu Bách khoa |
| Cửa Đông và Trạm Dịch Chuyển | 800–899 | Tường cao 18, cổng 20×18 x=874; 2 tháp dẫn lộ x=833/891; 5 bệ cổng biểu trưng ngũ hành; 1 sân đón xe 20×14 | Cổng ra/vào phía Đông và route selector tới mọi vùng đã mở |

**Nền dọc camera:** skyline xa gồm tường thành và mái chùa/hội quán theo lớp parallax; sông và cờ ở midground; NPC/quầy/cột ở gameplay plane; dây đèn, mái hiên thấp ở foreground nhưng không che thanh nhân vật hoặc telegraph. Dây đèn không rung gây nhiễu. Cả map dùng đèn ngày ấm; chiều tối chỉ đổi nhiệt độ màu và bật đèn, không giảm tương phản chữ/telegraph.

### 4. NPC và điểm dịch vụ

NPC dịch vụ là actor đứng cố định, có icon riêng theo chức năng. Bảng/terminal có thể mở panel nhưng phải có đối tượng world để tương tác. Tất cả báo giá, quyền, tồn kho, giới hạn mua và giao dịch do server trả; việc có NPC không có nghĩa item bán vô hạn.

| NPC / anchor | Tọa độ | Dịch vụ và luật |
|---|---:|---|
| `NPC_TL_GATEKEEPER_W` | (24,0) | Chọn tuyến về Thanh Lạc/Bến Mưa; xác nhận điều kiện quest; không cho bỏ qua mốc truyện |
| `NPC_TRADER` | (237,0) | Đồ thiết yếu và bán món thường; hàng khác với quầy tân thủ Thanh Lạc theo band/offerSet |
| `NPC_TL_APOTHECARY` | (181,0) | Potion, cleanse và thức ăn có trong catalog; không bán potion PvP/stat vượt chuẩn |
| `NPC_TL_AUCTION_CLERK` | (316,0) | Đăng/mua/thu hồi sàn người chơi; cùng phí và cap trong Economy spec; xác nhận giá/tổng phí |
| `NPC_TL_BANKER` | (322,0) | Kho cá nhân/account 120 ô mặc định, mở rộng tối đa 200 bằng Đồng/quest; thư có TTL 30 ngày như Economy spec; không nhận vật phẩm quest sai binding |
| `NPC_RELIC_MERCHANT` | (366,0) | Đổi token dungeon/raid/danh vọng lấy stock chọn lọc; có lịch refresh, không bán random gear và không trao đổi tiền thật |
| `NPC_BLACKSMITH` | (409,0) | Lò rèn duy nhất đủ chức năng: chế tạo, cường hóa +0…+15, socket, tinh luyện, sửa, phân giải; dùng quote/transaction của Forge spec |
| `NPC_VAN_NHU` | (455,0) | Ngoại hình gốc, ngoại trang, preview, nhuộm; lần chỉnh đầu miễn phí, quote Đồng trước save; vanity không cộng stat |
| `NPC_ACTIVITY_STEWARD` | (548,0) | Bảng hoạt động, lịch server, dungeon/raid, Mạch Triều và đăng ký trận; hiển thị yêu cầu/đếm ngược |
| `NPC_RAID_KEEPER` | (566,0) | Tổ đội, đăng ký dungeon/raid và Thí Luyện Hồi Ức; vé boss vẫn cá nhân, quota theo server |
| `NPC_ARENA_STEWARD` | (587,0) | Xác nhận roster 3v3, luật giải tuần, bracket, lịch trận, sẵn sàng và báo vắng |
| `NPC_ARENA_REWARD_CLERK` | (599,0) | Bảng xếp hạng tuần/mùa, lịch sử vinh danh và đổi Ấn Long Môn lấy vanity |
| `NPC_GUILD_CLERK` | (636,0) | Tạo/quản lý bang, kho bang, nhiệm vụ và cờ; quyền/nhật ký theo Guild spec |
| `NPC_TL_BEAST_TENDER` | (673,0) | Thú đồng hành, pet feed, gọi/thu, cosmetic thú; không bán chỉ số pet |
| `NPC_HA_MAC` | (723,0) | Bảng Truy Nã, daily/weekly và nhận tối đa 3 `TICKET-BOSS-01`/tài khoản/tuần; cùng tiến độ với Hạ Mặc ở Thanh Lạc |
| `NPC_COURT_ARCHIVIST` | (758,0) | C1-06, hồ sơ vùng, log sự kiện và Bách khoa; quest state không reset khi đổi map |
| `NPC_TL_GATEKEEPER_E` | (876,0) | Bảng dịch chuyển liên vùng; chỉ liệt kê map đã mở và vùng phù hợp cấp/quest |

`NPC_HA_MAC`, `NPC_GUILD_CLERK`, `NPC_BLACKSMITH`, `NPC_RELIC_MERCHANT`, `NPC_VAN_NHU`, `NPC_RAID_KEEPER` dùng cùng canonical NPC ID với các map hiện hữu nhưng mỗi điểm có `locationId`. Inventory, quest, bank và quyền guild theo account/character, không khởi tạo bản sao trạng thái.

**Bảng không phải NPC:** bảng nhiệm vụ phụ x=744, bảng tuyển nhóm x=560, bảng thông báo công thành x=651 và bảng tin chợ x=298. Chạm bảng mở đúng hệ thống; không nhận/gửi giao dịch chỉ từ tooltip.

### 5. Mua bán, chợ và panel khu phố

- Chợ NPC cho mua và bán món hợp lệ trong một panel: giá mua, giá bán lại, stock, giới hạn ngày, binding và thuế hiện trước xác nhận. Không có nút bán đồ đang mặc, đồ quest hoặc đồ khóa.
- Sàn đấu giá là chợ người chơi hiện có, không tạo thêm một loại tiền hay cơ chế giao dịch riêng. Phí niêm yết 2%, phí giao dịch 5%, 10 listing/nhân vật và 30/tài khoản như Economy spec. Giá và settlement là Đồng; chống giao dịch đôi bằng ledger/requestId.
- Kho cá nhân/account 120 ô; mở rộng theo tiến trình/Đồng tới 200 ô. Không dùng kho để chuyển item QUEST, item soulbound hoặc vượt giới hạn trade.
- Quầy vật liệu/đổi token ở x=366 lấy stock curated từ danh vọng, dungeon/raid token và hoạt động vùng. Vật phẩm có cap hiển thị cap còn lại; không có cửa hàng bán trực tiếp Cổ Vật hoặc món BiS.
- Phố nghề mở một shortcut duy nhất tới modal Forge/Crafting. Kết quả craft/upgrade trả về túi; actor không tự tiêu item bằng double-click hay tương tác mơ hồ.
- Vân Như mở phòng thay đồ; người chơi có thể thử skin chưa sở hữu, nhưng transaction mua/mặc/lưu màu là riêng. Quầy không bán lootbox.

### 6. Giải Đấu Trường Long Môn hàng tuần

Đấu trường ở khu Quảng trường, cổng vào nằm tại `(577,0)`. Sảnh công cộng hiển thị 16 bảng gỗ/e-paper theo nhóm, cúp mùa ở `(591,0)`, ba hàng khán đài nền. Trận PvP chạy trong arena instance tách biệt; người chơi đứng ở map thành không bị đánh, không có world PvP.

**Activity record:** `activityId=ACT_LONG_MON_WEEKLY`; `recordType=RankedPvPEvent`; `venueMapId=MAP_THANG_LONG`; `entryNpcId=NPC_ARENA_STEWARD`; `rewardNpcId=NPC_ARENA_REWARD_CLERK`; format `3v3`; season length 8 tuần; schedule source là server event calendar. Mỗi bản ghi kết quả khóa theo `seasonId + weekId + matchId + rosterSnapshot`; cùng dữ liệu dùng cho bảng tuần, bảng mùa và Bách khoa.

#### 6.1 Đăng ký và vòng đấu

| Mốc giờ server | Nội dung |
|---|---|
| Thứ Hai 05:00–Thứ Tư 04:00 | Mở đăng ký 3 người chính + 1 dự bị; captain tạo roster, từng thành viên xác nhận; tối đa 64 đội/region, dư vào waitlist |
| Thứ Tư 04:00 | Khóa roster và seed theo MMR đội; captain chỉ được đổi người chính với dự bị đã khóa đến 60 phút trước trận đầu của đội; account chỉ thuộc một đội trong tuần |
| Thứ Năm–Thứ Sáu | Từ 8 đội: vòng bảng, tối đa 16 bảng × 4 đội, round-robin; số trận theo cỡ bảng; khung ghép 18:00 và 21:00, được đăng ký một khung trước mỗi trận. Từ 4–7 đội: ladder Swiss 3 vòng, lấy tối đa 4 đội vào final. Dưới 4 đội: không trao podium tuần, người chơi tiếp tục queue ranked 3v3 thường để ghi rating mùa |
| Thứ Bảy 18:00–21:00 | Knock-out tùy cỡ bracket (vòng 16, tứ kết hoặc trận phân hạng); trận chạy song song theo arena instance; live bracket hiển thị tại NPC_ARENA_STEWARD |
| Chủ Nhật 18:00–21:00 | Bán kết (18:00), tranh hạng ba (19:00), chung kết (20:00); tất cả khung giờ dùng giờ server |

Một trận 3v3 là best-of-3 round, mỗi round 3 phút; nghỉ 45 giây. Thắng 2 round thắng match; hòa sau 3 round ghi hòa. Vòng bảng: thắng 3 điểm, hòa 1, thua 0; tiebreaker lần lượt là hiệu số round, đối đầu, MMR seed. Knockout là single-elimination; chung kết và tranh hạng ba best-of-5. Có 5 phút check-in; vắng mặt forfeits. Disconnect có 90 giây reconnect một lần, không tự xử thua nếu server mất kết nối vùng.

Từ 8 đội trở lên, bracket xếp đội theo điểm và tiebreaker; vào knock-out số đội là lũy thừa 2 lớn nhất không vượt quá số đội hợp lệ, tối đa 16 (ví dụ 8–15 đội đưa 8 đội vào, 16–64 đưa 16 đội vào). Seed cao gặp seed thấp. Với 4–7 đội, ladder Swiss 3 vòng đưa tối đa 4 đội vào final; với 1–3 đội, tuần đó không có podium/giải chính thức và người chơi ghép queue ranked 3v3 thường. Bảng nhóm có bye dùng win-rate, đối đầu và MMR seed để phân xử; UI công bố thể thức trước khi xác nhận đăng ký.

Điều kiện: level 20+, hoàn tất C1-06, 3 thành viên cùng region, không bị cấm PvP; đăng ký roster 3 chính + 1 dự bị. Sau khi khóa roster, không thêm/thay người ngoài dự bị; sau trận đầu không thay roster. Mỗi account tham gia một roster/tuần. Thể thức 4–7 đội và điều kiện không tổ chức podium khi dưới 4 đội phải hiện trước khi xác nhận đăng ký.

#### 6.2 Công bằng và xếp hạng

- PvP dùng profile chuẩn hóa theo cấp/gear; gear score, nâng cấp, set, pet stats và consumable không tạo lợi thế. Class-specific PvP coefficients lấy từ Combat spec; composition không khóa healer/tank.
- Chỉ loadout skill PvP hợp lệ; khóa potion, buff PvE, thú gây sát thương và item có thể dùng giữa round. Cosmetic được phép nhưng không che telegraph/team marker.
- Leaderboard tuần có đội, roster, thắng/thua/hòa, điểm bảng và seed; leaderboard mùa 8 tuần có rating cá nhân + đội. Lưu season/match ID, chỉ số công bằng và lý do xử lý disconnect/forfeit.
- Kết quả do server xác nhận. Không cho đổi thành viên/nhân vật sau khi trận bắt đầu để farm rating; không có reward nếu AFK hoặc bị xử phạt gian lận.
- Bảng xem trận chỉ phát spectator state trễ 30 giây; người đang đấu không thấy thông tin đối thủ qua khán giả. Spectator tối đa 20/tổ hợp match, tắt emote spam và tên ngoài roster nếu privacy setting.

#### 6.3 Phần thưởng

| Kết quả | Phần thưởng tuần | Phần thưởng mùa 8 tuần |
|---|---|---|
| Hoàn tất 1 trận hợp lệ | 5 Ấn Long Môn/trận; thưởng tham gia tối đa 30/account/tuần | tích điểm mùa |
| Hạng 9–16 | thưởng vị trí cao nhất: +5 Ấn Long Môn/người | điểm mùa theo kết quả |
| Hạng 4–8 | thưởng vị trí cao nhất: +10 Ấn Long Môn/người; huy hiệu hồ sơ tuần Top 8 | huy hiệu hồ sơ Top 8 mùa |
| Hạng 3 tuần | thưởng vị trí cao nhất: +20 Ấn Long Môn/người | nếu hạng 3 chung cuộc mùa: `COS-TITLE-06 — Tam Quân Long Môn` |
| Á quân tuần | thưởng vị trí cao nhất: +25 Ấn Long Môn/người | nếu á quân chung cuộc mùa: `COS-TITLE-05 — Á Quân Long Môn` |
| Vô địch tuần | thưởng vị trí cao nhất: +30 Ấn Long Môn/người, cúp trưng bày tại sảnh | nếu vô địch chung cuộc mùa: `COS-TITLE-04 — Quán Quân Long Môn` |

Ấn Long Môn là số dư ledger account-bound chỉ đổi ngoại trang, động tác và vật liệu trang trí ở `NPC_ARENA_REWARD_CLERK`; không đổi Đồng, gear, exp, buff hoặc stat. Thưởng tham gia tối đa 30/account/tuần; chỉ nhận một khoản thưởng vị trí cao nhất, tối đa thêm 30; tổng trần là 60/account/tuần. Thưởng tuần gửi thư sau khi bảng khóa. Danh hiệu mùa trao cho ba đội đứng đầu leaderboard mùa sau tuần thứ tám, gắn với roster snapshot hợp lệ ở tuần cuối và ghi vào Hall of Fame. Người chơi nhận Ấn khi hoàn tất trận nhưng không qua vòng bảng vẫn có đường mở vanity; top rank không phải cách duy nhất để nhận reward.

### 7. Cốt truyện: C1-06 — Con dấu qua phố

- **Mở khi:** hoàn thành C1-05; nhận lệnh từ Hạ Mặc ở MAP_THANH_LAC. Lần đầu mở `MAP_THANG_LONG` và waypoint thành.
- **Step 1 — Đưa sổ vào thành:** vào cổng Tây `(24,0)`, nói Hạ Mặc `(723,0)`; hiện quest marker và hướng dẫn bản đồ chợ.
- **Step 2 — Hóa đơn ở Đại Chợ:** xem `OBJ_THANG_LONG_CARGO_LEDGER=(246,0)` cạnh quầy ký gửi; đối chiếu tuyến xe đã chở bản đồng dấu.
- **Step 3 — Dấu lò:** tương tác `OBJ_THANG_LONG_FORGE_STAMP=(411,0)`; lò dùng hợp kim có bụi khoáng cùng loại với resin Mộc.
- **Step 4 — Sổ lưu trữ:** lấy `OBJ_THANG_LONG_ARCHIVE_PAGE=(748,0)`; so số hiệu lệnh với sổ triều đình. Không đánh nhau trong thành.
- **Step 5 — Báo cáo Hạ Mặc:** trả lời Hạ Mặc ở `(723,0)`, chọn “niêm chứng cứ” hoặc “sao lưu công khai”; cả hai giữ cốt truyện chung, chỉ đổi câu thoại/Trust.
- **Ý nghĩa:** dấu giả được vận chuyển qua tuyến thương mại, không do một cửa hàng hay môn phái đơn lẻ tạo ra. Bụi resin và sợi rễ trên sổ chỉ về Lâm Triều, mở C2-01.
- **Thưởng:** EXP theo level, 300 Đồng, 1 Huy hiệu Danh Vọng Thanh Lạc; mở dịch chuyển trung tâm tới các map đã mở, mở C2-01/route Lâm Triều. Không thưởng item tradeable có thể farm.
- **Fail/retry:** clue giữ sau chết/thoát; quest lặp lại chỉ xem lại thoại, không phát thưởng lần hai; item evidence là quest flag, không inventory drop.

### 8. Crowd, ambient và spawn

Không có quái, elite, boss hoặc tài nguyên tranh chấp trong thành. PvP/dungeon mở instance riêng. Ngoài instance, kỹ năng combat tắt; chỉ cho emote, ngồi, đi/chạy và thao tác NPC.

- Crowd ambience: 18 actor nền tĩnh theo 9 sector, tối đa 8 actor có animation trong camera và tối đa 4 actor tương tác; decor actor không đẩy collision và không nhận target.
- Người chơi: 80/người/instance thành; nếu vượt, tạo channel phụ và giữ party/guild cùng channel. Hiển thị chi tiết tối đa 30 player gần, còn lại dùng crowd marker/danh sách; setting Hide Others áp dụng.
- Mob spawn table: **0**. Quest C1-06 objects là interactables, không mob. Có 3 training dummy trong private practice scene, không ở city world.
- City map chat có filter trade/party/guild; anti-spam 3 msg/5s, nút report; broadcast server chỉ trong notice board/toast, không modal tự bật.

### 9. Art/VFX/audio và hiệu năng

- Mỗi sector có bộ module 2D riêng: tường/viên gạch, cửa hàng, mái ngói, mái vải, biển hiệu, đèn, xe hàng, cầu, cột cờ; 3 biến thể mỗi prop, random scale 0.92–1.08.
- Landmark skyline: cổng song long ở Tây, chợ mái vàng, trụ Ngũ Mạch ở quảng trường, mái hội quán Bang, lầu lưu trữ và cổng dịch chuyển Đông. Không đặt tên hoàng đế/triều đại lịch sử thật.
- Kênh thoại/ambience: tiếng rao nhỏ có vùng âm thanh cục bộ, chuông xe hàng, nước bến, trống thông báo 1 lần lúc mở giải. Mute crowd tắt lời rao nhưng giữ voice nhiệm vụ/cảnh báo.
- Weather: nắng, mưa nhẹ và đèn tối theo giờ; không có sét, hazard, camera shake hoặc mưa che UI. Không gắn gameplay bonus theo thời tiết.
- Target: ≤250 draw calls city ở PC, ≤180 mobile sau batching; ≤40 actor sprite visible, ≤12 near-field animated sprite sheets; streaming cell không làm spike frame >50ms trên cấu hình target. Tile LOD theo camera; 2D parallax rẻ; pixel tile/actor pages dùng atlas shared lossless.

### 10. Data/route contract và checklist bàn giao

Mỗi giao dịch gửi `{npcId, locationId, mapId, serviceId, characterId, accountId, contentVersion, requestId}`; server kiểm tra khoảng cách, giờ/điều kiện, quyền, giá/stock, binding và revision. Mọi portal gửi `destinationMapId + unlockFlags`; client không tự sinh lựa chọn map.

- [ ] Atlas dùng map ID `MAP_THANG_LONG`, 900×96 WU; anchor từng NPC/portal/object trùng tài liệu này.
- [ ] C1-05 → C1-06 → C2-01 không tạo nhánh campaign hoặc mất quest khi thoát/reconnect.
- [ ] Chợ NPC, auction, kho tài khoản, forge, guild, hoạt động, vanity và route selector mở đúng modal; fee/cap/data lấy server.
- [ ] Town combat tắt; instance arena tách hoàn toàn; NPC/terminal không spawn trùng ở cùng coordinate.
- [ ] Có walkthrough Tây→Đông ở 16:9, 20:9, mobile 1280×720; biển phố/quest/portal đọc được, không che sprite.
- [ ] Giải Long Môn kiểm tra bracket 64/32/16/8 đội, tie-break, waitlist, reconnect, forfeit, trao thưởng idempotent, reset tuần/mùa và quyền privacy.
- [ ] Theo dõi channel, player cap, streaming, draw call, chat/report và transaction ledger bằng telemetry.

### 11. Tài liệu tích hợp

- `Map_Production_Atlas_vi.md`: source map IDs, portals và tọa độ chung.
- `Quest_and_Narrative_Production_Spec_vi.md`: C1-06, thoại, checkpoint và quest flags.
- `Activities_Economy_PvP_Production_Spec_vi.md`: chợ, hoạt động, tournament và thưởng.
- `Guild_Social_Spec_vi.md`, `Forge_Crafting_Overlay_Spec_vi.md`, `Appearance_Buff_NPC_Service_Overlay_Spec_vi.md`: panel service tương ứng.
- `Art_Entity_Weather_UI_Visual_Bible_vi.md`: kiến trúc thành, NPC và ambient production.

