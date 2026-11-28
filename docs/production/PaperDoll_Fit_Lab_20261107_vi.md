# Phòng thử nhân vật paper-doll — 07/11/2026

Trạng thái: **công cụ authoring chạy được trong Godot**, chỉ dùng mẫu chưa duyệt. Chưa thay hero, chưa có wardrobe animation production hoặc tạo nhân vật online.

## Mở công cụ

Tại thư mục worktree có ClientGodot:

```powershell
.\ClientGodot\Run_PaperDoll_Lab.ps1
```

Launcher build bằng SDK .NET 8 đã khóa, import bằng Godot .NET portable rồi mở PaperDollLab.tscn. Có thể truyền -GodotPath/-DotnetPath nếu công cụ nằm nơi khác. -SkipBuild dùng khi đã build/import sau thay đổi gần nhất. Script chỉ đổi DOTNET_ROOT/PATH cho tiến trình hiện tại và khôi phục khi thoát; không sửa cấu hình SDK toàn máy.

```powershell
.\ClientGodot\Run_PaperDoll_Lab.ps1 -SkipBuild -Female -Indigo
.\ClientGodot\Run_PaperDoll_Lab.ps1 -SkipBuild -SelfTest
```

## Thao tác

1. Chọn base nam/nữ. Trái là coverage base, phải là look ghép lớp trên cùng body.
2. Chọn tóc, mắt, bộ áo/quần/giày, kiếm, mũ và áo choàng. Bộ đồ là preset thử gồm ba phần; từng phần vẫn có binding riêng.
3. Phát/tạm dừng, kéo timeline hoặc bước từng pose. Space phát/tạm dừng; Esc đóng. Đổi đồ không reset thời gian của actor.
4. Bật điểm neo. Chọn head/face/chest/hip/hand_near hoặc một part ở cột phải.
5. Chỉnh X/Y: với anchor là tọa độ master; với part là offset so với anchor. Mặc định chỉ sửa pose hiện tại. Tùy chọn “Áp cùng giá trị cho 16 pose” ghi 16 placement riêng.
6. Lưu/mở fit draft. Đây là dữ liệu authoring cục bộ, không equip hoặc trừ tiền.
7. Khôi phục guide gốc để bỏ chỉnh thử.

Chỉ S/idle có dữ liệu. Bảy nút hướng còn thiếu bị vô hiệu hóa, không lấy một ảnh quay mặt làm đủ tám hướng. Phóng 2×/4×/6× là zoom canvas chung, không kéo giãn riêng áo hoặc đầu.

## Mô hình dữ liệu và kiểm soát lỗi

- Nguồn: Art_Source/Modular_Characters_20261107/Sheets và Wardrobe_Study.
- Chạy python Tools/ArtProduction/export_paperdoll_lab.py để xuất catalog + sao chép PNG nguyên byte vào ClientGodot/assets/paperdoll_lab.
- --check xác minh catalog tái lập và PNG runtime giống byte nguồn. Không tạo, chỉnh, resample hoặc pack lại bitmap.
- Loader kiểm SHA-256 và đường dẫn allowlist của ba PNG trước khi dựng actor.
- Mỗi look đi qua ModularCharacterModel và cùng ModularCharacterRenderer. Đường review là internal, riêng công cụ; TryApply công khai vẫn kiểm production.
- Mỗi part có 16 placement gắn cùng body pose. Nguồn ảnh part hiện chỉ có một hình tĩnh, được báo đúng là một hình.
- Chỉnh anchor tạo fingerprint mới cho ứng viên đang authoring. Đây là thao tác thiết kế mới, không chứng nhận quần áo cũ đã fit.
- Draft lưu tại user://paperdoll_lab/fit_draft.json, gắn catalogueFingerprint. Ảnh, guide hoặc catalog thay đổi thì draft cũ bị từ chối.
- Import draft kiểm schema, ID, số placement, tọa độ và compile thử trước khi thay state. Lỗi giữ nguyên draft/preview cũ.
- Thiếu texture, vượt region/canvas, trùng slot hoặc sai rig không đổi dở một phần look.

## Hiệu chuẩn nguồn trong phòng thử

Ảnh tạo trước đây có kích thước nguồn khác nhau và chưa phải native master 96×96. Lab khai báo tỷ lệ cố định **6 source pixel / logical pixel cho toàn atlas body**, **12 cho toàn atlas trang bị**. Không tự scale mỗi món theo chiều cao alpha, không coi ảnh qua hiệu chuẩn là native pixel art.

SourcePixelsPerUnit được ghi trong draw command. Gameplay production bắt buộc giá trị 1 cho body và mọi layer. Mẫu review vẫn Approved=false và scope FIT_LAB_ONLY, nên không thể vượt gate chỉ bằng đổi tỷ lệ.

Guide ban đầu là seed được điều chỉnh qua render, còn cần fit từng pose. Không dùng alpha-bound heuristic như dữ liệu nghiệm thu cuối. Viền màu thừa của nguồn cũ vẫn là lỗi art đang giữ lại, không được che bằng báo cáo hash.

## Giới hạn hình ảnh đã thấy

- Base có viền màu/alpha thừa; nét chưa native pixel sạch.
- Áo và cape là hình tĩnh; không có đủ artwork deform theo pose.
- Coverage xám của base còn hiện tại vai; cần chia skin/coverage/arm thành pass đúng.
- Chưa có tay trước/sau để che cán kiếm chuẩn.
- Mũ hành lữ hiện ẩn tóc toàn bộ; chưa có tóc under-cap được vẽ riêng.
- Chưa có nhuộm theo palette/mask, skin tone, dấu mặt hay đủ preset khuôn mặt.
- Chưa có walk/run/attack/sáu skill và đủ tám hướng.
- Chưa có resolver item ownership, lưu diện mạo server, UI tạo nhân vật hoặc migration.

Hai screenshot nam/nữ là render thực của công cụ, không phải gameplay hoặc chứng nhận full animation. Screenshot đặt chữ “ảnh tĩnh · không đo FPS”; tránh dùng FPS ở vài khung đầu làm số đo.

## Điều kiện chuyển sang master thật

Khóa file nguồn layer 96×96, điểm chân (48,72), 16–20 pose thật/action/hướng. Tách coverage và skin; vẽ arm_far/arm_near, mask và paintOrder theo pose. Fit tóc/mũ/quần áo trên chính source master; kiểm bước chân, vạt áo, cán kiếm và lưng. Xuất offsets/anchors/fingerprint từ nguồn thật, duyệt hình và chuyển registry approved có SHA.

Pilot vẫn là Minh Kiếm nam/nữ với idle/walk/basic/skill01, 8 hướng, hai bộ đồ, hai tóc, hai kiếm, một mũ. Bộ lab hiện tại chưa hoàn thành pilot này. Gameplay yêu cầu đủ bộ action theo hợp đồng trước khi bật renderer modular cho hero.

## Kiểm chứng

Run_Modular_Character_Test.ps1 kiểm model hợp đồng. Run_PaperDoll_Lab.ps1 -SelfTest kiểm nguồn thật, renderer và signal của control. CI kiểm export tái lập và build C#; kiểm Godot native được chạy local và lưu evidence riêng.

Có thể đo cảnh preview bằng -Benchmark đường_dẫn.json. Báo cáo chỉ có hai actor preview, không đại diện đám đông Thăng Long Thành, gameplay combat hoặc thiết bị khác.
