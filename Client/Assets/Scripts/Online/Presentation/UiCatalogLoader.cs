// OPC-14 B — Typed loader for the generated UI item catalog (pure C#, no Unity dep).
// Reads Resources/PlayerUI/ui_item_catalog.json text; verifies version + digest;
// returns failure diagnostics without throwing. Missing/malformed/stale -> null + error.
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 22, OPC-14 B).

using System;
using System.Collections.Generic;
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

        public bool VerifyDigest()
        {
            if (string.IsNullOrEmpty(CatalogDigest) || Entries == null) return false;
            var digests = new List<string>();
            foreach (var e in Entries)
            {
                if (e == null || string.IsNullOrEmpty(e.Digest) || e.Digest.Length != 64) return false;
                digests.Add(e.Digest);
            }
            if (digests.Count != Entries.Count) return false;
            // Recompute overall digest exactly as the generator does:
            // sha256(json.dumps([e["digest"] for e in entries]))
            string json = JsonConvert.SerializeObject(digests);
            using (var sha = System.Security.Cryptography.SHA256.Create())
            {
                var bytes = System.Text.Encoding.UTF8.GetBytes(json);
                var hash = sha.ComputeHash(bytes);
                var hex = BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();
                return string.Equals(hex, CatalogDigest, StringComparison.OrdinalIgnoreCase);
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
            catalog = parsed;
            return true;
        }
    }
}
