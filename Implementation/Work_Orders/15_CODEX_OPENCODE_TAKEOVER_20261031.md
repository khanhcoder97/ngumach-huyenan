# Codex nhận bàn giao toàn bộ phần OpenCode

Lệnh chủ dự án: nhận bàn giao toàn bộ công việc OpenCode và làm tiếp. Owner update đã đăng tại [issue40](https://github.com/khanhcoder97/ngumach-huyenan/issues/40#issuecomment-6525476066). Không giao lại các phần này cho OpenCode; tiếp tục trực tiếp bằng code/tests/PR của Codex.

## Checkpoint được giữ nguyên

| Phần | Exact HEAD đã nhận |
|---|---|
| Coverage #31 | `628d043bcc371e3d123796c58c758d709e4d6776` |
| Manifest/migration #43 | `85127fae4d9e582d606637468476308fcde14648` |
| PNG/meta #61 | `7886193d0656abb2a719d930930d04b1b529c18d` |
| Preview #62 | `40922893a7e6394ebbecda1fa842bfd45cccb4dc` |
| Pack/unpack #67 | `e3dab0dd03ef40cd2001460cda5cf96934e8f266` |
| One-command/CI #69 | `e4542e9280dec7fc2e5114e4c975cf0d13bddeb8` |
| OPC11 compiler | Untracked WIP10files/145725bytes tại `D:/opc05b-wt-11`, đã snapshot+SHA256 trước tiếp nhận |
| OPC12 map adapter | Checkout từ main8298c61, chưa có implementation tại checkpoint |

Backup local: `D:/Project/NGUMACHHUYENAN-tools/handoff/opencode-20261030/` gồm WIP và snapshot hashes; không chứa credential. Hai phiên CLI dự án đã idle, scoped interrupt trả interrupted:false; shared OpenCode service/model/auth không thay đổi. Không reset/clean/stash hoặc chỉnh WIP ở checkout gốc của OpenCode, Qoder hay agent khác.

## Thực thi của Codex

1. Nhánh `codex/opencode-takeover-20261030`: tích hợp đúng các heads trên, xử lý workflow/README conflicts, giữ cả coverage và PNG/migration/pack checks; tái tạo coverage theo catalog556/2236 hiện hành. Kiểm CLI/HTTP/pack/digest/negative inputs và browser thật với asset Muse, không lấy findings lịch sử ở heads cũ làm kết quả mới.
2. Gói code tiếp trên nhánh riêng sau checkpoint tích hợp: hoàn OPC11 CLI/build/check/diff/tests và bundle candidate có nguồn/units/digest/field-level unresolved; OPC12 sidecar importer với schema/input budgets,16px/20PPU, atlas/pivot/8directions, layers/props/original→candidate XY. Tạo generated candidates có nhãn, không ghi runtime/Qoder sources.
3. Một command và CI từ clone sạch chạy asset pipeline + compiler + map adapter; missing/LFS/corrupt/stale/ref/digest phải fail. Browser kiểm thật khi được yêu cầu; Unity/native/device riêng UNVERIFIED tới khi có môi trường.
4. Bàn giao cho Qoder/Codex client/Muse bằng exactSHA/CLI/examples/unresolved report, tiếp implementation thuộc tooling thay vì chờ một giao việc nhỏ khác. Không tạo nguồn IDs/catalog/compiler cạnh tranh với canonical source, không tự REVIEWED placements hoặc kích hoạt dữ liệu chưa duyệt.

Quyền tool này không chuyển quyền server gameplay, DB, PlayerUI hay artwork. Existing PRs OpenCode là lịch sử/dependencies tới khi nhánh tích hợp được review; không đóng hàng loạt chỉ vì đã merge chúng vào một nhánh WIP, chưa merge main.
