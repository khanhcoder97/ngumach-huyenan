# Bến Mưa bám concept —05/11/2026

## Kết quả

Thay scene rải nhà theo hai hàng bằng district có bố cục theo ben_mua_topdown_wide_v2: đình giữa, nhà và vườn phía bắc/tây, chợ phía đông bắc, đường nhánh nối sân, bờ sông chéo, bến chính/bến nhỏ,thuyền,sen,lau,đá và ruộng bờ nam. Nguồn hình là5atlas mới độc lập cùng một sốprops mới của Codex ở lô trước. Không dùng concept làm nền hoặc artMuse.

Bản thực thi nằm ClientGodot/Preview.tscn; layout113placement/14tuyến ở assets/ben_mua_v3/layout.json. World128×96WU, khu tham chiếu64×36WU; vẫn camera rộng vàHUDCanvasLayer. Tỷ lệhero36pixel cao, villagers32pixel trong viewport720cao. Native screenshot là engine render thật, không là ảnh concept đã gắn HUD.

Cải thiện chính: textureterrain128–160pixel theo thế giới thay256→16; polygon đường có mép biến thiên, sông cong, sân đất, vườn rào, mái/cây/đồ vật theo chân neo vàysort. Nước chặn bằng collisionpolygon theo cùng bờ, subtract các footprint cầu tàu để đi xuống bến. Tán cây/công trình che hero mờ còn48% rồi phục hồi. Không đổi canonicalnav/placement/serverAOI.

## Kiểm tra đã chạy

- Locked build Godot4.7.2.NET / .NET8:0error/0warning.
- Inspector mới:5PNGsource/runtime byte-identical,29region có padding/rect/pivot,113IDkhông trùng. Inspector lô cũ vẫn qua.
- Camera/route headless:48assertions qua, gồm mặc định64×36WU,HUDarc,biênworld,spawnwalkable,nướcblocked,pierwalkable và5route BFS.
- Scenario input/physics:9assertions qua ở cả headless và render WindowsGeForce820M. Dùng Input.ParseInputEvent đi qua polling/physics thực:đi phải,thảphím,focusout,focusinphảithảrồibấmlại,đi vào cuối bến bị chặn,canopyfade/restoration. Đây là testinput được inject vào engine, không giả log thao tác người dùng.
- Scopeguard4test qua. Parser/build checks được giữ.
- Native clean vàHUD captures1280×720 trong Evidence/BenMua_Concept_Rebuild_20261105; đã xem sau chỉnh dảiđá. Không cam kếtFPS từ ảnh chụp.

## CI và tính tái lập

Sửa workflow visual Python3.x thành3.12 để tương thích Pillow11.3wheel. Bổ sung LFSinclude/inspector của atlas mới. Coverage legacy tái tạo từ42nguồn vì PixelArtstandard đã cập nhật; không tắt stalecheck. Báo cáo coverage đó vẫn đo catalog/assetpipeline lịch sử, không tự coi113decor là NPCđã hoàn thiện toàngame.

## Giới hạn còn lại

Bản dựng đã có môi trường thực và đường đi để thử; chưa là clientonline. Người dân là ambient decor,hero idle8hướng,chưa animationcombat/walk hoặc NPCdịch vụ. Một sốloại nhà,cây vẫn lặp; textureterrain còn cần authoring/variation thêm và artpolish. Chưa đánh giácrowd/mobile/performance dài hạn. MapA2 là artstaging; migration geometry/canonical services/quest/nav phải đi gói đồng bộ riêng. ThăngLong và toànbộgame chưa được dựng hết từlần này.
