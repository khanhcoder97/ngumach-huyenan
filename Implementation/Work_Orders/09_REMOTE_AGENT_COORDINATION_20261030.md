# Điều phối Antigravity và QODER Remote qua GitHub

Ngày giao: 2026-10-30, Asia/Tokyo. Chủ dự án yêu cầu tạo nhánh và chia thêm việc cho hai agent trên máy khác; nhận cả epic, triển khai code và bàn giao lên GitHub. Đây là lệnh giao việc, chưa chứng minh agent đã nhận hoặc code đã hoàn thành.

## 1. Nhánh và baseline

Repo: https://github.com/khanhcoder97/ngumach-huyenan . Remote machine dùng clone riêng, không cần truy cập ổ D: của máy điều phối.

Issue nhận việc: [Antigravity #80](https://github.com/khanhcoder97/ngumach-huyenan/issues/80), [QODER Remote #79](https://github.com/khanhcoder97/ngumach-huyenan/issues/79). Agent comment ACK và cập nhật milestone tại issue tương ứng; điều phối chung tại [#4](https://github.com/khanhcoder97/ngumach-huyenan/issues/4).

| Agent | Nhánh giao việc | Code baseline trước commit giao việc | Epic |
|---|---|---|---|
| Antigravity | `antigravity/ag-01-player-ui-20261030` | `92adee098fcb58acb5b280dcb167db9beecb8932` — client PR #51, chưa merge main | UI người chơi, túi đồ, journal, NPC, settings, bản đồ và accessibility |
| QODER Remote | `qoder-remote/qr-01-durable-state-20261030` | `8298c61058e5016f8a0fe86d3dd4a9b815596a49` — main | Thư viện DB, transactions, ownership, session recovery, outbox, migration và restore |

Hai nhánh chứa cùng bộ work order 09–11. SHA trên là điểm xuất phát của code, không phải SHA bàn giao cuối. Không đoán main đã chứa server v2/client v2. Đọc dependency trong PR trước khi tích hợp.

Snapshot công việc song song: Qoder local đang ở PR #78 `72da690b25d58e2df91c1d4852a25c6b86d3e55e` trên #77 `f3b37ddbb04caae29bbbb9202f510806d9f6d136` và #75 `32d57bcc4ad76e7a8cc1545bb73240fa454402ae`; fix replay #76 `514c3f20c077175c7752706d845d11d78d464eda` là nhánh riêng, chưa mặc nhiên có trong #78. OpenCode #43 đã tiến tới `85127fae4d9e582d606637468476308fcde14648` và có worktree OPC-07..12. Đây là snapshot, phải fetch và đọc lại issue trước khi tiếp tục.

## 2. Owner hiện hành

| Owner | Được sửa trong gói này | Không ghi đè |
|---|---|---|
| Antigravity | Client UI mới, view-model và test thuộc work order 10; glue UI cũ trong giới hạn ghi rõ | Transport/combat/audio core, server, art Muse, tool OpenCode |
| QODER Remote | `Server/Persistence/**`, `Server/Persistence.Tests/**`, `Server/Persistence.Harness/**`, proposal/evidence của gói 11 | `Server/Health/**`, gameplay/canonical contracts, runtime compiler của Qoder local |
| Qoder local | Stack server gameplay, quest, combat, loot, spawn, integration adapter vào Health sau review | Không tạo DB library cạnh tranh với QODER Remote |
| OpenCode | Asset validator/preview/bundle/CI, content candidate compiler và Muse map adapter | Gameplay authority, client UI và DB library |
| Muse | Pixel art/sprite/animation/tilemap/UI artwork/VFX/cinema, native engine art acceptance | UI business logic, runtime protocol và persistence |
| Codex | Điều phối, correctness review, tích hợp, quyết định design còn thiếu và audio | Không sửa song song file đang giao nếu chưa cập nhật issue |

Quyền này tách ownership phần durable implementation khỏi backlog QOD-20 cũ. Qoder local vẫn chịu trách nhiệm nối storage đã review vào command handlers; không tự bật persistence hoặc gọi DB harness là MMO chạy thật. Codex nhường phần UI mới cho Antigravity; PR #51 vẫn cần native Unity/device acceptance.

## 3. Quy trình nhận việc trên máy khác

Nếu chưa có clone:

```sh
git clone https://github.com/khanhcoder97/ngumach-huyenan.git
cd ngumach-huyenan
git fetch origin
```

Antigravity chạy:

```sh
git switch --track origin/antigravity/ag-01-player-ui-20261030
```

QODER Remote chạy:

```sh
git switch --track origin/qoder-remote/qr-01-durable-state-20261030
```

Nếu đã có local branch thì `git switch <tên-nhánh>`; không lặp `--track` để thay branch đang tồn tại. Nếu clone đang có thay đổi chưa commit, dùng clone/worktree khác, không reset/clean/stash hộ người khác. Không cấu hình lại credential hoặc gửi token qua issue. Repo public cho phép đọc, **push/comment cần quyền GitHub đã đăng nhập**; nếu không có quyền push, dùng fork và mở PR về repo gốc.

Đầu tiên comment vào issue riêng: agent/máy biệt danh, branch, HEAD, clean/WIP, toolchain và milestone bắt đầu. Không đăng username máy, đường dẫn cá nhân hoặc secret. Sau ACK bắt đầu code ngay; không dừng sau kế hoạch. Issue là kênh nhận việc và tiến độ, không giả định việc tạo issue đã tự khởi động agent trên máy khác.

## 4. Bàn giao bắt buộc

1. Mỗi milestone đủ lớn có commit/push và PR linked issue; không dồn cả epic thành một diff khó review. Nhánh đầu tiên dùng đúng tên đã cấp; các nhánh sau giữ prefix `antigravity/` hoặc `qoder-remote/`, tạo từ checkpoint đã ghi rõ.
2. Antigravity mở PR đầu về `codex/p1-client-integration-20261029` để chỉ hiện diff UI, ghi dependency #51. Nếu #51 đã merge thì rebase/retarget sau khi kiểm baseline. QODER Remote mở PR đầu về `main`; storage là module độc lập nên không kéo toàn stack Qoder local vào PR.
3. Các PR tiếp theo có thể stacked trên milestone trước; ghi base/dependency, không tự merge main hoặc force-push nhánh của agent khác. Dùng `Refs #<issue>` ở milestone; chỉ đóng epic khi toàn gói đạt nghiệm thu.
4. Báo cáo `Implementation/Reports/AG01_*` hoặc `QR01_*`: source HEAD, file list, tool/OS/version, lệnh chạy, output và exit code, fixtures, ảnh/video/log nếu thực sự chạy, known gaps, integration instructions. Không tự khai hash của commit chưa được tạo; báo evidence commit bằng comment sau push.
5. Không đưa DB/save người thật, credentials, Unity Library, caches, build output lớn hoặc runtime clip gốc ngoài LFS policy vào git. Synthetic test data phải ghi nhãn. Chưa chạy Unity/HTTP/device/crash test thì ghi UNVERIFIED/BLOCKED theo đúng phần đó.
6. Cập nhật issue sau mỗi milestone và khi có blocker; khi chờ review, làm tiếp module/test/docs độc lập. Không dừng cả epic sau một PR và không tự bịa source/endpoint để báo hoàn tất.

Mẫu PR cần có: vấn đề và hành vi sau sửa; scope; exact base/source/dependencies; cách chạy từ clone sạch; test thực tế; giới hạn; bước tích hợp của Codex/Qoder local. Các thay đổi contract ghi proposal trước, chưa duyệt thì UI/action ở trạng thái unsupported, không fake success.

## 5. Gates chung

- Unity 6.3 LTS / URP 2D, pixel top-down XY, 8 hướng; 20 PPU, Point, tile16px = 0,8WU. Không đổi engine hoặc chuyển sang isometric/3D.
- DEC-019: 6 slot skill theo vòng cung quanh nút đánh thường. DEC-021: HUB_WIDE960×540, combat640×360; HUD không co nhỏ theo world zoom.
- DEC-023: 100 ô túi = 4 trang ×25 ô5×5; đầy túi giữ quest READY; stat alias không cộng hai lần; max HP/MP đổi giữ current tuyệt đối và clamp, không tự heal/revive. Không có Undo item/heal đã commit.
- Không đổi canonical IDs/349XY/map review state. UI chỉ trình bày state server đã xác nhận; in-memory, synthetic fixtures và offline preview có nhãn rõ. Không dùng thông số browser demo làm dữ liệu production.
- Mốc cuối vẫn cần Codex review, tích hợp server/client và bằng chứng engine/device. Hai epic này không bao gồm toàn bộ game và không chứng nhận production-ready.
