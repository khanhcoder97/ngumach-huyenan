# Bộ âm thanh gốc Ngũ Mạch v1

195 cue / 541 clip runtime có thật: 173 cue ngắn × 3 biến thể WAV và 22 loop OGG (9 nhạc, 13 môi trường). Mỗi clip có master FLAC 24 bit. Nhạc có score JSON chỉnh từng nốt; âm hiệu có recipe và mã DSP. Không tải sample, trích âm JAR, sao giai điệu tham khảo hoặc nhân bản giọng người.

Đây là **bộ ứng viên để nghe duyệt**, chưa nối vào AudioManager, chưa kiểm import/phối âm Unity, chưa có thoại NPC có lời. Kiểm tra kỹ thuật không đánh giá chất lượng nghệ thuật. Chi tiết sản xuất và nghiệm thu: `docs/production/Audio_Pack_V1_Delivery_vi.md`.

## Nghe ngay

Mở `Tools/AudioProduction/player.html` bằng trình duyệt: dữ liệu nhúng sẵn, không cần npm hoặc Unity. Tìm theo tên/cue, chọn môn phái, chọn biến thể. Nhạc/môi trường lặp; nút Dừng tất cả ngừng phát. Chỉ nạp 24 thẻ mỗi trang, không tự phát.

Nếu trình duyệt chặn file local:

```powershell
python Tools/AudioProduction/preview_server.py --port 8078
```

Mở `http://127.0.0.1:8078/`. Server chỉ nghe localhost và phục vụ trang nghe/audio; Ctrl+C để tắt. Bốn MP3 nghe nhanh nằm ở `Art_Source/Audio/Previews/`, timeline montage có trong manifest.

## Kiểm tra / tái tạo

Chạy tại gốc checkout; Python 3.12+:

```powershell
git lfs pull
python -m venv .venv-audio
.venv-audio/Scripts/python -m pip install -r Tools/AudioProduction/requirements.txt
.venv-audio/Scripts/python -m unittest discover -s Tools/AudioProduction -p 'test_*.py' -v
.venv-audio/Scripts/python Tools/AudioProduction/validate_pack.py
```

Linux dùng `.venv-audio/bin/python`. Có thể dùng môi trường Python đã cài requirements thay cho venv. Không cần scipy, ffmpeg hoặc DAW. Không commit thư mục venv.

Sửa `Art_Source/Audio/game_audio_recipes_v1.json` để đổi recipe; sửa `Art_Source/Audio/Scores/*.json` để đổi nốt/nhịp/nhạc cụ. Render lại toàn bộ rồi validate để cập nhật manifest, master, preview và trang nghe:

```powershell
python Tools/AudioProduction/render_pack.py
python Tools/AudioProduction/validate_pack.py --report Implementation/Reports/Audio_Pack_V1_Technical_QA.json
```

`--only SFX/SKILL/` chỉ render thử một prefix, **có ghi đè file** nhưng không xuất lại manifest toàn bộ. Dùng checkout thử riêng; sau khi chọn phải render đầy đủ và validate trước bàn giao. `--recompose` thay score đã sửa bằng motif mặc định, chỉ dùng khi chủ động muốn soạn lại. Không chạy hai renderer đồng thời.

Seed cố định theo cue và variant; không dùng RNG gameplay. Cùng nguồn có thể xuất bitstream OGG/MP3 khác khi đổi libsndfile/codec, vì vậy lưu master đã giao và so SHA của chính lần render; không cam kết bit-identical giữa mọi nền tảng. Source text kiểm SHA chuẩn UTF-8/LF (CRLF checkout được chuẩn hóa); audio/master luôn kiểm byte nguyên bản.

## Đường dẫn bàn giao

- `Client/Assets/Audio/PackV1/`: WAV 16 bit mono / OGG stereo, đều 48 kHz, Unity `.meta` riêng.
- `Client/Assets/AudioManifests/game_audio_v1.json`: cue, biến thể, frame loop, hash, nguồn, binding; dữ liệu audio riêng, không dùng schema sprite của Muse.
- `Art_Source/Audio/Masters/`: 541 master FLAC 24 bit.
- `Art_Source/Audio/Scores/`: 9 score gốc, không phải MIDI/sample pack bên ngoài.
- `Implementation/Reports/Audio_Pack_V1_Technical_QA.json`: báo cáo giải mã toàn bộ clip, không chứng nhận nghe duyệt/Unity.

`DesignBaselines/audio_cues_v1.json` là snapshot thiết kế ban đầu còn MISSING, được giữ nguyên để không đánh tráo lịch sử. Tình trạng file thực tế lấy từ manifest mới. Chỉ tích hợp khi có presentation adapter đúng event và review nghe/engine.
