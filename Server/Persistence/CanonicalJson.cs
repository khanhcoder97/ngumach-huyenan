using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace NguMach.Server.Persistence;

/// <summary>
/// Deterministic JSON normalization used for request/result/state hashes.
/// Object keys are sorted ordinally, numbers keep their literal representation and
/// strings use the System.Text.Json escaping rules. Two semantically identical
/// requests therefore produce the same hash across processes and runtimes.
/// </summary>
public static class CanonicalJson
{
    public static string Normalize(string json)
    {
        if (json is null)
        {
            throw new ArgumentNullException(nameof(json));
        }

        using var document = JsonDocument.Parse(json);
        var builder = new StringBuilder(json.Length);
        Write(document.RootElement, builder);
        return builder.ToString();
    }

    public static string Hash(string value)
    {
        ArgumentNullException.ThrowIfNull(value);
        var bytes = Encoding.UTF8.GetBytes(value);
        return Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    }

    public static string HashJson(string json) => Hash(Normalize(json));

    /// <summary>Hash of the operation plus the canonical request body.</summary>
    public static string HashRequest(string operation, string requestJson)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(operation);
        return Hash(operation + "\n" + Normalize(requestJson));
    }

    private static void Write(JsonElement element, StringBuilder builder)
    {
        switch (element.ValueKind)
        {
            case JsonValueKind.Object:
                builder.Append('{');
                var first = true;
                foreach (var property in element.EnumerateObject().OrderBy(p => p.Name, StringComparer.Ordinal))
                {
                    if (!first)
                    {
                        builder.Append(',');
                    }

                    first = false;
                    builder.Append(JsonSerializer.Serialize(property.Name));
                    builder.Append(':');
                    Write(property.Value, builder);
                }

                builder.Append('}');
                break;

            case JsonValueKind.Array:
                builder.Append('[');
                var firstItem = true;
                foreach (var item in element.EnumerateArray())
                {
                    if (!firstItem)
                    {
                        builder.Append(',');
                    }

                    firstItem = false;
                    Write(item, builder);
                }

                builder.Append(']');
                break;

            case JsonValueKind.String:
                builder.Append(JsonSerializer.Serialize(element.GetString()));
                break;

            case JsonValueKind.Number:
                builder.Append(element.GetRawText());
                break;

            case JsonValueKind.True:
                builder.Append("true");
                break;

            case JsonValueKind.False:
                builder.Append("false");
                break;

            case JsonValueKind.Null:
            case JsonValueKind.Undefined:
                builder.Append("null");
                break;

            default:
                throw new ArgumentOutOfRangeException(nameof(element), element.ValueKind, "Unsupported JSON value kind.");
        }
    }
}
