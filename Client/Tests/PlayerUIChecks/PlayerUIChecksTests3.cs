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

    public class CinemaPresenterTests
    {
        [Fact]
        public void Cinema_StartsInIdle()
        {
            var presenter = new CinemaPresenter();
            Assert.Equal(CinemaPlaybackPhase.Idle, presenter.State.Phase);
            Assert.Null(presenter.State.SceneId);
            Assert.False(presenter.State.IsPlaying);
            Assert.False(presenter.State.IsEnded);
        }

        [Fact]
        public void Cinema_PlaySceneLoadsSceneMetadata()
        {
            var presenter = new CinemaPresenter();
            presenter.Play("CIN_001");

            Assert.Equal(CinemaPlaybackPhase.Playing, presenter.State.Phase);
            Assert.Equal("CIN_001", presenter.State.SceneId);
            Assert.Equal("Nước không soi bóng", presenter.State.Title);
            Assert.Equal("P00-01", presenter.State.QuestId);
            Assert.Equal(36f, presenter.State.DurationSeconds);
            Assert.True(presenter.State.IsPlaying);
            Assert.True(presenter.State.CanSkip);
        }

        [Fact]
        public void Cinema_UpdateAdvancesProgressAndSubtitles()
        {
            var presenter = new CinemaPresenter();
            presenter.Play("CIN_001");

            Assert.Equal("Bến Mưa lúc rạng đông... sương mờ che khuất mặt sông.", presenter.State.CurrentSubtitle);

            presenter.Update(12f);
            Assert.Equal(12f, presenter.State.ElapsedSeconds);
            Assert.True(presenter.State.ProgressNormalized > 0.3f);
            Assert.Equal("Một phong thư lạ lạc giữa bến trúc.", presenter.State.CurrentSubtitle);

            // Fast forward past duration
            presenter.Update(30f);
            Assert.Equal(CinemaPlaybackPhase.Ended, presenter.State.Phase);
            Assert.True(presenter.State.IsEnded);
            Assert.False(presenter.State.IsPlaying);
        }

        [Fact]
        public void Cinema_SkipEndsPlaybackWithoutReward()
        {
            var presenter = new CinemaPresenter();
            presenter.Play("CIN_001");
            presenter.Skip();

            Assert.Equal(CinemaPlaybackPhase.Ended, presenter.State.Phase);
            Assert.True(presenter.State.IsEnded);
            Assert.False(presenter.State.IsPlaying);
            Assert.False(presenter.State.CanSkip);
        }

        [Fact]
        public void Cinema_UnknownSceneFallsBackToHarness()
        {
            var presenter = new CinemaPresenter();
            presenter.Play("CIN_TEST_CUSTOM");

            Assert.Equal(CinemaPlaybackPhase.Fallback, presenter.State.Phase);
            Assert.True(presenter.State.IsPreviewHarness);
        }

        [Fact]
        public void Cinema_CloseResetsToIdle()
        {
            var presenter = new CinemaPresenter();
            presenter.Play("CIN_001");
            presenter.Close();

            Assert.Equal(CinemaPlaybackPhase.Idle, presenter.State.Phase);
            Assert.Null(presenter.State.SceneId);
        }
    }

    public class QuestJournalCopyTests
    {
        private sealed class JournalAdapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState => UIConnectionState.Ready;
            public bool HasPendingMutation => false;
            public string LastErrorCode => null;
            public string LastCorrelationId => null;
            public P1Self Self => null;
            public P1World World => null;
            public P1WorldV2 WorldV2 => null;
            public P1Inventory Inventory => null;
            public P1Quest[] Quests { get; set; }
            public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> AcceptQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> InteractAsync(string id, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> TurnInQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> RetryPendingAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
        }

        [Fact]
        public async Task Journal_ResolvesP0001Copy()
        {
            var adapter = new JournalAdapter
            {
                Quests = new[]
                {
                    new P1Quest
                    {
                        questId = "P00-01",
                        state = "ACTIVE",
                        stepId = "STEP_BEN_MUA",
                        revision = 1,
                        objectiveCounters = new Dictionary<string, int> { ["OBJ_P00_01_PACKAGES"] = 2 }
                    }
                }
            };

            var presenter = new QuestJournalPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            Assert.NotNull(presenter.State.Value);
            var active = presenter.State.Value.Active;
            Assert.Single(active);
            Assert.Equal("Khởi Đầu Tại Bến Mưa", active[0].DisplayName);
            Assert.Equal("Thu thập gói hàng Bến Mưa (2/3).", active[0].ObjectiveDesc);
        }

        [Fact]
        public async Task Journal_PinTogglesPinnedTracker()
        {
            var adapter = new JournalAdapter
            {
                Quests = new[]
                {
                    new P1Quest { questId = "P00-01", state = "ACTIVE" }
                }
            };

            var presenter = new QuestJournalPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            Assert.False(presenter.State.Value.HasPinnedTracker);
            presenter.TogglePin("P00-01");
            Assert.True(presenter.State.Value.HasPinnedTracker);
            presenter.TogglePin("P00-01");
            Assert.False(presenter.State.Value.HasPinnedTracker);
        }

        [Fact]
        public async Task Journal_SeparatesActiveAndCompletedQuests()
        {
            var adapter = new JournalAdapter
            {
                Quests = new[]
                {
                    new P1Quest { questId = "P00-01", state = "READY_TO_TURN_IN" },
                    new P1Quest { questId = "P00-02", state = "COMPLETED" }
                }
            };

            var presenter = new QuestJournalPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            Assert.Single(presenter.State.Value.Active);
            Assert.Equal("P00-01", presenter.State.Value.Active[0].QuestId);
            Assert.Single(presenter.State.Value.Completed);
            Assert.Equal("P00-02", presenter.State.Value.Completed[0].QuestId);
        }
    }

    public class MapMarkerResolutionTests
    {
        private sealed class MapAdapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState => UIConnectionState.Ready;
            public bool HasPendingMutation => false;
            public string LastErrorCode => null;
            public string LastCorrelationId => null;
            public P1Self Self { get; set; }
            public P1World World { get; set; }
            public P1WorldV2 WorldV2 => null;
            public P1Inventory Inventory => null;
            public P1Quest[] Quests => null;
            public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> AcceptQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> InteractAsync(string id, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> TurnInQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> RetryPendingAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
        }

        [Fact]
        public void Map_ResolvesNpcMarkerLabels()
        {
            var adapter = new MapAdapter
            {
                Self = new P1Self { characterId = "P1", x = 10, y = 10 },
                World = new P1World
                {
                    mapId = "MAP_BEN_MUA",
                    self = new P1Self { characterId = "P1", x = 10, y = 10 },
                    entities = new[]
                    {
                        new P1Entity { entityId = "ENT_MAN_BM_NPC_LYAN", kind = "NPC", x = 12, y = 15 },
                        new P1Entity { entityId = "ENT_MAN_BM_NPC_TA_VAN_KHANH", kind = "NPC", x = 20, y = 25 }
                    }
                }
            };

            var presenter = new MapPresenter(adapter);
            presenter.Refresh();

            Assert.NotNull(presenter.State);
            Assert.Equal("MAP_BEN_MUA", presenter.State.MapId);
            Assert.Equal(3, presenter.State.Markers.Count);

            var lyan = presenter.State.Markers[1];
            Assert.Equal("ENT_MAN_BM_NPC_LYAN", lyan.Id);
            Assert.Equal("Lý An", lyan.Label);

            var tvk = presenter.State.Markers[2];
            Assert.Equal("ENT_MAN_BM_NPC_TA_VAN_KHANH", tvk.Id);
            Assert.Equal("Tạ Vân Khanh", tvk.Label);
        }

        [Fact]
        public void Map_ZoomClampsBetweenBounds()
        {
            var adapter = new MapAdapter
            {
                Self = new P1Self { characterId = "P1", x = 0, y = 0 },
                World = new P1World { mapId = "M1", self = new P1Self { characterId = "P1" } }
            };

            var presenter = new MapPresenter(adapter);
            presenter.Refresh();

            presenter.SetZoom(10f);
            Assert.Equal(4f, presenter.State.ZoomLevel);

            presenter.SetZoom(0.01f);
            Assert.Equal(0.25f, presenter.State.ZoomLevel);
        }

        [Fact]
        public void Map_HandlesNullWorldGracefully()
        {
            var adapter = new MapAdapter { Self = null, World = null };
            var presenter = new MapPresenter(adapter);
            presenter.Refresh();
            Assert.Null(presenter.State);
        }
    }

    public class ScriptedJourneyP0001Tests
    {
        private sealed class JourneyAdapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState => UIConnectionState.Ready;
            public bool HasPendingMutation => false;
            public string LastErrorCode => null;
            public string LastCorrelationId => null;
            public P1Self Self { get; set; }
            public P1World World { get; set; }
            public P1WorldV2 WorldV2 => null;
            public P1Inventory Inventory { get; set; }
            public P1Quest[] Quests { get; set; }

            public string LastInteractedTargetId { get; private set; }
            public string LastAcceptedQuestId { get; private set; }
            public string LastAcceptedNpcId { get; private set; }
            public string LastTurnedInQuestId { get; private set; }
            public string LastTurnedInNpcId { get; private set; }

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
                return Task.FromResult(P1Result.Ok());
            }

            public Task<P1Result> TurnInQuestAsync(string q, string n, CancellationToken ct)
            {
                LastTurnedInQuestId = q;
                LastTurnedInNpcId = n;
                return Task.FromResult(P1Result.Ok());
            }

            public Task<P1Result> RetryPendingAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
        }

        [Fact]
        public async Task Journey_FullP0001ProgressionFlow()
        {
            // 1. Initial State: Player at Ben Mua, P00-01 AVAILABLE
            var adapter = new JourneyAdapter
            {
                Self = new P1Self { characterId = "PLAYER_01", classId = "CLASS_MINH_KIEM", hp = 100, maxHp = 100, x = 10, y = 10 },
                World = new P1World
                {
                    mapId = "MAP_BEN_MUA",
                    self = new P1Self { characterId = "PLAYER_01", x = 10, y = 10 },
                    entities = new[]
                    {
                        new P1Entity { entityId = "ENT_MAN_BM_NPC_LYAN", kind = "NPC", x = 12, y = 12 },
                        new P1Entity { entityId = "ENT_MAN_BM_NPC_TA_VAN_KHANH", kind = "NPC", x = 30, y = 30 }
                    }
                },
                Quests = new[]
                {
                    new P1Quest { questId = "P00-01", state = "AVAILABLE", stepId = "STEP_BEN_MUA", revision = 1 }
                }
            };

            var dialogue = new NpcDialoguePresenter(adapter);
            var journal = new QuestJournalPresenter(adapter);
            var map = new MapPresenter(adapter);
            var cinema = new CinemaPresenter();

            // Verify Map displays NPCs
            map.Refresh();
            Assert.Equal("Lý An", map.State.Markers[1].Label);
            Assert.Equal("Tạ Vân Khanh", map.State.Markers[2].Label);

            // 2. Interact with Ly An (world entity ID) -> AcceptQuest choice
            await dialogue.InteractAsync("ENT_MAN_BM_NPC_LYAN", CancellationToken.None);
            Assert.Equal("ENT_MAN_BM_NPC_LYAN", adapter.LastInteractedTargetId);
            Assert.Contains(dialogue.State.Value.Choices, c => c.ActionType == DialogueActionType.AcceptQuest);

            // 3. Accept quest -> wire sends canonical template ID NPC_LYAN
            await dialogue.AcceptQuestAsync("P00-01", "ENT_MAN_BM_NPC_LYAN", CancellationToken.None);
            Assert.Equal("P00-01", adapter.LastAcceptedQuestId);
            Assert.Equal("NPC_LYAN", adapter.LastAcceptedNpcId);

            // 4. Server updates quest to ACTIVE (0/3 packages)
            adapter.Quests = new[]
            {
                new P1Quest
                {
                    questId = "P00-01",
                    state = "ACTIVE",
                    stepId = "STEP_BEN_MUA",
                    revision = 2,
                    objectiveCounters = new Dictionary<string, int> { ["OBJ_P00_01_PACKAGES"] = 0 }
                }
            };
            await journal.LoadAsync(CancellationToken.None);
            Assert.Equal("Thu thập gói hàng Bến Mưa (0/3).", journal.State.Value.Active[0].ObjectiveDesc);

            // 5. Player collects packages: 3/3 -> state becomes READY_TO_TURN_IN
            adapter.Quests = new[]
            {
                new P1Quest
                {
                    questId = "P00-01",
                    state = "READY_TO_TURN_IN",
                    stepId = "STEP_BEN_MUA",
                    revision = 3,
                    objectiveCounters = new Dictionary<string, int> { ["OBJ_P00_01_PACKAGES"] = 3 }
                }
            };
            await journal.LoadAsync(CancellationToken.None);
            Assert.Contains("Tạ Vân Khanh", journal.State.Value.Active[0].ObjectiveDesc);

            // 6. Interact with Ta Van Khanh -> TurnInQuest choice
            await dialogue.InteractAsync("ENT_MAN_BM_NPC_TA_VAN_KHANH", CancellationToken.None);
            Assert.Equal("ENT_MAN_BM_NPC_TA_VAN_KHANH", adapter.LastInteractedTargetId);
            Assert.Contains(dialogue.State.Value.Choices, c => c.ActionType == DialogueActionType.TurnInQuest);

            // 7. Turn in quest -> wire sends canonical template ID NPC_TA_VAN_KHANH
            await dialogue.TurnInQuestAsync("P00-01", "ENT_MAN_BM_NPC_TA_VAN_KHANH", CancellationToken.None);
            Assert.Equal("P00-01", adapter.LastTurnedInQuestId);
            Assert.Equal("NPC_TA_VAN_KHANH", adapter.LastTurnedInNpcId);

            // 8. Server completes quest -> moves to Completed in journal
            adapter.Quests = new[]
            {
                new P1Quest { questId = "P00-01", state = "COMPLETED", stepId = "STEP_BEN_MUA", revision = 4 }
            };
            await journal.LoadAsync(CancellationToken.None);
            Assert.Empty(journal.State.Value.Active);
            Assert.Single(journal.State.Value.Completed);
            Assert.Equal("P00-01", journal.State.Value.Completed[0].QuestId);

            // 9. Cinema CIN_001 playback can trigger
            cinema.Play("CIN_001");
            Assert.True(cinema.State.IsPlaying);
            cinema.Skip();
            Assert.True(cinema.State.IsEnded);
        }
    }

}
