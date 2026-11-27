# Cốt truyện dùng trong gameplay, bản viết lại v3

Nguồn văn bản mới gồm `campaign_rewrite_vi.json` (36quest chính), `side_stories_rewrite_vi.json` (40quest phụ) và `dialogue_expansions_vi.json` (phân trang/lựa chọn/cảnh sau giao nhận của tuyến đã tích hợp). Đọc liền tại `CAMPAIGN_REWRITE_V3_vi.md`, được sinh từ chính resource game. Đây là một lượt viết lại toàn bộ prose, chưa là toàn76quest đã chạy được hoặc đã có diễn xuất/cinematic final.

CSV production giữ ID, graph, speaker, điều kiện, choice/flags, text keys và lịch sử biên tập. Exporter lấy cấu trúc ấy rồi ghép textv3, không đổi objective/reward hoặc lấy Ink checkpoint mô phỏng làm sự kiện. Client resource `Client/Assets/Resources/Narrative/dialogue_vi.json` có229unique nodes (230CSVrows có hai hàng cho cùng choice node),104NPCbindings có nguồn, digest và source hashes.

```powershell
python Implementation/Tools/build_dialogue_text.py
python Implementation/Tools/build_dialogue_text.py --check
dotnet run --project Client/Tests/NarrativeChecks/NarrativeChecks.csproj -c Release -- Client/Assets/Resources/Narrative/dialogue_vi.json
python Tools/Gameplay/run_narrative.py --configure-client
```

Lệnh cuối chạy DEV profile ở5000 nếu cổng chưa dùng; dùng `--port` để đổi. `--dotnet <path>` hỗ trợ SDKportable. Nó tạo `client-config.local.json` chỉ trong checkout đang chạy; không ghi đè file local đã có, không bật flags production trong appsettings. TitleBootstrap ưu tiên local profile khi có. Client mặc định vẫn giữ v1 cho tương thích; DEV profile chọnv2 vì v1 không có entityNPC. Không cài Unity trên máy yếu; Muse VM chạy engine từ cùng commit để nghiệm thu.

## Đường chạy đã nối

HUD nhận đúng `UIDocument` → P1NarrativeOverlay → P1NarrativeFlow → P1Client. Tương tác NPC đọc world/quest snapshots và kiểm đúng entity/map/instance/floor/proximity; endpoint world/interact đóng hiện chỉ cho parcel/node nên không gửiNPC vào đó. Nhận/nộp chỉ từ nút riêng sau trang hướng dẫn hoặc skip; gọi command P1Client hiện có, không chạy on_enter_event của CSV bằng cách hiện văn bản.

Mất phản hồi giữ pending và thử lại nguyên request. Cảnh sau nộp chỉ sau receipt đã xác nhận và inventory readback thành công. Close/skip/reply không grant, không đổi Trust/flags. Đổi phiên/map/floor/đi xa/expiry đóng context, callback muộn không mở lại. UI cùng modal input gate, Esc đóng đúng lớp, không pollingSpace riêng. Overlay dispose chỉ cây của mình.

HTTP acceptance đã đi trọn P00-01: bước tớiNPC → đọc → nhận → ba kiện thật → TạREADY → mất phản hồi nộp → retry cùng key → receipt/inventory → cảnh tiếp. Không tương đương Unity import/playmode. Native vẫn cần Muse chạy trên6000.3.17f1, đặc biệt font/cỡ chữ/mobile/safe area và input.

## Phạm vi được mở và phần còn thiếu

P00-01 executable trong DEV server. P00-02..05 hiện có catalog nhưng sourceblocked; tiếp quest event/anchor/boss doQoder đảm nhiệm. Các chương còn lại mới có textv3+IDs, chưa có runtime graph hoàn chỉnh. Client không mở questLOCKED hoặc dựngNPC chưa xuất hiện để cho đọc trước. Placement Hạ Mặc/Sầm tạiThăngLong còn cần phase binding; NPC_MASTER_BY_PLAYER_CLASS còn cần mapping theo class/phase trước khi phục vụ lớp ngoài slice. Không lấy UI metadata thay authoritative story permission.

CHOICE công bố ởC3-05 cần checkpoint sau boss, trong khi CSV chỉ cóQUEST_ACTIVE. Resource đánh dấu `requiredCheckpoint`, catalog bỏ node đó khỏi live selection khi chưa có feedcheckpoint đã review. Không cấpflag bằng reply cục bộ hoặc hiện lựa chọn trước trận. Map/floor/story checkpoint chuẩn vẫn cần server contract versioned; chưa có thì giữ thiếu ở đúng chỗ.

Profile DEV bật QuestAccept/Interact/QuestTurnIn/CombatV2/CombatDamage để HPprojection hợp lệ, MobBehaviorOFF cho lượt nghiệm thu narrative. Ở serverf2649f3, CombatDamageOFF từng trả quáiALIVE/targetable vớiHP0 khi vàoAOI; đã gửiQoder sửa riêng, không nới validationclient để nhận dữ liệu ấy. Không dùng profile này làm tuyên bố cân bằng/bản đồproduction đã duyệt.

Reading room có nút “Bản viết lại v3 ·76nhiệm vụ”, cho biên tập viên xem mọi giai đoạn và tải feedback theo digest. Nó không liên kết tài khoản hoặc mở tiến độ trong game. Skill/new prose quality vẫn cần người đọc/diễn xuất review; compiler/HTTPPASS chỉ kiểm chức năng.
