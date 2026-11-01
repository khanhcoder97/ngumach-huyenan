# OPC-13 producer review — 01/11/2026

Reviewed PR101 head `66ddddf1e26a98c316f4ef8e02a0a071b53b703e`, 6commits/29files từ d0b7d52. Agent đang idle sau báo cáo A→D, không có bằng chứng vẫn chạy task. Antigravity không được phục hồi.

Đã chạy độc lập original `dotnet test Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj -c Release --nologo --verbosity minimal` với SDK10 portable + DOTNET_ROLL_FORWARD=LatestMajor: **140/140PASS,exit0**;3xUnit2013 warnings cũ. Original csproj net8 giữ nguyên. Syntax runner **52files×3profiles,0errors**, không Unity types/import/device. CI exact head **13/13SUCCESS**. Native packet đã có nhưng chưa có kết quả Muse VM được xác minh; reduced-motion/flash/hints còn preview; camera rectangle/waypoint unsupported.

## OPCREV-01 [P1] Space đi xuyên modal topmost, editing focus không chặn cinema

`Presentation/ModalOrchestration.cs:93` bỏ qua layer trước mặt nếu không ConsumesSpace rồi skip cinema phía sau. Producer console dùng actual compiled assembly/class, không patch source:

```text
PROBE1: narrative OPEN above cinema OPEN: consumed=Cinema, backgroundCinemaSkips=1
FAIL: foreground modal bypassed; background cinema skipped
```

P1OnlinePanel:176 dispatch Space trước AllowsGameplay; editing focus(:201) chỉ gửi vào gameplay gate. Phải phân biệt blocked/handled/no-modal và stop tại topmost open layer; text editing không kích hoạt lower cinema. Test narrative+cinema simultaneous, focused editor, close/rearm/pending/expired/pause/two-document. Không sửa tests thành cho phép bỏ qua overlay.

## OPCREV-02 [P1] Map clamp không khớp projection canvas

MapPanel vẽ280×280 bằng một scale280/bounds.Width×zoom cho cả hai trục. MapPresenter.ClampPan:134 lại dùng halfY=Height/(2zoom). Real presenter bounds360×84,zoom4,panY20 trả center50, dù cửa sổ nhìn90WU đã phủ toàn bộ height84 và phải lock center30:

```text
PROBE2: actual presenter centerY=50; actual square-canvas projection sees Y[5,95], canonical Y[-12,72]
FAIL: Y axis pans despite viewport spanning the whole map height
```

Dùng một projection/view transform cho renderer+gesture+clamp, actual viewport/aspect; test zoom0.25/1/4/corners/resize/v1v2. Refresh(:42/62) chỉ reset nếu bounds đổi, còn thiếu mapId khác với bounds bằng nhau và clear/disconnect; chỉ dùng field wire hiện có, không invent floor/topology authority.

## OPCREV-03 [P1] HUD Hidden bị writer display khác bật lại

PlayerUIButtonBar.RefreshVisibility:138 mỗi frame connected ghi displayFlex. ApplySafeAreaPolicy:170 return sớm khi decision unchanged nên Hidden(:178) chỉ ẩn frame đầu; frame sau display bị bật lại. Finding từ source flow, **chưa Unity tree proof**. Gộp visibility=connection+safearea+pin về một writer/reducer; test Hidden nhiều frames, Hidden→Full, disconnected/expired→ready, rebind/two-doc. Không hide mất mọi đường mở menu/settings trên viewport khả dụng.

## Bằng chứng và tiếp theo

Producer harness/log tại `D:/Project/NGUMACHHUYENAN-tools/dispatch/opc101-review-20261101/`: Program.cs,ModalProbe.csproj,modal-map-probe.log. Lệnh `dotnet run --project <path>/ModalProbe.csproj -c Release` link ProjectReference original PlayerUIChecks (same implementation), exit1/failures2. **HEADLESS_DIAGNOSTIC_NOT_UNITY**; probe2 dùng extent đúng công thức MapPanel, không là screenshot/native test. Không sửa source/test agent hay đưa stub Unity vào kết luận.

Chưa merge101/main. Tiếp cả M0→M4 trong workorder21: sửa101 trước rồi accessibility/fullcatalog/HTTP acceptance/native executable tests. Giữ80/85 mở, sửa PR title phản ánh UI code. Native packet không đồng nghĩa nativePASS.
