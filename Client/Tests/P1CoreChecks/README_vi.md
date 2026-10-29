# Client P1 — kiểm tra không cần Unity

`dotnet run --project Client/Tests/P1CoreChecks/P1CoreChecks.csproj -c Release` compile **cùng các file Core** được Unity dùng, rồi chạy fault scenarios: mất phản hồi, retry giữ nguyên request/key, readback MP, session expiry, stale snapshot, sai session, thiếu field, dictionary quest, inventory revision, cancellation và command serialization.

`dotnet run --project Client/Tests/P1CoreChecks/P1CoreChecks.csproj -c Release -- --http http://127.0.0.1:5000` cần server mặc định quest-accept OFF. Test tạo phiên riêng, move, đọc quest/inventory, nhận feature-off (404/405 tùy route matching) và cast Phản Quang rồi đọc lại MP. `combat.effect` không được đổi thành damage/counter animation giả.

CI `client-core-validation` chạy cả fault suite và HTTP với server build thật; không cần cài Unity trên máy người dùng. CI này **không compile Unity-specific transport/UI/presenter** và không chứng minh Android/IL2CPP, font/UI/safe area, input hoặc animation playback. Chỉ máy Unity mới kiểm phần đó.

Json.NET test dùng13.0.2; Unity dùng package chính thức `com.unity.nuget.newtonsoft-json`3.2.2 (changelog ghi DLL13.0.2 từ3.1). Nguồn: https://docs.unity3d.com/Packages/com.unity.nuget.newtonsoft-json@3.2/manual/index.html và changelog cùng package. Không thêm DLL NuGet trực tiếp vào Assets để tránh duplicate assembly. Package resolution/lock do Unity thực hiện; không ghi giả packages-lock chưa resolve.
