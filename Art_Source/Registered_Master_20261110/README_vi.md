# Registered master V2 — nguồn có layer

Đây là **master kỹ thuật**, chưa phê duyệt mỹ thuật hoặc dùng cho hero gameplay.

- minh_kiem_m_registered_master.aseprite: nam, 20 layer × 16 frame.
- minh_kiem_f_registered_master.aseprite: nữ, 20 layer × 16 frame.
- Tag IDLE_S_16_MASTER, 96×96, RGBA32, 100 ms/frame.
- Body/outfit dùng cùng pose và geometry; outfit là một bộ áo + quần.
- Có variant outfit, giày, kiếm, mắt, tóc, under-hat, mũ và cape. Variant không mặc tắt mặc định.
- Canvas/gốc chân giữ cố định; source rig V2 không trộn với quần áo V1.

Nguồn sinh master: ClientGodot/scripts/RegisteredPaperDollMaster.cs và ClientGodot/assets/paperdoll_master/master.json. File .aseprite dùng để retouch trên cùng canvas/layer. Bộ kiểm độc lập: Tools/ArtProduction/inspect_registered_master.py --check.

Nguồn hiện hành được mở bằng Run_PaperDoll_Lab.ps1. Nút “Xuất master gốc .aseprite” xuất source chưa áp fit draft vào user://paperdoll_lab/registered_sources. Các thay đổi fit lưu riêng; importer cho bản .aseprite retouch chưa hoàn tất.

Không dùng master kỹ thuật để báo đã có đủ 8 hướng, combat hoặc art đẹp đã nghiệm thu. Cần retouch, đủ hành động/hướng và review trước production. Cỡ hiển thị world/camera phải được nghiệm thu riêng vì master 54 px chưa thay hero hiện tại.
