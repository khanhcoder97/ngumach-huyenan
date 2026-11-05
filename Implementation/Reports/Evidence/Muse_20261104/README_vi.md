# Bằng chứng review Muse trên Windows — 04/11/2026

Source #111: `765a0d62ac597b8b9fbc07ae2a5a89a8a1f60b46`. Source #112: `bf75cc784123292657458ccc867738a4f8d06b9e`. Server P1 của bài online: `42a44914f0f3e8c9bfedcde6aa36a9581f59f5af`, build riêng tại worktree review; mặc định alpha OFF. Không dùng server của người chơi.

- Máy: Windows, i3-4030U, RAM khoảng8GB, GeForce820M. Godot4.7.2 stable mono Windows, commit engine `ed1daf0bf`; Compatibility/OpenGL3.3, driver ghi trong gui-main.log.
- Godot zip chính thức SHA256: `a2a48473a7414c5f19fab690518caebb738c09ef9601f6bd2388676a7f53b3c0`.
- SDK8.0.404 zip Windows SHA512: `fe2a799726fafa252352e6397dd790717f7263903408ccfedb0fb275ba93f96a7840dacc7f188e94d87671313d2a48480ea8387408ed5772b43c363e2dbba1ba`.
- Cả hai đối chiếu metadata chính thức trước giải nén. Dùng portable tools, không bắt cài Unity. Không đưa SDK/engine binaries/cache vào Git.

`build-sdk8-clean.log`: restore với NUGET_PACKAGES mới, local feed được hydrate qua Git LFS, RestoreLockedMode=true, SDK8.0.404; build0error/7obsoletewarnings. `build-sdk10.log` là lần build tương thích riêng, không thay cho chứng cứ SDK8.

`native-sdk8/`: import ấm +8suite offline nguyên bản. 8/8 PASS theo exitcode+marker, **SELFTEST vẫn có8ERROR do4placeholder PNG thiếu**. Import có một EditorSettings shutdown error; không gọi log sạch hoặc bỏ qua bằng cách chỉgrep RESULT. Import lạnh Windows bằng SDK10 trước đó mất99,9s; import ấm SDK8 14,19s. Không dùng số này làm FPS gameplay.

`native-online/`: NETTEST PASS, ONLINETEST FAIL ở wall-slide (dx8,35/dy−1,06, ngưỡng|dy|≤0,9). `native-online-retest/`: chỉ chạy lại ONLINETEST một lần sau khi đóng GUI; wall-slide PASS nhưng north-distance FAIL (dy6,65, ngưỡng≤6,6). Giữ cả hai kết quả thất bại, không chọn lần có lợi. Server được mở/dừng bằng child PID, không dùng `fuser -k` hay giết process theoport.

`producer-main.log`: driver riêng `diagnostic_main.gd` load scene nguyên bản, kích trạng thái SetMoveInput(Zero,false) tương đương nhánh thả joystick và gửi InputEventKey D. Vị trí không đổi; sau ClearInjectedInput, cùng phím làm di chuyển21,33px. Đây là kiểm API/input của engine, **không phải thao tác drag chuột qua Windows**. Đồng thời Main có0TileMapLayer. Driver không sửa C# hoặc scene của Muse.

`source_asset_audit.json`: chỉ đếm PNG tracked, bỏ capture sinh sau. 71PNG/52.847.262byte đều hydrate, sheet khớp bảng48×64;4scene resource properties trỏ placeholder không tồn tại. World map450×60, cell0,8WU, blocked5.069unique;306watercells unique, đúngdelta0→1/ground/pathnull.

`gameplay_main_1280x720.png`: frame do chức năng screenshot có sẵn của client xuất bằng renderer thật, đã xem ảnh. Công cụ Windows Computer Use nhận được cửa sổ nhưng chụp hai lần bị timeout; không dùng nó làm bằng chứng click/touch. Ảnh engine và log chứng minh render khởi động, chưa chứng minh thao tác đầy đủ hoặc exported EXE chạy trên máy không SDK.

Các helper được lưu ở `Tools/ProducerReview/Muse/`. Ví dụ tái lập (thay đường dẫn theo máy):

```text
python Tools/ProducerReview/Muse/audit_source_assets.py <checkout> <output.json>
dotnet build <checkout>/ClientGodot/NgumachPrototype.csproj -c Debug -p:RestoreLockedMode=true
python Tools/ProducerReview/Muse/run_native_review.py --godot <console.exe> --project <ClientGodot> --dotnet-root <SDK8> --output <artifacts> --stage import
python Tools/ProducerReview/Muse/run_native_review.py --godot <console.exe> --project <ClientGodot> --dotnet-root <SDK8> --output <artifacts> --stage offline
python Tools/ProducerReview/Muse/run_online_review.py --godot <console.exe> --project <ClientGodot> --dotnet-root <SDK8> --server-dotnet <SDK10/dotnet.exe> --server-dll <Health.dll> --server-cwd <serverCheckout> --output <onlineArtifacts>
```

Online helper từ chối chạy nếu cổng5000 đang được process khác dùng vì source Muse hiện hard-code cổng này. Sau sửa client cho endpoint cấu hình, runner production phải dùng cổng ngẫu nhiên; helper này chỉ dành tái lập review hiện hành.
