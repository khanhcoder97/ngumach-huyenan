# ART BIBLE: TẠO HÌNH NPC, QUÁI, THỜI TIẾT VÀ SKIN UI
## Ngũ Mạch: Huyền Ấn — pixel art production v2.0

> DEC-016 (2026-10-28): áp dụng `Top_Down_Gameplay_World_Spec_vi.md`. Các bảng kích thước/placement cũ là blockout chưa nghiệm thu top-down. Y luôn là Bắc–Nam trên mặt đất. “Platform” là bệ/cầu/vùng an toàn có đường đi hoặc floor link, không yêu cầu nhảy; chiều cao silhouette/capsule cũ không dùng làm collider. ID được giữ; không tự chuyển tọa độ cũ thành độ cao.


### 1. Quy chuẩn hình ảnh tổng thể

**Ngôn ngữ tạo hình:** fantasy võ hiệp huyền thuật pixel art, lấy chất liệu từ thủ công vùng sông–rừng–sa mạc–thành đá nhưng dùng kiến trúc, phù văn, nhân vật và trang phục nguyên bản của Lạc Châu. Vẽ theo cụm pixel sạch, silhouette rõ, palette có giới hạn, shading theo dải màu/dither; không dùng anti-aliasing, blur hay gradient mượt. Tuyệt đối không dùng sprite/UI/âm thanh/hình cắt hoặc dấu hiệu nhận diện từ KPAH/JAR tham chiếu. Chuẩn kỹ thuật chi tiết theo [`Pixel_Art_Production_Standard_vi.md`](Pixel_Art_Production_Standard_vi.md).

**Tỉ lệ chuẩn:** giữ map 1 WU=0,5m, hero cell 48×64 px, footprint capsule ngang 1,2×0,6 WU, camera 18 WU ở 16:9. Sprite 20 PPU trên logical canvas 640×360 nên hero nằm trong cell cao 64 source px; output 1080p phóng nguyên 3× thành tối đa 192 screen px. Boss cao 1,6–3 lần theo spec. Gameplay sprite frame-based; pivot chân và anchor vũ khí/tay/đầu/hông/tâm thân khai báo theo pixel. Animation không điều khiển vị trí server.

**Lưới asset:**
- Actor thường dùng sprite sheet 512²–1024² chia page theo state; boss 1024²–2048²/page theo phase/layer. Không ép mọi frame thành cùng ô nếu trim metadata/pivot vẫn chính xác.
- Quái thường 512²; elite 512²–1024²; boss/environment 1024²–2048²/page. Lossless, no mipmap, point filter, không nén mất dữ liệu; giữ PPU 20.
- Icon item 32²–64²; skill/UI 32²–48²; portrait 64²–96² source pixel. Chỉ tăng khi detail gameplay cần và phải chỉ rõ scale nguyên tại 640×360.
- Gameplay top-down XY dùng8hướng N/NE/E/SE/S/SW/W/NW theo DEC-015/016; sheet actor48×64native, pivot chân. Menu/model sheet front/back/side chỉ là tham chiếu tạo hình, không thay8hướng runtime.
- Outline actor 1–2 source px; team/target outline là pixel overlay có shape rõ, không shader làm mềm.
- Tạo test sáng/tối và color-blind/pattern cho item/quái; màu luôn đi cùng shape/icon.
- VFX pixel sprite trên lớp actor; weather/parallax có pattern riêng; telegraph boss luôn nằm trên actor/weather và dùng silhouette/shape tương phản.

### 2. Bảng màu và vật liệu

| Token | Mã | Dùng |
|---|---|---|
| Ink-900 | #16222B | chữ/viền panel, bóng |
| Ink-700 | #2D3D46 | nền HUD tối |
| Paper-100 | #F1E8D5 | giấy, panel sáng |
| Paper-200 | #D8C9AC | border giấy, tooltip |
| Rain-Blue | #71B7C9 | Thủy, hồi phục, minimap |
| Kim-Gold | #D9B75D | Kim, trang bị, interact complete |
| Moc-Green | #7EB57A | Mộc, heal safe, gathering |
| Hoa-Ember | #E67749 | Hỏa, danger secondary, forge |
| Tho-Stone | #AE9A79 | Thổ, defense, terrain |
| Enemy-Alert | #EF604B | telegraph nguy hiểm, không dùng một mình |
| Ally-Help | #73D8BD | buff đồng minh, safe interaction |
| Disabled | #7D8587 | nút/mục tiêu không khả dụng |

Mỗi nguyên tố có hình thức phụ: Kim = lục giác/đường thẳng, Mộc = nhánh/rễ, Thủy = vòng gợn, Hỏa = tam giác/tia, Thổ = khối vuông/nứt. Mù màu vẫn đọc được qua pattern và icon. Vật liệu nhận diện bằng cụm pixel: kim loại có vệt sáng cạnh cứng 1–2 px, vải có mảng chuyển sắc theo bậc, gỗ có vân ngang ngắt quãng, đá có điểm hạt tương phản thấp, nước có dải phản sáng rộng theo từng mảng màu; không dùng specular shader hoặc gradient liên tục.

#### Bộ tạo hình môi trường Thăng Long Thành

Thăng Long Thành dùng gạch đất nung xám ấm, đá lát không đều, gỗ sơn son, mái ngói cong màu chàm/đất, mái vải ngũ sắc giảm bão hòa, đèn lồng giấy và đồng chạm. Hệ kiến trúc là thiết kế fantasy Việt cổ nguyên bản; không lấy trực tiếp mẫu cung điện/di tích lịch sử có thật. Landmark theo trục 900 WU: cổng song long phía Tây, thuyền/bến Ngự, mái Đại Chợ, biển cân hàng, trụ Ngũ Mạch, hội quán bang, lầu lưu trữ và tháp cổng dịch chuyển phía Đông.

Asset kit gồm: 4 module tường (thẳng/góc/cổng/tháp), 6 module mái, 8 mặt tiền nhà, 6 quầy vải, 4 biển hiệu, 3 xe hàng, 3 thuyền, 5 kiểu cờ, 4 đèn lồng, 3 cầu, 2 mái hiên foreground. Mỗi họ có tối thiểu 3 biến thể; bảng màu từng phường khác nhau nhưng gameplay silhouette/player outline không bị chìm. Nước trang trí ở bến không có collision/hazard; mái hiên/dây đèn không che nhân vật, NPC marker, quest marker hoặc telegraph.

### 3. Thiết kế NPC có tên

| ID / nhân vật | Silhouette, tuổi hình ảnh, trang phục | Màu/đạo cụ/portrait | Idle, diễn xuất, giọng |
|---|---|---|---|
| NPC_LYAN — Ly An | 4,3 WU; thiếu nữ 17–19; dáng nhỏ nhanh, áo khoác mưa vạt ngắn, túi chéo lớn | xanh mưa + vàng đất; thư sáp ở tay; tóc buộc lệch | vuốt mép thư khi lo, nhìn thẳng khi quyết; giọng sáng, nói ngắn |
| NPC_TA_VAN_KHANH — Tạ Vân Khanh | 5,2 WU; người trưởng thành 40–50; dáng thẳng nhưng vai trái cứng | áo hộ ấn xanh đen, một tay quấn băng; kiếm gãy đeo sau lưng | kiểm tra dây băng, hạn chế quay trái; giọng thấp, giữ khoảng lặng |
| NPC_HA_MAC — Hạ Mặc | 4,8 WU; học giả 30–40; dáng gầy, nhiều túi giấy/cuộn bản đồ | áo xám giấy + lam mực, kính lúp gập và thẻ ghi chép | ghi nhanh, cắn đầu bút khi suy nghĩ; giọng rõ, tò mò nhưng không lên lớp |
| NPC_CO_VO_TUONG — Cơ Vô Tướng | 5,5 WU; người già 55–65; dáng gầy cao, lưng bị khung máy nâng | áo choàng mực đen, lõi đồng ở ngực, nửa mặt nạ sứ nứt | nhịp thở máy 2 nhịp/1 chu kỳ, bàn tay rung khi ký ức xuất hiện; giọng kép rất nhẹ |
| NPC_SAM_CHU_QUY — Sầm Chủ Quỹ | 4,4 WU; trung niên chắc người, thân thiện | áo thương nhân đỏ nâu, cân gỗ, ống nước treo hông | cân đồng xu, chùi bàn tay; nói nhanh, có tiếng cười mũi |
| NPC_VAN_NHU — Vân Như, nghệ nhân nhuộm | 4,6 WU; người trưởng thành 28–35; tay khéo, dáng thẳng | áo thợ nhuộm xanh mực, tạp dề vải sáng có vệt màu, khuyên đồng hình giọt; cầm bảng mẫu vải | kéo dải lụa qua tay, pha màu bằng chén nhỏ; giọng bình tĩnh, giải thích ngắn; không làm cử chỉ như pháp sư |
| NPC_FOREMAN_MOC — Quản đốn Mộc | 5 WU; phụ nữ/nam trung niên khỏe, bắp tay rõ | áo da xanh rêu, găng chặt cây, rìu cất sau vai | thử lưỡi rìu, nheo mắt nhìn tán cây; giọng vang, không khoa trương |
| NPC_WATER_KEEPER — Người Giữ Nước | 4,9 WU; lớn tuổi, dáng gầy vững | áo xanh lam nhạt nhiều dây van, trượng đo mực nước | quan sát giọt nước, chậm quay đầu; giọng đều, có hơi khàn |
| NPC_MEDIC_SA_HOA — Y sư Sa Hỏa | 4,8 WU; phụ nữ 35–45; chắc tay, mắt quan sát | khăn lọc bụi, áo cát sáng có túi cứu thương đỏ | chỉnh mặt nạ, kiểm tra túi thuốc; giọng nhanh, bình tĩnh |
| NPC_FORGE_MASTER — Chủ Lò | 5,1 WU; dáng vuông, tay lớn | tạp dề đen, kính che mắt, kẹp kim loại màu đồng | gõ kẹp ba nhịp; mỗi lần nói chỉ ngẩng mắt sau câu đầu |
| NPC_REFUGEE_LEADER — Trưởng đoàn tị nạn | 4,7 WU; dáng mảnh nhưng đứng chắn trước người khác | áo vải chắp nhiều lớp, khăn che bụi, bản đồ gấp | đếm người bằng ngón tay; giọng chắc, không van xin |
| NPC_GUARD_CAPTAIN — Đội trưởng cổng | 5,2 WU; dáng quân nhân đứng rộng chân | giáp xanh đá, bảng hiệu lệnh, giáo ngắn | chào nghi thức, gõ cán giáo; giọng kỷ luật |
| NPC_CAPTAIN_TRAN_SON — Đội trưởng Trấn Sơn | 5,3 WU; lực lưỡng, sẹo mảnh ở cằm | giáp lắp ghép xám xanh, cờ gấp sau lưng | nhìn theo đường thành, đặt tay lên bản đồ; giọng trầm |
| NPC_GUILD_SCOUT — Trinh sát bang | 4,8 WU; thanh mảnh, chân nhẹ | áo choàng xanh xám, ống nhòm và cờ tín hiệu | quan sát nóc thành, ra dấu tay; giọng nhỏ, chính xác |
| NPC_TONG_BANH — Tống Bành | 5,8 WU khi đội giáp; thân người 5 WU | giáp công thành nhiều mảng vuông, vai phải to, cờ lệnh rách | đứng yên như tượng; khi nói xoay toàn thân trước khi quay đầu; giọng đục |
| NPC_DIVER_LEAD — Đội trưởng thợ lặn | 5 WU; khỏe, vai/đùi phát triển | áo áp suất xanh ngọc, bình khí đôi, kính tròn | kiểm tra van sau vai; giọng vang nhưng bị lọc qua mặt nạ |
| NPC_CLASS_TRIAL — Quan sát viên nhập môn | 4,8 WU; người trung tính, dáng tĩnh | áo vải ngà, năm dải màu nhỏ trên tay áo, thẻ thử thách | ghi nhận kết quả, không biểu lộ thiên vị; thoại được điều kiện hóa theo lớp |
| NPC_TL_AUCTION_CLERK — Chấp sự ký gửi | 4,7 WU; trung niên, tay áo gọn, tư thế ghi chép | áo lam đậm, túi đựng thẻ giá, bảng giao dịch bằng gỗ; huy hiệu hình cân | chỉ tay vào giá/fee trước confirm; giọng rõ, không thúc mua |
| NPC_TL_BANKER — Thủ khố | 4,9 WU; dáng vững, chuyển động tiết kiệm | áo xanh mực viền đồng, chùm chìa khóa và sổ kho; không mặc giáp | kiểm sổ hai lần trước khi xác nhận; giọng điềm tĩnh |
| NPC_TL_APOTHECARY — Dược sư kinh thành | 4,6 WU; nhanh nhẹn, vai đeo túi thuốc | áo màu ngà/xanh lá, hộp dược chia ngăn, thẻ dược liệu | sắp lọ theo nhóm effect; không tạo aura/heal giả khi idle |
| NPC_ACTIVITY_STEWARD — Quan viên lịch hội | 4,8 WU; tư thế cởi mở, dáng người chạy việc | áo nâu đỏ, thẻ lịch, trống tay nhỏ và bảng giờ | đọc giờ hoạt động, gõ bảng một nhịp; thoại ngắn, hiện timezone |
| NPC_ARENA_STEWARD — Trọng tài Long Môn | 5,1 WU; dáng thẳng, hai tay rõ | áo trọng tài chàm-trắng, phù hiệu vòng đấu, cờ hiệu hai mặt | giơ cờ khi check-in/forfeit; animation dứt khoát, không thiên vị phe |
| NPC_ARENA_REWARD_CLERK — Thủ quỹ giải | 4,6 WU; dáng nhỏ gọn, ngồi cạnh tủ cúp | áo vàng đồng tối, bảng xếp hạng, hộp huy hiệu và sổ mùa | trao huy hiệu bằng hai tay; luôn nhìn ra roster trước khi hiển thị reward |
| NPC_COURT_ARCHIVIST — Quan thư lầu | 5 WU; trưởng thành 45–55, vai áo vuông, bàn tay dính mực | áo tím mực/giấy ngà, thẻ thư khắc số, cuộn hồ sơ niêm dây đỏ | mở một trang mỗi câu, không xé/đốt tài liệu; giọng chuẩn mực, ít cảm thán |
| NPC_TL_GATEKEEPER_W/E — Quan giữ lộ Tây/Đông | 5,2 WU; dáng hộ vệ cổng nhưng không đe dọa | giáp nhẹ xám đá, áo choàng đỏ đất, bảng lộ trình; hai đầu thành khác phù hiệu | chỉ tuyến bằng tay, không vẫy người chơi đi vào route chưa mở |
| NPC_TL_BEAST_TENDER — Người giữ thú | 4,8 WU; thân thiện, dáng hơi cúi về thú | áo vải rêu nhạt, còi gọi thú, túi thức ăn và khăn lau | tương tác với thú player không chặn đi; giọng ấm, không coi pet là combat loot |

### 4. Năm trưởng môn/phái

| ID | Phái | Tạo hình/đạo cụ | Điệu bộ và màu nhận diện |
|---|---|---|---|
| NPC_MASTER_MINH_KIEM | Minh Kiếm/Kim | áo dài chéo vạt, kiếm bản mảnh, khóa kim loại lục giác | đứng thẳng, tay luôn gần chuôi; vàng nhạt/xám bạc |
| NPC_MASTER_ANH_DAO | Ảnh Đao/Hỏa | áo ôm gọn, khăn vai lệch, đao ngắn kép | dựa gót chân, nhìn mục tiêu trước khi nói; cam than/đỏ sẫm |
| NPC_MASTER_HUYEN_BUT | Huyền Bút/Thủy | tay áo rộng có khóa, bút dài bằng cẳng tay, hộp mực | xoay bút giữa ngón tay, nét cử động mềm; lam mực/xanh ngọc |
| NPC_MASTER_THACH_CHUY | Thạch Chùy/Thổ | áo giáp vải dày, chùy thấp, gối bọc đá | chân mở rộng, động tác tiết kiệm; nâu đá/đồng |
| NPC_MASTER_LINH_CUNG | Linh Cung/Mộc | cung gập, dây tên lá, áo choàng nhiều lớp ngắn | quay về phía gió, nhìn đường bắn; xanh lá/vàng cỏ |

Mỗi NPC master có 3 state: idle quảng trường, thoại, bài thử. Hệ thống ẩn 4 master không thuộc lớp người chơi trong góc camera nếu crowd density cao, nhưng cho phép gặp trong quest C1-05/C5-04.

### 5. NPC chức năng và NPC đám đông

Các NPC dưới đây dùng base sprite/face variants chia sẻ nhưng từng ID có outfit/đạo cụ nhận ra được. Dữ liệu quest và chức năng bám Map Atlas.

| ID hoặc nhóm | Tạo hình và nhiệm vụ |
|---|---|
| NPC_FISHER_01 | ngư dân lớn tuổi, mũ lá cong, giỏ cá; animation giật cần và cúi nhặt cá |
| NPC_MEDIC_BEN | áo sáng, hộp cứu thương gỗ, khăn xanh; icon shop thuốc |
| NPC_BOAT_KEEPER | áo phao vải, sào chống, còi; hoạt ảnh kéo dây thuyền |
| NPC_BLACKSMITH / NPC_REPAIRER | thợ rèn/tu bổ khác nhau; tạp dề, búa/kìm, animation kiểm tra item |
| NPC_TRADER / NPC_RELIC_MERCHANT / NPC_WATER_SELLER | ba merchant class: chợ, cổ vật, nước; mỗi người có bảng giá/props riêng |
| NPC_GUILD_CLERK / NPC_SIEGE_CLERK / NPC_TELEPORTER / NPC_RAID_KEEPER | clerk có hồ sơ/biểu tượng UI cụ thể, không cần tên thoại dài |
| NPC_WOODCUTTER_01 / NPC_MUSHROOMER / NPC_LT_MECHANIC / NPC_WATER_KEEPER | lao động Lâm Triều; rìu, giỏ nấm, dây van, thước nước |
| NPC_CARAVAN_GUARD | hộ vệ đoàn xe, áo cát có khiên gỗ, spear; animation kiểm tra đường |
| NPC_DIVER_LEAD và NPC_BY_DIVER_01..03 | outfit áp suất cùng family; diver lead có 2 bình khí, nhóm có 1 bình và màu khăn riêng |
| NPC_TL_WITNESS_01/02 | hai người bán hàng làm nhân chứng; silhouette thấp/cao, một người cầm giỏ, một người chống gậy |
| NPC_TL_GUARD_RESCUE | hộ vệ bị kẹt cạnh cọc điều khiển; giáp mỏng, không có weapon attack |
| NPC_BM_RESCUE_01/02 | dân chài mắc rễ; áo ướt, biểu cảm hoảng sợ rồi bình tĩnh sau rescue |
| NPC_SH_WORKER_01..04 | công nhân lò khác màu khăn/đồ bảo hộ; chỉ trạng thái “chưa cứu/đã cứu”, không tạo sprite-set riêng |
| NPC_TS_REFUGEE_A/B/C | ba nhóm hộ tống; 4 actor mỗi nhóm, dùng LOD/crowd proxy khi ở xa |
| NPC_TS_ENVOY_01/02 | sứ giả hai phe; áo quân phục khác màu nhưng cùng silhouette, đưa văn kiện |
| NPC_LYAN_ESCORT | dùng sprite-set/ID NPC_LYAN, chỉ là quest state và waypoint, không sinh bản sao |
| NPC_MASTER_[CLASS] | token quest được biên dịch sang một trong năm ID master cụ thể theo lớp |

Các ID NPC_BM_RESCUE, NPC_SH_WORKER, refugee group và witness có thể là actor phụ không có thoại tự do; interaction panel vẫn dùng portrait/key dialogue riêng.

### 6. Bestiary: quái thường và tinh anh

Thông số dưới đây là actor bounds WU; HP được định nghĩa theo tier tương đối để combat config có thể scale theo level. Thời gian báo đòn theo clock server/client; sprite frame cadence không quyết định gameplay. Mỗi quái có state machine Idle → Detect → Approach/Position → Telegraph → Attack → Recovery → Return/Death. Không cho quái tự đẩy người chơi khỏi map; anti-stuck reset nếu nav không tiến triển 3s.

| ID/quái | Kích thước / vai trò | Tạo hình và bảng màu | Hành vi/đòn chính/telegraph | Loot/biến thể |
|---|---|---|---|---|
| MOB_CARPLING — Cá Linh | 2,2×1,8; swarm | cá thân dài, vây như lá mưa, xanh lam bạc | nhảy từ vũng; cú đớp line ngắn báo 0,45s; hồi 0,5s | cá/nguyên liệu; biến thể vây đỏ elite |
| MOB_WATERROOT — Rễ Nước | 2,5×3; area denial | rễ gỗ ướt với hạt sáng xanh | mọc dưới đất, vòng gợn 0,7s rồi quật thẳng; có thể chặt khi lộ | gỗ/dược; nở gai elite |
| MOB_SHORE_STALKER — Kẻ Rình Bờ | 4×4; ambusher | thú bốn chân, mõm dài, lưng sậy | nấp trong cỏ, mắt lóe 0,5s; lao ngang, recovery 0,8s | da/cá; elite để lại vệt bùn |
| MOB_MOSS_BEAST — Thú Rêu | 3×3; bruiser | thân rùa/mèo tròn, lưng rêu có đốm | húc ngắn, cuộn tròn 0,9s; chậm xoay | gỗ/dược; elite có khiên rêu |
| MOB_DREAM_ROOT — Rễ Mộng | 3,8×4,5; control | thân cây thấp, mặt không người, rễ tách như ngón | rễ đâm line theo mục tiêu sau 0,8s; vùng ký ức xanh hiện hình | gỗ/linh phách; tinh anh có rễ phụ |
| MOB_SAND_BEETLE — Bọ Cát | 2,3×1,5; skirmisher | mai cát dạng nêm, chân 6 điểm, vàng sẫm | đào xuống báo bụi 0,6s, trồi lên gây hitbox nhỏ | quặng/da; elite tạo 2 dấu giả |
| MOB_ASH_RAIDER — Cướp Tro | 4,2×4,6; melee humanoid | mặt nạ lọc, áo quấn vải, đao rỉ | chém ngang báo 0,45s, ném tro làm mù 0,7s; không gây mù màn hình toàn phần | Đồng/vải; elite ném bom có vùng |
| MOB_FURNACE_WARDEN — Người Canh Lò | 5×5; armored | giáp sắt nóng, lõi đỏ sau lưng, chùy ngắn | đập đất cone báo 0,7s; giáp sau lưng mở sau đòn; fire sweep line | quặng/linh phách; tinh anh có thêm vent |
| MOB_FALSE_SIGIL — Kẻ Giả Phù | 4,3×4,8; agile human | áo thường, phù giả phát sáng sai màu, nửa mặt che | đổi vị trí nhanh, đâm chéo; marker giả tắt trước attack 0,5s | giấy phù/Danh Vọng |
| MOB_SMALL_STATUE — Tượng Nhỏ | 4×5; sentry | tượng đá khớp đồng, mắt hình vòng | bắn viên đá đơn; khóa line 0,7s; cọc điều khiển có thể phá | đá/quặng |
| MOB_FLAME_SENTINEL — Tượng Gác Lò | 5×6; elite, không phải boss | tượng đồng/đá cùng họa tiết với Tượng Hành Hỏa, lõi nhỏ hình tam giác | quét ngắn báo 0,7s, gọi một cột lửa báo 1s; không có phase gate hoặc mechanic dập cọc | quặng đồng; elite có vật liệu lò |
| MOB_STONE_AUTOMATON — Tượng Cơ | 4,8×5,5; guard | đá khối có cơ cấu kim loại ở khuỷu | chậm, block frontal; đòn nện vòng 0,75s | đá/linh phách |
| MOB_FALSE_SOLDIER — Binh sĩ giả lệnh | 4,8×5; human melee | hai phe màu sắc nhưng dấu sáp giả giống nhau | đội hình đôi, đâm line; gọi viện khi mục tiêu xa | huy hiệu chiến trường |
| MOB_AMBUSH_TROOPER — Phục kích binh | 4,5×4,8; melee | áo giáp nhẹ, khăn che mặt, cờ giả | xuất hiện theo wave, ném móc báo 0,6s | Đồng/vải/weapon common |
| MOB_SIEGE_ENGINE — Phá Thành Cơ | 8×7; siege hazard | xe công thành thấp, 2 nỏ, bánh bọc sắt | lane shot 1s, có dây neo phá được; cần né ngang | quặng/achievement |
| MOB_MIRRORFISH — Cá Gương | 3×2; ranged | cá thân trong, mặt gương hình thoi | bắn bubble line báo 0,65s; phản chiếu hình giả 0,8s | vảy uyên |
| MOB_PRESSURE_GUARD — Kẻ Gác Buồng | 4,5×5; guard underwater | giáp vòm, bình áp suất sau lưng | đẩy áp lực cone, rồi slow bubble; áp suất lên màu/shape | linh phách/vảy |
| MOB_DROWNED_EXILE — Kẻ Lưu Vong | 4,8×5; humanoid | áo thành phố chìm, dải vải trôi lên | đánh lướt, để lại water pool; không mất máu vì nước | Đồng, đồ cấp vùng |
| MOB_MACHINIST — Kẻ Đục Mạch | 4,2×4,6; objective add | áo thợ máy, khoan mạch gắn tay | khoan vào cột; cần interrupt/đánh lùi trước 10s | MAT-CORE, raid contribution |
| MOB_RIFT_HUNTER — Thợ Săn Mạch | 4,8×5,2; ranged | giáp nhiều đoạn, mặt nạ khe dọc, dây sáng tím | bắn 3 projectile có spread, vòng target 0,8s | đá mạch |
| MOB_BOSS_ADD — Hộ Vệ Lõi | 4–5×5; raid add | mỗi add mang một biểu tượng hành động: ngắt, giải, phá giáp | 3 hành vi dễ đọc, không cần class bắt buộc | token encounter |

### 7. Boss: tạo hình, hoạt ảnh và đòn nhận diện

| Boss | Silhouette/body segment | Đòn bắt buộc và tín hiệu | Palette/VFX pixel đặc trưng |
|---|---|---|---|
| BOSS_FLAME_SENTINEL — Tượng Hành Hỏa | tượng hộ vệ đồng/đá 8 WU; lõi lò tam giác, hai vai bất đối xứng | 3 pha: quét ngang báo 0,8s; gọi 3 cột lửa có vòng đất báo 1s; vent làm lộ lõi 4s sau khi dập cọc | đồng hun/đá đen, lửa cam; cột lửa không che chân và lối thoát |
| BOSS_MANG_COT — Mãng Cốt | thân rắn xương dài 15 WU; đầu có sừng gãy, cổ nhiều đốt | theo DEC-017/Rules §4: quét cone120°/8WU báo0,9s; lặn-trồi radius4WU báo1,2s; vòng bọt riêng annulus3..7WU báo1s | xương trắng ngà, rêu lam; nước bắn thấp, không che chân; vòng bọt không chỉ là VFX điểm trồi |
| BOSS_ANCIENT_TREE — Cổ Thụ Trăm Mắt | cây 28 WU cao, thân lệch, 12 cụm mắt nhưng tối đa 5 sáng cùng lúc | rễ đuổi 1s; 3 rễ sáng cần chạm theo A-B-C; nấm độc có đường thoát | gỗ đen xanh, mắt xanh rêu; lá rơi theo vùng |
| BOSS_FURNACE — Lò Trời | golem lò 12 WU, ống khói, lõi tròn | ba van giảm nạp; pha 1 giáp, pha 2 tắt van, pha 3 ba lane lửa | cam đồng/đen; heat haze không làm méo telegraph |
| BOSS_TONG_BANH — Tống Bành | actor người 5,8 WU trong giáp tháo rời có 2 ụ phụ | giáp trước/sau; hai bẫy giáp đánh dấu; đòn lao ngang báo cờ kéo | thép xám xanh, bụi nặng khi bước, không có máu |
| BOSS_TIDE_SERPENT — Mẫu Xà Thủy | xà biển 16 WU, cổ dài, vảy gương, đuôi rộng | nước dâng platform; đớp theo target line; phân thân, sóng âm chỉ thân thật | xanh lam/teal; caustic dưới chân, không bloom trắng |
| BOSS_COSM — Cơ Vô Tướng | thân người 5,5 WU, vòng cơ khí sau lưng 12 WU, mặt nạ sứ | line/sweep/orb; thiết bị ký ức; 5 socket cuối; telegraph phải đọc ở 20vfx | tím mực + đồng, hình học gãy; camera không cắt cảnh |
| BOSS_YOUNG_TREE — Cổ Thụ Con | thân cây 9 WU, 4 rễ chuyển động và 3 nụ mắt; nhỏ hơn rõ rệt Cổ Thụ Trăm Mắt | rễ hình nón báo 0,9s; nấm độc 3 vùng; rễ sáng lộ khiên để phá | gỗ non sẫm, nhựa xanh; nấm giữ silhouette người chơi |
| BOSS_ASH_FURNACE — Lò Tro | golem lò 10 WU, hai ống xả lệch và 3 van có thể đọc được | nạp lò 10s; đóng ít nhất 2/3 van; ba lane lửa có khe thoát | sắt ám tro, lõi cam; dùng hình bóng khác Lò Trời |
| BOSS_SIEGE_ENGINE — Phá Thành Cơ | cỗ máy 11×8 WU trên càng kéo, nỏ kép và dây neo nhìn thấy được | bắn 3 lane báo trước; cắt neo sau; lao ngang báo cờ kéo; tiến độ neo giữ qua wipe | thép xanh xám, dây vải đỏ; không tạo khói che vùng đánh |
| BOSS_YOUNG_SERPENT — Mẫu Xà Non | xà nước 12 WU, thân mảnh, hai vây trong; không có clone trang trí | đớp theo target line; nhấn chìm hai lane; sóng âm đánh dấu thân thật ở phase cuối | xanh ngọc lạnh; safe platform có viền sáng và ký hiệu |
| BOSS_PRESSURE_HEART — Tim Áp Suất | lõi tinh thể 9 WU lơ lửng trong khung bốn trụ; không có mặt người | tia theo ba lane; đánh dấu trụ nhận tia; đồng bộ hai van trong 6s; safe platform khi nước dâng | tinh thể lam/trắng mờ; tương phản cao, không bloom trắng |

Tống Bành là boss nhân vật campaign; Phá Thành Cơ là máy công thành riêng. Không reuse actor cùng model với Tượng Hành Hỏa hoặc Cơ Vô Tướng.

### 8. Thời tiết và môi trường theo vùng

Thời tiết client-sync theo weather seed của shard; mỗi chuyển trạng thái blend bằng sprite frame/palette step trong 8s, state tồn tại 5–12 phút. Weather không thay đổi sát thương/tốc độ/trúng đòn trừ hazard được nêu riêng trong encounter và có telegraph. Mỗi hiệu ứng có LowFX mode: giảm particle 70%, tắt layer trang trí, giữ silhouette và cảnh báo; không dùng lens/blur.

| Map | Phân bố thời tiết | Thiết kế FX | Ánh sáng/âm thanh | Tác động gameplay |
|---|---|---|---|---|
| Bến Mưa | mưa nhẹ 55%, mưa rào 20%, tạnh 25% | 60/120 hạt mưa trước/sau, tốc 18–27 WU/s, giọt mái hiên, puddle ripple | trời lam xám, đèn ấm; mưa stereo thấp, sấm rất xa | cosmetic; bờ/trơn không làm đổi vật lý |
| Thanh Lạc | nắng mây 65%, mây râm 25%, mưa bụi 10% | bụi nắng 12 hạt/s, cờ bay chậm | daylight vàng nhạt, chợ ambience | không impact combat |
| Lâm Triều | sương thấp 35%, mưa tán cây 35%, nắng khe 30% | fog band cao 2–4 WU, leaf fall 8–20 hạt/s, tầm nhìn xa giảm tối đa 15% | rừng ẩm, tiếng nước/chim | chỉ hazard scripted; minimap không mờ |
| Sa Hỏa | gió cát 35%, nắng gắt 45%, đêm tro 20% | cát ngang theo dải pixel 15 WU/s, heat shimmer là tile banding nền, ash pixels tối đa 20/s | vàng/cam theo palette step; lọc gió tắt dần ở khu thông gió | gas damage chỉ vùng quest, không do weather |
| Trấn Sơn | mây thấp 40%, tro xa 25%, nắng xám 35% | cờ bay theo gió, bụi chân khi combat, tro xa 10/s | ambience cờ/kim loại, không mưa dày | cosmetic ngoài siege |
| Bạch Uyên | caustic nước 100%, triều theo encounter | tia sáng di chuyển 0.4 WU/s; bong bóng nền 6/s; không làm rung UI | âm underwater filter, giảm high frequency | tide hazard là encounter riêng, báo 2s |
| Vực Nghịch Mạch | nhịp mạch 60s sáng/30s yên; bụi void | đường sáng chạy trong khe, hạt tím tối đa 16/s; vệt hư không hình dải | exposure không nhấp nháy; low-frequency pulse nhẹ | pulse ambient cosmetic, không gây damage |
| Đại Ngũ Mạch | theo cánh nguyên tố, 5 phút/cycle | hạt theo màu/tốc độ riêng, giới hạn 30/s cục bộ | chuyển màu crossfade 8s, âm thanh tầng lớp | world event hazard chỉ khi alert/objective hiện |

Sấm sét không đánh ngẫu nhiên vào player. Không có mưa làm giảm accuracy, sương làm NPC/quái ẩn, heat haze làm lệch hitbox. Weather transition không được xảy ra giữa gameplay telegraph boss; giữ khuôn thời tiết hiện tại trong encounter instance.

### 9. Skin UI và nguyên tắc minh họa

**UI visual language:** pixel-art panel gợi giấy dó với viền mực theo grid; header dùng tile gỗ/đồng; button có shape theo chức năng, không dùng icon nhận diện KPAH. Nền panel Ink-900/Paper-100 là mảng pixel; border theo source pixel grid. Ornament chỉ ở góc, không đặt dưới text. Bitmap font bao phủ tiếng Việt; không blur/anti-aliasing.

| Component | Kích thước/kiểu | Trạng thái |
|---|---|---|
| Primary button | 56dp cao mobile / 48 CSS px PC; frame pixel 9-slice; nền Kim-Gold palette ramp | normal, hover, pressed, disabled, loading |
| Secondary button | 48 CSS px; nền Ink-700, viền pixel Paper-200 | focus có pixel frame Ally-Help |
| Icon item | 32–64px source art; render integer-scale; khung rarity có pattern | equipped, locked, new, quest, broken |
| Skill slot | 58–70dp mobile; silhouette rõ ở 40px | ready, cooldown sweep, insufficient MP, disabled, cast |
| Panel title | 28–36px desktop, 22sp mobile | icon section + title; back/close luôn rõ |
| Tooltip | 320–420px desktop; mobile full bottom sheet | stat rows, compare, source, binding, effect |
| HP/MP bar | cao 10–14px desktop, 8–12dp mobile | số hiện khi low state; color + text/icon |
| Quest tracker | max 3 pin, 2 dòng/quest | collapse, tracking, complete, blocked |
| Chat bubble | 12s fade world chat, no blocking interaction | muted/block/report options |
| Damage text | 20px ordinary, 24px crit | color + shape/icon; cap density |
| Weather overlay | safe area full screen, alpha ≤0.18 | LowFX toggle, no UI occlusion |

Item rarity uses both color and mark: Thường circle, Tinh triangle, Linh diamond, Huyền double-line, Cổ Vật seal. Element icons are geometry + color; quest objective is never indicated only by sparkle.

### 10. Animation and VFX budget

- NPC idle loop 2–5s, no repeated blink synchronized for every crowd actor; random seed per actor but deterministic enough for replay.
- Quái thường 8 clips minimum: idle, turn, walk, run, telegraph, attack, hit, death. Elite 11 clips; boss 16–24 clips including phase transitions and break states.
- Character class common set: idle, run, jump, fall, land, hurt, death, interact, attack combo 3, skill 6, dodge; visual should expose weapon silhouette in all states.
- Weather GPU/CPU budget: 120 foreground particles + 400 background pixel sprites max on high; mobile 35 foreground/150 background; no full-screen blur/post-processing.
- Combat VFX budget per actor: ≤2 persistent effects; per skill burst ≤40 major particles on mobile, ≤120 on high; repeated hit damage text merge if >8 targets.
- Boss telegraph render order top; alert icons at screen edge for off-screen line attacks. Camera shake ≤0.12s and setting default 30% amplitude.
- LowFX preserves VFX shape/telegraph, disables small spark pixels, persistent pet trails and camera shake.

### 11. Handoff assets and naming

Asset path pattern: Art/Characters/NPC_ID, Art/Enemies/MOB_ID, Art/Bosses/BOSS_ID, Art/Environment/MAP_ID, Art/UI/ComponentName, VFX/Skill/SKILL_ID. Every delivery includes lossless pixel source, exported sprite/tile atlas, palette, frame state table, pivot/scale WU, PPU/import preset, thumbnail, collision guide and transparent preview. Existing NPC registry fields named `rig_id`/`animation_set_id` remain stable data keys; values resolve to pixel sprite sets, not bone-deformed meshes.

A character sheet includes pixel front/side/back, face closeup, palette swatches, props, 5 expressions, outfit variants and scale next to hero. Enemy sheet includes neutral, telegraph silhouettes, attack/hit/death, elite palette variant, shadow size and collision box. Weather sheet includes still, loop, LowFX, palette before/after. UI sheet includes 16:9 and 20:9 plus normal/focus/disabled/loading/error at integer scale. Asset IDs must match Map Atlas, Combat Spec and Item Master CSV exactly.

### 12. Monster stat and AI profile baseline

Các giá trị dưới đây là baseline cấp 1–100. Spawn entry trong Map Atlas cung cấp level thực tế; tinh chỉnh bằng config. Sát thương quái không dùng stat gear của người chơi.

- Base thường: HP = 120 + 24 × level; Attack = 10 + 2 × level; Defense = 2 + 0,8 × level.
- Damage nhận trước defense = Attack × hệ số đòn; damage cuối = damage nhận × 100/(100 + Defense mục tiêu). Chống nguyên tố xử lý riêng.
- Elite: nhân HP ×6, Attack ×1,6, Defense ×1,8 so với archetype; reward thêm token.
- Boss quest/world: HP = BaseHP ×35 × (1 + 0,65 × (partySize−1)); attack multiplier theo boss table; boss scale theo party 1–5, raid dùng hệ số riêng.
- Raid boss 10 người: HP = BaseHP ×100 × (1 + 0,45 × (partySize−1)); objective/phase là giới hạn chính, không chỉ HP.
- Aggro radius đo bằng mét; leash reset về spawn anchor sau 14–24m. Enemy không theo player qua portal. Boss có arena boundary/target reset.
- Quái thường báo đòn cận chiến ≥0,45s, đòn nặng ≥0,7s, projectile ≥0,65s, boss AoE ≥0,9s. Telegraph không bị weather/LowFX tắt.

| Enemy ID | HP× | ATK× | DEF× | Tốc độ m/s | Aggro m | Đòn thường | Đòn nặng / special |
|---|---:|---:|---:|---:|---:|---:|---|
| MOB_CARPLING | 0,8 | 0,75 | 0,7 | 3,0 | 7 | đớp 0,8× Attack, 2m | nhảy 1,1×, báo 0,45s |
| MOB_WATERROOT | 1,1 | 1,0 | 1,1 | 0,5 | 5 | roi rễ 1,0×, 2,6m | chồi đất 1,5×, line 4m, báo 0,7s |
| MOB_SHORE_STALKER | 0,9 | 1,15 | 0,8 | 3,4 | 8 | vồ 1,0× | lao 1,4×, báo mắt/bụi 0,6s |
| MOB_MOSS_BEAST | 1,5 | 1,0 | 1,3 | 2,2 | 7 | húc 1,0× | cuộn 1,6×, radius 2,4m, báo 0,75s |
| MOB_DREAM_ROOT | 1,2 | 0,95 | 1,2 | 1,6 | 8 | quật rễ 0,9× | rễ đâm 1,3×, line 5m, báo 0,8s |
| MOB_SAND_BEETLE | 0,8 | 1,1 | 0,8 | 3,2 | 7 | cắn 0,9× | trồi đất 1,25×, báo bụi 0,6s |
| MOB_ASH_RAIDER | 1,0 | 1,1 | 0,9 | 2,5 | 8 | chém 1,0× | tro mù 0,2× + slow 10%, báo 0,7s |
| MOB_FURNACE_WARDEN | 1,7 | 1,25 | 1,6 | 1,5 | 10 | chùy 1,1× | nện cone 1,7×, báo 0,8s |
| MOB_FALSE_SIGIL | 0,9 | 1,0 | 0,7 | 3,2 | 10 | đâm 1,0× | đổi hướng rồi chém 1,4×, báo 0,6s |
| MOB_SMALL_STATUE | 1,1 | 0,9 | 1,2 | 1,0 | 12 | đá bắn 0,8× | chùm 3 viên ×0,6, báo 0,7s |
| MOB_STONE_AUTOMATON | 1,4 | 1,0 | 1,3 | 1,5 | 8 | đấm 1,0× | nện vòng 1,6×, báo 0,8s |
| MOB_FALSE_SOLDIER | 1,0 | 1,0 | 1,0 | 2,3 | 8 | giáo 1,0× | lệnh đội hình 1,4×, báo cờ 0,7s |
| MOB_AMBUSH_TROOPER | 0,95 | 1,1 | 0,85 | 2,8 | 9 | chém 1,0× | móc kéo 0,8× + reposition, báo 0,6s |
| MOB_SIEGE_ENGINE | 3,0 | 1,3 | 1,8 | 0,8 | 14 | bolt 1,2× | volley 3×0,7× trên lane, báo 1s |
| MOB_MIRRORFISH | 0,9 | 1,0 | 0,7 | 2,6 | 10 | cắn 0,8× | bubble line 1,2×, báo 0,65s |
| MOB_PRESSURE_GUARD | 1,3 | 1,1 | 1,4 | 1,6 | 9 | giáo áp 1,0× | bubble slow 0,6× + slow 20%, báo 0,75s |
| MOB_DROWNED_EXILE | 1,0 | 1,0 | 0,95 | 2,4 | 8 | vũ khí 1,0× | lướt 1,3×, báo 0,65s |
| MOB_MACHINIST | 0,8 | 0,7 | 0,7 | 2,4 | 9 | khoan 0,6× | channel lên cột, ngắt được trong 10s |
| MOB_RIFT_HUNTER | 1,0 | 1,05 | 1,0 | 2,9 | 12 | bolt 0,8× | spread 3×0,65×, báo 0,8s |
| MOB_BOSS_ADD | 0,7 | 0,85 | 0,8 | 2,2 | 9 | đòn theo role 0,8× | skill interrupt/cleanse/break có cue riêng |

Boss table: BOSS_MANG_COT HP×35/ATK×2.0; BOSS_FLAME_SENTINEL HP×45/ATK×2.0; BOSS_ANCIENT_TREE HP×60/ATK×1.8; BOSS_FURNACE HP×70/ATK×2.2; BOSS_TONG_BANH HP×55/ATK×2.0; BOSS_TIDE_SERPENT HP×75/ATK×2.1; BOSS_COSM raid HP×100/ATK×2.2. Cơ Vô Tướng có objective/phase gates; damage bị giới hạn ở ngưỡng phase để tránh skip cơ chế. Boss attack hệ số riêng và cooldown không thể bị stat người chơi rút ngắn.

### 13. Roster NPC phụ theo ID

Mỗi ID dưới đây có một sheet outfit/portrait riêng. Crowd archetype có thể dùng chung base sprite sheet nhưng cần ít nhất 3 biến thể mặt/tóc/khăn/palette để dân cư không lặp thành bản sao. NPC không combat có HP=0/invulnerable, không bị target, không nhận knockback; NPC rescue/escort có HP quest-state riêng nhưng không hiện thanh HP trừ khi encounter yêu cầu.

| NPC ID | Tạo hình riêng | Animation/UX chức năng |
|---|---|---|
| NPC_FISHER_01 | người chài lớn tuổi, nón bẹ cong, áo tay ngắn màu lam đất, giỏ lưới | thả câu, giật cần, nhặt cá; bảng câu cá mở bằng E |
| NPC_MEDIC_BEN | y sĩ trẻ, áo sáng xanh, hộp thuốc gỗ ở hông | mở shop thuốc; kiểm tra mạch tay khi idle |
| NPC_BOAT_KEEPER | người chèo thuyền trung niên, áo phao vải vàng, sào dài | kéo dây neo; mở cổng sau P00-05 |
| NPC_BLACKSMITH | thợ rèn lớn tuổi, tạp dề than, búa ngắn, kính che mắt | gõ đe 3 nhịp; mở repair/craft/upgrade |
| NPC_REPAIRER | thợ vá giáp dáng nhỏ, dây da và kim khâu lớn | đo độ bền, vá 1 đường; repair-only panel |
| NPC_TRADER | người bán chợ trung niên, áo khoác nhiều túi, sổ giá | mở buy/sell; chỉ tay vào món, không animation barter dài |
| NPC_RELIC_MERCHANT | nhà sưu tầm, áo choàng ngà, kính lúp/khay đá | preview relic/appraisal; hiện dòng ẩn khi giám định |
| NPC_WATER_SELLER | người chở nước, bình sành đôi, khăn xanh nhạt | bơm nước vào bình; shop consumable Sa Hỏa |
| NPC_GUILD_CLERK | thư lại trẻ, áo xám viền xanh, con dấu guild | mở guild create/manage; gọi panel, không hội thoại rườm rà |
| NPC_SIEGE_CLERK | lính ghi danh, giáp nhẹ, bảng roster | mở đăng ký/roster/schedule công thành |
| NPC_TELEPORTER | người giữ cổng, áo dài chẻ vạt, găng kim loại | chạm vòng dịch chuyển; hiển thị tuyến đã mở/chưa mở |
| NPC_RAID_KEEPER | thủ vệ lobby, giáp nghi lễ, token raid trước ngực | mở ready-check; animation giơ cờ khi group đủ người |
| NPC_WOODCUTTER_01 | thợ rừng trẻ, rìu cán dài, áo xanh cũ | đốn cây loop; thoại/quest mở nguyên liệu |
| NPC_MUSHROOMER | người hái nấm đội nón rộng, giỏ lưng thấp | nhặt nấm, soi đất; bật marker dược liệu |
| NPC_LT_MECHANIC | thợ máy Lâm Triều, dây đo và cờ lê, áo ngắn | kiểm van, chạy giữa checkpoint; escort path theo Map Atlas |
| NPC_CARAVAN_GUARD | hộ vệ Sa Hỏa, khiên ván, khăn lọc bụi | đi vòng quanh xe; combat pose khi wave xuất hiện |
| NPC_PRESSURE_KEEPER | kỹ sư Bạch Uyên, bộ đo áp suất 3 ống, kính vòm | thao tác van; portrait/indicator hiển thị pressure state |
| NPC_BY_DIVER_01 | diver khăn vàng, dáng cao, bình đơn | kéo dây cứu hộ; actor quest C5-01 |
| NPC_BY_DIVER_02 | diver khăn đỏ, thấp hơn, bình đôi | ngồi kiểm rò khí; actor quest C5-01 |
| NPC_BY_DIVER_03 | diver khăn trắng, áo vải xanh đậm, chân bị thương | tựa tường; đứng dậy sau rescue trigger |
| NPC_BY_WITNESS_MINH_KIEM | bản chiếu ký ức Minh Kiếm, giáp nhẹ Kim viền trong như nước, kiếm gãy thành dải sáng | tương tác thoại không va chạm tại waypoint Map Atlas |
| NPC_BY_WITNESS_ANH_DAO | bản chiếu ký ức Ảnh Đao, khăn vai Hỏa và hai vệt đao chéo | tương tác thoại không va chạm tại waypoint Map Atlas |
| NPC_BY_WITNESS_HUYEN_BUT | bản chiếu ký ức Huyền Bút, tay áo lam và nét mực treo trong không khí | tương tác thoại không va chạm tại waypoint Map Atlas |
| NPC_BY_WITNESS_THACH_CHUY | bản chiếu ký ức Thạch Chùy, giáp Thổ vuông cạnh và chùy trong mờ | tương tác thoại không va chạm tại waypoint Map Atlas |
| NPC_BY_WITNESS_LINH_CUNG | bản chiếu ký ức Linh Cung, cung Mộc có dây lá phát sáng | tương tác thoại không va chạm tại waypoint Map Atlas |
| NPC_TL_WITNESS_01 | người bán trà cao, tạp dề xanh rêu, quạt nan | chỉ vào dấu phù, phản ứng sợ khi Kẻ Giả Phù lộ mặt |
| NPC_TL_WITNESS_02 | người gác sạp thấp, khăn vàng, gậy tre | quay đầu theo NPC impostor; thoại phụ khác witness 01 |
| NPC_TL_GUARD_RESCUE | hộ vệ Thanh Lạc, giáp lam nhạt, giáo rơi cạnh | trạng thái mắc kẹt/đã cứu; không combat AI |
| NPC_BM_RESCUE_01 | dân chài áo xanh ướt, chân kẹt rễ ở x=135 | tương tác cắt rễ 1,2s, đứng dậy và chạy tới bờ |
| NPC_BM_RESCUE_02 | người chèo đò khăn đỏ, tay giữ đèn ở x=148 | tương tác tháo dây rễ, đi theo đến checkpoint |
| NPC_SH_WORKER_01..04 | cùng bộ bảo hộ lò; biến thể khăn đỏ/vàng/lam/trắng, khuôn mặt khác nhau | nằm/ho khan trước cứu, đứng/đi sau cứu; không bị damage từ gas quest |
| NPC_TS_REFUGEE_A | nhóm 4 người, một xe kéo và áo choàng xám | đi theo tuyến trại→cổng, checkpoint A |
| NPC_TS_REFUGEE_B | nhóm 4 người, trẻ em và thùng đồ, khăn vàng | di chuyển chậm hơn, có animation đỡ xe |
| NPC_TS_REFUGEE_C | nhóm 4 người, một người bị thương, băng vải xanh | dừng tại checkpoint C để cứu thương |
| NPC_TS_ENVOY_01 | sứ giả quân phía Bắc, áo đỏ nâu, lệnh cuộn dây đỏ | đưa lệnh, chỉ ra dấu sáp giả |
| NPC_TS_ENVOY_02 | sứ giả quân phía Nam, áo xám lam, lệnh cuộn dây bạc | giơ hai tay khi bị hỏi, thoại đối chiếu khác NPC 01 |
| NPC_LYAN_ESCORT | cùng sprite set/face Ly An, không spawn bản sao; chỉ đổi quest state | chạy tới x=80/120, chờ người chơi tại checkpoint, có snap cứu nếu stuck |
| NPC_MASTER_[CLASS] | token chọn trainer tương ứng 1 trong 5 master đã định nghĩa | narrative compiler resolve ID theo class; không dùng placeholder trong build data |

Mỗi NPC interaction có profile: range 2,5m, tap E/Interact, interaction cooldown 0,4s, quest condition server-side, idle/turn/talk/confirm sprite animation, voice subtitle key. NPC shop/guild/raid mở panel; rescue/quest actor phát dialogue graph; ambient NPC không giành focus khi nhân vật đang combat.
