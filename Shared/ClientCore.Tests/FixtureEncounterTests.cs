using System;
using System.IO;
using Newtonsoft.Json.Linq;
using NguMach.Client.Core.Encounter;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class FixtureEncounterTests
    {
        private static string LoadReference()
        {
            var candidates = new[]
            {
                Path.Combine("Fixtures", "encounter_snapshot_v1_reference_20261104.json"),
                Path.Combine("..", "..", "..", "Fixtures", "encounter_snapshot_v1_reference_20261104.json"),
                Path.Combine("..", "..", "..", "..", "Shared", "ClientCore.Tests", "Fixtures", "encounter_snapshot_v1_reference_20261104.json"),
            };
            foreach (var c in candidates) if (File.Exists(c)) return File.ReadAllText(c);
            throw new FileNotFoundException("reference fixture not found");
        }

        private static JObject ReferenceObject()
        {
            return JObject.Parse(LoadReference());
        }

        private static void AssertRejected(string json)
        {
            Assert.False(EncounterSnapshotValidator.TryParse(json, out _, out var err),
                "expected rejection, got success");
            Assert.False(string.IsNullOrWhiteSpace(err));
        }

        private static void AssertRejected(JObject obj)
        {
            AssertRejected(obj.ToString());
        }

        [Fact]
        public void Reference_ParsesStrictly()
        {
            var json = LoadReference();
            Assert.True(EncounterSnapshotValidator.TryParse(json, out var snap, out var err), err);
            Assert.NotNull(snap);
            Assert.Equal("ENC-0123456789ABCDEF01234567", snap.EncounterId);
            Assert.Equal("P00-05", snap.QuestId);
            Assert.Equal("MAN-BM-SPAWN_BM_05_QUEST", snap.BossRecordId);
            Assert.Equal(1L, snap.BossLifeId);
            Assert.Equal(8L, snap.BossRevision);
            Assert.Equal(EncounterStatus.Open, snap.Status);
            Assert.Equal(BossPhase.Phase1, snap.Phase);
            Assert.Equal(1200, snap.BossHp);
            Assert.Equal(1200, snap.BossMaxHp);
            Assert.Equal(2000L, snap.ServerTick);
            Assert.NotNull(snap.RegisteredCharacterIds);
            Assert.Single(snap.RegisteredCharacterIds);
            Assert.NotNull(snap.ActiveMove);
            Assert.Equal("CAST-ALPHA-00000001", snap.ActiveMove.CastId);
            Assert.Equal(MoveState.Telegraph, snap.ActiveMove.State);
            Assert.Equal(18, snap.ActiveMove.TicksRemaining);
            Assert.Equal(2018L, snap.ActiveMove.StateEndsAtTick);
            Assert.Equal(MoveShapeKind.Cone, snap.ActiveMove.Shape.Kind);
            Assert.Equal(178.0, snap.ActiveMove.Shape.CenterXWu);
            Assert.Equal(0.0, snap.ActiveMove.Shape.CenterYWu);
            Assert.Equal(120.0, snap.ActiveMove.Shape.AngleDegrees);
            Assert.Equal(8.0, snap.ActiveMove.Shape.RangeWu.Value);
            Assert.Equal(1.0, snap.ActiveMove.Shape.FacingX.Value);
            Assert.Equal(0.0, snap.ActiveMove.Shape.FacingY.Value);
            Assert.NotNull(snap.MoveCooldownRemainingTicks);
            Assert.Equal(3, snap.MoveCooldownRemainingTicks.Count);
            Assert.NotNull(snap.Arena);
            Assert.Equal("CIRCLE", snap.Arena.Shape);
            Assert.Equal(11.0, snap.Arena.RadiusWu);
            Assert.NotNull(snap.SafePads);
            Assert.Equal(2, snap.SafePads.Count);
            Assert.NotNull(snap.PhaseNpc);
            Assert.Equal("NPC_TA_VAN_KHANH", snap.PhaseNpc.NpcId);
            Assert.False(snap.TrialNpcVisible);
            Assert.True(EncounterSnapshotValidator.IsValid(snap, out var reason), reason);
        }

        [Fact]
        public void Reference_ViewAppliesAndTracksCast()
        {
            var json = LoadReference();
            Assert.True(EncounterSnapshotValidator.TryParse(json, out var snap, out _));
            var view = new EncounterView();
            var upd = view.Apply(snap);
            Assert.True(view.HasSnapshot);
            Assert.True(view.IsTelegraphActive);
            Assert.True(upd.IsNewEncounter);
            Assert.True(upd.IsNewCast);
            Assert.Null(view.LastCastId);
            view.CommitCast();
            Assert.Equal("CAST-ALPHA-00000001", view.LastCastId);
            var upd2 = view.Apply(snap);
            Assert.False(upd2.IsNewCast);
        }

        [Fact]
        public void Reference_Strict_RejectsUnknownTopLevelProperty()
        {
            var obj = ReferenceObject();
            obj["registration"] = new JObject { ["owner"] = "x" };
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsUnknownArenaProperty()
        {
            var obj = ReferenceObject();
            ((JObject)obj["arena"])["owner"] = new JObject { ["characterId"] = "x" };
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsUnknownSafePadProperty()
        {
            var obj = ReferenceObject();
            ((JObject)((JArray)obj["safePads"])[0])["velocity"] = 1;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsUnknownActiveMoveProperty()
        {
            var obj = ReferenceObject();
            ((JObject)obj["activeMove"])["radiusWu"] = 3.0;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsCooldownObjectValue()
        {
            var obj = ReferenceObject();
            ((JObject)obj["moveCooldownRemainingTicks"])["D"] = new JObject { ["ticks"] = 10 };
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsMissingRequiredField()
        {
            var obj = ReferenceObject();
            obj.Remove("bossHp");
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsMissingNullableShapeField()
        {
            var obj = ReferenceObject();
            ((JObject)((JObject)obj["activeMove"])["shape"]).Remove("radiusWu");
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsMissingActiveMoveKey()
        {
            var obj = ReferenceObject();
            obj.Remove("activeMove");
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsMissingWipeCountdownKey()
        {
            var obj = ReferenceObject();
            obj.Remove("wipeCountdownTicks");
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsMissingSafePadField()
        {
            var obj = ReferenceObject();
            ((JObject)((JArray)obj["safePads"])[0]).Remove("applies");
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsNullRequiredField()
        {
            var obj = ReferenceObject();
            obj["status"] = JValue.CreateNull();
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsWrongTypeWithoutThrowing()
        {
            var obj = ReferenceObject();
            obj["bossHp"] = "1200";
            AssertRejected(obj);

            obj = ReferenceObject();
            obj["arena"] = "not-an-object";
            AssertRejected(obj);

            obj = ReferenceObject();
            obj["registeredCharacterIds"] = "CHR_X";
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsInvalidStatusCasing()
        {
            var obj = ReferenceObject();
            obj["status"] = "open";
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsInvalidMoveStateCasing()
        {
            var obj = ReferenceObject();
            ((JObject)obj["activeMove"])["state"] = "telegraph";
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsInvalidShapeKindCasing()
        {
            var obj = ReferenceObject();
            ((JObject)((JObject)obj["activeMove"])["shape"])["kind"] = "cone";
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsInvalidMoveId()
        {
            var obj = ReferenceObject();
            ((JObject)obj["activeMove"])["moveId"] = "D";
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsInvalidCastIdPattern()
        {
            var obj = ReferenceObject();
            ((JObject)obj["activeMove"])["castId"] = "cast-1";
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsInvalidTargetLock()
        {
            var obj = ReferenceObject();
            ((JObject)obj["activeMove"])["targetLock"] = "PLAYER_POSITION";
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsImpactStateNotInPublishedSchema()
        {
            // QOD-21 Q2 publishes only TELEGRAPH and RECOVERY; IMPACT is not a
            // serialized snapshot state.
            var obj = ReferenceObject();
            ((JObject)obj["activeMove"])["state"] = "IMPACT";
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsInvalidEncounterIdPattern()
        {
            var obj = ReferenceObject();
            obj["encounterId"] = "enc-1";
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsInvalidQuestIdPattern()
        {
            var obj = ReferenceObject();
            obj["questId"] = "P5";
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsInvalidBossRecordIdPattern()
        {
            var obj = ReferenceObject();
            obj["bossRecordId"] = "BOSS_05";
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsInvalidBossEntityIdPattern()
        {
            var obj = ReferenceObject();
            obj["bossEntityId"] = "boss-05";
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsInvalidOwnerPattern()
        {
            var obj = ReferenceObject();
            obj["registeredCharacterIds"] = new JArray("owner-1");
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsBossRevisionZero()
        {
            var obj = ReferenceObject();
            obj["bossRevision"] = 0;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsMissingCooldownKey()
        {
            var obj = ReferenceObject();
            ((JObject)obj["moveCooldownRemainingTicks"]).Remove("B");
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsUnknownCooldownKey()
        {
            var obj = ReferenceObject();
            ((JObject)obj["moveCooldownRemainingTicks"])["D"] = 10;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsOutOfRangePhase()
        {
            var obj = ReferenceObject();
            obj["phase"] = 9;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsOutOfRangeHp()
        {
            var obj = ReferenceObject();
            obj["bossHp"] = 1201;
            AssertRejected(obj);

            obj = ReferenceObject();
            obj["bossHp"] = -1;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsNaN()
        {
            var obj = ReferenceObject();
            ((JObject)((JObject)obj["activeMove"])["shape"])["facingX"] = double.NaN;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsInfinity()
        {
            var obj = ReferenceObject();
            var shape = (JObject)((JObject)obj["activeMove"])["shape"];
            shape["rangeWu"] = double.PositiveInfinity;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsNonNormalizedFacing()
        {
            var obj = ReferenceObject();
            ((JObject)((JObject)obj["activeMove"])["shape"])["facingX"] = 2.0;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsDuplicateProperties()
        {
            var json = LoadReference().Replace(
                "\"bossHp\": 1200,",
                "\"bossHp\": 1200,\n  \"bossHp\": 1200,");
            AssertRejected(json);
        }

        [Fact]
        public void Reference_Strict_RejectsTrailingJson()
        {
            AssertRejected(LoadReference() + "{}");
        }

        [Fact]
        public void Reference_Strict_RejectsCircleCarryingFacing()
        {
            var obj = ReferenceObject();
            var shape = (JObject)((JObject)obj["activeMove"])["shape"];
            shape["kind"] = "CIRCLE";
            shape["radiusWu"] = 3.0;
            shape["angleDegrees"] = null;
            shape["rangeWu"] = null;
            // facingX/facingY deliberately retained
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsAnnulusCarryingFacing()
        {
            var obj = ReferenceObject();
            var shape = (JObject)((JObject)obj["activeMove"])["shape"];
            shape["kind"] = "ANNULUS";
            shape["angleDegrees"] = null;
            shape["rangeWu"] = null;
            shape["innerRadiusWu"] = 1.0;
            shape["outerRadiusWu"] = 4.0;
            // facingX/facingY deliberately retained
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsAnnulusInnerNotLessThanOuter()
        {
            var obj = ReferenceObject();
            var shape = (JObject)((JObject)obj["activeMove"])["shape"];
            shape["kind"] = "ANNULUS";
            shape["angleDegrees"] = null;
            shape["rangeWu"] = null;
            shape["facingX"] = null;
            shape["facingY"] = null;
            shape["innerRadiusWu"] = 4.0;
            shape["outerRadiusWu"] = 4.0;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsConeMissingFacing()
        {
            var obj = ReferenceObject();
            var shape = (JObject)((JObject)obj["activeMove"])["shape"];
            shape["facingX"] = null;
            shape["facingY"] = null;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsTickMismatch()
        {
            var obj = ReferenceObject();
            ((JObject)obj["activeMove"])["ticksRemaining"] = 17;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsSafePadOutsideArena()
        {
            var obj = ReferenceObject();
            ((JObject)((JArray)obj["safePads"])[0])["centerXWu"] = 500.0;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsPhaseNpcOutsideArena()
        {
            var obj = ReferenceObject();
            ((JObject)obj["phaseNpc"])["xWu"] = 500.0;
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsMultipleOwners()
        {
            var obj = ReferenceObject();
            obj["registeredCharacterIds"] = new JArray("CHR_A", "CHR_B");
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsEmptyOwnerList()
        {
            var obj = ReferenceObject();
            obj["registeredCharacterIds"] = new JArray();
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsDuplicateOwner()
        {
            var obj = ReferenceObject();
            obj["registeredCharacterIds"] = new JArray("CHR_A", "CHR_A");
            AssertRejected(obj);
        }

        [Fact]
        public void Reference_Strict_RejectsEmptyAndGarbageWithoutThrowing()
        {
            Assert.False(EncounterSnapshotValidator.TryParse(null, out _, out _));
            Assert.False(EncounterSnapshotValidator.TryParse("", out _, out _));
            Assert.False(EncounterSnapshotValidator.TryParse("null", out _, out _));
            Assert.False(EncounterSnapshotValidator.TryParse("[1,2,3]", out _, out _));
            Assert.False(EncounterSnapshotValidator.TryParse("{", out _, out _));
        }

        [Fact]
        public void IsValid_RejectsTamperedDto()
        {
            Assert.True(EncounterSnapshotValidator.TryParse(LoadReference(), out var snap, out var err), err);
            snap.ActiveMove.Shape.FacingX = 3.0;
            Assert.False(EncounterSnapshotValidator.IsValid(snap, out var reason));
            Assert.False(string.IsNullOrWhiteSpace(reason));
        }
    }
}
