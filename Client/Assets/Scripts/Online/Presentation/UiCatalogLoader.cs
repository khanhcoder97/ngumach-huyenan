// OPC-14 B — Typed loader for the generated UI item catalog (pure C#, no Unity dep).
// Reads Resources/PlayerUI/ui_item_catalog.json text; verifies version + digest;
// returns failure diagnostics without throwing. Missing/malformed/stale -> null + error.
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 22, OPC-14 B).

using System;
using System.Collections.Generic;
using System.Text;
using Newtonsoft.Json;

namespace NguMach.Client.Presentation
{
    public sealed class UiCatalogSource
    {
        [JsonProperty("file")] public string File { get; set; }
        [JsonProperty("row")] public int Row { get; set; }
    }

    public sealed class UiCatalogEntry
    {
        [JsonProperty("item_id")] public string ItemId { get; set; }
        [JsonProperty("display_name")] public string DisplayName { get; set; }
        [JsonProperty("category")] public string Category { get; set; }
        [JsonProperty("slot")] public string Slot { get; set; }
        [JsonProperty("class_id")] public string ClassId { get; set; }
        [JsonProperty("element")] public string Element { get; set; }
        [JsonProperty("required_level")] public string RequiredLevelRaw { get; set; }
        [JsonProperty("rarity_pool")] public string RarityPool { get; set; }
        [JsonProperty("binding")] public string Binding { get; set; }
        [JsonProperty("tradeable")] public string Tradeable { get; set; }
        [JsonProperty("stack_limit")] public string StackLimit { get; set; }
        [JsonProperty("durability")] public string Durability { get; set; }
        [JsonProperty("weapon_power")] public string WeaponPower { get; set; }
        [JsonProperty("armor")] public string Armor { get; set; }
        [JsonProperty("primary_stat")] public string PrimaryStat { get; set; }
        [JsonProperty("primary_value")] public string PrimaryValue { get; set; }
        [JsonProperty("secondary_stat")] public string SecondaryStat { get; set; }
        [JsonProperty("secondary_value")] public string SecondaryValue { get; set; }
        [JsonProperty("affix_rule")] public string AffixRule { get; set; }
        [JsonProperty("socket_rule")] public string SocketRule { get; set; }
        [JsonProperty("set_id")] public string SetId { get; set; }
        [JsonProperty("set_name")] public string SetName { get; set; }
        [JsonProperty("set_bonus_2")] public string SetBonus2 { get; set; }
        [JsonProperty("set_bonus_4")] public string SetBonus4 { get; set; }
        [JsonProperty("hidden_effect_id")] public string HiddenEffectId { get; set; }
        [JsonProperty("hidden_effect_unlock")] public string HiddenEffectUnlock { get; set; }
        [JsonProperty("hidden_effect")] public string HiddenEffect { get; set; }
        [JsonProperty("source_map")] public string SourceMap { get; set; }
        [JsonProperty("source_rule")] public string SourceRule { get; set; }
        [JsonProperty("description")] public string Description { get; set; }
        [JsonProperty("_source")] public UiCatalogSource Source { get; set; }
        [JsonProperty("digest")] public string Digest { get; set; }

        public int RequiredLevel
        {
            get { int v; return int.TryParse(RequiredLevelRaw, out v) ? v : 0; }
        }
    }

    public sealed class UiCatalog
    {
        [JsonProperty("schemaVersion")] public int SchemaVersion { get; set; }
        [JsonProperty("catalogDigest")] public string CatalogDigest { get; set; }
        [JsonProperty("sourceDigests")] public Dictionary<string, string> SourceDigests { get; set; }
        [JsonProperty("count")] public int Count { get; set; }
        [JsonProperty("entries")] public List<UiCatalogEntry> Entries { get; set; }

        private Dictionary<string, UiCatalogEntry> _byId;

        // Canonical field list, sorted exactly like Python json.dumps(sort_keys=True).
        private static readonly string[] DigestFields =
        {
            "affix_rule", "armor", "binding", "category", "class_id", "description",
            "display_name", "durability", "element", "hidden_effect", "hidden_effect_id",
            "hidden_effect_unlock", "item_id", "primary_stat", "primary_value",
            "rarity_pool", "required_level", "secondary_stat", "secondary_value",
            "set_bonus_2", "set_bonus_4", "set_id", "set_name", "slot", "socket_rule",
            "source_map", "source_rule", "stack_limit", "tradeable", "weapon_power"
        };

        /// <summary>
        /// OPC-14 O1: recompute every entry digest from the loaded content (not just trust
        /// the stored hex), verify source provenance exists for each row, then recompute the
        /// overall digest exactly like the generator (Python json.dumps list format).
        /// A stale/tampered catalog must fail loudly instead of leaking wrong metadata.
        /// </summary>
        public bool VerifyDigest()
        {
            if (string.IsNullOrEmpty(CatalogDigest) || Entries == null || SourceDigests == null) return false;
            if (Entries.Count != Count) return false;

            var digests = new List<string>(Entries.Count);
            foreach (var e in Entries)
            {
                if (e == null || string.IsNullOrEmpty(e.ItemId) || string.IsNullOrEmpty(e.Digest) || e.Digest.Length != 64) return false;
                if (e.Source == null || string.IsNullOrEmpty(e.Source.File) || e.Source.Row < 2) return false;
                if (!SourceDigests.ContainsKey(e.Source.File)) return false;

                string actual = ComputeEntryDigest(e);
                if (!string.Equals(actual, e.Digest, StringComparison.OrdinalIgnoreCase)) return false;
                digests.Add(e.Digest.ToLowerInvariant());
            }

            // Python: hashlib.sha256(json.dumps([e["digest"] for e in entries], ensure_ascii=False))
            var sb = new StringBuilder();
            sb.Append('[');
            for (int i = 0; i < digests.Count; i++)
            {
                if (i > 0) sb.Append(", ");
                AppendJsonString(sb, digests[i]);
            }
            sb.Append(']');
            string overall = Sha256Hex(sb.ToString());
            return string.Equals(overall, CatalogDigest, StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>Recompute one entry digest from its canonical fields (generator parity).</summary>
        public static string ComputeEntryDigest(UiCatalogEntry entry)
        {
            if (entry == null) return "";
            var sb = new StringBuilder();
            sb.Append('{');
            for (int i = 0; i < DigestFields.Length; i++)
            {
                if (i > 0) sb.Append(", ");
                string field = DigestFields[i];
                AppendJsonString(sb, field);
                sb.Append(": ");
                AppendJsonString(sb, Field(entry, field));
            }
            sb.Append('}');
            return Sha256Hex(sb.ToString());
        }

        private static string Field(UiCatalogEntry e, string name)
        {
            switch (name)
            {
                case "affix_rule": return e.AffixRule;
                case "armor": return e.Armor;
                case "binding": return e.Binding;
                case "category": return e.Category;
                case "class_id": return e.ClassId;
                case "description": return e.Description;
                case "display_name": return e.DisplayName;
                case "durability": return e.Durability;
                case "element": return e.Element;
                case "hidden_effect": return e.HiddenEffect;
                case "hidden_effect_id": return e.HiddenEffectId;
                case "hidden_effect_unlock": return e.HiddenEffectUnlock;
                case "item_id": return e.ItemId;
                case "primary_stat": return e.PrimaryStat;
                case "primary_value": return e.PrimaryValue;
                case "rarity_pool": return e.RarityPool;
                case "required_level": return e.RequiredLevelRaw;
                case "secondary_stat": return e.SecondaryStat;
                case "secondary_value": return e.SecondaryValue;
                case "set_bonus_2": return e.SetBonus2;
                case "set_bonus_4": return e.SetBonus4;
                case "set_id": return e.SetId;
                case "set_name": return e.SetName;
                case "slot": return e.Slot;
                case "socket_rule": return e.SocketRule;
                case "source_map": return e.SourceMap;
                case "source_rule": return e.SourceRule;
                case "stack_limit": return e.StackLimit;
                case "tradeable": return e.Tradeable;
                case "weapon_power": return e.WeaponPower;
                default: return null;
            }
        }

        // Python json.dumps(ensure_ascii=False) string escaping.
        private static void AppendJsonString(StringBuilder sb, string value)
        {
            sb.Append('"');
            if (value != null)
            {
                foreach (char c in value)
                {
                    switch (c)
                    {
                        case '"': sb.Append("\\\""); break;
                        case '\\': sb.Append("\\\\"); break;
                        case '\b': sb.Append("\\b"); break;
                        case '\f': sb.Append("\\f"); break;
                        case '\n': sb.Append("\\n"); break;
                        case '\r': sb.Append("\\r"); break;
                        case '\t': sb.Append("\\t"); break;
                        default:
                            if (c < 0x20) sb.Append("\\u").Append(((int)c).ToString("x4"));
                            else sb.Append(c);
                            break;
                    }
                }
            }
            sb.Append('"');
        }

        private static string Sha256Hex(string text)
        {
            using (var sha = System.Security.Cryptography.SHA256.Create())
            {
                var bytes = Encoding.UTF8.GetBytes(text);
                var hash = sha.ComputeHash(bytes);
                var hex = new StringBuilder(hash.Length * 2);
                foreach (byte b in hash) hex.Append(b.ToString("x2"));
                return hex.ToString();
            }
        }

        public UiCatalogEntry Find(string id)
        {
            if (string.IsNullOrEmpty(id)) return null;
            if (_byId == null)
            {
                _byId = new Dictionary<string, UiCatalogEntry>(StringComparer.OrdinalIgnoreCase);
                if (Entries != null)
                    foreach (var e in Entries)
                        if (e != null && !string.IsNullOrEmpty(e.ItemId) && !_byId.ContainsKey(e.ItemId))
                            _byId[e.ItemId] = e;
            }
            UiCatalogEntry v;
            return _byId.TryGetValue(id, out v) ? v : null;
        }
    }

    public static class UiCatalogLoader
    {
        public const int ExpectedSchemaVersion = 1;

        public static bool TryLoad(string json, out UiCatalog catalog, out string error)
        {
            catalog = null;
            error = null;
            if (string.IsNullOrWhiteSpace(json)) { error = "empty catalog json"; return false; }
            UiCatalog parsed;
            try { parsed = JsonConvert.DeserializeObject<UiCatalog>(json); }
            catch (Exception ex) { error = "json parse error: " + ex.Message; return false; }
            if (parsed == null) { error = "catalog deserialized to null"; return false; }
            if (parsed.SchemaVersion != ExpectedSchemaVersion) { error = "unsupported schemaVersion " + parsed.SchemaVersion; return false; }
            if (parsed.Entries == null) { error = "entries missing"; return false; }
            if (parsed.Count != parsed.Entries.Count) { error = "count mismatch: declared " + parsed.Count + " actual " + parsed.Entries.Count; return false; }
            // digest sanity
            foreach (var e in parsed.Entries)
            {
                if (e == null || string.IsNullOrEmpty(e.ItemId)) { error = "entry missing item_id"; return false; }
                if (string.IsNullOrEmpty(e.Digest)) { error = "entry missing digest: " + e.ItemId; return false; }
            }
            // OPC-14 O1: content-level digest recompute (entry + overall + provenance).
            if (!parsed.VerifyDigest()) { error = "catalog digest mismatch (stale or tampered)"; return false; }
            catalog = parsed;
            return true;
        }
    }
}
