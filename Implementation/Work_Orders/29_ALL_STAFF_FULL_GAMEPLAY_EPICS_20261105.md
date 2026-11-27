# Gói 29 — phát triển liên tục tới bản MMORPG chơi được
Ngày 05/11/2026. Nguồn yêu cầu: chủ dự án giao các gói công việc lớn, sau đó Codex tiếp tục hình ảnh, VFX và dựng game.

## Quy tắc thực thi
Nhận toàn bộ chuỗi của mình. Push checkpoint có mã nguồn hoặc media thật, rồi làm tiếp phần độc lập; không dừng sau ACK, kế hoạch hay một bản sửa. Codex review và merge. Không bật production hoặc tự tuyên bố các hạng mục chưa kiểm là hoàn tất.

Work 28 và CAM-TOPDOWN-WIDE-20261105 tiếp tục có hiệu lực. Codex sở hữu toàn bộ đồ họa gameplay và Godot: sprite, animation, map, UI/UX, VFX, camera, input và tích hợp. Muse chỉ video, cinematic và âm thanh. Antigravity vẫn bị thu hồi.

## Baseline đã kiểm tra và quyết định mới
- Integration: 8bab575feb0bee941f86b2fa8d6b3d6d908964ef, PR #115 đã merge, 11 CI check xanh. Bến Mưa có 113 placement, 14 tuyến, camera 64×36 WU. Đây là art staging; chưa là vòng chơi online.
- OpenCode #109: 685b888, CI core/HTTP xanh; agent báo 135 unit test và 55 HTTP assertion. Qoder #106: 77bc3a6, CI xanh; agent báo 480 self-check, 352 smoke và E2E 11/110/33/99. Codex đang kiểm consumer thật; những con số này không chứng nhận mọi hệ thống đã hoàn tất.
- Remote #98 vẫn ở 5371a46 và thiếu project build được. Muse mới có inventory/câu hỏi, chưa giao media final.
- DEC-DEATH-RETURN-20261105 đã trả lời đủ sáu câu Qoder. Đọc death_return_decisions_20261105.json và DeathReturn_Approved_Decisions_20261105_vi.md; không giữ approval cũ làm blocker.
- DEC-MEDIA-P0-20261105 đã trả lời năm câu Muse; pack canonical được đồng bộ. Nguồn hiện tại có 20 scene, 63 shot, 378 giây; P0 gồm 12 shot/72 giây.
- Sửa templateId v1 để nhận underscore là correction theo ID catalog, không mở enum năm slot v1. V2 có 12 slot riêng. Quyết định XP floor, loot private opt-in và encounter của work 26 giữ nguyên.
- Feature chưa đủ vẫn OFF trong cấu hình phát hành. Demo/private alpha bật bằng profile hoặc biến môi trường riêng; runner phải kiểm đúng server và dừng đúng PID.

## OpenCode — OPC-16 đến OPC-18: toàn bộ tầng client portable
Tiếp nhánh và worktree PR #109 của mình. Không sửa Godot/art/server. Đầu mối consumer là Codex.

1. **O1 — hoàn hợp đồng và typed API.** Theo schema thực tại Qoder 77bc3a6: inventory v2 read/equip/unequip, 12 slot, unsupported[], templateId có underscore, current/detail encounter và capability. Giữ v1 nguyên. Death-return theo quyết định mới; parser/model/negative fixture có thể làm ngay, HTTP chỉ gọi sau checkpoint route thật. Không đoán field hoặc mock thành công.
2. **O2 — hoàn vòng đời phiên.** Login, expiry, reconnect, logout/relogin, epoch đơn điệu, stale response, poll cancellation, dispatcher và dispose. Mọi read/mutation phải đi qua composition thật. Giữ cùng key/payload khi mất phản hồi; replay cũ cần fresh read, không ghi đè state mới. Revision conflict, timeout và feature disabled phải thành kết quả UI đọc được.
3. **O3 — chạy toàn tutorial qua HTTP.** Dùng public API từ session tới P00-01..05, clue/rescue/escort/boss/fragment/trial, turn-in và chapter unlock. Thêm equip 12 slot, loot private opt-in, death-return và reconnect. Hai phiên chạy cùng lúc không lẫn owner/credit; retry không cấp tiền/vật phẩm hai lần. Không mutate domain bằng test helper để vượt objective.
4. **O4 — bộ read model/presenter cho toàn UI.** HUD, target, skill/cooldown, quest tracker, dialogue choice, journal, inventory, equipment, tooltip, map, portal, settings và system message. Immutable view/commands, localization tiếng Việt, priority modal và focus/hold-release. Codex dựng widget; OpenCode giao API/data binding và test trạng thái.
5. **O5 — dịch vụ MMORPG mở rộng.** Tiếp shop/buy/sell/storage, forge/upgrade/craft/gather, party/guild/social/mail/trade, codex/cosmetic/buff và activity theo contract đã công bố. Route chưa có: chuẩn bị presenter/policy/catalog và trả unsupported rõ; tiếp module khác. Không tự quảng cáo server enabled hoặc tạo backend giả. Pagination/search/selection không được tự grant.
6. **O6 — binding animation/VFX.** Stable cast/life/revision/cursor; cùng cast được poll nhiều lần không phát hiệu ứng lại. Cancel, death, logout và map change dọn đúng VFX. Timeline lấy server tick và geometry thật; cover rejected cast, late impact, reduced motion. Giao sample factory, public interface và payload capture cho Codex.
7. **O7 — giao gói dùng được trên máy yếu.** net8 library, tracked project/lock/license, dependency closure tái tạo được. Runner Windows có SDK8 client/SDK10 server, private port, health identity, timeout và cleanup theo PID mình tạo. Không yêu cầu Unity.
8. **O8 — regression và bàn giao liên tục.** Unit/HTTP test có ý nghĩa, assertion >0, TRX/raw log/CI URL/clean checkout. Giao O1/O2 sớm rồi tiếp O3–O8. Mỗi checkpoint nêu exact SHA, dependency Qoder, API thay đổi và leg chưa chạy; console test không là native Godot PASS.

## Qoder local — QOD-22 đến QOD-24: toàn backbone gameplay/server
Tiếp PR #106 và worktree QOD21. Không chờ Muse hoặc scene client để làm các module server độc lập.

1. **Q1 — player life và death-return.** Mọi đường damage có internal death record deterministic trong cùng lock/revision. Resurrection nâng lifeVersion đúng một lần; không thêm CombatEventV2 type. Freeze schema, request rỗng, response, lỗi và negative examples. Route dùng hai gate, anchor [18,0], HP ceil 50%, MP clamp, cooldown 60 tick và clear state thật. Real HTTP: chết, hồi, replay, chết lại, cooldown, reconnect, sai owner/map/body và gate OFF. Gửi #85/#1 checkpoint wire ngay.
2. **Q2 — khép tutorial HTTP.** P00-01..05, boss owner-targetable, phase/cast/guard/wipe/no-latejoin/stable attempt; rescue/escort credit từ nguồn thật. Kill receipt → loot opt-in → fragment → trial → turn-in → C1 AVAILABLE/level 11 gate. Hai owner đồng thời không lẫn instance/credit. Không skip endpoint thiếu, không thay E2E bằng self-check.
3. **Q3 — bundle navigation và map.** Export bounds/floor/axis/PPU/nav version/hash/footbox/portal/trigger cùng path và round-trip test. Giữ 349 placement/canonical quest refs cho tới migration được review. Art staging A2 chưa phải server map. Giao một packet chuyển sang map 2D có source→target cụ thể cho NPC/quái/node/quest/return/portal/arena và toàn đường đi; không x-only projection, không tự dời tọa độ hoặc gắn REVIEWED. Trong lúc Codex review packet, tiếp Q4–Q8.
4. **Q4 — phủ combat và AI.** Năm class/30 skill/passive/status/immunity/range/CD/MP theo source. Mob/boss AI, respawn, group credit và loot đều authoritative; VFX không quyết định hit. Chỗ thiếu numeric: gửi exact source/thiếu gì/options để Codex chốt, tiếp skill đã đủ dữ liệu. Equipment metadata không được báo là effective stats.
5. **Q5 — progression và economy.** XP/level/points, stat aggregation 12 slot, HP/MP clamp, buff stack, consumable, currency, shop/storage, forge/upgrade/craft/gather. Transaction/revision/capacity/receipt chống âm và double grant. DEC-023 hoặc công thức thiếu cần packet nguồn rõ, không tự bịa số và không dừng cả gói.
6. **Q6 — khám phá, chiến dịch và NPC.** Dialogue choice/clue/codex reveal guard, chapter/portal và service availability theo source đã duyệt. Không cấp quest hoặc thưởng qua video callback. Giữ lựa chọn, thứ tự tiết lộ và thoại đã biên tập; không thêm câu placeholder chung chung.
7. **Q7 — social/multiplayer.** Party/guild/chat/mail/trade/weekly arena/rank/reward theo spec, có membership/roster/owner/revision/receipt và giới hạn spam. Bật private alpha từng module có kiểm chứng, không route trả cứng để giả tính năng.
8. **Q8 — vận hành và persistence.** Launcher private Windows/health identity/stop owned PID, regression HTTP, capability/schema packet. Ghép QR adapter sau khi module build/transaction được review. Phải có restart HTTP proof trước khi gọi Health durable; mặc định production OFF.

## Qoder remote — QR-01 tới durable integration
Giữ PR #98/issue #79 cho tới checkpoint build được. Không chuyển sang client/art.

1. **R1 — source clone sạch.** Track library/test/harness csproj, ignore whitelist, dependency/version/lock/license. Sửa workflow dùng job/project thật. Restore/build/test với TRX count >0; gửi exact SHA, git ls-files và CI QR. Đây là checkpoint đầu, không chỉ ACK.
2. **R2 — atomic persistence.** State + expectedRevision + receipt(payloadHash/result) + ledger + outbox trong một DB transaction. Test rollback/replay/conflict/capacity/overflow/cross-owner và serialization ổn định. Không reflection private handle/callback mutate ngoài transaction.
3. **R3 — lease/fencing và hai process.** Dùng process/DB thật cho same-key contention, lease expiry, fencing token và stale-owner commit. Reconnect 120 giây giữ identity. Test clock điều khiển được, không sleep dài.
4. **R4 — crash/recovery/outbox.** Kill ở trước/sau commit, mất response và restart; claim/retry/ack/dedupe, cursor/job state durable. Không nhân tiền/vật phẩm/quest/life record. Simulate batch không thay crash proof.
5. **R5 — migration/backup/restore.** Versioned schema/index migration, SQLite backup API hoặc quiesce WAL; integrity check thật. Corrupt/truncated backup, disk-full/IO-denied và recovery runbook. Không copy DB đang WAL, không placeholder return true.
6. **R6 — domain adapters.** Inventory/quest/XP/currency/loot/equip/craft/mail/trade/guild/rank và player life/death/return receipt. Đồng bộ DTO/ownership/version với Qoder local. Không tự nối Health trước Codex review.
7. **R7 — ops/package.** Minimal dependency, metrics/audit redaction, test DB có nguồn, benchmark ghi cấu hình. Cleanup giới hạn đúng path/PID; không secret hoặc build artifacts trong source.
8. **R8 — bàn giao và tích hợp.** Giao R1 sớm rồi tiếp phần độc lập R2–R7. Sau review mới nối adapter feature-gated và chạy restart HTTP; library pass chưa chứng minh Health đã durable.

## Muse — MEDIA-02: toàn video/cinematic/âm thanh
Tiếp MEDIA-01 tại issue #116, muse/media-*. Chỉ root/extension của policy work 28; không sửa game asset/UI/VFX/map/Godot.

1. **M1 — inventory và nguồn.** Toàn scene/shot/VO/cue/biome/chapter, source hash và dependency. Theo DEC-MEDIA-P0 mới. Git proxy lỗi thì dùng nội dung decision/work order đã post và tiếp việc độc lập; không báo đã fetch.
2. **M2 — P0 animatic 72 giây.** CIN001/002/004: storyboard → keyframe/timing → edit; VO/SRT/ambience/music stems riêng. Q1 dùng bản B canonical; Ly An ở CIN004 là off-screen. Thiếu character lock chỉ chặn final picture shot đó, không chặn audio/timing/shot nước-dây-kiện.
3. **M3 — video toàn campaign.** Opening, discovery, rescue, boss key, điều tra kinh thành, bước ngoặt và ending theo canon. Có khám phá/khoảng nghỉ, không toàn đánh nhau. CIN006 alternate take có version, không tự thay canon. Hạ Mặc/Sầm là cinematic-only staging, không dời persistent NPC.
4. **M4 — nhạc toàn game.** Explore/town/Thăng Long/rain/swamp/mountain/dungeon/boss/arena/tragedy/resolution; loop, stems và transitions. Giai điệu/cadence theo audio direction; tone generator đủ số file chưa là final.
5. **M5 — SFX/ambience.** Vật liệu bước chân, năm vũ khí, 30 skill cast/impact/miss, boss warning, weather/water/market/forge/gather/UI/item/quest/cinema. Variants, minGap, voiceCaps, ducking/loudness theo cue ID. Audio không quyết định damage/grant.
6. **M6 — VO toàn truyện.** Giọng hư cấu, Ly An/Tạ/Hạ Mặc/Sầm phân biệt, phát âm tên riêng thống nhất, pickups/alt reads. Source WAV/subtitle mapping; không clone giọng thật hoặc dùng sample không license.
7. **M7 — delivery runtime.** MP4 review/master, OGV/Theora runtime, poster và SRT UTF8/NFC; low 640×360/standard 720p, delivery 30fps/pose 8–12fps. OGG/WAV, originals/stems/license/provenance/hash. Không optical-flow morph hoặc baked subtitle. Codex tích hợp mixer/player.
8. **M8 — media QA và gói lớn liên tục.** Codec/duration/sample rate/peak/loudness/loop-click/subtitle/hash, actual audition/video và playlist. Giao P0 + audio palette đầu, rồi chapter/cue/VO packs; không dừng sau một clip.

## Codex — phần mình tiếp tục
- Review/pin Shared và Health, nối Godot main thread/scene/network và launcher Windows. Phân biệt art preview và online; không fake grant hoặc movement server.
- Sản xuất nhân vật/NPC/quái/boss, tám hướng với frame walk/attack/hurt/death/skill thật, pivot/anchor vũ khí; map và UI pixel cùng chuẩn Bến Mưa mới.
- VFX 30 skill/boss: cast/travel/impact/buff/weather, timeline/pool/LowFX/reduced flash/cancel theo event. Gallery chỉ kiểm đọc hình, không tự gây damage.
- Hoàn NPC dialog/journal/túi/equipment/target/skill arc/minimap/input/game flow, tích hợp media Muse.
- Mốc chơi được phải thực sự vào game, đi/nhận quest/khám phá/đánh/trùm/chết-hồi/nhận thưởng; hai phiên không lẫn state. Ghi đúng leg thiếu, không gọi gallery là full online.

## Giao nhận
ACK tại issue của mình: branch, SHA, checkpoint đang code. Mỗi checkpoint có source/media thực, command, raw output, dependency và giới hạn. Push rồi tiếp module độc lập; chỉ hỏi lại phần source/contract thật sự chưa có. Không reset/stash/clean worktree người khác, không force-push hoặc mở lại phạm vi Antigravity/Muse cũ.
