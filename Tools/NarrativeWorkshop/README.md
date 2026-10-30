# Phòng biên kịch Ngũ Mạch: Huyền Ấn

Bộ viết, sửa và chơi thử cốt truyện tiếng Việt, không cần Unity. Gói đầu tiên là tuyến Bến Mưa P00-01–P00-05: **18 cảnh truyện và 8 checkpoint mô phỏng**, lựa chọn phản hồi có hội tụ; không thay số objective/thưởng hoặc 349 placements. Đây là authoring candidate, chưa là dialogue runtime.

## Đọc ngay và sửa bản thảo

Từ thư mục repo:

```powershell
cd Tools/NarrativeWorkshop
npm ci --ignore-scripts --no-audit --no-fund
npm run check
python server.py --port 8126
```

Mở http://127.0.0.1:8126. Có chọn tuyến, đọc nhánh, đọc lại, hiện/ẩn ghi chú biên kịch và tải feedback gắn source digest. Mọi trạng thái trong trang chỉ là bản đọc cá nhân, không gọi server game. Reader dùng `inkjs@2.4.0` pinned bởi package-lock, không CDN hoặc model/API trả phí. Node 24/Python 3.12+ đủ; không tải Unity/audio/art LFS để viết.

Nguồn duy nhất của lời mới là `docs/narrative/workshop/ink/*.ink`. Sau sửa, chạy `npm run build`, đọc lại nhánh đã đổi và `npm run check`. Ba output generated: compiled JSON, scene_manifest.json và `docs/narrative/workshop/BEN_MUA_SCREENPLAY_vi.md`. Không sửa các file generated bằng tay. `check` phát hiện output/source/canon drift, chạy thực Ink branches, kiểm replay, reveal gate và cinema timing; không chấm điểm văn hay.

## Inky và compiler portable

```powershell
python Tools/NarrativeWorkshop/setup_tools.py --dir D:/Project/NGUMACHHUYENAN-tools/narrative --editor
python Tools/NarrativeWorkshop/open_inky.py
```

Chạy từ repo root; câu `open_inky.py` là thao tác mở ứng dụng của người dùng. Setup tải official release và kiểm SHA256: Ink 1.2.1 (compiler Windows khoảng27MB), Inky 0.15.2 Windows 64 (archive khoảng225MB). Các binary nằm ngoài repo, không cài admin/global hooks. Không cần Inky để đọc browser. Compiler có pinned assets Linux/macOS; editor option hiện chỉ Windows 64. Máy khác có thể dùng default `~/.cache/ngumach-narrative` hoặc `open_inky.py --editor <path>`.

Compiler native độc lập:

```powershell
D:/Project/NGUMACHHUYENAN-tools/narrative/ink/v1.2.1/inklecate.exe -o <scratch.json> docs/narrative/workshop/ink/main.ink
node Tools/NarrativeWorkshop/verify.cjs --story <scratch.json>
```

## Skills và phương pháp

`python Tools/NarrativeWorkshop/install_skills.py` dùng bundled Codex skill-installer để cài 4 skill pinned: writing-principles, creative-writing-craft, story-review (haowjy, Apache 2.0) và dialogue (jwynia, individual skill declares MIT). Không overwrite skill khác; existing version khác thì giữ nguyên và báo. Có bản gốc/frontmatter provenance; chỉ bỏ field model-invocable không hỗ trợ trong Codex. Skill dự án `ngumach-narrative` nằm ở `.agents/skills/` và được copy vào local Codex skills; khả dụng từ lượt tiếp theo.

Không chạy bootstrap của repo ngoài để ghi AGENTS/canon/hooks của game, không đổi model/credential, không dùng Deno metrics tiếng Anh để kết luận văn Việt. Đọc VOICE_GUIDE_vi.md cho cách viết cảnh và INTEGRATION_AND_CANON_vi.md cho custody/reveal/proposal. Tham khảo kỹ thuật biên tập của các repo trong sources.lock.json; không sao chép thoại Sky Caravan hoặc gắn tác giả của họ vào văn mới.

## Bằng chứng và ranh giới

`node verify.cjs --report` ghi branch-report.json deterministic. Bộ này kiểm 2280 choice edges trên 947 decision states của bản mẫu hiện tại (merge state không phụ thuộc visit count vì các choice sticky và không dùng visit expressions), không tuyên bố kiểm hết vô hạn vòng đọc. Compiler không có warning. Browser smoke mở Chrome thật, tải story và click lựa chọn để xác minh advance:

```powershell
python Tools/NarrativeWorkshop/browser_smoke.py --screenshot <absolute.png> --report <absolute.json>
```

Server chỉ bind loopback và sáu route explicit, không expose source filesystem/.git/node_modules directory listing. Không có endpoint gameplay. CI Linux tái kiểm compiler/graph/canon, không cài skills/global tool hoặc model. Browser/Unity/video/art acceptance là các phép kiểm khác; thiếu browser phải ghi chưa xác minh. Inky đã cài không đồng nghĩa đã chạy native UI của nó. Không có video Muse mới được tạo trong gói này.
