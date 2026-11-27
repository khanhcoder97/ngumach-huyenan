# Review bàn giao agent — 09/11/2026

Đọc đầy đủ lịch sử issue bằng pagination, đối chiếu hai nhánh Qoder riêng và kiểm trong worktree pin theo SHA. Integration đã nhận PR129 tại `f715436367dc78116505abd1b960ce64e2652060` sau 9/9 check thành công: đây là baseline quyết định và work33–37, không phải merge gameplay. Gói38 tiếp các epic34–37 với thứ tự sửa dưới đây.

| Agent / PR | Pin review | Kết quả độc lập | Quyết định |
|---|---|---|---|
| OpenCode #109 | `9d4d811c6eb888307906fb3c6c2b29f3ac74115b` | 317/317 unit PASS; probe default identity nhận encounter của owner khác | Giữ lỗi wire cũ đã đóng; chặn adoption ClientSession tới khi sửa owner guard |
| Qoder #106 | `4cada354fc9efc1f1f4fff9c1d8acf9bccba6731` | Build sạch; 626/626 self-check; content và 35 schema/example PASS; public HTTP finale FAIL ở assertion đọc state cũ | Chưa nghiệm thu finale/portal; sửa runner rồi chạy lại |
| Qoder #91 / root | `fd04619326eb1ed19c1596622b48b2a35d320b4e` | Content validation FAIL37; branch tách khỏi QOD21; thay validator v1 không có contract tương ứng | Không merge hoặc cherry-pick nguyên gói; hợp nhất công việc trên QOD21 qua patch đã review |
| Muse #119 | `14b588c663a6d53295b34f1d632e84c48c7f5ca9` | 783 audio +107 cinematic references đúng byte/hash; policy PASS;21/21 playback entry có audio stream | Nhận checkpoint kỹ thuật có giới hạn; chưa nghe/native/final motion |
| Remote #98 | `5371a4675fbd8fc4b41b4748f2b1732ef2d81824` | Không head/ACK/source mới; chưa có tracked project/test/harness | R1 còn nguyên; chưa có cơ sở gọi đang chạy hoặc hoàn tất |

Snapshot CI lúc review: OpenCode21success; Muse11success; Qoder106 có29success/1failure (`e2e-alpha-p00`); Qoder91 có6failure/2success. Số này là check-run snapshot, không thay output độc lập. Không suy toàn stack sẵn sàng từ màu CI.

## OpenCode: owner guard bỏ qua identity server cấp

`Shared/ClientCore/Composition/ClientSession.cs:374` chỉ so `RegisteredCharacterIds` với `_characterId` khi constructor được truyền characterId. Field này readonly, không được cập nhật bằng `Client.World.self.characterId` sau Connect. Đường mặc định để server cấp character vì vậy chỉ kiểm shape.

Probe trong `Harness/OwnerProbe` gọi public API ClientSession qua transport fixture: Connect thành công với world `CHR_TEST`; encounter response đúng envelope/schema nhưng registered owner là `CHR_FOREIGN`. Cùng payload:

```text
explicitRequestedIdentity=False actualActor=CHR_TEST suppliedOwner=CHR_FOREIGN accepted=True outcome=Success deliveries=1
explicitRequestedIdentity=True actualActor=CHR_TEST suppliedOwner=CHR_FOREIGN accepted=False outcome=Error deliveries=0
```

Đây là lỗi defensive validation phía client, không phải bằng chứng server thật đã lộ snapshot khác owner. Cần capture authoritative identity cùng session epoch từ world/session đã connect, kiểm cả default/explicit/relogin/queued response; mismatch không cập nhật view/cache/event. Không lấy request preference làm authority. 317 unit hiện có kết thúc PASS nhưng chưa bắt đường default này. Không báo regression wire TALK/portal cũ còn mở: conformance, LF-normalized pins và bounded transport/adoption đã có tiến triển thật.

Handoff mới trên #85 bị mất dấu thành `?`; source/ADOPTION đọc được. Viết lại handoff bằng UTF-8 từ source/log thật. MAP_VIEWED đã có quyết định owner trên integration; còn thiếu server contract/implementation không được đổi thành “chưa có approval”. Native adoption thuộc Codex, chưa nhận ClientSession có finding này.

## Qoder: hai nhánh không đồng nghĩa một bàn giao

Merge-base QOD21 `4cada354` và QOD18/root `fd046193` là `ae2108809668cdd42534885b5d69b762f1eef72c`. QOD21 có node overlay, TALK, finale runner và partial MAP_VIEWED; root thêm catalog30skill, sửa canonical quests/runtime và report hoàn tất theo đường riêng. Không cộng số test hoặc tính năng của hai nhánh thành một build.

Root validator thực tế báo37 lỗi: role/weapon/targeting enums không thuộc schema; C1 có field không cho phép, MAP_VIEWED chưa được định nghĩa, targetIds rỗng, unlock sai type; BLOCKED thiếu gap, master token không resolve. `qoder-root-content-full.txt` giữ cả stderr và stdout. Contracts23/23 PASS chỉ kiểm schema/example đang có, không chứng minh validator runtime khớp. `P1Validation.SkillIdPattern` đã nới từ `^SK-MK-0[1-3]$` sang nhiều class/số mà không có thay đổi contract tương ứng.

`CreditMapEnter` và `ResolveClassMasterToken` chỉ có definition, không thấy production caller bằng rg. Không gọi implementation hoàn tất từ helper chưa nối. MAP_VIEWED đã duyệt là explicit `POST /p1/quests/map-viewed` với questId, không được credit do vào map/GET/portal. C1 alpha giữ objectives REPRESENTATIVES và TRIAL_REGISTRATION, append MAP_VIEWED theo approval; root đổi mục tiêu và sourceRef không thể thay baseline đó. P00-02 ACTIVE/canonical/runtime additions phải quay về quyết định overlay có gate/provenance.

Root còn đưa `temp_rgba.png` và `test.png` của workspace user vào diff. Chỉ loại khỏi proposed patch trong môi trường riêng và giữ nguyên file/history; không reset/clean hoặc xóa file người dùng. Completion report root tuyên bố source/boss/fragment thiếu trong khi QOD21 và owner approval đã có; cần sửa báo cáo dựa trên branch/head thật. Không cherry-pick toàn catalog vào v1 để né schema/model cast range/effect radius/status.

QOD21 pin4cada build Release0warning/0error, self-check626/0, content PASS và contracts35/35 PASS. Public HTTP chạy bằng server process riêng port5211 với profile enduranceHP2000/MP500 và gates alpha/TALK/portal. Runner dừng:

```text
FAIL: class confirm credited after successful TALK: 0
```

Tại `e2e_p1.py:2669`, assertion đọc biến `quests` lấy **trước** TALK; fresh `quests_after_talk` chỉ được fetch ở sau assertion. TALK HTTP200 đã qua check trước. Vì vậy FAIL này chứng minh runner không thể nghiệm thu finale; chưa chứng minh handler bỏ credit. Không sửa server theo state cũ hoặc bỏ assertion để đổi màu CI. Phải đọc quest mới, assert result/credit/READY/turn-in/chapter thật rồi đi tiếp.

Đoạn portal chưa chạy cũng sai approved source: dùng `BEN_MUA_THANH_LAC`, đích186, unpack dictionary `self`, và helper sinh key mới nhưng check replay cùng key. Registry đã đúng `TP_BM_THANH_LAC`: BM348→TL8; `TP_TL_BEN_MUA`: TL20→BM348. Cần giữ nguyên idempotency key/body để replay, changed body409, refusal đúng map/range và return journey thật. Không đổi registry theo expectation sai. Owned process4816 đã dừng trong finally; port5211 không còn listener. Raw server log6MB chỉ giữ local, output chọn lọc trong Evidence.

## Muse: checkpoint media đã tiến, dừng lặp QA cùng bytes

Source mới đã có đủ20 campaign mix cùng prologue; runtime audio783 gồm22 music/ambience,519SFXvariants,50VO,30mix,162composed. Có score/stems/transitions/intensity, voice palette, ambience variants, P0/campaign motion draft và ear audition pack196items/7playlists. Không giao lại phần metadata/mix đã hoàn thành.

Worktree Windows pin14b588 hydrate runtime audio/cinematics bằng LFS; audit độc lập783 audio references và107 cinematic references đều đúng size/hash, không mismatch. Owner policy validator PASS với22realOGV,380JSON/SRT,zeroCR. FFmpeg kiểm presence audio và decode50ms đầu mỗi21scene OGV:21embedded/0silent, exit0. 176fallbackfiles đã xác minh. Đây là runtime subset, không phải fsck toàn bộ source masters/7media roots hoặc proof download qua proxy. LFS cache có byte đúng không chứng minh đường network lỗi đã sửa.

M-G CP1/2/3/5 lặp fresh-checkout trên cùng783runtimebytes; CP4 là static Windows audit. Không tiếp tục tăng checkpoint bằng clone/hash cùng payload khi không có binary/policy/tool delta hay failure. Giữ một baseline QA và ghi exact delta.

Motion P0 A/B là DRAFT_POSE_ANIMATION/source candidate, runtime chưa thay. Source mô tả nhiều pose/procedural frames; chưa xem clip nên không kết luận đây chỉ là KenBurns hay đã đạt final animation. Cần giao một P0 review candidate có contact sheet/cut, timings và A/B selection rationale để Codex xem/nghe/ghép thử; cảnh chưa qua review giữ DRAFT. Ear pack vẫn NOT_AUDITIONED, chưa có ear audition, native Godot playback/export, full-stream decode/loudness remeasurement hoặc final casting/motion acceptance trong lượt này. Embedded soundtrack cần native chọn đúng một đường phát, tránh bật lại external mix/VO.

## Remote và việc tiếp theo

Persistence ở5371a46 vẫn chỉ có interface/feature gate, không project/test runner theo giao R1. Local Qoder gửi DTO không là Remote ACK. Giữ work36 đầy đủ: R1 buildable module trước rồi atomic transaction/fencing/two-process crash/recovery/outbox/adapters, clean clone tests>0/TRX. Không chuyển DB sang Qoder local thành writer thứ hai.

Gói38 giao sửa cụ thể kèm tiếp epic34–37; Codex giữ native/graphics/UI/UX/VFX/camera và nhận subset sau fix. Không merge gameplay hoặc media toàn bộ, không mở production gates. Chỉ comment đã gửi thành công mới gọi là đã giao; không đồng nhất assignment với agent đang chạy. Root workspace không bị sửa trong lượt review; toàn bộ bằng chứng/commit điều phối ở worktree riêng.
