# Qoder local — QOD-30→36: hoàn backbone gameplay authoritative

Owner Qoder local, issue #87 đồng bộ #41, tiếp PR #106/nhánh QOD21. Nhận toàn chuỗi Q-A→J. Head aaaa803 chỉ thêm report so với pin615 self-check/132 HTTP tại6814126; đã ACK gói32 nhưng chưa có code finale mới khi bắt đầu lượt review này. Gói lớn không có nghĩa gói32 đã hoàn tất.

Phạm vi: Server/Health, contracts, runtime data/export, tests và workflow server. Codex review/merge. Không sửa client/Godot, art/media, pipeline owner khác hoặc Server/Persistence của Remote. Production OFF; schema mới có example, negative fixtures và validator trước handler. Không mở lén world/combat enums đã đóng, không reset worktree khác.

## Q-A — mốc đầu: hoàn P00-05 và portal thật

Nhận tutorial_closure_20261108.json từ integration đã merge PR128. Node NPC_CLASS_TRIAL, text, graph và objective binding đã duyệt; không cần hỏi lại. Boss+fragment phải commit trước TALK, đúng owner/attempt/step/NPC/map/floor/range. Chỉ xác nhận class server, không respec, auto reward hoặc video grant. Replay receipt trước fresh reveal/map guards; cùng key khác body phải conflict.

Giao public HTTP từ P00-01 tới class-confirm → READY → turn-in → chapter permission → Bến Mưa348 → Thanh Lạc8, chiều về20 →348. Không dùng helper grant chương. Low-level C1-01 vẫn LOCKED. Triển khai MAP_VIEWED/QOD28 và escort projection/QOD29 đã có binding: schema/validator trước handler, negative controls kiểm đúng hành vi. Tọa độ/provenance cùng một sample, AOI dùng chính sample ấy; observer không nhận tọa độ ẩn của owner khác. Giữ one-shot attempt1 tới khi có allocator/reset policy và migration được duyệt.

## Q-B — cấp1→11 và effective stats thật

Theo DEC-023 và quyết định inventory mới: XP, level, điểm chưa phân phối, aggregation, reward, revision và receipt cùng transaction. Kiểm multi-level, cap100, overflow, rollback, retry và concurrent replay. Không ép năm quest đủ cấp11 bằng số bịa; giao bảng nguồn progression và exact gap còn thiếu, tiếp phần đã đủ nguồn.

Gate EffectiveStats riêng, default OFF cùng AlphaProfile; legacy REFERENCE_L5/HP2000 endurance là profile có nhãn riêng. Không cộng đôi weapon/armor alias hoặc scale rarity CSV lần nữa. Giữ oracles Attack20→weapon38, hatHP212/Armor14; maximum đổi thì giữ current tuyệt đối rồi clamp, HP0 vẫn0. Không reset cooldown/cast/life vì equip/level/respec. Modifier thiếu nguồn phải từ chối activation, không mặc định0 rồi gọi đầy đủ. Giao additive actor/stat/capability packet cho Core trước wire.

## Q-C — capacity, potion và inventory transaction

DEC-INVENTORY-ALPHA-20261108 đã trả lời hai packet QOD24; nhận JSON ngay. Bag100 stack hợp lệ, quantity theo stack_limit, stable slot IDs. Planner chung cho quest/gather/loot/unequip, tính cả batch trước commit. Equip có thể giải phóng chỗ, unequip có thể cần chỗ. Không suy mailbox/quest pouch để né fullbag.

inventory_full409 retryable: không đổi item/currency/XP/quest/revision hoặc success receipt; cùng key chưa commit có thể thử lại sau khi có chỗ. Full quest giữ READY. Loot full giữ cùng death/roll pending, không reroll hoặc mark PAID sớm. Item cũ vượt100 không bị xóa. Giao fixture seed có nhãn để kiểm fullbag qua HTTP, không endpoint seed trong release.

Consume có gate riêng: HP/MP sourced effects, floor/clamp, no_effect không spend; HP0 bị từ chối để không bypass life. Atomic spend một unit + actor pool + revision + receipt; bốn request cùng key chỉ spend/heal một lần. Codes mới đã duyệt; giao schema và errors cho Core. Food UTC/offline và skill status simulation tick là hai loại clock; chưa mở revive/repair/buff thiếu luật.

## Q-D — năm lớp,30skill và status có nguồn

Giao typed resource/cost/cooldown/targeting/cast/impact/status/passive. Nạp30row không đồng nghĩa hỗ trợ30skill. Thực thi từng subset đủ nguồn qua pipeline thật: class/level/resource/MP/CD/sequence/idempotency/LOS/geometry/instance/floor/life/invulnerability. Reserve cost và receipt nguyên tử; replay không reschedule hoặc phát resource.

Projectile, multi-hit, trap, zone và ally heal cần model biểu diễn đủ cast range/effect radius/duration/hit timing; không ép tất cả vào rangeWu đơn hoặc tự chọn telegraph0. Thiếu numeric thì gửi packet có source/options/ảnh hưởng, tiếp skill khác. Typed passive-cap parser được duyệt; effect chưa parse phải unsupported khi activation. Không đổi elite multiplier production để làm hai nguồn khớp. Fake clock/barrier kiểm counter overdue, stall, impact/death/map ordering và no-retarget/no-refund; giữ DEC022 oracles.

## Q-E — mob/boss/respawn và nhiều owner

AI threat/leash/telegraph/target lock/phase guard theo profile đã author; world-event boss và quest boss giữ identity riêng. Respawn/life/generation từ nguồn. Shared ba body không được đổi thành bốn body riêng mỗi người để đủ quest; hai owner phải qua respawn và kill credit thật. Late death, replay, wipe hoặc return không grant lại.

Giữ owner roster/no-late-join/stable attempt và phase đã duyệt. Transition/death/cleanup không cancel cast đời mới. Kiểm lock ordering snapshot/tick/portal; negative control phải bắt được deadlock/race. Không gọi globally atomic khi chỉ kiểm một lock. Party/raid chưa có runtime phải ghi unsupported.

## Q-F — economy và services

Triển khai theo source IDs: shop buy/sell/stock/quote, gather, craft/forge/upgrade, storage khi đủ contract. Expected revision, owner, binding, currency caps, fee, ledger và outbox interface rõ. Không debit từng món rồi fail nửa transaction. Catalog không là service đã bật.

RNG decision/version gắn key; retry/login không reroll. Coin band, socket/hidden distribution hoặc fee thiếu nguồn cần packet riêng, không default0. Bank120–200 chưa chốt thì chưa tự chọn số. Export phải preserve source rows/hash; không sửa report để đủ count. Rate-limit economy thuộc API boundary theo identity/units riêng, không mượn quota chat.

## Q-G — NPC, discovery và campaign

Dialogue/choice/flags/reveal/quest conditions có version. Resolve NPC_MASTER_BY_PLAYER_CLASS từ class server; không tạo NPC mới hoặc để client chọn lớp thay thế. Observation/hypothesis không thành world truth. Trust thiếu numeric thì giữ narrative flags, không tự phát điểm. Cinema seen/skip không cấp quest/loot.

Tiếp objective graph và instances C1 sau Bến Mưa. Không mở hàng loạt chapter route trả placeholder. Quest kind thiếu cần content model/dispatch/validator và binding thực, không đổi DEFEND thành KILL tùy tiện. New tracked anchor cần proposal/migration; không đưa76beats vào manifest349 để gọi map đã reviewed.

## Q-H — social/multiplayer

Party/guild/chat/mail/trade/activity/rank có packet trước: membership/roster/owner/revision/receipt, concurrent leave/join/reconnect và lease. Guild XP eligibility, contribution points và treasury currency không cùng đơn vị. Trade hai owner phải atomic, mail claim một lần, daily/weekly reset có clock/timezone/bucket. Domain fixtures làm độc lập; public routes OFF tới khi auth/persistence và semantics đủ.

## Q-I — navigation, ops và durable adapter

Giao migration349anchors, bounds/floor/axis/PPU/nav hash/footbox/path/portal/safe zone và conflict matrix. Không đổi canonical XY hoặc nâng SYNTHETIC/DRAFT thành REVIEWED. Camera/art không cho quyền nới AOI/range.

Remote giữ persistence. Giao full DTO global key/owner/hash/before-after life, inventory/quest/XP/currency transactions và outbox/reset clocks; không viết DB thứ hai. Không append writer sau domain mutation rồi gọi crash-safe. Chưa nối Health trước module review; restart HTTP proof bắt buộc trước durable claim. Launcher private port/health/PID/cleanup, metrics và capability matrix đúng trạng thái thực.

## Q-J — giao đủ chuỗi qua checkpoint

1. Finale/portal và MAP_VIEWED/escort.
2. Progression/stat/capacity/consume.
3. Combat năm lớp theo subset đủ nguồn, AI/boss nhiều owner.
4. Economy/campaign services.
5. Social/durable adapter/navigation/ops và regression tổng.

Mỗi checkpoint có source thật, exact SHA/source version, schema manifest, commands/raw HTTP/CI và negative cases. Push rồi tiếp phần độc lập; không thay bằng tăng số report/self-check hoặc ACK. Phần chưa có contract giữ unsupported rõ, không làm giả tính năng.