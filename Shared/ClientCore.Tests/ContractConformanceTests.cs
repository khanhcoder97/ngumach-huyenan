// OPC-17 O-A — Contract conformance against the pinned Qoder P1 contracts.
//
// The manifest (Fixtures/qoder-contract-pins.json) pins SHA-256 for every P1
// schema and example at server checkout 6814126e2def8a1c4270a1016f0ab85404cba46e.
// Vendored copies under Fixtures/qoder-contracts-6814126/ carry the pinned bytes
// for every file, so the typed models are always exercised against the pinned
// contract even where the client checkout's Implementation/ tree is behind
// (recorded as location=drift with its own inTreeSha256, never silently).
//
// Coverage: hash integrity (both trees, no unpinned file), then typed parse of
// the pinned examples for success/error/nullability/ID/finite/range/credited/
// replayed/receipt identity, then negative controls where a mutated example or
// a mutated byte must be rejected. Pure C#; no server is contacted.
// Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using NguMach.Client.Core.Encounter;
using NguMach.Client.P1;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class ContractConformanceTests
    {
        private const string ServerPin = "server-6814126e2def8a1c4270a1016f0ab85404cba46e";
        private static readonly string RepoRoot = FindRepoRoot();
        private static readonly string ManifestPath = Path.Combine(
            RepoRoot, "Shared", "ClientCore.Tests", "Fixtures", "qoder-contract-pins.json");
        private static readonly string VendoredRoot = Path.Combine(
            RepoRoot, "Shared", "ClientCore.Tests", "Fixtures", "qoder-contracts-6814126");
        private static readonly string InTreeRoot = Path.Combine(
            RepoRoot, "Implementation", "Contracts", "P1");

        // JSON-only DTOs: fields are populated by the deserializer.
#pragma warning disable CS0649
        private sealed class PinEntry
        {
            public string kind;
            public string name;
            public string sha256;
            public string location;
            public string inTreeSha256;
        }

        private sealed class PinManifest
        {
            public string pin;
            public string source;
            public string vendoredRoot;
            public string generated;
            public List<PinEntry> files;
        }
#pragma warning restore CS0649

        private static string FindRepoRoot()
        {
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            while (dir != null)
            {
                if (File.Exists(Path.Combine(dir.FullName, "Shared", "ClientCore.Tests", "Fixtures",
                    "qoder-contract-pins.json")))
                    return dir.FullName;
                dir = dir.Parent;
            }
            throw new FileNotFoundException("qoder-contract-pins.json not found above " + AppContext.BaseDirectory);
        }

        private static PinManifest LoadManifest()
        {
            var manifest = JsonConvert.DeserializeObject<PinManifest>(File.ReadAllText(ManifestPath));
            Assert.NotNull(manifest);
            Assert.NotNull(manifest.files);
            return manifest;
        }

        private static string Sha256Hex(string path)
        {
            using (var stream = File.OpenRead(path))
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
        }

        private static string VendoredPath(PinEntry entry)
        {
            return entry.kind == "example"
                ? Path.Combine(VendoredRoot, "Examples", entry.name)
                : Path.Combine(VendoredRoot, entry.name);
        }

        private static string InTreePath(PinEntry entry)
        {
            return entry.kind == "example"
                ? Path.Combine(InTreeRoot, "Examples", entry.name)
                : Path.Combine(InTreeRoot, entry.name);
        }

        // Pinned example bytes, always read from the vendored authority copy.
        private static string Example(string name)
        {
            var path = Path.Combine(VendoredRoot, "Examples", name);
            Assert.True(File.Exists(path), "vendored example missing: " + name);
            return File.ReadAllText(path);
        }

        private static string Schema(string name)
        {
            var path = Path.Combine(VendoredRoot, name);
            Assert.True(File.Exists(path), "vendored schema missing: " + name);
            return File.ReadAllText(path);
        }

        private static bool PrivateBool(string method, params object[] args)
        {
            var info = typeof(P1Client).GetMethod(method,
                BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public);
            Assert.NotNull(info);
            return (bool)info.Invoke(null, args);
        }

        // ── manifest integrity ────────────────────────────────────────────────

        [Fact]
        public void Manifest_PinsServerHead_AndCoversEveryContractFile()
        {
            var manifest = LoadManifest();
            Assert.Equal(ServerPin, manifest.pin);
            Assert.Equal("Shared/ClientCore.Tests/Fixtures/qoder-contracts-6814126", manifest.vendoredRoot);
            Assert.Equal(70, manifest.files.Count);
            Assert.Equal(70, manifest.files.Select(f => f.name).Distinct(StringComparer.Ordinal).Count());
            Assert.All(manifest.files, f => Assert.Contains(f.kind, new[] { "schema", "example" }));
            Assert.All(manifest.files, f => Assert.Contains(f.location, new[] { "in-tree", "vendored", "drift" }));
            Assert.All(manifest.files, f => Assert.Matches("^[0-9a-f]{64}$", f.sha256));

            // Every vendored byte is present and every vendored file is pinned:
            // the vendored tree and the manifest describe exactly the same set.
            var vendored = Directory.GetFiles(VendoredRoot, "*.schema.json", SearchOption.TopDirectoryOnly)
                .Select(Path.GetFileName)
                .Concat(Directory.GetFiles(Path.Combine(VendoredRoot, "Examples"), "*.example.json",
                    SearchOption.TopDirectoryOnly).Select(Path.GetFileName))
                .ToHashSet(StringComparer.Ordinal);
            var pinned = manifest.files.Select(f => f.name).ToHashSet(StringComparer.Ordinal);
            Assert.Equal(pinned, vendored);
        }

        [Fact]
        public void Manifest_VendoredBytes_MatchPinnedHashes()
        {
            foreach (var entry in LoadManifest().files)
            {
                var path = VendoredPath(entry);
                Assert.True(File.Exists(path), "vendored file missing: " + entry.name);
                Assert.Equal(entry.sha256, Sha256Hex(path));
            }
        }

        [Fact]
        public void Manifest_InTreeBytes_MatchRecordedLocation()
        {
            foreach (var entry in LoadManifest().files)
            {
                var path = InTreePath(entry);
                if (entry.location == "vendored")
                {
                    // Not in the client checkout yet: the vendored copy is the
                    // only source, and the checkout must not carry other bytes.
                    Assert.False(File.Exists(path),
                        "manifest says vendored but " + entry.name + " exists in-tree");
                    continue;
                }
                Assert.True(File.Exists(path), "in-tree contract missing: " + entry.name);
                var actual = Sha256Hex(path);
                if (entry.location == "in-tree")
                {
                    Assert.Equal(entry.sha256, actual);
                }
                else
                {
                    // Drift: the checkout carries older bytes, recorded here so
                    // it is visible; the pinned bytes come from the vendored copy.
                    Assert.NotNull(entry.inTreeSha256);
                    Assert.Equal(entry.inTreeSha256, actual);
                    Assert.NotEqual(entry.sha256, actual);
                }
            }
        }

        [Fact]
        public void InTreeContractTree_HasNoUnpinnedFiles()
        {
            var pinned = LoadManifest().files.Select(f => f.name).ToHashSet(StringComparer.Ordinal);
            var onDisk = Directory.GetFiles(InTreeRoot, "*.schema.json", SearchOption.TopDirectoryOnly)
                .Select(Path.GetFileName)
                .Concat(Directory.GetFiles(Path.Combine(InTreeRoot, "Examples"), "*.example.json",
                    SearchOption.TopDirectoryOnly).Select(Path.GetFileName));
            var unpinned = onDisk.Where(name => !pinned.Contains(name)).OrderBy(n => n, StringComparer.Ordinal)
                .ToList();
            Assert.True(unpinned.Count == 0,
                "unpinned contract files in checkout: " + string.Join(", ", unpinned));
            // And the checkout really has its expected share of the pin set.
            Assert.Equal(40, onDisk.Count());
        }

        [Fact]
        public void MutatedContractBytes_DifferFromPinnedHash()
        {
            // Negative control for the pin itself: flipping one byte of a pinned
            // example must produce a different digest, so the runner's --contract-pin
            // verification (same algorithm) cannot be satisfied by drifted content.
            var entry = LoadManifest().files.First(f => f.name == "TalkResponse.example.json");
            var bytes = File.ReadAllBytes(VendoredPath(entry));
            bytes[bytes.Length - 2] = bytes[bytes.Length - 2] == (byte)' ' ? (byte)'x' : (byte)' ';
            var temp = Path.Combine(Path.GetTempPath(), "qoder-pin-negative-" + Guid.NewGuid().ToString("N") + ".json");
            try
            {
                File.WriteAllBytes(temp, bytes);
                Assert.NotEqual(entry.sha256, Sha256Hex(temp));
            }
            finally { if (File.Exists(temp)) File.Delete(temp); }
        }

        // ── success + identity: world / quest / inventory (v1) ───────────────

        [Fact]
        public void WorldSnapshot_Example_MeetsWireContract()
        {
            var world = P1Wire.Decode<P1World>(Example("WorldSnapshot.example.json"));
            Assert.True(P1Wire.Valid(world));
            Assert.Equal("MAP_BEN_MUA", world.mapId);
            Assert.True(world.revision >= 0 && world.serverTick >= 0);
            Assert.True(P1Wire.Finite(world.self.x) && P1Wire.Finite(world.self.y));
            Assert.InRange(world.self.hp, 0, world.self.maxHp);
            Assert.InRange(world.self.mp, 0, world.self.maxHp == 0 ? 0 : world.self.maxMp);
            Assert.Equal(2, world.entities.Length);
            Assert.All(world.entities, e => Assert.False(string.IsNullOrEmpty(e.entityId)));

            // Negative: hp above maxHp must fail the same validator the client uses.
            var mutated = JObject.Parse(Example("WorldSnapshot.example.json"));
            mutated["self"]["hp"] = world.self.maxHp + 1;
            Assert.False(P1Wire.Valid(P1Wire.Decode<P1World>(mutated.ToString(Formatting.None))));
            Assert.False(P1Wire.Finite(double.NaN));
            Assert.False(P1Wire.Finite(double.PositiveInfinity));
        }

        [Fact]
        public void WorldSnapshotV2_Example_DecodesRequiredFields()
        {
            var world = P1Wire.Decode<P1WorldV2>(Example("WorldSnapshotV2.example.json"));
            Assert.Equal(2, world.schemaVersion);
            Assert.Equal("MAP_BEN_MUA#1", world.mapInstanceId);
            Assert.Equal("OVERWORLD", world.floorId);
            Assert.True(world.audience.aoiEnterWu > 0);
            Assert.True(world.audience.aoiLeaveWu >= world.audience.aoiEnterWu);
            Assert.Equal(4, world.entities.Length);
            Assert.All(world.entities, e =>
            {
                Assert.False(string.IsNullOrEmpty(e.healthState));
                Assert.True(e.revision >= 1 && e.lifeId >= 1);
            });
        }

        [Fact]
        public void QuestAndInventoryExamples_DecodeTypedAndValidate()
        {
            var quest = P1Wire.Decode<P1Quest>(Example("QuestState.example.json"));
            Assert.True(PrivateBool("ValidQuest", quest));
            Assert.Equal("P00-01", quest.questId);
            Assert.Equal(1, quest.objectiveCounters["OBJ_P00_01_PACKAGES"]);

            var accepted = P1Wire.Decode<P1Response<P1Quest>>(Example("QuestAcceptResponse.example.json"));
            Assert.Equal(1, accepted.schemaVersion);
            Assert.True(P1Wire.Hex32(accepted.requestId));
            Assert.True(P1Wire.Hex32(accepted.sessionId));
            Assert.True(PrivateBool("ValidQuest", accepted.result));
            Assert.Equal("ACTIVE", accepted.result.state);

            var inventory = P1Wire.Decode<P1Inventory>(Example("InventorySnapshot.example.json"));
            Assert.True(PrivateBool("ValidInventory", inventory));
            Assert.Equal(7, inventory.inventoryRevision);
            Assert.Equal(2, inventory.items.Length);
            Assert.Equal(20, inventory.currencies.Single().amount);

            var equipment = P1Wire.Decode<P1Response<P1Inventory>>(Example("EquipmentResponse.example.json"));
            Assert.True(P1Wire.Hex32(equipment.sessionId));
            Assert.True(PrivateBool("ValidInventory", equipment.result));
            Assert.Equal("EQUIPPED", equipment.result.items.Single().location);
        }

        // ── talk: credited/replayed/nullability + receipt identity ────────────

        [Fact]
        public void TalkResponse_Example_ParsesNullabilityAndReceiptIdentity()
        {
            var request = P1Wire.Decode<P1QuestTalkIntent>(Example("TalkRequest.example.json"));
            var response = P1Wire.Decode<P1Response<P1QuestTalkResult>>(Example("TalkResponse.example.json"));

            Assert.Equal(1, response.schemaVersion);
            // requestId is server-minted at this contract, not an echo of the
            // client's envelope id; it must still be a traceable hex32 id.
            Assert.True(P1Wire.Hex32(response.requestId));
            Assert.True(P1Wire.Hex32(response.sessionId));
            Assert.Matches("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", response.serverTimeUtc);
            Assert.Null(response.error);

            var receipt = response.result;
            Assert.NotNull(receipt);
            // Receipt identity: the answer describes the node that was asked for.
            Assert.Equal(request.npcId, receipt.npcId);
            Assert.Equal(request.nodeId, receipt.nodeId);
            Assert.Matches("^[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]{2}$", receipt.questId);
            Assert.Matches("^NPC_[A-Z0-9_]+$", receipt.npcId);
            Assert.Matches("^[A-Z][A-Z0-9_]{2,63}$", receipt.nodeId);
            // Nullability: pure narrative node carries no objective, no flag and
            // no credit receipt id — all three are explicitly null on the wire.
            Assert.Null(receipt.objectiveId);
            Assert.Null(receipt.appliedFlag);
            Assert.Null(receipt.eventId);
            Assert.False(receipt.credited);
            Assert.False(receipt.replayed);
            Assert.True(receipt.revision >= 0);
            Assert.True(PrivateBool("ValidTalk", receipt));
        }

        [Fact]
        public void TalkResponse_MissingRequiredRevision_Throws()
        {
            var json = JObject.Parse(Example("TalkResponse.example.json"));
            ((JObject)json["result"]).Remove("revision");
            Assert.ThrowsAny<JsonException>(() =>
                P1Wire.Decode<P1Response<P1QuestTalkResult>>(json.ToString(Formatting.None)));
        }

        [Fact]
        public void TalkResponse_MutatedReceipts_AreRejected()
        {
            var receipt = P1Wire.Decode<P1Response<P1QuestTalkResult>>(Example("TalkResponse.example.json")).result;

            // A credited node must carry its deterministic receipt id.
            receipt.credited = true;
            Assert.False(PrivateBool("ValidTalk", receipt));
            receipt = P1Wire.Decode<P1Response<P1QuestTalkResult>>(Example("TalkResponse.example.json")).result;

            // Pattern mutations on every guarded field.
            receipt.questId = "p00-05";
            Assert.False(PrivateBool("ValidTalk", receipt));
            receipt = P1Wire.Decode<P1Response<P1QuestTalkResult>>(Example("TalkResponse.example.json")).result;

            receipt.npcId = "LYAN";
            Assert.False(PrivateBool("ValidTalk", receipt));
            receipt = P1Wire.Decode<P1Response<P1QuestTalkResult>>(Example("TalkResponse.example.json")).result;

            receipt.eventId = "PQTALK_not-hex-64-chars";
            Assert.False(PrivateBool("ValidTalk", receipt));
            receipt = P1Wire.Decode<P1Response<P1QuestTalkResult>>(Example("TalkResponse.example.json")).result;

            receipt.revision = -1;
            Assert.False(PrivateBool("ValidTalk", receipt));
        }

        // ── portal: server-owned destination + applied/replayed ──────────────

        [Fact]
        public void PortalResponse_Example_ParsesAndMatchesRequestedPortal()
        {
            var request = P1Wire.Decode<P1Envelope<P1WorldPortalIntent>>(Example("PortalRequest.example.json"));
            var response = P1Wire.Decode<P1Response<P1WorldPortalResult>>(Example("PortalResponse.example.json"));

            Assert.True(P1Wire.Hex32(response.requestId));
            Assert.True(P1Wire.Hex32(response.sessionId));
            Assert.Null(response.error);

            var receipt = response.result;
            Assert.Equal(request.payload.portalId, receipt.portalId);
            Assert.Matches("^MAP_[A-Z0-9_]+$", receipt.mapId);
            Assert.Matches("^P1PORTAL_[0-9a-f]{64}$", receipt.eventId);
            Assert.True(P1Wire.Finite(receipt.xWu) && P1Wire.Finite(receipt.yWu));
            Assert.InRange(receipt.xWu, -100000, 100000);
            Assert.InRange(receipt.yWu, -100000, 100000);
            Assert.True(receipt.applied);
            Assert.False(receipt.replayed);
            Assert.True(receipt.revision >= 0);
            Assert.True(PrivateBool("ValidPortal", receipt));
        }

        [Fact]
        public void PortalResponse_MutatedReceipts_AreRejected()
        {
            var fresh = () => P1Wire.Decode<P1Response<P1WorldPortalResult>>(
                Example("PortalResponse.example.json")).result;

            var receipt = fresh();
            receipt.portalId = "TP_UNKNOWN_PORTAL";
            Assert.False(PrivateBool("ValidPortal", receipt));

            receipt = fresh();
            receipt.xWu = 100001;
            Assert.False(PrivateBool("ValidPortal", receipt));

            receipt = fresh();
            receipt.yWu = double.NaN;
            Assert.False(PrivateBool("ValidPortal", receipt));

            receipt = fresh();
            receipt.eventId = "P1PORTAL_ZZ";
            Assert.False(PrivateBool("ValidPortal", receipt));

            receipt = fresh();
            receipt.inflightCastsCancelled = -1;
            Assert.False(PrivateBool("ValidPortal", receipt));
        }

        // ── death return: applied/replayed XOR, zero penalties, range ────────

        [Fact]
        public void DeathReturnResponse_Example_Parses()
        {
            var response = P1Wire.Decode<P1Response<P1DeathReturnResultV1>>(
                Example("DeathReturnResponse.example.json"));
            Assert.True(P1Wire.Hex32(response.requestId));
            Assert.True(P1Wire.Hex32(response.sessionId));

            var receipt = response.result;
            Assert.True(receipt.applied);
            Assert.False(receipt.replayed);
            Assert.Matches("^MAP_[A-Z0-9_]+$", receipt.mapId);
            Assert.True(P1Wire.Finite(receipt.xWu) && P1Wire.Finite(receipt.yWu));
            Assert.InRange(receipt.hp, 1, receipt.maxHp);
            Assert.InRange(receipt.mp, 0, receipt.maxMp);
            Assert.Equal(0, receipt.penalties.xp);
            Assert.Equal(0, receipt.penalties.currency);
            Assert.Equal(0, receipt.penalties.durability);
            Assert.True(receipt.cleared.inflightCasts >= 0 && receipt.cleared.reservedCounters >= 0);
            Assert.True(receipt.nextReturnAllowedAtTick.Value >= 0);
            Assert.True(PrivateBool("ValidDeathReturn", receipt));
        }

        [Fact]
        public void DeathReturn_MutatedReceipts_AreRejected()
        {
            var fresh = () => P1Wire.Decode<P1Response<P1DeathReturnResultV1>>(
                Example("DeathReturnResponse.example.json")).result;

            var receipt = fresh();
            receipt.replayed = true; // applied == replayed is not a valid receipt
            Assert.False(PrivateBool("ValidDeathReturn", receipt));

            receipt = fresh();
            receipt.penalties.currency = 1; // death return never charges currency
            Assert.False(PrivateBool("ValidDeathReturn", receipt));

            receipt = fresh();
            receipt.hp = receipt.maxHp + 1;
            Assert.False(PrivateBool("ValidDeathReturn", receipt));

            receipt = fresh();
            receipt.mapId = "BEN_MUA"; // missing MAP_ prefix
            Assert.False(PrivateBool("ValidDeathReturn", receipt));
        }

        // ── inventory v2: twelve closed slots, nullability, dedupe ───────────

        [Fact]
        public void InventoryV2Response_Example_Parses()
        {
            var response = P1Wire.Decode<P1Response<P1InventorySnapshotV2>>(
                Example("InventoryV2Response.example.json"));
            Assert.Equal(2, response.schemaVersion);
            Assert.True(P1Wire.Hex32(response.requestId));
            Assert.True(P1Wire.Hex32(response.sessionId));

            var inv = response.result;
            Assert.Equal(2, inv.schemaVersion);
            Assert.Equal("V2_SIDE_BY_SIDE_KEEP_V1_FIVE_SLOT_CONTRACT", inv.slotSpec);
            Assert.Equal(100, inv.bagSlots);
            Assert.Equal(12, inv.slots.Length);
            Assert.Equal(new[] { "HAT", "CHEST", "LEGS", "WEAPON", "GLOVES", "BOOTS",
                "NECK", "RING_L", "RING_R", "PENDANT", "CLOAK", "SEAL" },
                inv.slots.Select(s => s.slotId).ToArray());
            // Nullability: an empty slot carries an explicit JSON null item.
            Assert.Null(inv.slots.Single(s => s.slotId == "CHEST").item);
            Assert.Null(inv.bag.Single().slotId);
            Assert.Empty(inv.unsupported);
            Assert.True(PrivateBool("ValidInventoryV2", inv));
        }

        [Fact]
        public void InventoryV2_MutatedSnapshots_AreRejected()
        {
            var fresh = () => P1Wire.Decode<P1Response<P1InventorySnapshotV2>>(
                Example("InventoryV2Response.example.json")).result;

            var inv = fresh();
            inv.bagSlots = 99;
            Assert.False(PrivateBool("ValidInventoryV2", inv));

            inv = fresh();
            inv.slots = inv.slots.Take(11).ToArray();
            Assert.False(PrivateBool("ValidInventoryV2", inv));

            inv = fresh();
            // Duplicate instance across slot and bag must be rejected.
            inv.bag[0].instanceId = inv.slots.Single(s => s.slotId == "HAT").item.instanceId;
            Assert.False(PrivateBool("ValidInventoryV2", inv));

            inv = fresh();
            inv.slotSpec = "V1_FIVE_SLOT";
            Assert.False(PrivateBool("ValidInventoryV2", inv));
        }

        // ── interact / turn-in: credited rewards and quest updates ───────────

        [Fact]
        public void InteractAndTurnInExamples_DecodeTyped()
        {
            var interact = P1Wire.Decode<P1Response<P1InteractResult>>(Example("InteractResponse.example.json"));
            Assert.True(P1Wire.Hex32(interact.requestId));
            Assert.True(P1Wire.Hex32(interact.sessionId));
            var result = interact.result;
            Assert.True(P1Wire.Hex32(result.interactionId));
            Assert.Equal("ENT_MAN_BM_OBJ_BM_PACKAGE_01", result.targetId);
            Assert.Equal("INTERACTABLE", result.kind);
            Assert.Equal("collected", result.outcome);
            Assert.Equal("DEPLETED", result.targetState);
            Assert.Single(result.questUpdates);
            Assert.Equal(3, result.questUpdates[0].revision);
            Assert.True(result.questUpdates.All(q => PrivateBool("ValidQuest", q)));

            var turnIn = P1Wire.Decode<P1Response<P1TurnInResult>>(Example("TurnInResponse.example.json"));
            Assert.True(P1Wire.Hex32(turnIn.requestId));
            Assert.Equal("COMPLETED", turnIn.result.questState.state);
            Assert.Equal(20, turnIn.result.rewards.currency.Single().amount);
            Assert.False(turnIn.result.rewards.xp.applied);
            Assert.Contains("P00-02", turnIn.result.unlocks);
            Assert.True(PrivateBool("ValidQuest", turnIn.result.questState));
        }

        // ── encounter: strict additionalProperties validator ─────────────────

        [Fact]
        public void EncounterSnapshot_Example_PassesStrictValidator()
        {
            var json = Example("EncounterSnapshotV1.example.json");
            Assert.True(EncounterSnapshotValidator.TryParse(json, out var snapshot, out var error), error);
            Assert.Equal("ENC-0123456789ABCDEF01234567", snapshot.EncounterId);
            Assert.Equal("P00-05", snapshot.QuestId);

            // Negative controls: unknown property, bad enum, hp over max — the
            // strict validator must reject all three instead of best-effort parsing.
            var unknown = JObject.Parse(json);
            unknown["notInSchema"] = 1;
            Assert.False(EncounterSnapshotValidator.TryParse(
                unknown.ToString(Formatting.None), out _, out _));

            var badStatus = JObject.Parse(json);
            badStatus["status"] = "CLOSED";
            Assert.False(EncounterSnapshotValidator.TryParse(
                badStatus.ToString(Formatting.None), out _, out _));

            var overMax = JObject.Parse(json);
            overMax["bossHp"] = (int)overMax["bossMaxHp"] + 1;
            Assert.False(EncounterSnapshotValidator.TryParse(
                overMax.ToString(Formatting.None), out _, out _));
        }

        [Fact]
        public void EncounterResponse_Envelope_DecodesResultForStrictValidator()
        {
            var response = P1Wire.Decode<P1Response<JToken>>(Example("EncounterResponseV1.example.json"));
            Assert.NotNull(response);
            Assert.Equal(1, response.schemaVersion);
            Assert.True(P1Wire.Hex32(response.requestId));
            Assert.True(P1Wire.Hex32(response.sessionId));
            Assert.NotNull(response.result);
            Assert.True(EncounterSnapshotValidator.TryParse(
                response.result.ToString(Formatting.None), out var snapshot, out var error), error);
            Assert.Equal(EncounterStatus.Open, snapshot.Status);
        }

        // ── combat v2: page cursor order, result mapping ─────────────────────

        [Fact]
        public void CombatV2Examples_DecodeTypedAndValidate()
        {
            var page = P1Wire.Decode<P1EventPageV2>(Example("CombatEventPageV2.example.json"));
            Assert.Equal(2, page.schemaVersion);
            Assert.True(P1Wire.Hex32(page.sessionId));
            Assert.False(page.resyncRequired);
            Assert.Equal(42, page.nextCursor);
            Assert.True(PrivateBool("ValidEvents", page.events, 0L));
            Assert.True(page.events.Select(e => e.cursor).SequenceEqual(page.events.Select(e => e.cursor).OrderBy(c => c)));

            var result = P1Wire.Decode<P1CastResultV2>(Example("CombatResultV2.example.json"));
            Assert.True(P1Wire.Hex32(result.castId));
            // Wire name nextInputSequence maps to the accepted sequence field.
            Assert.Equal(7, result.acceptedInputSequence);
            Assert.True(result.mpCost >= 0 && result.mp >= 0);
            Assert.Single(result.events);

            var combatEvent = P1Wire.Decode<P1CombatEvent>(Example("CombatEvent.example.json"));
            Assert.True(P1Wire.Hex32(combatEvent.eventId));
            Assert.Equal(18, combatEvent.payload.damage);
            Assert.True(combatEvent.payload.hit.Value);

            // Negative: a duplicated eventId breaks the page's dedupe contract.
            var mutated = JObject.Parse(Example("CombatEventPageV2.example.json"));
            mutated["events"][1]["eventId"] = mutated["events"][0]["eventId"];
            var dupPage = P1Wire.Decode<P1EventPageV2>(mutated.ToString(Formatting.None));
            Assert.False(PrivateBool("ValidEvents", dupPage.events, 0L));
        }

        // ── request envelopes: identity + payload shapes ─────────────────────

        [Fact]
        public void RequestEnvelopeExamples_DecodeTyped()
        {
            var envelope = P1Wire.Decode<P1Envelope<P1Move>>(Example("Envelope.example.json"));
            Assert.True(P1Wire.Hex32(envelope.requestId));
            Assert.True(P1Wire.Hex32(envelope.idempotencyKey));
            Assert.Equal(1, envelope.payload.inputSequence);
            Assert.Equal(1, envelope.payload.moveX);
            Assert.Equal(0, envelope.payload.moveY);

            var move = P1Wire.Decode<P1Move>(Example("MoveIntent.example.json"));
            Assert.Equal(1, move.inputSequence);

            var equip = P1Wire.Decode<P1Envelope<P1EquipV2>>(Example("EquipV2Request.example.json"));
            Assert.Equal(2, equip.schemaVersion);
            Assert.True(equip.payload.expectedRevision >= 1);
            Assert.Matches("^ITM_", equip.payload.itemInstanceId);

            var unequip = P1Wire.Decode<P1Envelope<P1UnequipV2>>(Example("UnequipV2Request.example.json"));
            Assert.Equal("RING_L", unequip.payload.slotId);

            var portalRequest = P1Wire.Decode<P1Envelope<P1WorldPortalIntent>>(Example("PortalRequest.example.json"));
            Assert.Equal("TP_BM_THANH_LAC", portalRequest.payload.portalId);

            var talkRequest = P1Wire.Decode<P1QuestTalkIntent>(Example("TalkRequest.example.json"));
            Assert.Matches("^NPC_[A-Z0-9_]+$", talkRequest.npcId);

            var acceptRequest = P1Wire.Decode<P1QuestAccept>(Example("QuestAcceptRequest.example.json"));
            Assert.Equal("P00-01", acceptRequest.questId);

            var interactRequest = P1Wire.Decode<P1Interact>(Example("InteractRequest.example.json"));
            Assert.False(string.IsNullOrEmpty(interactRequest.targetId));

            var combatInput = P1Wire.Decode<P1Cast>(Example("CombatInput.example.json"));
            Assert.True(combatInput.inputSequence >= 1);
            Assert.True(P1Wire.Finite(combatInput.aimX) && P1Wire.Finite(combatInput.aimY));

            var combatInputV2 = P1Wire.Decode<P1CastV2>(Example("CombatInputV2.example.json"));
            Assert.Equal("SKILL", combatInputV2.actionKind);

            // Payload-only intents with no dedicated client type keep their wire
            // shape asserted directly — never a fabricated model.
            var deathReturn = JObject.Parse(Example("DeathReturnRequest.example.json"));
            Assert.Empty(deathReturn.Properties()); // payload is deliberately empty
            var teleport = JObject.Parse(Example("TeleportRequest.example.json"));
            Assert.Equal(new[] { "mapId", "reason", "xWu", "yWu" },
                teleport.Properties().Select(p => p.Name).OrderBy(n => n, StringComparer.Ordinal).ToArray());
            var turnInRequest = JObject.Parse(Example("TurnInRequest.example.json"));
            Assert.Equal(new[] { "npcId", "questId" },
                turnInRequest.Properties().Select(p => p.Name).OrderBy(n => n, StringComparer.Ordinal).ToArray());
        }

        // ── error envelope: refusal shape from the pinned schema ─────────────

        [Fact]
        public void ErrorEnvelope_ParsesTypedRefusal()
        {
            // Shape taken verbatim from the pinned TalkResponse.schema.json
            // error definition (code/messageKey/retryable required; the schema
            // documents a closed reveal gate answering 409 invalid_transition
            // with fieldErrors naming revealGate).
            var json = @"{
              ""schemaVersion"": 1,
              ""requestId"": ""99999999999999999999999999999999"",
              ""sessionId"": ""0123456789abcdef0123456789abcdef"",
              ""serverTimeUtc"": ""2026-11-06T07:00:00Z"",
              ""error"": {
                ""code"": ""invalid_transition"",
                ""messageKey"": ""P1.ERROR.INVALID_TRANSITION"",
                ""retryable"": true,
                ""fieldErrors"": [""revealGate""],
                ""correlationId"": ""88888888888888888888888888888888""
              }
            }";
            var response = P1Wire.Decode<P1Response<P1QuestTalkResult>>(json);
            Assert.NotNull(response.error);
            Assert.Equal("invalid_transition", response.error.code);
            Assert.Equal("P1.ERROR.INVALID_TRANSITION", response.error.messageKey);
            Assert.True(response.error.retryable);
            Assert.Equal(new[] { "revealGate" }, response.error.fieldErrors);
            Assert.Null(response.result); // a refusal never carries a receipt
            // Good() semantics used by ApplyTalk: error present => definite refusal,
            // not an unknown outcome.
            Assert.True(response.error != null);

            // Malformed error code (pattern violation in the pinned schema) must
            // not parse as a typed refusal either.
            var bad = json.Replace("invalid_transition", "Invalid-Transition");
            var badResponse = P1Wire.Decode<P1Response<P1QuestTalkResult>>(bad);
            Assert.NotNull(badResponse.error);
            Assert.DoesNotMatch("^[a-z][a-z0-9_]{3,63}$", badResponse.error.code);
        }

        // ── schemas themselves are valid JSON documents ───────────────────────

        [Fact]
        public void EveryPinnedSchema_IsReadableJsonSchemaDocument()
        {
            foreach (var entry in LoadManifest().files.Where(f => f.kind == "schema"))
            {
                var text = Schema(entry.name);
                var json = JObject.Parse(text);
                Assert.Equal("https://json-schema.org/draft/2020-12/schema", (string)json["$schema"]);
                Assert.False(string.IsNullOrEmpty((string)json["$id"]));
                Assert.Equal("object", (string)json["type"]);
                Assert.NotNull(json["properties"]);
                Assert.NotNull(json["required"]);
            }
        }
    }
}
