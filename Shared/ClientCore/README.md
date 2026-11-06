# NguMach.Client.Core

Engine-agnostic P1 client core for the NguMach Huyền An Godot client. Target:
`net8.0`. No Unity or Godot assembly reference is required.

## Contents

- Session composition, typed P1 contracts, capability/service availability.
- Encounter snapshot validation and renderer-neutral VFX binding.
- Portable UI read models/presenters: inventory v2, death-return, combat HUD,
  quest journal, dialogue, map, TALK/portal/MAP_VIEWED and system messages.
- Inventory v2, death-return and tutorial transport helpers.

Every presenter projects server-authoritative data. The library does not grant
XP, loot, quest progress or map movement locally, and it does not turn a 404 into
an "available" service.

## Build and test

```sh
dotnet restore Shared/ClientCore/ClientCore.csproj
dotnet build Shared/ClientCore/ClientCore.csproj -c Release
dotnet test Shared/ClientCore.Tests/ClientCore.Tests.csproj -c Release
dotnet pack Shared/ClientCore/ClientCore.csproj -c Release -o TestResults/package
```

`packages.lock.json` is tracked. CI restores in locked mode; update the lock file
with an explicit restore when a dependency changes.

## Dependencies

- `Newtonsoft.Json` 13.0.1 (MIT). See `THIRD-PARTY-NOTICES.md`.

## License status

The upstream repository does not currently contain a first-party `LICENSE` file.
This package therefore does **not** declare an SPDX license and must not be
published as MIT/Apache/other until the project owner supplies the actual
first-party license. Third-party notices are included for the dependency above.

## Production gates

All private-alpha gates remain OFF by default (`DeploymentProfile.ProductionOff`).
A service is reported available only when the deployment profile advertises all
of its routes and the relevant gate is enabled.
