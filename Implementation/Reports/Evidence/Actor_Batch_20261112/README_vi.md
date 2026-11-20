# Bằng chứng asset/animation/VFX — 12/11/2026

Các PNG là screenshot viewport Godot native, không phải concept ghép. `minh_dodge.png` và `boatkeeper_idle.png` xem 8 hướng, `minh_death_end.png` xem frame cuối của chuỗi gục. `kiem_tran_studio.png` xem thành phần và timing; `vfx_runtime_sheet.png` dùng chính SkillVfxPlayer của client, đóng băng để kiểm hình, không đo FPS.

`minh_dodge_preview.mp4` được Godot Movie Maker ghi 120 khung ở time step 1/60 giây, sau đó chuyển AVI sang H.264 bằng ffmpeg local. Đây là preview offline dài 2 giây; FPS mã hóa không chứng nhận FPS chơi game trên máy yếu. PNG nguồn không bị chỉnh/cắt/vẽ bằng ffmpeg hoặc Python.

`originals_preserved.json` đối chiếu đúng 46 PNG của snapshot lần chốt sprite cũ; các PNG mới không thay đổi baseline. Batch registry tại `Art_Source/Actor_Library_20261107/batch_20261112.json` liệt kê 14 sheet, 560 ô nguồn được gắn, 8 ô dư không dùng, prompt/hash/file runtime.

Các log chứa build, Studio self-test, actor-library binding checks, component runtime test và visual regression. Test kỹ thuật không thay thế nghiệm thu mọi chuỗi chuyển động hoặc chứng nhận game hoàn chỉnh.
