# Online, lưu dữ liệu và vận hành — hợp đồng bổ sung v1

Áp dụng cùng Production_Rules_Complete_v1_vi.md, DEC-016 và completion bundle. Đây là yêu cầu kỹ thuật phải được code/kiểm thử; thông số vận hành là mục tiêu thiết kế, không phải cam kết hạ tầng đã được cấp.

## 1. Tài khoản và quyền sở hữu

Production auth cấp access token15phút, refresh token30ngày, rotate mỗi refresh; refresh token lưu hash, reuse token đã rotate revoke session family. Guest upgrade giữ accountId qua provider-link transaction, không tạo nhân vật mới. Không thu password provider vào game server. Principal có accountId/region/sessionFamily; mọi character command kiểm account ownership, không tin characterId tự khai.

Tối đa4 character/account. Tạo tên NFC/case-fold so trùng trong region, 3–16 ký tự hiển thị, không control/invisible. Xóa pending7ngày, khóa trade khi pending, restore trước purge. Account đang có escrow/sanction không tự purge; tài liệu retention thị trường phải được owner phê duyệt trước release. Không ghi token/email vào gameplay log.

Heartbeat15s; 45s mất heartbeat chuyển RECONNECTING, grace120s DEC-004. Reconnect cần resume token single-use30s, character ownership và cùng region; thay connection epoch, bỏ command epoch cũ. Tournament giữ luật một lần90s riêng. Đăng nhập cùng nhân vật lần hai hỏi takeover, revoke connection cũ trước khi nhận input mới, không tạo hai actor.

## 2. Network contract

HTTP cho login/economy/quest; WebSocket cho move/combat/snapshot khi P2. HTTP P1 hiện hữu được giữ cho dev, không đổi thành production chỉ bằng mở port. Protocol handshake {clientBuild,protocolVersion,bundleVersion,lastSeenRevision}; mismatch trả UPDATE_REQUIRED trước khi vào world. Payload max32KiB, text chat max500 Unicode scalar sau normalize.

Simulation20Hz, snapshot10Hz, full snapshot mỗi5s và khi resync; client interpolation100ms, prediction chỉ self movement. Movement intent tối đa20/s, combat tối đa10/s, economy5/s burst10, chat1/s burst5, report5/phút/account. Giới hạn theo account+session; IP là hàng rào phụ, không ban cả mạng dùng chung.

State message có connectionEpoch/serverTick/mapInstanceId/revision. Command sequence monotonic actor; bỏ duplicate, reject gap vượt1024 và yêu cầu snapshot. Delta có baseRevision; thiếu base thì xin full, không áp một phần. Command timeout3s: query state trước khi retry mutation; giữ idempotency key. Không replay input trước map transition epoch.

AOI PvE radius40WU, hysteresis8WU; party markers ngoài AOI chỉ vị trí thô nếu mode cho phép. PvP không gửi địch ngoài vùng visibility vào client/minimap. Reliable command/result/events; snapshot có thể thay frame cũ. Slow consumer queue >256KiB thì gửi resync và ngắt nếu không hồi phục trong5s, không làm nghẽn zone tick.

## 3. Persistence và transaction

PostgreSQL là nguồn durable; Redis chỉ cache/session/queue. Tối thiểu tables: accounts, external_identities, characters, character_stats, skill_loadouts, item_instances, inventory_slots, currency_balances, currency_ledger, quest_states, quest_events, reward_ledger, activity_caps, cosmetic_unlocks, guilds, guild_members, market_listings, trade_escrows, mail, idempotency, outbox, moderation_audit.

Unique constraints: provider+subject, region+normalizedName, character+slot, reward recipient+sourceEvent+bucket, actor+operation+idempotencyKey, itemInstance escrow owner, guildId+memberId. Currency BIGINT >=0; quantities integer>0; revision BIGINT nonnegative. Timestamps timestamptz UTC, IDs immutable. Không cascade-delete ledger khi xóa nhân vật; pseudonymize theo chính sách được duyệt.

Transaction thứ tự: authenticate → validate request hash/idempotency → lock rows theo ID tăng → expectedRevision → guards → tính outcome server → update state+append ledger+outbox+cached result → commit → respond. Lỗi DB trước commit rollback; lỗi response sau commit retry đọc cached result. Idempotency economic giữ>=30ngày; movement không ghi mỗi tick vào economic ledger.

Position checkpoint mỗi10s ngoài combat, sau encounter, trước transition và logout. Inventory/quest/currency ghi đồng bộ transaction, không chờ autosave. Zone crash khôi phục position checkpoint, giữ mọi ledger commit; không khôi phục HP để bypass death reward. Actor đang combat trở về checkpoint với trạng thái recovery, không phát loot từ attempt mất.

Transition: reserve destination slot→persist checkpoint/pendingTransition→issue route token TTL30s→destination consumes token once→activate epoch→release origin. Failure trước consume trả actor origin, sau consume query destination không spawn lại origin. Pending cleanup theo transitionId, không client tự chọn tọa độ đích.

Migration expand→backfill→dual-read verify→switch→contract; đổi schema destructive chỉ khi mọi client/server cũ đã hết support. Migration script có up/down compatibility note và fixture restore. Rollback app không đảo ngược reward đã commit.

## 4. Release, monitoring và incident

Build artifact có commit SHA/editor/runtime/package lock, content hash, protocol version và asset manifest hash. Bundle immutable, SHA256 từng file, signature server key ngoài repo; client verify trước load. Hot balance tạo version mới, encounter đang chạy pin version cũ; item roll hiện hữu không tự roll lại.

Staging cùng schema production, data giả. Rollout5%→25%→100%, tối thiểu15phút/giai đoạn; auto halt nếu command error>1%/5phút hoặc transaction failure>0,1%. SLO mục tiêu tick p95<=50ms, ack p95<=150ms ở RTT<=100ms; không đánh giá trên chỉ một máy dev.

Dashboard: active connections/zone, tick p50/p95/p99, input rejection, DB lock wait, outbox lag, currency minted/burned, reward dedupe, inventory conflicts, crash/reconnect, patch failures và moderation queue. Alert khi outbox lag>60s/5phút, zone tick p95>50ms/5phút, DB unavailable30s, ledger anomaly bất kỳ. Log correlationId/actor pseudonym/eventId/bundleVersion, không chat raw toàn cục.

Backup daily full+WAL liên tục; mục tiêu provisional RPO15phút/RTO4giờ. Restore vào isolated staging mỗi tháng, verify balances+inventory+quest+outbox, chặn phát mail/payment ra ngoài trong restore drill. Chỉ sau drill có biên bản mới gọi backup usable.

Incident: phát hiện→freeze domain bị ảnh hưởng bằng feature flag→snapshot/audit→rollback code/content tương thích→reconcile ledger→compensation unique ID→mở lại→postmortem. Không sửa balance trực tiếp bằng SQL bỏ ledger. Admin economy/reward adjustment cần reason+ticket+two-person approval, giới hạn theo role.

Moderation report gắn message/event ID, trạng thái NEW→TRIAGED→ACTIONED/DISMISSED→APPEALED→CLOSED; không auto-ban chỉ vì nhiều report. Mute chặn channel được scope; block chặn whisper/invite nhưng không xóa evidence. SLA nội bộ: critical exploit triage1giờ khi có trực, harassment24giờ; chưa có nhân sự trực thì không công bố SLA cho người chơi.

## 5. Device và art evidence

Gameplay landscape, top-down XY. PC1280×720/1920×1080/2560×1440, mobile720p và1080p safe area. Target mobile30FPS/PC60FPS; chỉ ký khi đo 30phút sustained trên thiết bị mục tiêu ghi model/OS/RAM. Texture pages<=2048; LowFX giữ telegraph, giảm weather particles. Không lấy headless compile làm số đo FPS.

Asset evidence gồm original source/license, PNG thật đã fetch LFS, frame rectangles/pivot, playback video các hướng, scene log exact SHA/Editor, ảnh 640×360 và upscale nguyên. Art status DRAFT→ART_APPROVED→ENGINE_IMPORTED→INTEGRATED→DEVICE_QA; schema hiện tại chưa có các field này thì dùng evidence sidecar và proposal schema, không thêm key phá validator.

## 6. Nghiệm thu theo hành trình

| Gate | Luồng phải chạy | Bằng chứng bắt buộc |
|---|---|---|
| SLICE | create→Bến Mưa→P00-01..05→boss→reward→equip→logout/login | video hai client, server log, DB snapshot, IDs/bundle |
| CONTENT | 76 quest,30 active,5 lớp,46 map,349 placements | executable records đầy đủ, graph/ref/nav validation, map sign-off |
| ECONOMY | buy/sell/craft/trade/market/claim/retry/concurrent | atomicity và10000 replay không duplicate, audit ledger |
| MULTIPLAYER | party/raid/PvP/siege/reconnect | match state/reward/tie/void, test network40/100/180ms |
| RECOVERY | server kill, DB interruption, deploy rollback | restore result RPO/RTO, không mất ledger/nhân bản actor |
| SHIP | onboarding→progression→social→endgame trên PC/mobile | artifact signing, performance, moderation/support, license và market approval |

Máy local yếu: coding/data validator chạy local, Unity build/gameplay QA trên máy ảo có license, server build/smoke trên CI. Không thay engine giữa chừng chỉ để bỏ qua gate thiết bị. Không đánh dấu SHIP khi vẫn có DRAFT map/asset hoặc lỗi P0/P1.
