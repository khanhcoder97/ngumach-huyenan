$ErrorActionPreference = 'Stop'
$reviewClient = 'D:/Project/NGUMACHHUYENAN-review-opc-20261112'
$reviewServer = 'D:/Project/NGUMACHHUYENAN-review-qod-20261109'
$env:DOTNET_CLIENT = 'D:/Project/NGUMACHHUYENAN-tools/dotnet8/dotnet.exe'
$env:DOTNET_SERVER = 'D:/Project/NGUMACHHUYENAN-tools/dotnet10/dotnet.exe'
# Original review run: nested content root exposes the empty-fingerprint gap.
# This preserves the original arguments; it is not complete content-pinned acceptance.
python "$reviewClient/Shared/ClientCore.HttpRunner/run_http.py" --client-root $reviewClient --server-root $reviewServer --client-head 85719a7ecdaa10d3ad2d20d32077a78cea88b92b --server-head 4cada354fc9efc1f1f4fff9c1d8acf9bccba6731 --content-root "$reviewServer/Implementation/Content" --contract-pin "$reviewClient/Shared/ClientCore.Tests/Fixtures/qoder-contract-pins.json" --mode private-alpha --artifacts-root 'D:/Project/NGUMACHHUYENAN-tools/handoff-20261112/evidence/paired'
exit $LASTEXITCODE
