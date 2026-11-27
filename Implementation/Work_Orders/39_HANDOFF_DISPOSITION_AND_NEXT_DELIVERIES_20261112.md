# Gói39 — disposition bàn giao và các khối việc tiếp theo

Ngày12/11/2026 JST. Tiếp work34–38 trên integration9ac73dc; review/evidence mới trong `Implementation/Reports/Review_20261112/Agent_Handoff_Review_vi.md`. Các epic34–37 còn hiệu lực. Từng checkpoint có source/fullSHA, actual delta, commands/output/CI và remaining gaps; ACK rồi push artifact, không dùng report thay implementation. Production OFF; không reset/clean/force-push hoặc đụng sửa dở của owner khác.

## OpenCode LOCAL — issue85, PR109, tiếp portable client

Pin85719a7 đã qua độc lập324unit; probe foreign owner mặc định/explicit đều từ chối, zero delivery. Đóng repro O38-A cụ thể. Nhận Escort/Trace/Media như source draft, chưa nhận toàn work34 hoàn tất.

**O39-A — projection có provenance trước adoption.** EscortPresenter hiện dùng NPC chứa chuỗi LYAN rồi fallback v1 khi v2 không có. Probe cho worldv2 ThanhLac/tick500 khôngNPC, worldv1 BếnMưa/tick10 có staticNPCx90 vẫn xuất escort InAudience/IsOnRoad tại ThanhLac/tick500. Sửa: chọn một authoritative snapshot/epoch nhất quán, không ghép v1 vào v2; generic NPC không thành owner escort do substring/toạ độ. Chờ packet escort/current đã duyệt, giữ trạng thái escort unsupported/not-served khi thiếu provenance, không chờ route mà đoán. Có packet thì bind owner/life/attempt/actor/instance/floor/sample, quest/lifecycle status; test static NPC, stale v1/v2, khác map/floor/owner, absent/late response. Trace fixtures giữ nhãn fixture, không là live combat acceptance.

**O39-B — media bridge đọc đúng artifact bàn giao.** MediaMetadata hiện là DTO host tự tạo, tests dùng Assets/Media giả. Thêm parser/loader portable từ PLAYBACK_METADATA_v1 thực của Muse (pin b1472f2), SRT fixture thực và canonical root-relative paths. Resolve/canonicalize dưới content root, chặn traversal/absolute/URI ngoài policy; role/ownership/codec/subtitle capability có type. Không dùng substring vo_/standalone để quyết audio. Probe hiện chấp nhận ../.. khi có trong AllowedPaths và cho phép WAV mix với EmbeddedSoundtrackOnly; chưa có filesystem player nên đây là boundary validation gap, chưa là exploit. Embedded mode chỉ chọn video soundtrack; external alternate mode phải rõ và mutually exclusive. Kiểm actual21entries, clean-video/SRT và burned-subtitle-review exclusion, fallback/seek/clock/seen/rewatch không grant gameplay. Host player/Godot/widget vẫn Codex.

**O39-C — paired evidence và disposition.** Encounter routes đã tồn tại trên4cada35 (`/p1/encounters/current`, `/{encounterId}`); domain404 encounter_not_found khi không có active owned encounter không chứng minh route thiếu. Probe khi encounter sống trước boss death/portal cleanup, observer/foreign404 là negative. Giữ consume/map-viewed/escort404/405 là chưa triển khai theo pin. Portal wire thuộc Qoder: giữ strict parser; typed success phải nhận receipt mới được gọi supported. Một suite exit0 có UNVERIFIED không là full alpha acceptance. `content_fingerprint` không được pass với zero/missing runtime sources; kiểm path-discovery/fingerprint đúng các file server thực nạp, negative control sai root. Không hash file khác rồi gọi pin runtime.

**O39-D — portable handoff tiếp.** Giao benchmark executable độc lập có warm-up/fixed workload, allocations/poll/eventbuffer/lane latency, distribution và environment/SDK; không tự gọi caps-test là low-device performance hoặc đặt production budget. Giao adoption matrix theo module, source dependency closure và sample dùng real metadata/provenance. Relogin/queued owner regression tiếp đủ, explicit preference không thay authoritative identity. First-party license giữ UNSPECIFIED; thêm LICENSE thuộc quyết định chủ dự án, không chặn sửa source/measurement. Không sửa compiler pipeline/Godot/server/media assets.

## Qoder local — issue87, đồng bộ41 và PR91/106

**Q39-A — khối P0 vẫn chưa bàn giao.** PR106 còn4cada35; PR91 chỉ thêm báo cáo tạifc86916 và vẫn FAIL37content. Root local có commit/sửa dở chưa đồng bộ: giữ nguyên, không reset/cherry-pick nguyên gói. ACK rõ fullSHA/nhánh sắp push trên QOD21, patch inventory cho delta QOD18. Sửa báo cáo “all completed”, phân biệt helper chưa nối, canonical BLOCKED và alpha overlays. Tiếp Q38-A→D, không dùng tổng kết WO32 cũ để đóng work38.

**Q39-B — thêm portal wire defect vào checkpoint finale.** P1Results.PortalSuccess serialize domain PortalResult với DestinationMapId/DestinationXWu/DestinationYWu; schema yêu cầu mapId/xWu/yWu và additionalProperties=false. Map domain receipt sang wire DTO đúng schema; giữ semantics/revision/eventId/cleanup/idempotency. Kiểm JSON serialize thật của fresh/replay/refusal so schema và chạy typed client85719a7 hoặc head sửa O39 mới. Không đổi frozen schema theo DTO sai hoặc cho Core chấp nhận cả hai để xanh.

**Q39-C — finale→discovery→inventory giao theo thứ tự.** Sửa runner stale quests/portal ID/destination/replay như gói38; full public finale→348→8→20→348 và hai owner, level11 gate thật. MAP_VIEWED explicit acknowledgement, migration/one-shot/schema và escort same-sample provenance theo approval. Kế tiếp capacity100stack-slots/consume/effective-stat: planner atomic, inventory_full/no partial receipt, sourced HP/MP/no heal-revive, DEC023 oracles. Giao private test fixtures cho actual downed→return→replay→reconnect và fullbag quest READY/retry; không release seed endpoint hoặc grant giả. Client runner có thể mở assertion ngay khi có pin thật.

Encounter route đang tồn tại: cung cấp active encounter fixture/lifecycle checkpoints, không tạo route trùng để xử lý một domain404. Q-D→J work35 tiếp domain/contracts đủ nguồn song song; Persistence vẫn Remote, không DB writer thứ hai.

## Muse — issue116, PR119, tiếp media-only

**M39-A — bắt đầu sản xuất SFX đã chốt.** Nhận đề xuất CP2a và giao JSON `media_sfx_draft_execution_20261112.json`: P-GUARD +4weapon +grass, mỗi cue3variant =18draftvariants. Đây là quyền sáng tác asset/provenance/manifest/playlist, chưa là runtime key/event hoặc final audible approval. Giữ catalogue1cue/skill và shared miss/impact theo event thật; không phát minh60phase keys. Guard-expire không phát metal_parry/success. Giao khối guard+grass trước, rồi4weapon; đo peak/loudness/duration/codec, negative clipping/hash/source integrity. Không thêm Godot/gameplay code.

**M39-B — gỡ chờ đúng phạm vi.** Candidate M38-A/B, continuityv2,720p review và26hold slices đã có source; không dựng lại pack/clone cùngbyte. Giữ640runtime candidate,720MP4/3OGVsamples làm review; full246MBupscaledOGV deferred. Chưa có lựa chọn casting thì giữ originals; được làm level-matched review comparison trên palette hiện có, không thay runtime/commit final voice. 32shot character-lock cần Codex định sau, tiếp SFX độc lập ngay. Contact sheet P0 đã được xem trong review này; chưa đủ final animation/native/audition, không tự nâng DRAFT.

**M39-C — handoff cập nhật.** Source headb1472f2 đã có CP3b/3c/ME2a và subtitled720 nhưng issue116 còn tổng kếtc0caf22. Gửi một delta handoff fullSHA mới (artifact có sẵn, không thêm report-onlycheckpoint). Nêu exact candidate/timing/manifest supersedes và link approval mới. Runtime audio783 giữ nguyên tới khi delta asset được review; source standard720 không tự làm runtime audio count tăng. Production/generic player binding vẫn Codex.

## Qoder Remote — issue79, PR98, tiếp work36

Head5371a46 và R1 chưa đổi, không có ACK/source mới. Chưa đủ chứng cứ coi agent đang chạy. Khối kế tiếp giữ cụ thể: tracked library + test/harness projects, locked dependencies/config, clean-clone build/test count>0 +TRX; ACK môi trường/branch và push fullSHA. Nếu không chạy được, gửi command/error cụ thể để điều phối, không báo server CI là persistence PASS. Sau R1 mới transaction/outbox/fencing/two-process crash-recovery/restart adapter. Không giao local Qoder viết DB thay hoặc tạo writer thứ hai.

## Disposition các leg OpenCode hỏi

| Leg | Owner / quyết định |
|---|---|
| Portal wire | Qoder Q39-B, còn BLOCKED typed success tới fix; Core giữ strict |
| Encounter | Route có thật; OpenCode đổi thời điểm/domain probe, Qoder giao fixture |
| Consume/MAP_VIEWED/escort | Qoder work35/Q39-C; Core unsupported tới pin mới |
| Downed/fullbag | Qoder private fixtures + OpenCode paired acceptance; không chốt alpha hoàn tất |
| Native/player/graphics/UI/UX/VFX/camera | Codex; nhận subset sau provenance/media boundary fixes |
| License | Giữ UNSPECIFIED, không tự cấp license game; không chặn độc lập source/tests |
| Low-device performance | OpenCode portable benchmark trước; Codex native/device measurement sau |
| Media audible/casting/final motion | Codex/director sau xem/nghe thực; Muse được bắt đầu18SFXdraft ngay |

Codex chỉ merge coordination/source approval/evidence của gói này sau checks; gameplay/media stacks giữ review riêng. Comment gửi thành công là assignment; ACK/push/test/acceptance là các trạng thái khác nhau.
