# Owner validation probe

Original run: OpenCode `9d4d811c6eb888307906fb3c6c2b29f3ac74115b`, SDK8, output in `../../Evidence/opc-owner-probe.txt`. Copied harness replaces only the original absolute checkout paths with configuration. It injects a fixture through public ClientSession APIs; it does not claim a real HTTP server leaked owner data.

PowerShell, with pinned checkout at the chosen path:

```powershell
$env:CLIENT_SOURCE_ROOT = 'D:/Project/NGUMACHHUYENAN-review-opc-20261109'
dotnet run --project Probe.csproj -c Release "-p:ClientSourceRoot=$env:CLIENT_SOURCE_ROOT"
```

Current diagnostic prints default vs explicit identity acceptance. After repair, foreign owner must be rejected in both cases with zero event deliveries. Agent should add lifecycle and positive tests in its own suite.
