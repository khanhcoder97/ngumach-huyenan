# Rà soát nội dung và đặc tả game — 2026-10-30

## Kết luận

**Còn thiếu; chưa đủ để giao một gói tài liệu rồi tự động xây xong toàn game mà không cần thiết kế chi tiết, sản xuất nội dung và nghiệm thu tiếp.** Phạm vi hệ thống đã rộng; không cần mở thêm tính năng lớn để gọi là MMORPG. Cần chuyển những thiết kế đã có thành dữ liệu thực thi, giải quyết các precision còn hở, tích hợp bản chơi online và kiểm chứng từng hành trình.

Baseline main: `abae06144a4c058e5b02600b9a9f87f5f7b4b3ea`. Inventory toàn bộ58Markdown/8.242dòng và12CSV trực tiếp trong production ở baseline, đối chiếu schemas/examples, narrative, world migration, audio và bàn giao đang mở. Đây là kiểm kê toàn thư mục và rà semantic có trọng tâm; **không** chứng nhận đã biên tập từng dòng item, playtest từng quest hoặc xem từng pixel của mọi asset. Bằng chứng máy đọc: [Content_Readiness_Inventory_20261030.json](../../Implementation/Reports/Content_Readiness_Inventory_20261030.json).

## 1. Nội dung đã có — tránh giao viết lại

| Miền | Nguồn và lượng nội dung hiện có | Giới hạn cần giữ rõ |
|---|---|---|
| Cốt truyện/khám phá | Quest/Narrative Specs, Narrative_Depth;76quest =36chính+40phụ | Có thiết kế và beats; chưa phải76quest server chạy được |
| Lời thoại |230dòng đã line-edit,229prompt riêng;17vai nói gồm macro thầy theo lớp | Không còn VI_BASELINE trong bảng; chưa là hội thoại mọi trạng thái cho83NPC, chưa VO/font QA |
| Cinema |20scene/63shot/378giây prompt có trigger, reveal, skip, fallback | Prompt và binding âm thanh không phải video final, engine playback hoặc device proof |
| Lớp/chiêu |5lớp,30active,40passive,30thẻ art/VFX; guard DEC-022 | Đã có số/công thức ở Rules và DesignBaselines; chưa export đủ30SkillDefinition hoặc balance đủ5lớp |
| Trang bị | Sau sửa:556master=420gear+136fixed;2.236rarity rows=2.100gear+136fixed | Là catalog thiết kế; instance roll, stat aggregation, loader/schema và migration vẫn phải làm |
| NPC/thế giới |83NPC canonical;349placements trên46map |104NPC placements không phải104NPC khác nhau;29boss placements không phải29boss canonical |
| Quái/boss |21base mob/add,9elite profiles,12boss canonical; stat/archetype formula và một số timeline | Cần resolved records, encounter graph, geometry/nav và reward policy từng encounter |
| Hoạt động/xã hội | Dungeon/raid/tháp/PvP/bang/chợ/mail/trade/nghề/farm/fishing/pet/mount đã có spec | Đừng ghi “chưa thiết kế bang hội” khi thực tế chưa code; chưa có gameplay evidence toàn bộ |
| Âm thanh |195cue/541runtime clip ứng viên,9nhạc/13ambience,46map bindings |195không phải195nhạc; binding/shared cue không phải âm riêng cho từng NPC/quái; chưa nghe duyệt/device QA/VO |
| UI/pixel/camera | HUD vòng cung6skill, settings/forge/bách khoa/buff/túi/bang, top-down8hướng, STANDARD/HUB_WIDE | Concept/HTML spec không phải UI Unity đã nối đủ state server; HUB_WIDE và Thăng Long v2 còn cần integration |
| Backend/vận hành | Contracts, Rules, Online Persistence, QA gates đã viết auth/ledger/recovery/release | Đó là yêu cầu; in-memory DEV và CI không chứng minh PostgreSQL/auth/backup thật |

Số19record địa điểm/hoạt động trong bách khoa không trực tiếp mâu thuẫn46mapID: các tầng tháp được gộp dưới record cha, thêm activity entries. Counter phải tính từ registry theo policy, không ép mọi bảng bằng nhau.

## 2. Những lỗi đã sửa trong đợt này

| ID | Phát hiện tái hiện được | Sửa và phạm vi |
|---|---|---|
| AUD-01 | TOOL-ROD-01 có trong master nhưng không trong rarity catalog; master thực tế556, văn bản555 | Copy nguyên dòng fixed từ master, không tạo ID/stat mới; rarity2235→2236; cập nhật Item Bible/Index/counter bách khoa2532→2533 |
| AUD-02 | Túi100ô/4×25 nhưng Character Spec ghi6×5ô/trang; UI_UX ghi5×5 | Đồng bộ5×5, giữ100slot; không tăng sức chứa hoặc đổi save |
| AUD-03 | Túi cũ cho quest reward vào thư mặc định, Addendum yêu cầu inventory_full/READY | Đồng bộ câu UI theo transaction rule đã có; không tạo thêm mail grant |
| AUD-04 | Index còn215lời baseline và63cue MISSING dễ bị hiểu là sản phẩm hiện tại | Đánh dấu trạng thái lịch sử, trỏ230lời hoàn tất lượt viết và195cue/541clip ứng viên |
| AUD-05 | Parser có thể cộng armor/weapon_power và primary cùng giá trị hai lần | DEC-023 chốt alias, conflict fail, oracle sword38/hatArmor14; chưa sửa loader của Qoder |
| AUD-06 | Chưa rõ currentHP/MP khi level/equip/respec đổi maximum | DEC-023 chốt giữ current tuyệt đối rồi clamp, không tự heal/revive; migration refill cũ vẫn chỉ một lần |
| AUD-07 | Auto-potion có nút Undo trong khi heal có thể đã commit | Đổi thành tắt auto cho lần kế tiếp, không hoàn item/HP sau commit |
| AUD-08 | “Tiêu vé sau spawn” và “tại ACTIVE” cần ranh giới nguyên tử | Precision yêu cầu prepare→activation transaction/outbox, không debit từng người rồi bắt đầu trận một phần |

Chi tiết và oracle ở [Runtime_State_and_Catalog_Precision_vi.md](Runtime_State_and_Catalog_Precision_vi.md), DEC-023. Các thay đổi này là tài liệu/catalog, không tự thay code/runtime đã bàn giao.

## 3. Backlog còn thiếu — phân đúng loại và điều kiện đóng

`PRECISION` = còn thiếu quyết định/field rõ; `DATA` = đã có nguồn nhưng chưa thành record executable; `BUILD` = còn implementation/integration; `EVIDENCE` = cần chạy và lưu bằng chứng. Một hàng có thể có nhiều loại. Owner là ranh giới trách nhiệm hiện có, không phải xác nhận agent đã nhận việc mới trong lượt audit này.

| Ưu tiên / ID | Miền / loại | Phần còn phải làm | Owner / bằng chứng đóng |
|---|---|---|---|
| P0 / GAP-01 | Stat/progression DATA+BUILD |5class records, rank/loadouts, level/XP/points; resolved starter gear, alias/rounding, migration fixture | Qoder; export/loader tests và reward→level→equip/relog không double stat/refill |
| P0 / GAP-02 | Combat DATA+BUILD |30active+40passive runtime; basic/dodge/status, server tick impacts, hit/death/resource; guard đã có precision | Qoder; deterministic timeline/shape/range/LOS tests, replay không lặp hit/death, PC/mobile event presentation |
| P0 / GAP-03 | Boss PRECISION+DATA |Ngoài subset: phaseGuard, interruptible, attack descriptors/chooser, resolved stats/loot, arena/safe-pad geometry từng boss | Qoder+Codex+Muse; phase/wipe/CC/reconnect và nav telegraph từng encounter; không nhân bản Mãng Cốt cho12boss |
| P0 / GAP-04 | Quest DATA+BUILD |76objective graphs với record targets/count/floor/share/checkpoints/rewards; branch flags và macro5thầy được compile | Qoder; campaign graph/ref checks và chơi các nhánh/fail/retry/turn-in; dialogue coverage không thay objective coverage |
| P0 / GAP-05 | World PRECISION+DATA |46topologies;349placements đều TOPDOWN_REVIEW_REQUIRED;129NEW_PROPOSED là trạng thái thiết kế khác, không phải số đã review | Muse layout, Qoder nav/data, Codex review; migration/source hash, route/nav/collision/portal/floor bằng scene thật |
| P0 / GAP-06 | Bến Mưa PRECISION+EVIDENCE |Fisher(112,0) cách spawn(116,0)4WU trái safe-NPC18WU; arena/đường thoát/bệ an toàn chưa được nav sign-off | Candidate dời/phân vùng/phasing có original→new và review; không tự đổi349XY hoặc gắn REVIEWED |
| P0 / GAP-07 | Online BUILD+EVIDENCE |Nối move/quest/collect/turn-in/combat v2/events/reconnect vào client; không hiển thị damage giả từ accept | Qoder server, Codex client; hai client cùng tuyến có logs/receipts/state và exact SHAs |
| P0 / GAP-08 | Durable state BUILD+EVIDENCE |Auth/account ownership, DB transactions/migrations/outbox, restart và zone transition | Qoder; crash/retry/concurrent/restart/restore không mất/nhân item,quest,tiền; in-memory không đóng hàng này |
| P1 / GAP-09 | Gear/economy PRECISION+DATA |Đồng quái theo band; phí/scope giám định; tài nguyên% khi resource nguyên; phân phối socket/hidden; source precedence | Codex design+Qoder data; bảng số/version, oracle RNG/cap và báo lỗi field thiếu; giữ grant chưa đủ dữ liệu OFF |
| P1 / GAP-10 | Gear/economy BUILD+EVIDENCE |Item instance/affix/hidden/set/upgrade/salvage/repair/gem,100slot/bank,market/trade/mail đầy đủ | Qoder+CodexUI; transaction/double-spend/fullbag/retry/concurrent và ledger evidence; nhiều phí nâng cấp/tinh luyện đã có, không viết lại |
| P1 / GAP-11 | Balance EVIDENCE |TTK/sống sót5lớp,XP/cấp,skill/resource builds,rare drops,craft costs,faucet/sink,party scaling | Codex design+Qoder simulation; report ruleset/input/seed/percentiles, sau đó playtest; không dùng fixture browser làm balance final |
| P1 / GAP-12 | Social/PvP BUILD+EVIDENCE |Party/guild permissions/treasury/chat,Long Môn,3v3,BG10,siege,disconnect/tie/void,quota | Qoder+CodexUI; đủ roster concurrent,không tự approve quỹ,server result/reward dedupe,network tests |
| P1 / GAP-13 | Activities/life sim DATA+BUILD |4dungeon,2raid×3encounter,tháp30tầng,6worldboss,nghề/farm/fishing/pet/mount runtime | Qoder; spawn/phase/entry/caps/reset/checkpoints,party participation; CSV có11crop/fish không chứng minh minigame đã chạy |
| P1 / GAP-14 | Narrative UX DATA+BUILD |NPC/service greeting/error/postquest matrix,ambient reactions/reveal gates,journal/clue/puzzle interaction,choice persistence | Codex narrative+Qoder triggers; map mỗi luồng tới textKey/flag/reward source; không bắt mọi NPC có giọng riêng hoặc thêm quest ngoài scope |
| P1 / GAP-15 | Art DATA+EVIDENCE |5class/gear variants,NPC/mob/boss/pet/environment/UI/icons/font,30VFX/weather; native source/license/manifest | Muse; art approval→engine import→integrated→device,không lấy concept collage/PNG header làm sheet/map pass |
| P1 / GAP-16 | Cinema BUILD+EVIDENCE |20scene thành storyboard/animatic/video/subtitles/stems; skip/fallback/replay trong game | Muse+Codex; không pause shared world/auto reward; clip encode thật,device/memory/seek/failed load evidence |
| P1 / GAP-17 | Audio BUILD+EVIDENCE |Nghe duyệt195cue,loops/mix,semantic bindings/dedupe/lifetime với event thật,low volume/device; spoken VO scope riêng | Codex+Muse picture lock; waveform/hash QA không thay listening/LUFS/true peak hoặc Unity playback |
| P1 / GAP-18 | UI/input BUILD+EVIDENCE |Toàn panel state/revision/error/offline/focus/modal/safe area,HUD arc,localization/font,accessibility | Codex; PC/mobile touch/keyboard/fullbag/long text/reducedFX; giữ telegraph khi mute/LowFX |
| P1 / GAP-19 | Camera/capital BUILD+EVIDENCE |HUB_WIDE,stream/culling,Thăng Long12phường target extent; safe hub→combat camera transition | Codex+Muse; native pixel integer scale,wide view và đo performance,nav/portal migration;2048×1536WU vẫn design-only |
| P1 / GAP-20 | Asset pipeline BUILD+EVIDENCE |Sửa PNG/.meta/root confinement/preview/browser playback; candidate compiler+map adapter | OpenCode; tái kiểm đúng SHA với fixture hỏng/hostilepaths/clean clone và browser thật; CI xanh không xóa9finding lịch sử |
| P1 / GAP-21 | Platform/ops BUILD+EVIDENCE |Unity build/import,patch/bundle compatibility,load/soak/recovery/anti-cheat/rate limits/monitoring/moderation | Qoder+Codex+MuseVM; exact artifact/log/device30phút,network40/100/180ms và restore drill; không chỉ headless compile |
| P2 / GAP-22 | Product decisions |Hosting/CCU/budget,thị trường/privacy/retention,title/licenses,store/payment/support/VO/locales | Chủ sản phẩm trước release; giữ pending có người chịu trách nhiệm, không chặn prototype hoặc tự tạo chữ ký |

## 4. Đối chiếu các bàn giao đang mở

Snapshot GitHub trong lượt audit, không phải chứng nhận code review hoặc CI trên mọi nhánh:

- Qoder đã thêm PR[#73](https://github.com/khanhcoder97/ngumach-huyenan/pull/73), head `d1ce792576ab091802ee200b0e324fc4c6071f01`, xếp trên53→54→57→60→65→66→68→71. PR73 có gated v2 endpoints/event polling và **accept-only**; chính mô tả bàn giao ghi chưa damage/hit/death/loot. Không tiếp tục dùng báo cáo cũ “chưa có endpoint proposal” để đánh giá nhánh này; cũng không coi endpoint accepted là đánh trúng. Stack chưa merge main tại snapshot.
- Client PR[#51](https://github.com/khanhcoder97/ngumach-huyenan/pull/51), head `73dab87caf4bb0c7afe0737866b94a3584ab5adb`, còn draft; chưa đủ client v2/collect/turn-in/Unity/device acceptance. Các test client .NET đã có chỉ xác nhận phạm vi test của chúng.
- OpenCode PR43/61/62/67/69 vẫn ở heads đã nêu trong review trước. Producer review PR61/62 có1pass/9fail ở các SHA lịch sử; cần head sửa mới và tái kiểm, không dùng số test tự báo để thay finding. Chưa có bằng chứng đã sửa trong snapshot này.
- Muse PR[#22](https://github.com/khanhcoder97/ngumach-huyenan/pull/22) là animation candidate chưa merge; map handoff Bến Mưa PR72 đã merge là **brief+reference**, không phải tilemap Muse đã hoàn thành. Không có acknowledgement mới được xác minh trong lượt này.
- Main có bản chơi browser Bến Mưa một người với5quest/boss/save local. v1.1 target-lock/hold attack/save recovery ở branch `codex/ben-mua-playability-20261030`, head `280323421e571eaaa70fffc1caf47b5f2d14804c` đã thấy trên remote; chưa có PR merge tại snapshot. Hai bản đều không thay Unity/MMO authority, không đồng bộ save vào server.

## 5. Gói việc nên hoàn tất theo thứ tự

1. **Chốt Bến Mưa online:** review stack server theo thứ tự, tick damage/quest/reward/DB thực, client v2 và nav candidate đã duyệt. Cần video hai client create→P00-01..05→boss→reward→equip→portal→relog; mất mạng ở turn-in không phát hai lần. Đây là mốc ưu tiên hơn mở thêm map/hệ thống.
2. **Đủ dữ liệu toàn game:** export có provenance/units cho5lớp,30active,40passive,76quest,items/rewards và46map; input thiếu field fail có ID/field. Chốt GAP-09 bằng bảng số có mô phỏng, không sửa từ name/icon. Dùng compiler OpenCode và runtime loader Qoder, không tạo một nguồn ID cạnh tranh.
3. **Sản xuất nội dung theo tuyến chơi:** Muse làm blockout/native kit→scene/combat assets→cinema; Codex hoàn NPC/journal/UI/audio integrations theo scene đang chạy. Duyệt sample trước sản xuất hàng loạt nhưng không dừng các phần độc lập của gói.
4. **Khóa alpha rồi release:** toàn campaign/endgame/social/economy có evidence, art/device/network/performance/recovery đủ gates; product owner chốt GAP-22. Không báo “game hoàn chỉnh” vì số lượng tài liệu tăng.

## 6. Kiểm tra đã thực hiện và giới hạn

Đợt audit chạy lại content/contracts/narrative/guard/VFX design validators, dialogue invariants và audio design validator. Các lệnh này kiểm đúng phạm vi được công bố; ví dụ audio baseline còn63cue MISSING là bảng kế hoạch lịch sử, không phủ nhận gói âm thanh195cue đã render. Kết quả kỹ thuật audio pack và các checks bổ sung nằm trong inventory report cập nhật của audit.

Đã kiểm đủ541runtime clip và541master trên đĩa, đường dẫn/byte size/SHA256 khớp manifest,0finding. Không chạy lại được decode validator trong interpreter hiện tại vì thiếu dependency `soundfile`; báo BLOCKED_LOCAL_DEPENDENCY, không báo PASS cho phần giải mã. Technical QA trước đây vẫn là bằng chứng lịch sử theo SHA của gói, chưa là nghe duyệt hoặc Unity evidence. Bản chơi main qua68engine assertions và4HTTP tests; không suy thành multiplayer test.

Kiểm cross-catalog sau sửa: fixed IDs/master row phải hiện đủ trong rarity, mỗi ID duy nhất,420gear templates và2.100variants vẫn giữ nguyên. Manifest hash khớp migration snapshot,349originalXY không đổi; không phát sinh REVIEWED giả. Các oracle DEC-023 là yêu cầu test cho implementation, không phải test server đã chạy.

Tái kiểm fixed catalog từ root worktree bằng Python tiêu chuẩn (không sửa dữ liệu):

```python
import csv
from pathlib import Path
p = Path('docs/production')
def load(name):
    with (p / name).open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    result = {r['item_id']: r for r in rows}
    assert len(result) == len(rows), 'duplicate item ID'
    return result
master = load('Item_Master_Catalog_vi.csv')
variants = load('Item_Rarity_Variant_Catalog_vi.csv')
fixed = {i: r for i, r in master.items() if not i.startswith('EQ-')}
assert all(variants.get(i) == r for i, r in fixed.items()), 'fixed item drift'
print(len(master), len(variants), len(fixed))  # 556, 2236, 136 at this snapshot
```

Không chạy Unity, không nghiệm thu thiết bị hay load MMO trong lượt này. Không đưa tỷ lệ “hoàn thành chung” khi chưa có denominator/evidence cùng cấp. Kết luận cho phép tiếp tục phát triển theo gates, **chưa CONTENT_LOCK/P1_ONLINE/SHIP**.
