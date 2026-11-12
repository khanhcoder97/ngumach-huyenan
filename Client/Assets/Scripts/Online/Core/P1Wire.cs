using System;
using System.IO;
using Newtonsoft.Json;

namespace NguMach.Client.P1
{
    public static class P1Wire
    {
        // No polymorphic types, automatic date coercion, or unbounded JSON depth.
        private static readonly JsonSerializerSettings Settings = new JsonSerializerSettings
        {
            TypeNameHandling = TypeNameHandling.None,
            MetadataPropertyHandling = MetadataPropertyHandling.Ignore,
            DateParseHandling = DateParseHandling.None,
            NullValueHandling = NullValueHandling.Ignore,
            MaxDepth = 48
        };
        public static string Encode(object value) { return JsonConvert.SerializeObject(value, Settings); }
        public static T Decode<T>(string json)
        {
            if (string.IsNullOrWhiteSpace(json) || json.Length > 1024 * 1024)
                throw new JsonException("Empty or oversized P1 response.");
            using (var sr = new StringReader(json))
            using (var reader = new JsonTextReader(sr) { MaxDepth = 48, DateParseHandling = DateParseHandling.None })
            {
                var result = JsonSerializer.Create(Settings).Deserialize<T>(reader);
                if (reader.Read()) throw new JsonException("Trailing JSON content.");
                return result;
            }
        }
        public static bool Finite(double value) { return !double.IsNaN(value) && !double.IsInfinity(value); }
        public static bool Hex32(string value)
        {
            if (value == null || value.Length != 32) return false;
            foreach (char c in value) if (!(c >= '0' && c <= '9') && !(c >= 'a' && c <= 'f')) return false;
            return true;
        }
        public static bool Valid(P1World world, string characterId = null)
        {
            if (world == null || world.self == null || world.entities == null || world.revision < 0 ||
                world.serverTick < 0 || string.IsNullOrEmpty(world.mapId)) return false;
            var s = world.self;
            if (string.IsNullOrEmpty(s.characterId) || string.IsNullOrEmpty(s.classId) ||
                (characterId != null && s.characterId != characterId) || !Finite(s.x) || !Finite(s.y) ||
                s.maxHp < 1 || s.hp < 0 || s.hp > s.maxHp || s.maxMp < 0 || s.mp < 0 || s.mp > s.maxMp ||
                s.swordIntent < 0 || s.swordIntent > 5) return false;
            foreach (var e in world.entities)
                if (e == null || string.IsNullOrEmpty(e.entityId) || !Finite(e.x) || !Finite(e.y)) return false;
            return true;
        }
    }
}
