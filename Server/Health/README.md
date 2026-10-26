# Ngu Mach Huyen An — Health Server

Minimal ASP.NET Core API (net10.0) exposing a single health-check endpoint.

## Endpoint

`GET /health` returns:

```json
{
  "status": "ok",
  "service": "ngu-mach-huyen-an-server",
  "correlationId": "<correlation-id>"
}
```

The `X-Correlation-ID` request header is honored when present and at most 128 characters long; otherwise a new GUID is generated. The resolved correlation ID is echoed back in the `X-Correlation-ID` response header and written to the logs.

## Run

```bash
dotnet run --project Server/Health/Health.csproj
```

Then:

```bash
curl -i http://localhost:5000/health
```
