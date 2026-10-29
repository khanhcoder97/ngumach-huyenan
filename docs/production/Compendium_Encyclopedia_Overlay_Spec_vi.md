# ĐẶC TẢ BÁCH KHOA LẠC CHÂU — COMPENDIUM OVERLAY
## Ngũ Mạch: Huyền Ấn — bản sản xuất v1.0

### 1. Mục tiêu, phạm vi và nguồn dữ liệu

Bách khoa Lạc Châu là sổ tra cứu kiến thức trong game, mở được từ menu chính/HUD, nhật ký nhiệm vụ, bản đồ, item tooltip, bestiary và NPC chức năng. Cửa sổ giúp người chơi tìm vật phẩm, nhiệm vụ, boss, quái, kỹ năng và địa điểm; giải thích cách dùng và nguồn sở hữu; điều hướng sang hệ thống tương ứng nếu đã mở khóa. Đây là lớp tra cứu và điều hướng: chọn kết quả không tự mua, dùng, rèn, nhận thưởng hay tiêu vật phẩm.

Đây là dự án Ngũ Mạch: Huyền Ấn, hình ảnh fantasy võ hiệp pixel-art 2D nhìn từ trên theo `Pixel_Art_Production_Standard_vi.md`; không sao chép UI, dữ liệu hay asset từ KPAH. Tên item, phẩm chất, nghề, lớp, map và ID phải lấy từ content registry của game. Nguồn chuẩn hiện có:

- Item và phẩm chất: `Item_Master_Catalog_vi.csv`, `Item_Rarity_Variant_Catalog_vi.csv`, `Item_Catalog_and_Set_Bible_vi.md`.
- Nhiệm vụ và diễn biến: `Quest_and_Narrative_Production_Spec_vi.md`, `Content_Bible_Ngu_Mach_Huyen_An_vi.md`.
- Quái/NPC/tạo hình: `Art_Entity_Weather_UI_Visual_Bible_vi.md`.
- Map/điểm đặt: `Map_Production_Atlas_vi.md`.
- Dungeon/raid/world boss/tháp: `Activities_Economy_PvP_Production_Spec_vi.md`.
- Kỹ năng/telegraph: `Combat_Skills_VFX_Animation_Spec_vi.md`.

### 2. Danh mục khởi điểm và cách tính counter

Counter do content registry trả về theo phiên bản dữ liệu; không hardcode vào giao diện và không cộng chồng record lặp. Snapshot tiền sản xuất hiện tại dự kiến có **2.533 record duy nhất**:

| Danh mục sidebar | Số record khởi điểm | Phạm vi được đếm |
|---|---:|---|
| Tất cả | 2.533 | Tổng record duy nhất: item + quest + NPC + boss + bestiary + pet/mount/fish + active/passive skill + địa điểm/hoạt động |
| Vật phẩm & nguyên liệu | 2.236 | 2.100 biến thể trang bị theo phẩm chất + 136 item cố định trong catalog |
| Nhiệm vụ & công việc | 76 | 36 nhiệm vụ chính + 40 nhiệm vụ phụ đã viết chi tiết; daily/weekly mới chỉ tính khi có record riêng |
| NPC & dịch vụ | 83 | 83 actor canonical; map placements có thể lặp nhưng inspector gộp theo ID |
| Trùm | 12 | 6 boss vùng/thế giới + 4 boss dungeon + 2 boss raid; bản quest/world dùng chung một hồ sơ boss canonical |
| Quái vật & linh thú | 21 | Base monster/boss-add templates; elite variant dùng template gốc nếu không có ID riêng |
| Thú đồng hành, thú cưỡi & cá | 16 | 5 companion + 5 mount + 6 fish species; đây là record độc lập trong pet/life-sim data |
| Vũ khí | 175 | 5 lớp × 7 tier × 5 phẩm chất; là bộ lọc con của Vật phẩm & nguyên liệu |
| Pháp bảo & trang bị | 1.925 | 385 template không phải vũ khí × 5 phẩm chất; là bộ lọc con của Vật phẩm & nguyên liệu |
| Bí tịch & kỹ năng | 70 | 30 active skill + 40 passive node có ID ổn định; filter theo lớp/nhánh/cấp/effect |
| Bản đồ & bí cảnh | 19 | 9 map thế giới + siege map + 4 dungeon + 2 raid + Tháp Lạc Ấn + ACT_LONG_MON_WEEKLY + ACT_TRAN_SON_10V10; 30 tầng tháp nằm dưới một record cha |

“Vũ khí” và “Pháp bảo & trang bị” là shortcut/filter vào tập item, không phải thêm record khi tính Tất cả. Khi chọn nhóm chính rồi nhóm con, item chỉ xuất hiện một lần trong kết quả. Counter thay đổi theo ngôn ngữ, quyền xem, giai đoạn khám phá và filter hiện hành; phía trên sidebar luôn cho biết `Đã khám phá / Tổng khả dụng` khi trạng thái khám phá đang được bật.

### 3. Trạng thái khám phá và giới hạn spoil

Mỗi record có một trong bốn trạng thái phía người chơi:

| State | Trạng thái tile | Inspector |
|---|---|---|
| `unknown` | Ẩn mặc định; chỉ hiện nếu bật `Hiện mục chưa khám phá` | Không tiết lộ tên đầy đủ, loot, nội dung quest hay boss mechanic |
| `rumor` | Hiện silhouette và tên mơ hồ nếu quest/lore đã nhắc | Chỉ hiện đoạn gợi ý đã được duyệt; nút dẫn đường yêu cầu mở khóa map |
| `discovered` | Icon và tên hiện đầy đủ | Mô tả cơ bản, loại, khu vực; dữ liệu chiến thuật/nguồn cụ thể có thể còn khóa |
| `recorded` | Viền sáng nhẹ, dấu `Đã ghi chép` | Hiện đầy đủ trường được phép xem sau lần gặp/clear/nhặt/học |

Mặc định `Ẩn nội dung chưa mở khóa` bật. Nhiệm vụ chưa gặp không nêu twist, nhân vật phản diện hoặc reward bất ngờ. Boss có thể hiện mô tả nền sau khi được nhắc tới; phase, telegraph, điểm yếu và loot chi tiết chỉ mở sau khi người chơi đã gặp encounter hoặc bật `Hiện gợi ý chiến đấu` trong cài đặt. Tắt spoiler được áp dụng cho preview card, search suggestion, breadcrumb và related entries, không chỉ inspector.

### 4. Kiến trúc cửa sổ và khung nhìn

Cửa sổ mở trên gameplay đã pause input điều khiển nhân vật; nền phủ slate tối phẳng 64%, không blur. Overlay dùng Ink-900/#16222B, texture gỗ lặp tile, viền pixel 9-slice theo grid và điểm nhấn Kim-Gold/#D9B75D. Hoa văn góc không lấn text. Rarity trang bị dùng frame/icon pixel đúng ký hiệu Ngũ Mạch: Thường vòng xám, Tinh tam giác lục, Linh thoi lam, Huyền hai vạch tím, Cổ Vật ấn vàng; boss/element dùng icon-shape, không dựa riêng vào màu.

| Khung nhìn | Kích thước và cột | Hành vi |
|---|---|---|
| Desktop ≥1440px | dialog tối đa 1380×860px; cột trái 18%, giữa 54%, phải 28% | ba pane cố định, cuộn độc lập; header và category toolbar giữ nguyên |
| Desktop 1024–1439px | 96vw × 92vh; trái 220px, phải 340px, giữa co giãn | grid tự giảm cột; inspector giữ tối thiểu 310px |
| Mobile ngang 720–1023px | full-screen; header 56px; tab `Danh mục / Danh sách / Chi tiết` | một pane hiển thị mỗi lần; filter/search giữ state khi đổi tab |
| Mobile dọc hoặc cửa sổ hẹp <720px | full-screen theo safe area | mở vào `Danh sách`; tab bar 3 mục dưới header; Details có nút quay về kết quả |
| Controller/keyboard | không đổi kích thước cột theo focus | focus tuần tự sidebar → search/filter → grid → inspector action; gamepad bumper đổi tab mobile |

Trên desktop cột trái có chiều rộng 220–250px; cột giữa 1fr, phải 340–390px. Modal không che notch/safe area, không kéo camera gameplay và đóng bằng X, Esc/Back hoặc nút Quay lại. Mở từ một entity deep-link sẽ khởi đầu ở đúng category, chọn sẵn record và cuộn tile vào vùng nhìn thấy.

### 5. Header

Header hiển thị:

- Tên game-flavor **BÁCH KHOA LẠC CHÂU**, icon quyển sách/ấn Ngũ Mạch, nút pin nếu người chơi muốn giữ cửa sổ mở.
- Nhãn nguồn: `Toàn bộ`, `Vật phẩm`, `Nhiệm vụ`… tùy entry point; breadcrumb ghi rõ category hiện tại.
- Sync badge: trạng thái `Đang đồng bộ`, `Đã đồng bộ HH:MM`, `Ngoại tuyến · dữ liệu đến HH:MM`, hoặc `Có dữ liệu mới` + nút tải lại. Kèm `Nội dung vX.Y` trong panel thông tin nhỏ.
- Nút đóng 44×44px, tooltip `Đóng · Esc`; khi có update đồng bộ thì không chặn đóng.

Thời gian là server timestamp đã đổi theo timezone/cài đặt người chơi, hiển thị 24 giờ. Không cập nhật đồng hồ mỗi giây; chỉ đổi khi nhận event sync hoặc mở panel.

### 6. Sidebar danh mục

Sidebar có vùng cuộn độc lập, icon 24px, label, counter tabular, focus ring vàng. Mục được chọn có nền đồng mờ và thanh chỉ báo ở mép trái. Danh sách:

1. **Tất cả** — record duy nhất, không gồm mục unknown đang bị ẩn.
2. **Vật phẩm & nguyên liệu** — filter con: Vũ khí, Trang bị, Ngọc, Nguyên liệu, Tiêu hao, Quest item, Mỹ phẩm, Công thức.
3. **Nhiệm vụ & công việc** — Chính, Phụ, Nghề/thu thập, Guild, Daily, Weekly; nhóm chưa có record thì không hiện tab giả.
4. **NPC & dịch vụ** — nhân vật dịch vụ, người giao nhiệm vụ, dân cư và vai trò; hiển thị map, service ID và hội thoại đã mở.
5. **Trùm** — boss vùng/thế giới, dungeon, raid, chiến dịch; hiển thị một hồ sơ canonical dù xuất hiện ở nhiều nơi.
6. **Quái vật & linh thú** — quái thường, tinh anh và encounter add.
7. **Thú đồng hành, thú cưỡi & cá** — companion, mount và loài cá có hồ sơ LIFE_FISH.
8. **Vũ khí** — kiếm/đao/bút/chùy/cung theo năm môn phái, tier và phẩm chất.
9. **Pháp bảo & trang bị** — 11 slot không phải vũ khí trong bộ 12 slot, set, affix, socket và dòng ẩn.
10. **Bí tịch & kỹ năng** — 30 active skill + 40 passive node có ID; filter lớp, vai trò, nhánh, effect và cấp mở.
11. **Bản đồ & bí cảnh** — 9 map thế giới, siege map variant, DG-01…04, RD-01…02, Tháp Lạc Ấn và tầng con, cùng hoạt động PvP có registry record.
Counter mặc định hiển thị `đã mở / tổng record có thể xem` nếu category có discovery; ví dụ `8/75`. Có nút `Chỉ hiện đã khám phá`, `Đánh dấu mới` và `Đặt lại bộ lọc`. Sidebar giữ scroll position khi mở inspector hoặc deep-link quay lại.

### 7. Search, filter và kết quả

Search full-width tối thiểu cao 48px: icon kính lúp, placeholder `Tìm tên, công dụng, ID hoặc khu vực…`, nút xóa và phím tắt `/` trên PC. Gõ từ ký tự đầu, debounce 120ms; mở đầu bằng local index/cached manifest, server bổ sung metadata mới khi kết nối.

Tìm trên tên hiện tại, alias/localized name, ID khi bật chế độ QA, mô tả đã khám phá, tag, slot, class, element, set, map, source, recipe, NPC và loại hoạt động. Chuẩn hóa Unicode tiếng Việt không dấu để tìm `Co Thu` ra `Cổ Thụ`; hỗ trợ chuỗi con, token đảo thứ tự và typo tối đa một ký tự khi query dài ≥5. Không index hidden lore/unknown data vào suggestion.

Filter bar thay đổi theo category, tối đa 2 hàng trước khi gom vào `Bộ lọc`. Facet chuẩn:

| Category | Facet |
|---|---|
| Item | subtype, slot, tier/cấp, phẩm chất, lớp, element, set, binding, tradeable, đã sở hữu, công thức đã học/có thể chế tác |
| Quest | chương, map, trạng thái (chưa nhận/đang làm/hoàn tất), loại, class-specific, có reward đã khám phá |
| Boss/monster | khu vực, level band, encounter type, đã gặp/đã hạ, loot đã khám phá, nguyên tố/role |
| Skill | class, loại kỹ năng, resource, level unlock, đã học, preset đang trang bị |
| Map/activity | region, level range, solo/party/raid, unlocked, đang mở, first clear |

Sort mặc định: relevance (exact name > ID > alias > tag > description), sau đó tên địa phương. Thêm sort tên A–Z, cấp/tier, phẩm chất, vùng/chương, mới mở, chưa ghi chép. Bộ lọc có chip removable và `Xóa tất cả`; kết quả count cập nhật theo query ngay, empty state cho gợi ý sửa từ khóa hoặc bỏ filter.

### 8. Grid kết quả và card

Grid 3–5 cột desktop tùy chiều rộng cột giữa, 2 cột mobile ngang, 1 cột nếu item row portrait. Card desktop 132–164px rộng × 150px cao; touch target ít nhất 48×48dp. Virtualize list khi >80 kết quả; giữ scroll anchoring khi thêm metadata, không tự nhảy lên đầu khi chỉ count đổi.

Card chung gồm icon/portrait pixel-art 32–64px source (integer-scale khi render), name tối đa 2 dòng bitmap font, category/type tag, grade/tier hoặc level band, badge discovery/quest state. Border rarity theo shape và token game. Các variant:

- Gear: icon/giáp, `Vũ khí · T5`, phẩm chất, class glyph, socket count; nếu record là variant hiện rõ `Linh`/`Huyền` thay vì trộn với master.
- Nguyên liệu/consumable: `Nguyên liệu · Chế tác`, stack type hoặc effect ngắn; không hiện giá chưa biết.
- Quest: icon chương, status, map start và objective hiện tại nếu đang làm.
- Boss: portrait/mini silhouette, loại encounter, khu vực, recommended level/party khi đã biết.
- Mob: portrait, role tag (đánh gần/xa, control, elite), vùng sống.
- Skill: icon, môn phái, role, level unlock, cooldown ngắn nếu đã học.
- Map/activity: thumbnail environment, cấp đề nghị, party size, trạng thái khóa/clear.

Rê/giữ focus mở tooltip 0,45s; tap/click chọn và bind inspector; double-click không kích hoạt giao dịch. Click card đã chọn lần nữa không đổi scroll. Skeleton tải icon giữ đúng silhouette vùng, không nhấp nháy; nếu thiếu art hiển thị placeholder theo element/category.

### 9. Inspector bên phải

Inspector có vùng đầu ổn định: icon 96px, tên bản địa, breadcrumb category, grade/status badges, nút `Ghim` và `Sao chép ID` (ID chỉ khi QA mode). Phần nội dung cuộn độc lập, dùng cùng thứ tự để người chơi hình thành thói quen:

1. **Tổng quan:** mô tả chức năng/lore 1–3 đoạn; label nội dung gameplay/lore riêng; chiều dài desktop tối đa 500 ký tự trước `Đọc thêm`.
2. **Thuộc tính:** key-value, đơn vị, class/level/slot/quality; so sánh hiện tại → record này nếu có item instance tương ứng; không trộn số base và instance.
3. **Cách dùng:** hành động, duration/cooldown, ràng buộc, hiệu ứng PvE/PvP, cảnh báo mất item, requirement mở khóa.
4. **Nguồn/Cách sở hữu:** node, quái/boss, quest, dungeon/raid, recipe, NPC, lịch xuất hiện, weekly cap, tradeability. Drop rate chỉ hiện nếu server có con số công khai; nếu không ghi `Tỷ lệ không công bố`.
5. **Liên quan:** recipe tạo/tiêu, boss rơi, quest mở, map chứa, skill tương khắc, set có cùng mảnh. Tối đa 6 chip ban đầu và `Xem tất cả`.

Inspector category-specific:

| Loại record | Trường bắt buộc |
|---|---|
| Gear/weapon | base/variant ID, 12-slot slot, tier, quality, class, stat nền, affix range, socket, set bonus 2/4, hidden effect state, enhancement cap +15, binding, durability |
| Material/consumable | stack limit, binding/tradeable, effect hoặc recipe use, use restrictions, source list |
| Quest | chapter, start NPC/map, prerequisites, objective đang mở, reward đã biết, replay/reset, quest status; ẩn bước cốt truyện chưa tới |
| Boss | level/party range, region/encounter, phase summary đã khám phá, mechanic/telegraph hint, weekly schedule, loot known, contribution rule |
| Monster | level band, role/behavior, element/defense/resistance nếu canonical data có, telegraph, habitat, loot known |
| Skill | class/resource, level unlock, cooldown/cost, targeting/range, effect PvE/PvP, upgrade rule, VFX preview tĩnh/loop nhẹ, trạng thái học/trang bị |
| Map/activity | level band, entrances/teleports, key landmarks, NPC/encounter, time window, group size, unlock prerequisite, map preview và discovered fog |

Không hiển thị field rỗng/giá trị 0 như dữ liệu có ý nghĩa. Dấu `—` đi cùng tooltip `Chưa có dữ liệu thiết kế`; không suy ra stat/loot. Mọi số có unit, tooltip giải thích nếu là base stat, scaling, chance hay giới hạn tuần.

### 10. Actions và deep-link

Footer sticky tối đa hai CTA, quyết định theo loại record và quyền:

| Record | CTA chính | Hành vi |
|---|---|---|
| Item đang có trong túi | `Xem trong túi` | đóng/thu gọn compendium theo lựa chọn, mở bag và focus item instance; không auto-equip |
| Công thức đã học | `Mở lò rèn` | chuyển sang Forge với recipe được chọn; tiêu hao chỉ sau confirm trong Forge |
| Quest đang nhận | `Theo dõi` / `Định vị` | đặt pin quest, mở map và marker nếu vùng đã mở |
| Quest chưa mở | `Điều kiện mở` | hiển thị prereq đã được khám phá, không nhận quest thay người chơi |
| Boss/quái | `Đánh dấu khu vực` | ghim nguồn/mob lên tracker; không teleport tự động; map đóng khi bấm nút điều hướng thứ hai |
| Skill | `Mở kỹ năng` | mở panel skill tại skill này; equip/reset phải confirm trong panel skill |
| Map/bí cảnh | `Mở bản đồ` / `Vào hàng chờ` | map chỉ khi discovered; queue chỉ khi unlock đủ và action do người chơi bấm |
| Mục chưa khả dụng | CTA disabled + lý do | lý do cụ thể: chưa mở vùng, chưa học recipe, level thấp, offline… |

Secondary CTA là `Ghim vào sổ` hoặc `So sánh`; không có mua/nhận/rèn/dismantle trực tiếp. Back từ deep-link trả đúng panel trước, filter và scroll position trước khi mở compendium.

### 11. Data contract và indexing

Mỗi record có canonical key và source references; nội dung chia trường hiển thị, unlock và data quyền riêng tư. Không dùng tên hiển thị làm khóa. Đề xuất manifest chung:

```json
{
  "entryId": "ITEM:EQ-MK-WEAPON-T5:LINH",
  "entityType": "item",
  "canonicalId": "EQ-MK-WEAPON-T5",
  "variantId": "EQ-MK-WEAPON-T5:LINH",
  "category": "weapon",
  "subcategory": "class_weapon",
  "displayNameKey": "item.eq_mk_weapon_t5.name",
  "iconKey": "items/eq_mk_weapon_t5",
  "rarity": "LINH",
  "levelBand": "T5",
  "classIds": ["CLASS_MINH_KIEM"],
  "summaryKey": "item.eq_mk_weapon_t5.summary",
  "detailKeys": ["item.eq_mk_weapon_t5.use"],
  "searchTags": ["kiếm", "vũ khí", "Sơn Thệ", "Minh Kiếm"],
  "relatedIds": ["SET-T5-MK"],
  "sourceRefs": [{"type":"map","id":"MAP_TRAN_SON","unlock":"quest:C4-05"}],
  "discoveryRule": "loot_or_inspect",
  "spoilerLevel": 0,
  "contentVersion": 1
}
```

`entryId` phải duy nhất; item variant giữ `canonicalId` trỏ về master. Thêm `localizedName`, `searchAliases`, `attributes[]` (key/value/unit/source), `usage[]`, `acquisition[]`, `unlockState`, `discoveryState`, `recordedAt`, `sourceMapId`, `sourceEncounterId`, `schedule`, `quota`, `tradeability`, `lastModified` cho domain tương ứng. Chỉ để field được phép trong index công khai; account state (sở hữu, quest progress, seen) là overlay riêng theo nhân vật.

Client nhận `catalogManifestVersion`, manifest nhỏ theo category, paging cursor, local search index và player discovery delta. Static art/text cache theo version; trạng thái sở hữu/quest không ghi vào cache dùng chung account khác. Server lọc dữ liệu spoiler trước khi trả về, không gửi tất cả lore rồi dựa vào UI để giấu.

### 12. Luồng đồng bộ, trạng thái và lỗi

1. Mở compendium: render category/cached manifest trong 100ms mục tiêu; load entry deep-link trước rồi fetch category page.
2. Đồng bộ version: compare ETag/contentVersion; chỉ tải domain đã đổi và player discovery delta. Ghi timestamp khi payload hợp lệ đã commit.
3. Search: client lọc trong page/cache; request thêm page khi scroll gần đáy hoặc từ khóa dài cần server search. Query request chứa language, category, filters, spoiler policy, cursor và manifestVersion.
4. Chọn item: inspector nhận `entryId` + player overlay state; đổi entry không roundtrip nếu đủ cache.
5. Mất mạng: đọc record cached đã mở; banner báo giờ dữ liệu; filter/sort/search cục bộ vẫn dùng được; CTA cần live state disable và giải thích.
6. Version mismatch/record đã gỡ: giữ tên và icon cache nếu đã khám phá, hiện `Nội dung đã cập nhật` và nút tải lại; không vứt người chơi khỏi tab đang xem.

Lỗi: `ManifestUnavailable` giữ cache; `EntryRemoved` dùng tombstone nếu entry từng được sở hữu/hoàn thành; `DiscoveryDenied` trả về silhouette/rumor; `CursorExpired` fetch page đầu nhưng giữ query; `StalePlayerState` refresh overlay, không reset filters. Không hiện stack trace/ID backend cho người chơi.

### 13. Tương tác, input và accessibility

- Mouse/touch: tap chọn; swipe cuộn trong pane đang chạm; pinch không phóng toàn overlay. Long-press card mở context menu (Ghim/So sánh/Sao chép ID trong QA).
- Keyboard: `/` focus search; Esc đóng filter/popup trước rồi modal; Enter chọn card; Tab/Shift+Tab theo thứ tự có ý nghĩa; mũi tên di chuyển trong grid.
- Controller: d-pad đổi card; trigger đổi category/page; A chọn; B quay lại/đóng; focus không mất khi count realtime đổi.
- Font body 15–17px desktop, 14–16sp mobile; minimum readable 12sp cho metadata, text scale tới 150%; card tăng chiều cao theo text.
- Contrast tối thiểu 4.5:1 cho chữ nhỏ. Trạng thái rarity, locked, discovered có shape/icon/label cùng màu. Colorblind không dựa riêng vào năm màu nguyên tố.
- Screen reader đọc: tên, loại, rarity, state, category position, nút/disabled reason; icon thuần trang trí bị ẩn khỏi accessibility tree.
- Reduced motion: dừng sprite shimmer/aura animation, giữ highlight palette tĩnh; VFX preview skill dừng nếu tab nền; không có animation vô tận.

### 14. Hiệu suất và an toàn nội dung

- Search index n-gram/token theo locale; category virtualized khi >80 card; inspector chỉ nạp ảnh lớn của entry đang chọn.
- Icon 64/96px từ atlas; portrait detail dùng 256px; map thumbnail 320px; cache LRU tối đa 40MB trên mobile, clear theo version.
- Không autoplay video hoặc âm thanh. Skill preview là loop 3–5s muted, chỉ chạy khi người dùng nhấn Play; telegraph dùng clip ngắn và caption.
- Text/mô tả từ content pipeline phải được sanitize; link ngoài không mở trong game overlay. Ghi analytics chỉ gồm query category không nhạy cảm, click entry và action; không ghi chuỗi chat/tên tìm kiếm nhạy cảm.
- Không cho compendium truy cập dữ liệu private của inventory, guild vault, thư, trade escrow hoặc quest reward chưa unlock; chỉ player service trả về `owned=true/false` và record đã được phép.

### 15. Acceptance criteria bàn giao

- Mockup desktop 1920×1080, 1366×768; mobile ngang 1280×720 và mobile dọc; có Category/List/Details transitions.
- Counter đúng manifest snapshot: 2.533 unique record khởi điểm, category con không cộng lặp; dữ liệu thêm mới cập nhật mà không đổi code UI.
- Search `Co Thu`, `Cổ Thụ`, ID/item use, class/map/recipe đều ra đúng record; thứ tự relevance đúng và query được xóa bằng một thao tác.
- Gear variant hiển thị đúng 5 phẩm chất game, 12 slot, set/affix/socket; không nhầm master template với item instance.
- Quest/boss spoiler khóa theo discovery; search suggestion và related entries cũng không leak nội dung ẩn.
- Source guide nêu chính xác map/encounter/recipe/NPC theo content registry; không bịa drop rate hoặc lịch chưa định nghĩa.
- Deep-link từ HUD, map, quest, inventory và Forge mở đúng entry; Back quay đúng scroll/filter; CTA không tạo giao dịch.
- Test offline cache, update version, empty state, no art, long localized labels, text scale, controller, keyboard, touch, screen reader, reduced motion và colorblind patterns.

### 16. Tài liệu liên quan

- Item/quality/set/affix: `Item_Catalog_and_Set_Bible_vi.md`, `Item_Master_Catalog_vi.csv`, `Item_Rarity_Variant_Catalog_vi.csv`.
- Boss/bestiary/NPC: `Art_Entity_Weather_UI_Visual_Bible_vi.md`, `Activities_Economy_PvP_Production_Spec_vi.md`.
- Vị trí theo map và nguồn/đầu ra nghề: `World_Spawn_Gathering_Manifest_Spec_vi.md`, `World_Spawn_Gathering_Manifest_vi.csv`.
- Quest/story: `Quest_and_Narrative_Production_Spec_vi.md`, `Content_Bible_Ngu_Mach_Huyen_An_vi.md`.
- Map/dungeon/raid: `Map_Production_Atlas_vi.md`, `Activities_Economy_PvP_Production_Spec_vi.md`.
- Skill effect/preview: `Combat_Skills_VFX_Animation_Spec_vi.md`.
- Navigation/HUD: `UI_UX_Spec_vi.md`, `Gameplay_HUD_Overlay_Spec_vi.md`.




