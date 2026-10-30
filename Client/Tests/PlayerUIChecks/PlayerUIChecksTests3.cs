// PlayerUIChecksTests3 — Extended tests for AG-02 Milestone 2:
//   - NPC entity vs template mapping & lifetime token (AGR2-01, AGR2-02)
//   - Character sheet & equipment slot normalization (DEC-021, DEC-023)
//   - Item metadata resolver & tooltip resolution
//   - Single Escape ownership & modal stack (AGR2-03)
//   - Full P00-01 quest journey flow through presenters
// Owner: Antigravity Remote — Issue #85.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using Xunit;

namespace PlayerUIChecks
{
    public class DialogueIdentityAndLifetimeTests
    {
        private sealed class TestAdapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState => UIConnectionState.Ready;
            public bool HasPendingMutation => false;
            public string LastErrorCode => null;
            public string LastCorrelationId => null;
            public P1Self Self { get; set; }
            public P1World World => null;
            public P1WorldV2 WorldV2 => null;
            public P1Inventory Inventory { get; set; }
            public P1Quest[] Quests { get; set; }

            public string LastInteractedTargetId { get; private set; }
            public string LastAcceptedQuestId { get; private set; }
            public string LastAcceptedNpcId { get; private set; }
            public string LastTurnedInQuestId { get; private set; }
            public string LastTurnedInNpcId { get; private set; }

            public Func<string, Task<P1Result>> OnInteract;

            public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());

            public Task<P1Result> AcceptQuestAsync(string q, string n, CancellationToken ct)
            {
                LastAcceptedQuestId = q;
                LastAcceptedNpcId = n;
                return Task.FromResult(P1Result.Ok());
            }

            public Task<P1Result> InteractAsync(string id, CancellationToken ct)
            {
                LastInteractedTargetId = id;
                return OnInteract != null ? OnInteract(id) : Task.FromResult(P1Result.Ok());
            }

            public Task<P1Result> TurnInQuestAsync(string q, string n, CancellationToken ct)
            {
                LastTurnedInQuestId = q;
                LastTurnedInNpcId = n;
                return Task.FromResult(P1Result.Ok());
            }

            public Task<P1Result> RetryPendingAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
        }

        private static TestAdapter WithQuest(string state) => new TestAdapter
        {
            Quests = new[]
            {
                new P1Quest
                {
                    questId = "P00-01",
                    state = state,
                    stepId = "STEP_BEN_MUA",
                    revision = 1,
                    objectiveCounters = new Dictionary<string, int>()
                }
            }
        };

        [Theory]
        [InlineData("NPC_LYAN", "AVAILABLE", DialogueActionType.AcceptQuest)]
        [InlineData("NPC_TA_VAN_KHANH", "READY_TO_TURN_IN", DialogueActionType.TurnInQuest)]
        public async Task TemplateIdentityControl(string id, string state, DialogueActionType action)
        {
            var presenter = new NpcDialoguePresenter(WithQuest(state));
            await presenter.InteractAsync(id, CancellationToken.None);
            Assert.Contains(presenter.State.Value.Choices, c => c.Enabled && c.ActionType == action);
        }

        [Theory]
        [InlineData("ENT_MAN_BM_NPC_LYAN", "AVAILABLE", DialogueActionType.AcceptQuest)]
        [InlineData("ENT_MAN_BM_NPC_TA_VAN_KHANH", "READY_TO_TURN_IN", DialogueActionType.TurnInQuest)]
        public async Task WorldEntityIdentityMustResolveQuestAction(string entityId, string state, DialogueActionType action)
        {
            var adapter = WithQuest(state);
            var presenter = new NpcDialoguePresenter(adapter);
            await presenter.InteractAsync(entityId, CancellationToken.None);

            // Wire request preserved entity ID
            Assert.Equal(entityId, adapter.LastInteractedTargetId);

            // Choices resolved canonical quest action
            Assert.Contains(presenter.State.Value.Choices, c => c.Enabled && c.ActionType == action);
        }

        [Fact]
        public async Task ClearedDialogueMustIgnoreLateCompletion()
        {
            var response = new TaskCompletionSource<P1Result>(TaskCreationOptions.RunContinuationsAsynchronously);
            var adapter = WithQuest("AVAILABLE");
            adapter.OnInteract = _ => response.Task;
            var presenter = new NpcDialoguePresenter(adapter);

            var request = presenter.InteractAsync("NPC_LYAN", CancellationToken.None);
            Assert.True(presenter.State.IsLoading);

            presenter.Clear();
            response.SetResult(P1Result.Ok());
            await request;

            Assert.Equal(LoadPhase.Idle, presenter.State.Phase);
            Assert.Null(presenter.State.Value);
        }

        [Fact]
        public async Task AcceptQuest_SendsCanonicalNpcId()
        {
            var adapter = WithQuest("AVAILABLE");
            var presenter = new NpcDialoguePresenter(adapter);
            await presenter.InteractAsync("ENT_MAN_BM_NPC_LYAN", CancellationToken.None);

            await presenter.AcceptQuestAsync("P00-01", "ENT_MAN_BM_NPC_LYAN", CancellationToken.None);

            // Canonical template ID sent to accept endpoint
            Assert.Equal("P00-01", adapter.LastAcceptedQuestId);
            Assert.Equal("NPC_LYAN", adapter.LastAcceptedNpcId);
        }

        [Fact]
        public async Task TurnInQuest_SendsCanonicalNpcId()
        {
            var adapter = WithQuest("READY_TO_TURN_IN");
            var presenter = new NpcDialoguePresenter(adapter);
            await presenter.InteractAsync("ENT_MAN_BM_NPC_TA_VAN_KHANH", CancellationToken.None);

            await presenter.TurnInQuestAsync("P00-01", "ENT_MAN_BM_NPC_TA_VAN_KHANH", CancellationToken.None);

            // Canonical template ID sent to turn-in endpoint
            Assert.Equal("P00-01", adapter.LastTurnedInQuestId);
            Assert.Equal("NPC_TA_VAN_KHANH", adapter.LastTurnedInNpcId);
        }
    }

    public class CharacterPresenterTests
    {
        private sealed class FakeAdapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState => UIConnectionState.Ready;
            public bool HasPendingMutation => false;
            public string LastErrorCode => null;
            public string LastCorrelationId => null;
            public P1Self Self { get; set; }
            public P1World World => null;
            public P1WorldV2 WorldV2 => null;
            public P1Inventory Inventory { get; set; }
            public P1Quest[] Quests => null;
            public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> AcceptQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> InteractAsync(string id, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> TurnInQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> RetryPendingAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
        }

        [Fact]
        public void Presenter_IdleWhenSelfNull()
        {
            var adapter = new FakeAdapter { Self = null };
            var presenter = new CharacterPresenter(adapter);
            presenter.Refresh();
            Assert.Equal(LoadPhase.Idle, presenter.State.Phase);
        }

        [Fact]
        public void Presenter_LoadsAuthoritativeVitals()
        {
            var adapter = new FakeAdapter
            {
                Self = new P1Self
                {
                    characterId = "PLAYER_01",
                    classId = "CLASS_MINH_KIEM",
                    hp = 120,
                    maxHp = 150,
                    mp = 50,
                    maxMp = 80,
                    x = 12.5,
                    y = 34.0
                }
            };

            var presenter = new CharacterPresenter(adapter);
            presenter.Refresh();

            Assert.True(presenter.State.IsLoaded);
            var view = presenter.State.Value;
            Assert.Equal("PLAYER_01", view.CharacterId);
            Assert.Equal("CLASS_MINH_KIEM", view.ClassId);
            Assert.Equal(120, view.Hp);
            Assert.Equal(150, view.MaxHp);
            Assert.Equal(50, view.Mp);
            Assert.Equal(80, view.MaxMp);
            Assert.Equal(12.5, view.X);
            Assert.Equal(34.0, view.Y);
        }

        [Fact]
        public void Presenter_MapsEquipmentSlotsCorrectly()
        {
            var adapter = new FakeAdapter
            {
                Self = new P1Self { characterId = "P1", classId = "CLASS_MINH_KIEM", hp = 100, maxHp = 100 },
                Inventory = new P1Inventory
                {
                    inventoryRevision = 1,
                    items = new[]
                    {
                        new P1Item { instanceId = "WEAPON_INST", templateId = "EQ-MK-WEAPON-T1", location = "EQUIPPED", slot = "MAIN_HAND", durability = 100, version = 1 },
                        new P1Item { instanceId = "HAT_INST", templateId = "EQ-MK-HAT-T1", location = "EQUIPPED", slot = "HEAD", durability = 95, version = 1 },
                        new P1Item { instanceId = "BAG_ITEM", templateId = "POT-HP-01", location = "BAG", slot = "0", stack = 5 }
                    }
                }
            };

            var presenter = new CharacterPresenter(adapter);
            presenter.Refresh();

            var view = presenter.State.Value;
            Assert.NotNull(view);

            var weapon = view.GetEquippedItem("EQUIP_WEAPON");
            Assert.NotNull(weapon);
            Assert.Equal("WEAPON_INST", weapon.InstanceId);
            Assert.Equal("Kiếm Mưa Khởi Minh Kiếm", weapon.DisplayName);

            var hat = view.GetEquippedItem("EQUIP_HAT");
            Assert.NotNull(hat);
            Assert.Equal("HAT_INST", hat.InstanceId);
            Assert.Equal("Nón Mưa Khởi Minh Kiếm", hat.DisplayName);

            // Bag item is not in equipment
            Assert.Null(view.GetEquippedItem("EQUIP_CHEST"));
        }

        [Fact]
        public void Presenter_MarksMissingCombatStatsAndDisablesActions()
        {
            var adapter = new FakeAdapter
            {
                Self = new P1Self { characterId = "P1", classId = "CLASS_MINH_KIEM" }
            };
            var presenter = new CharacterPresenter(adapter);
            presenter.Refresh();

            var view = presenter.State.Value;
            Assert.False(view.HasAuthoritativeCombatStats);
            Assert.Null(view.PhysicalAttack);
            Assert.Null(view.Armor);
            Assert.Contains("missing server field", CharacterViewState.MissingStatReason);

            Assert.False(view.CanEquip);
            Assert.False(view.CanUnequip);
            Assert.False(view.CanSalvage);
        }

        [Fact]
        public async Task Presenter_UnequipReturnsUnsupportedEndpoint()
        {
            var adapter = new FakeAdapter { Self = new P1Self { characterId = "P1" } };
            var presenter = new CharacterPresenter(adapter);
            var result = await presenter.UnequipAsync("EQUIP_WEAPON", CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal("UNSUPPORTED_ENDPOINT", result.Code);
        }
    }

    public class ItemMetadataResolverTests
    {
        [Theory]
        [InlineData("EQ-MK-HAT-T1", "Nón Mưa Khởi Minh Kiếm", "EQUIP_HAT", "Thường")]
        [InlineData("EQ-MK-WEAPON-T1", "Kiếm Mưa Khởi Minh Kiếm", "EQUIP_WEAPON", "Thường")]
        [InlineData("POT-HP-01", "Dược Bến Mưa", null, "Thường")]
        [InlineData("GEM-KIM-01", "Ngọc Kim", null, "Thường")]
        [InlineData("MAT-CORE-01", "Lõi Mạch", null, "Tinh")]
        public void Resolver_ResolvesCatalogMetadata(string templateId, string expectedName, string expectedSlot, string expectedRarity)
        {
            var meta = ItemMetadataResolver.Resolve(templateId);
            Assert.Equal(expectedName, meta.DisplayName);
            Assert.Equal(expectedRarity, meta.Rarity);
            if (expectedSlot != null) Assert.Equal(expectedSlot, meta.Slot);
        }

        [Fact]
        public void Resolver_ProvidesCleanFallbackWithoutUnresolvedString()
        {
            var meta = ItemMetadataResolver.Resolve("UNKNOWN_CUSTOM_ITEM");
            Assert.Equal("UNKNOWN_CUSTOM_ITEM", meta.DisplayName);
            Assert.DoesNotContain("UNRESOLVED", meta.DisplayName);
            Assert.Equal("Thường", meta.Rarity);
        }
    }

    public class SingleEscapeOwnerTests
    {
        [Fact]
        public void Router_SingleCloseTopPopsOnlyOneModal()
        {
            var router = new PanelRouter();
            router.Open(PlayerPanel.Inventory, UIConnectionState.Ready);
            Assert.Equal(PlayerPanel.Inventory, router.Current);
            Assert.Equal(0, router.ModalDepth);

            // Open second modal
            router.Open(PlayerPanel.Character, UIConnectionState.Ready);
            Assert.Equal(PlayerPanel.Character, router.Current);
            Assert.Equal(1, router.ModalDepth);

            // Single Escape / CloseTop must only pop the top modal
            router.CloseTop();
            Assert.Equal(PlayerPanel.Inventory, router.Current);
            Assert.Equal(0, router.ModalDepth);

            // Second CloseTop closes the base modal
            router.CloseTop();
            Assert.Equal(PlayerPanel.None, router.Current);
            Assert.Equal(0, router.ModalDepth);
        }
    }
}
