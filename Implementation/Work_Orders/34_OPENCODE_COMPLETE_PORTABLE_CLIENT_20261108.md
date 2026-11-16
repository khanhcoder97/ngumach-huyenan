# OpenCode — OPC-17→20: hoàn tầng client portable và gói tích hợp

Owner OpenCode LOCAL, issue85, tiếp PR109/nhánh và worktree hiện có; Codex review. Nhận toàn chuỗi O-A→I bên dưới. Source review pin `f41397f07515f0c640b7f44481eccfecba2198bb`, server pin `6814126e2def8a1c4270a1016f0ab85404cba46e`; cập nhật successor bằng fetch/pin, không giữ blocker cũ sau khi handler có thật.

Giữ ownership portable Core/Presentation/typed protocols/runner/package/tests/workflow của mình. Không sửa Godot scene/widget, graphics/map/VFX asset, server mechanics, Muse media, pipeline/compiler đã thu hồi. Không merge cả PR103/109 stack. Đích là library/adapters đủ cho Codex nối native và dùng được trên máy thấp; console PASS chưa chứng minh native.

Finding wire/confirmed refusal trước đã được đóng bằng lượt review mới tại f41397f:280unit PASS và138pairedHTTP private-alpha PASS. Giữ regression; không làm lại mốc đó như thể chưa sửa. Phần còn thiếu là portal positive/full tutorial, death-return khi downed, owner encounter snapshot, MAP_VIEWED/escort mới và adoption vào native.

## O-A — khép conformance và chuẩn bị adoption

Tiếp gói32, đừng gọi conformance done chỉ vì model khớp vài field. Giữ actual Qoder schemas/examples có pin/hash; success, error, nullability, ID/finite/range/credited/replayed và receipt identity phải đúng. Không yêu cầu echo requestId nếu contract hiện hành server-minted; dùng lane/session/operation identity đúng, trace/correlation vẫn giữ. Khác owner hoặc stale session không được mutate cache.

Paired runner đã giao phải tiếp hai mode, client/server/content root riêng và exact heads/hash/health/PID. Negative controls: pin sai, content mismatch, assertion0, server không khởi động, process con sống sau timeout phải FAIL. CI artifacts mode-scoped; không đưa output chính nhánh client thành serverQoder proof.

Giao patch/package adoption tối thiểu cho Codex: source/dependency closure, namespace collisions với NativeOnlineSession hiện tại, schema manifest, methods/reentrancy/thread semantics, migration/version notes. Không copy cả legacy UI hoặc tạo hai P1Client type đang cùng build. Gói net8 và lock/notice/license trạng thái thật; thiếu first-party LICENSE không tự gán MIT cho game.

## O-B — session lifecycle cho mọi read/mutation

Unify login/logout/expire/reconnect/relogin/return/map transition, monotonic epoch và captured client. Trước apply receipt/cache/pending/cooldown và trước follow-up read phải kiểm captured epoch/token; queued dispatch kiểm lại khi chạy, kể cả failed login. Không apply rồi restore state của phiên mới. Pending command mất response giữ đúng body/key/owner để reconcile; confirmed refusal release lane/pending đúng code/field/retryability. Retry historical receipt không dùng như snapshot hiện tại.

Tất cả typed API mới đi qua composition boundary thật; không để presenter gọi Core thiếu lifetime guard. Dispose không chặn UI thread, cleanup awaitable/bounded và xử lý transport không tuân cancellation. Test queued-success-before-dispose/relogin, single-thread context, subscription đổi giữa queue/run, cancel sau commit, duplicate concurrent call. Timing tests dùng controllable seam, không sleep đoán hoặc deadline500ms phụ thuộc host.

## O-C — toàn hành trình nhiều owner qua public HTTP

Giao runner P00-01..05/clue/rescue/trial/escort/boss/fragment/class-confirm/turn-in/chapter/portal hai chiều khi source node mới vào server. C1low-level LOCKED, conformancelevel11 có nhãn khác natural progression. Nối MAP_VIEWED + escort projection mới sau schema; wrong owner/map/floor/life/attempt/offAOI/replay/conflict đều có acceptance. Không fake grant để bypass finale/portal.

Inventory12slot + capacity100, consumeHP/MP, no-effect/dead/stale/fullbag, equip/unequip, loot và XP receipt; death thật→return→freshworld→replay→reconnect, encountercurrent/detail/owner-targetability/cast-shape timing. Hai owner song song dùng claims/spawn thật, no shared receipt/credit; đóng góp không phải party khi server solo-only.

Không đòi server thiếu khi chỉ thiếu profile/runner. Khi endpoint thật chưa có, giữ unsupported/capability và tiếp fixtures/models/presenters độc lập; ghi legUNVERIFIED thay vì skip rồi báo full campaignPASS. Job dài có bounded waits theo state/tick, health/process identity và cleanup đúng process mình tạo.

## O-D — read models/presenters cho toàn UI chơi được

Giao immutable view+commands cho HUD/target/skill-resource/cast/cooldown/death-return; inventory100slot/12equipment/tooltip/consume/quest-pouch-unsupported; tracker/journal/NPCdialogue/map/portal/escort/arrival; settings/accessibility/system/errors. Authoritative slotId/instanceId không đổi theo search/page/order;5×5/page là layout source, responsive không sinhslot. Model rõ loading/stale/unsupported/disabled/rejected/replay/refreshpending, không local grant.

Dialogue đọc node/text/version và đúng current objective, không đoán node đầu; journal phân quan sát/giả thuyết/đã đối chiếu theo source/receipt, không đưa suy đoán thành flag server. Cảnh báo/tooltip tiếng Việt dùng localization keys/fallback; không hiển thị debugcontract vào UI nếu người chơi không cần. Codex dựng actual widgets, OpenCode giao data binding và state traces có thể tái hiện.

## O-E — combat presentation và multiplayer consistency

Năm class/30skill dùng catalog đã reviewed; unsupported skill không tạo accepted animation. Resource và cooldown theo server, typed shape/cast/life/owner/tick/cursor; cast accepted chưa là hit. VFX/audionotice binding API phải dedupe từng stage/hit, cancel/death/logout/map/encounter cleanup đúng, impact muộn của targetlife cũ không phát lại. ReducedMotion/LowFX/flash/telegraph readability là policy/API, không sửa asset hoặc vẽ hitbox khác mechanics.

AOI/resync/page overflow không giả entity chết hay miễn nhiễm; reconcile snapshot và authoritative events. Không tự nới AOI40/48/range do camera64×36. Giao trace fixtures cast→guard/counter→impact/miss→death/respawn, twoowners/observer/late event và event gap, kèm sample factory Codex dùng được.

## O-F — economy/crafting/service/social client

Sau các contract Qoder giao, typed APIs/read models cho shopbuy/sell/storage/gather/craft/forge/upgrade; partyroster/guild/chat/mail/trade/activity/rank. ExpectedRevision/priceQuote/stock/contentversion/cap/owner/hash theo schema thật; không dùng catalog/policy làm HTTPsuccess giả. Route chưa có phải unsupported rõ và actiondisabled hợp lý, không requestspam.

Nhiều panel/page/filter dùng cùng selection identity; modal/focus/input release có API không tự thao tác Godot. Transactions trả lịch sử receipt rồi freshread; không doubleclick grant hoặc cố dùng key mới để ép thành công. Unknownfields/errors có version strategy, không bịa snapshot “tốt nhất”.

## O-G — media bridge và runtime boundary

Đọc Muse PLAYBACK_METADATA/audio manifest/content hashes qua validated model, source paths trong root allowlist; missing/LF/LFS-pointer/codec unsupported thành fallback có nghĩa. EmbeddedSoundtrackOnly không schedule standalone mix/VO cùng lúc; clean video+SRT, không doublecaption. Seen/skip/rewatch/fallback chỉ presentation, không grant quest hoặc gọi turn-in.

Giao adapter interfaces/samples/main-thread dispatch và diagnostics có bounded data cho Codex; không code player Godot/widget. Playbackclock/paused/resume/subtitle cue/seek/reducedmotion/mixer policy phải minh bạch; metadata proposal chưa là audible approval.

## O-H — regression/performance/package

Maintain unit+public-core adversarial+pairedHTTP+pack/sample/source closure. Từ clone sạch SDK8client/SDK10server, trackslock/README/notice, noUnity requirement. CI assertions>0/TRX/rawoutput and pin hash; timeout/abort không là PASS. Measure allocation/poll backlog/eventbuffer/lane latency trên cấu hình thật, no unboundedqueues/task leaks; benchmark ghi fixture/load, không hứa mượt máy yếu từ console.

## O-I — giao trọn gói qua checkpoints

Checkpoint1 O-A/B + paired current routes; checkpoint2 fulltutorial/newschema+capacityconsume; checkpoint3 wholepresenters/combatbindings; checkpoint4 economy/social modules theo handlers; checkpoint5 media/package/performance/regression/adoption. Push đủ review rồi tiếp phần độc lập; không chờ wholeMMO mới giao Core có pin. Báo exactSHA/dependency, API deltas và actual remaining legs tại#85.
