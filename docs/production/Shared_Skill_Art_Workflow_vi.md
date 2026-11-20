# Quy trình asset kỹ năng dùng chung

Mỗi nhân vật chuẩn bị ba hướng nguồn là Bắc, Đông và Nam. Hướng Tây lật sprite Đông. Đông Bắc và Tây Bắc dùng thân Bắc. Đông Nam và Tây Nam dùng thân Nam. Hướng ngắm dùng đủ tám hướng và VFX luôn lấy hướng ngắm gốc.

| Động tác trong hồ sơ kỹ năng | Clip dùng lại |
| --- | --- |
| `STRIKE` · ra đòn | Đánh thường |
| `BRACE` · trụ thế, thủ hoặc tụ lực | Đứng |
| `STEP` · cơ động | Bước |

Mỗi clip thân giữ 16 tư thế nguồn. Khi thêm kỹ năng cho một nhân vật đã có ba động tác này, phần hình ảnh chỉ cần dựng VFX riêng nếu hiệu ứng chưa có trong thư viện. Nguồn VFX vẽ một lần trên nền trong suốt, gắn với tọa độ thân, đích hoặc điểm kết thúc. Hiệu ứng có hướng thì xoay theo hướng ngắm. Vòng đất và biểu tượng trạng thái dùng hướng màn hình khi cần giữ bố cục.

## Thử và chỉnh trong Godot

```powershell
& ./ClientGodot/Run_Skill_Assembly.ps1 -Profile SK_TC_01 -Caster CLASS_THACH_CHUY
```

Chọn nhân vật trên thanh công cụ. Timeline, hiệu ứng và dữ liệu kỹ năng giữ nguyên khi đổi nhân vật. Chọn lớp VFX để chỉnh thời điểm, vị trí, điểm bám và kích thước, sau đó dùng **Xuất bản chỉnh JSON**. Chọn **Mở bản chỉnh JSON** để nạp lại. Tùy chọn `-Legacy` mở bộ hồ sơ cũ với các động tác riêng đã dựng.

Studio có 18 kỹ năng để thử trên năm lớp nhân vật. Sáu kỹ năng Thạch Chùy dùng 20 atlas VFX đã vẽ, mỗi atlas có 16 tư thế. Trấn Sơn và Chấn Địa dùng cùng động tác ra đòn và căn khung giữa của động tác theo mốc tác động riêng. Các biến thể trúng, trượt, chắn đường và hết trạng thái minh họa khi nào từng lớp nên xuất hiện. Cấu hình này phục vụ dựng và kiểm hình. Điều kiện học kỹ năng, sát thương, tài nguyên và xác nhận trúng đòn trong trận vẫn do hệ thống gameplay xử lý.

## Thêm kỹ năng

1. Chọn ID kỹ năng, một kiểu động tác chung và các biến thể cần xem. Hồ sơ kỹ năng chỉ chứa timeline và ID hiệu ứng.
2. Dùng component đã có hoặc đăng ký PNG nền trong suốt, các vùng frame và điểm neo. Chỉ thêm sprite thân khi thật sự thiếu động tác chung hoặc cần một tư thế đặc trưng.
3. Chạy `python Tools/ArtProduction/build_compact_skill_assemblies.py` để cập nhật bộ xem mặc định. Dùng `--check` để soát tính tái lập của dữ liệu và mã băm PNG.
4. Chạy `ClientGodot/Run_Skill_Assembly.ps1 -SelfTest`, đổi nhân vật trong Studio và soát mốc tác động cùng bố cục ở góc chéo, hướng Tây và chế độ LowFX.

Hàng đợi mới nằm ở `Art_Source/Actor_Library_20261107/shared_production_plan.json`. Tạo lại bằng `python Tools/ArtProduction/build_actor_library_plan.py --shared`. Hàng đợi này tập trung vào 50 động tác nền của năm lớp, mỗi động tác ba hướng thân. 30 mục kỹ năng chỉ lập yêu cầu cho VFX dùng độc lập. Các hạng mục môi trường và sinh vật tiếp tục theo đặc tả riêng.
