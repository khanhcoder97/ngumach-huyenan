# QA MATRIX VÀ RELEASE GATES
## Ngũ Mạch: Huyền Ấn — tiêu chí kiểm thử và nghiệm thu production

## 1. Chiến lược kiểm thử

Test server rules trước UI presentation; mọi kiểm tra kinh tế/PvP chạy qua authoritative server build. Data validation là pipeline bắt buộc ở mỗi bundle. Mỗi test lưu build SHA, data bundle version, thiết bị, region, seed nếu có, log correlation ID và ảnh/video khi lỗi hình ảnh.

| Tầng | Bao phủ | Gate |
|---|---|---|
| Unit | stat formula, cooldown, status stack, reward caps, timezone boundary, permission | P0: core rules pass; không flaky |
| Data import | IDs, refs, graph, bounds, probabilities, item/reward links | mọi content bundle phải import sạch; lỗi P0/P1 chặn build |
| Integration | quest→reward, forge→inventory, market escrow, match→ledger, reconnect | exactly-once transaction; rollback on error |
| Client UX | HUD, inventory, settings, forge, compendium, combat feedback | resolution/device/accessibility matrix đạt |
| Security/exploit | forged damage, speed, item, cooldown, proximity, replay, race | critical/high exploit = release blocker |
| Performance/load | tick, zone occupancy, queue, DB, WS, event fanout | đạt target build và capacity plan đã ký |
| Live ops/recovery | deploy/rollback, backup/restore, event pause, compensation | drill có biên bản và owner trực |

## 2. P0/P1 feature test cases

| ID | Thiết lập / hành động | Kết quả mong đợi | Severity |
|---|---|---|---|
| QA-ID-001 | Gửi lại cùng quest turn-in 5 lần cùng idempotency key | một quest completion, một reward transaction | Blocker |
| QA-ID-002 | Hai client đồng thời equip một item instance | một thành công; client kia revision conflict; không nhân bản | Blocker |
| QA-ID-003 | Forge commit với nguyên liệu vừa bị trade ở transaction song song | một operation fail clean; không âm stack/currency | Blocker |
| QA-ID-004 | Client gửi damage 100×/cooldown âm/out-of-range target | server từ chối; audit metric ghi anomaly | Critical |
| QA-ID-005 | Disconnect ngay trước reward commit và reconnect trong 120s | snapshot phản ánh chính xác committed/not committed; không duplicate | Blocker |
| QA-ID-006 | C2-03 escort wipe tại van B rồi reconnect | resume ở van B; timer/step không reset toàn quest | High |
| QA-ID-007 | Scheduler qua daily reset 05:00 Asia/Ho_Chi_Minh và DST/UTC boundary | ledger reset đúng một lần theo region; client timezone không đổi quota | Blocker |
| QA-ID-008 | BG10 capture point bị hai team tranh chấp cùng tick | progress dừng; không có score race/client authority | Critical |
| QA-ID-009 | BG10 relic holder disconnect/kill/reconnect | relic chỉ có một state owner/ground/home; không duplicate scoring | Critical |
| QA-ID-010 | BG10 queue-abandon/AFK at thresholds | cảnh báo/penalty/reward cap đúng; server-void không phạt | High |
| QA-ID-011 | Boss weekly schedule chuyển tuần | selected `sourceBossId` canonical, scale/modifier/reward hash immutable trong tuần | High |
| QA-ID-012 | Passive reset/equip với node chưa mở hoặc hai preset cập nhật đồng thời | server từ chối invalid prereq; preset revision nguyên tử; tối đa 2 equipped | High |
| QA-ID-013 | Party đổi map giữa reward state và zone transition | checkpoint trước route, quest/item state không mất | Blocker |
| QA-ID-014 | Trade confirm ở một bên, bên còn lại sửa offer | cả hai confirm invalidated; escrow rollback | Blocker |
| QA-ID-015 | Import bundle chứa trùng ID, item ref thiếu hoặc loot probability >100% | pipeline fail với dòng/field chính xác | Blocker |

## 3. Regression map/content

Mỗi map kiểm tra đường đi đầu-cuối, bounds, camera, collision, jump/ladder/platform, portal, spawn phase, safe zone, weather occlusion, mobile touch safe areas, NPC interact distance và không có soft-lock quest. Tối thiểu test với 1 người chơi mới, một nhân vật cấp cap, party đủ người và reconnect giữa encounter. Manifest `NEW_PROPOSED` phải được level design sign-off hoặc còn bị đánh dấu blockout; không chuyển sang release content khi chưa đo navmesh/collision.

| Suite | Cases cần có |
|---|---|
| Campaign | 36 main quests + 40 side quests; prereq, alternate dialogue, fail/retry, checkpoint, reward, unlock |
| Class | 5 class × active kit/passive loadout, gear restriction, PvE/PvP coefficient, death/respawn |
| Equipment/economy | 12 slots, 100 bag, 120 bank, stack cap, binding, durability, salvage, craft, market tax |
| Activities | 4 dungeon, 2 raid × 3 encounters, 6 world boss, 30 tower floors, 10v10, 3v3, 20v20, Mạch Triều |
| Social/safety | party/guild permission, block/mute, report, chat rate, account deletion, restore/deletion audit |

## 4. Device/network/accessibility matrix

- Layout QA: PC 1280×720, 1920×1080, ultrawide 2560×1080; mobile 720×1600, 1080×2400, 20:9; test safe area/notch, text scale 100/125/150%, HUD scale 80–120%.
- Performance target: PC baseline 60 FPS; mobile low preset 30 FPS sustained. Record frame-time p95, memory, thermal state, loading and battery drain after 30-minute session.
- Network: RTT 40/100/180ms; jitter 0/30ms; packet loss 0/2/5%; reconnect, duplicate, reorder and 10-minute offline transition. Combat feedback stays clear; server outcome authoritative.
- Accessibility: colorblind-safe team/objective states, telegraph not color-only, scalable UI text, reduced flash/shake, remappable controls, subtitles, non-audio critical cues.

## 5. Load, soak, resilience

Capacity is not yet a signed product requirement. Benchmark separately at 100, 500 and 1,000 simulated concurrent players across hubs/zones/instances; report CPU/memory/network/DB/queue p95 and cost per active player. Do not declare release capacity until hosting topology, target CCU and budget owner approve. Run 24-hour soak for memory leak/tick drift; kill one zone worker, database connection pool, event bus consumer and scheduler during staging. Verify instance isolation, outbox replay, backup restore, graceful degradation and no double reward.

## 6. Release gates and sign-off

| Gate | Required evidence | Sign-off owner |
|---|---|---|
| P0 Foundation | build reproducibility, auth/data migration, server-authoritative core, telemetry/privacy review | engineering + security |
| P1 Vertical slice | Bến Mưa end-to-end, PC/mobile, reconnect/reward integrity, performance baseline | producer + QA + design |
| P2 Systems | all five classes, combat/passive regression, party/zone routing, functional item flows | gameplay + QA |
| P3 Progression | campaign graph/data import, economy atomicity, craft/market exploits closed | design + backend + QA |
| P4 Multiplayer | arena/BG10/siege rules, moderation, anti-cheat, load and disconnect scenarios | PvP + security + ops |
| P5 Content alpha | approved map placements, 76 quests, all boss/activity data, asset IDs resolve, Vietnamese localization | narrative + art + level design + QA |
| P6 Release | legal/title/asset rights, privacy/store, retention/deletion, incident/restore drill, support staffing, capacity budget | product owner + legal + ops |

Release-blocking: unresolved P0 decision; critical/high security exploit; data import error; lost/duplicated currency or item; main quest soft-lock; crash/data corruption; unlicensed asset; unrecoverable save migration. Sign-off record includes named owner, build/data versions, open risks and rollback version.
