# Gói việc lớn tiếp theo — lát cắt Bến Mưa có thể bàn giao

Chủ dự án yêu cầu kiểm tiến độ và giao tiếp gói lớn. Văn bản này cập nhật thứ tự thực hiện của work order 04–06, giữ các quyền sửa và gate đang có. Không thay design canonical hoặc chứng nhận game production-ready. Mỗi agent nhận cả gói của mình, chia PR theo milestone, tiếp tục phần độc lập khi chờ review; không kết thúc cả gói sau một file hoặc một PR.

## 1. Đích chung và bằng chứng

Một người khác clone repo có thể kiểm tra asset, xem preview, chạy scenario đầu game và biết chính xác phần nào đã dùng được. Vòng mục tiêu: vào phiên → đi trên XY → gặp NPC → nhận nhiệm vụ → khám phá/nói chuyện/thu thập → chiến đấu subset hỗ trợ → nhận thưởng một lần → đọc lại túi/nhiệm vụ → tiếp tục quest đã có định nghĩa. UI, âm thanh và cinema chỉ phản ánh kết quả authoritative đã xác nhận.

Hai profile tách biệt: default giữ production gates OFF khi chưa có topology reviewed; dev scenario gắn nhãn fixture để tái tạo. Không gọi việc đi hết P00-01 là đã có toàn bộ P00-01..05. Không gọi script kiểm text là Unity compile/playback, không gọi source WIP là bàn giao đã merge.

Mỗi milestone giao exact SHA, PR/dependency, lệnh/output đã chạy, file/source/metadata, feature matrix implemented/fixture/missing và phần tiếp theo. Chưa có công cụ phù hợp ghi blocker và chuyển phần độc lập trong gói. Không tự merge; Codex review và tích hợp. Không reset/stash checkout của người khác.

## 2. OpenCode — hoàn thiện dây chuyền art và dữ liệu đầu game

Issue chủ: #40; duy trì #2/#33 và PR #31/#43. Máy local không cần Unity. Worktree đang dùng `D:/opc05b-wt` có OPC-07 WIP: bảo toàn các file chưa commit và checkpoint trước khi chuyển branch, không xóa scratch/WIP tự động.

### OPC-A — dọn nợ review và giao validator hoàn chỉnh

- Sửa finding PR #43 tại `migrate_manifest_v2.py:141`: frame columns phải được tính từ frameWidth đã resolve; case sheet288px/6frame/columnStart1 không được báo migration thành công với output invalid. Kiểm output bằng v2 validator trước ghi, thêm test không đổi nguồn/không ghi output khi blocked. Gửi head mới trên đúng PR.
- PR #31 cập nhật report từ main mới sau thay đổi thoại/narrative, giữ source SHA/digest khớp evidence. Báo cáo tĩnh được phép ghi finding Bilinear; không tự sửa `.meta` của Muse để làm report xanh.
- Hoàn thiện OPC-07 hiện làm: PNG decode/CRC/truncation/alpha/LFS/decompression limits và parser `.meta` trong subset hỗ trợ. Unsupported phải hiện unverified. Test corruption thật, duplicate GUID, rect sai, Point/PPU/pivot/mipmap; trình bày structural/static/art/engine riêng.
- Phân biệt OPC-07 WIP với code đã push; bỏ debug tạm khỏi commit bằng allowlist file, không xóa dữ liệu chưa rõ chủ.

### OPC-B — phòng review asset chạy trên trình duyệt

Triển khai OPC-08 cho cả actor/map/UI/VFX có mapping rõ: nearest-neighbor, native scale, frame grid, play/pause, 8 hướng/clip, palette/background, thông số/source/findings; timeline phase VFX khi metadata thật đã có. Missing/concept phải hiển thị đúng trạng thái. Một actor thật và effect synthetic có nhãn để demo trước khi Muse giao đủ.

Python stdlib server localhost, allowlist/traversal guards, không npm/Unity bắt buộc. Có thể liên kết sang trang nghe của `Tools/AudioProduction`, không sửa DSP/manifest audio của Codex hoặc đưa audio vào schema sprite. Chụp công cụ thực đang mở và hướng dẫn tái tạo; không gắn nhãn benchmark engine.

### OPC-C — gói bàn giao tái tạo được và CI từ clone mới

Hoàn thiện OPC-09/10 thành một luồng validate → preview → pack → unpack/verify digest: runtime allowlist, dependency/source/license/version, LFS hydration, path safety, deterministic file inventory/timestamp policy. Gói draft ghi draft; thiếu nguồn hoặc file phải fail đúng lý do. Không đưa Library/cache/token/debug vào archive.

Coverage phân biệt design IDs, runtime definitions, placements và assets; present/absent/unknown/unverified có SHA evidence. Giao README từ clone → LFS → một lệnh kiểm → xem trước → đóng gói, CI có pass/fail fixtures và artifacts. Các test phải bắt sai đầu vào thật, không chỉ phản chiếu hằng số trong code.

### OPC-D / OPC-11 — compiler dữ liệu ứng viên cho Bến Mưa

Sau phần cốt lõi OPC-A/B, làm module mới độc lập `Implementation/Tools/ContentPipeline/**`, đầu ra `Implementation/Content/BuildCandidates/**`; đây là mở rộng quyền tooling cho OpenCode. Không sửa `Server/**`, các script `build_world_*` của Qoder, runtime hiện hành hoặc bảng canonical của Codex.

- Đọc nguồn chuẩn để xuất ứng viên P00-01..05, actor profile cơ bản, ba mob đầu game, starter-item references và event/objective mapping. Dùng `P1_Design_Resolution_20261029_vi.md`, Rules §1–3, Art Bible §12 và CSV production làm source map. Không tự làm đầy số liệu thiếu hoặc thay số canonical.
- Mỗi field có sourceRef/version/units/transform; referential validation cho quest/NPC/map/item/skill, duplicate/unresolved IDs, quan hệ prerequisite và giới hạn giá trị. Thiếu reward/rounding/gear vector ghi unresolved và fail activation, không mặc định0 như thể đã thiết kế.
- Output candidate schema/proposal trước; cùng input → cùng bytes/digest sau chuẩn newline. Giao golden fixtures, một lệnh build/check và diff theo field. Qoder/Codex review rồi mới migration/runtime activation; không có hai compiler cạnh tranh ghi cùng file.

Nếu v2 đang chờ duyệt, tiếp tục preview legacy/PNG/pack/candidate compiler; không bắt Muse đổi manifest trước khi schema được duyệt.

## 3. Qoder — vòng chơi đầu game đúng transaction và có read model

Issue chủ #41; PR #53/#54 là các milestone đang review, chưa là hoàn tất epic. Bảo toàn checkout local `D:/Project/NGUMACHHUYENAN`, không chạy clean/reset để đổi base. Nhánh stacked phải ghi đúng dependency; không tự đóng #41 khi mới xong QOD-14.

### QOD-A — sửa correctness trước mở rộng

Review cụ thể đã gửi trên PR #53/#54. Trước merge:

- #53: claim/replay/grant/progress/result phải có transaction ownership phù hợp. `ConcurrentDictionary.TryGetValue` rồi gán không phải reserve nguyên tử. Parallel cùng character/node chỉ một yield; cùng key cùng result; khác character theo rule node hiện hành. Rollback không xóa reservation của request khác.
- #54: sửa CS0246/CS0535 ở `QuestTurnInOutcome`/service; recheck state, floor/map/range/LOS, idempotency và ledger trong transaction ổn định. Không grant inventory trước khi biết có thể commit quest. Rollback/failure injection tại từng bước, cả inventory/quest/ledger/idempotency nguyên vẹn. Cùng key khác npcId phải conflict theo hash toàn payload; so floor actor với anchor.
- Test bằng service thật/barrier hoặc hook điều phối, không mô phỏng riêng thuật toán bằng Python. Bao gồm same/different key đồng thời, túi đầy/overflow, wrong floor, fail giữa commit, replay sau timeout; không sleep chờ race ngẫu nhiên.
- XP `applied:false` chấp nhận cho prototype chưa có XP; báo rõ chưa cấp XP. Unlock một ID chưa có catalog chỉ là tham chiếu, không báo quest đó đã chơi được.

### QOD-B — world projection và combat subset dùng được

Hoàn thiện QOD-11/12 còn thiếu: snapshot trả entity read model có instance/map/floor/state/position/revision và visibility policy; NPC không trở thành mục tiêu damage. Xác định audience và schema delta trước wire. Client không phải tự dựng quái từ tên sprite hoặc placement.

Chuyển nguồn numeric đã có thành export/loader/tests có version và gate; phối hợp candidate compiler OPC-11, không viết đè module của OpenCode. Trong lúc chờ approval làm domain/tests với fixture ghi rõ. Chốt rounding/missing fields qua proposal, không lấy HP100/MP50 fixture làm cân bằng final.

Thực hiện chính xác supported subset ba skill hiện có, mob HP/damage/death/respawn/kill ownership và loot eligibility có source. Phản Quang chỉ counter khi điều kiện thật đạt; MK03 hitIndex/hệ số từng nhát đúng nguồn. Thiếu precision thì ghi unsupported, gửi case cần quyết định và tiếp tục phần không phụ thuộc. Không dùng `combat.effect` chung làm bằng chứng damage/status/hit.

### QOD-C — chuỗi khám phá P00-01..05 và thưởng

Sau acceptance P00-01, mở rộng các quest kế tiếp có đủ dữ liệu canonical; bổ sung talk/exploration/collect/kill semantic theo từng objective. Mỗi mục tiêu có event server, record/map/floor/range/LOS/prerequisite và dedupe scope phù hợp; nhiều objective cùng target không được mất tiến triển do dùng chung contribution key sai scope. Skip/end cinema không tự cộng quest/reward.

Trang bị/túi/thưởng dùng service đã có; chỉ thêm hành vi còn thiếu, không viết lại module ổn. Cấp đúng item/currency/XP đã hỗ trợ, schema mới cần proposal. Quest thiếu số hoặc definition giữ trạng thái blocked có nguồn, không viết tiến độ giả để demo hết chương.

### QOD-D — E2E và bàn giao client toàn luồng

Hoàn thiện QOD-15: một lệnh start/scenario từ clone mới cho default-OFF và dev-synthetic, đi hết accept → tương tác → progress → turn-in → readback → retry/parallel không nhân thưởng. Có disconnect/reconnect, stale/out-of-order, entity despawn, wrong map/floor và cleanup session/claim/cooldown. Thêm kịch bản nhiều client với số client/giới hạn đo rõ, không gọi đó là benchmark MMO live.

Giao Codex request/response/event examples và feature matrix chính xác cho adapter quest/inventory/target/VFX/audio; server timing và hit/status/cancel/end đủ correlation. In-memory mất sau restart phải ghi rõ. Durable DB/auth/economy live là giai đoạn có proposal riêng sau correctness; không mở payment/market/guild/PvP live trong gói này.

## 4. Muse — hai bộ art lớn và một gate engine

Issue chủ #1, VFX #39, cinema #29; sửa tiếp PR #22. Không đổi ownership sang code server hoặc schema tooling. Không yêu cầu PC local cài Unity. Ghi checkpoint VM/branch và công cụ nào đang dùng được; không có bằng chứng mới thì trạng thái vẫn chờ bàn giao.

### MUSE-A — bộ art Bến Mưa chơi được

1. Hoàn thiện quality gate ba pose S/SE/N của Minh Kiếm48×64 native, top-down XY, foot pivot/20PPU. Đối chiếu concept đã duyệt, sửa palette/tóc/giáp/guard và `.meta` Bilinear→Point/no mipmaps trong phạm vi của Muse. Sau gate mới nhân thành8hướng idle/walk/run/combat thiết yếu, rồi các action phụ của PR #22. Không đưa jump/fall platformer vào gameplay; Shift không tự biến thành tăng tốc.
2. Giao kit Bến Mưa: tile16px, terrain/nước/bờ/cầu/nhà/cây/đá, NPC/monster/node/portal sprites và anchors theo record IDs. Có editable source, native atlas, layer/occlusion/collision proposal, scale/origin/WU mapping, blockout đường khám phá. Topology draft giao Qoder, Codex review; không tự đặt REVIEWED.
3. UI art: HUD sáu skill trên vòng cung quanh attack, status/quest/minimap; inventory/equipment/forge trước, rồi settings/compendium/appearance. Có button states, icons, 9-slice và mockup720p/1080p/20:9. HUB_WIDE mở world view, HUD giữ kích thước đọc/chạm độc lập.
4. Thăng Long là modular kit tiếp theo: nam môn, chợ/lò rèn, quảng trường PvP với bbox/origin và mô-đun dùng lại. Quy hoạch2048×1536WU/12phường vẫn design-only; không thu thành một ảnh map nhỏ, không vẽ toàn thành bằng hàng trăm ảnh unique hoặc tự bật bounds runtime.

### MUSE-B — combat VFX và kể chuyện có chiều sâu

- Giao gate #39 Phản Quang/Mưa Tinh bằng frame trong suốt native, prep/release/hold/end, attach/pivot/timing/LowFX/icon và preview; sau review triển khai cả30skill theo5board/30card, chia lô có thể review. Sheet runtime khác concept board, hướng/clip không được đoán bằng mirror khi tạo hình bất đối xứng.
- Cinema #29: sáu keyframe/contact sheet opening với Ly An/Bến Mưa, nhịp khám phá/cảm xúc và nút thắt theo cinema pack; sau storyboard review dựng animatic rồi video. Giao editable/video/subtitle/timecode/shot sidecar và avatar variants theo spec. Bản thoại VI_EDITED_P1 dùng CSV mới, 215 dòng còn baseline chưa được sản xuất voice hàng loạt.
- Audio #55 đã merge `c85c037`: 195cue/541clip có master/score. Dùng cho audition/animatic có ghi candidate; không tự ghi spoken NPC đã có, không dựng stinger chung thành cinema picture-locked. Đặt tên/source/timing của mọi âm thêm mới, tách background/VO khi bàn giao.

### MUSE-C — kiểm chứng Unity cho lô tích hợp, khi VM cho phép

PR #51 client của Codex vẫn draft: import/compile/play trong checkout riêng, ghi exact head/Editor/packages/full logs và video thật. Kiểm login/session flow, XY8hướng, HP/MP authoritative, journal/bag, six-skill arc, reconnect và safe area. Báo file/line/log cho Codex sửa client; không sửa server hoặc builder ngoài phần đã sở hữu.

Audio audition kiểm loop/mixer/mute/voice count và đổi map. Thiếu AudioManager chưa thể kiểm gameplay thì ghi NOT_CONNECTED, chỉ audition standalone và trả dependency Codex. Chưa có engine/license thì chuyển nguồn art, native sheets, storyboard hoặc map kit; không để toàn bộ Muse dừng theo một gate Unity.

## 5. Codex và các điểm giao nhau

Codex nhận review các PR, quyết định precision/proposal, client #51, adapter quest/world/audio, biên tập thoại và nghiệm thu. Không lấy lại code server/tooling/art đã giao. Không merge #53/#54 khi còn finding transaction, #43 khi migration vẫn xuất output invalid, #51 khi chưa có engine evidence.

OpenCode → Muse: validator/preview/bundle và finding; Muse → Qoder: topology/anchor draft có scale; OpenCode → Qoder/Codex: BuildCandidates/source map; Qoder → Codex: contracts/events/read model đã kiểm; Muse → Codex: art/Unity evidence; Codex → Muse: source/concept/audio và review. Các artifact có SHA, không copy-file thủ công vào checkout của nhau.

Trong issue chủ, xác nhận nhận cả gói, milestone đang làm, worktree/branch, PR dependency và bước tiếp theo. Nếu đang có draft của chủ dự án trong app, không ghi đè. Giao việc qua GitHub là thông báo đã gửi, chưa phải bằng chứng agent đã đọc hoặc tự chạy nền; báo riêng acknowledgement và sản phẩm khi có.
