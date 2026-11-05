using System.Threading;
using System.Text.Json;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;
using Server.Health.Contracts;
using Server.Health.Gameplay.Alpha;
using Server.Health.Gameplay.Combat;
using Server.Health.Gameplay.Interactions;
using Server.Health.Gameplay.Inventory;
using Server.Health.Gameplay.Pets;
using Server.Health.Gameplay.Progress;
using Server.Health.Gameplay.Quests;
using Server.Health.Gameplay.Teleport;
using Server.Health.World;

namespace Server.Health.Smoke;

public static class ServiceSelfCheck
{
    private const string PlayerClassId = "CLASS_MINH_KIEM";

    public static int Run(IServiceProvider services, ILogger logger)
    {
        var options = services.GetRequiredService<IOptions<P1WorldOptions>>().Value;
        var maps = services.GetRequiredService<MapBoundsCatalog>();
        var combat = services.GetRequiredService<ICombatService>();
        var combatSkills = services.GetRequiredService<ICombatSkillCatalog>();
        var targets = services.GetRequiredService<InMemoryCombatTargetProvider>();
        var quests = services.GetRequiredService<IQuestService>();
        var questCatalog = services.GetRequiredService<IQuestCatalog>();
        var inventory = services.GetRequiredService<IInventoryService>();
        var equipment = services.GetRequiredService<IEquipmentService>();
        var itemCatalog = services.GetRequiredService<ItemCatalog>();
        var teleport = services.GetRequiredService<ITeleportService>();
        var questAccept = services.GetRequiredService<IQuestAcceptService>();
        var npcAnchors = services.GetRequiredService<NpcAnchorCatalog>();
        var questTurnIn = services.GetRequiredService<IQuestTurnInService>();
        var rewardLedger = services.GetRequiredService<RewardLedgerStore>();

        var results = new List<(string Name, bool Passed, string? Detail)>();
        void Check(string name, bool passed, string? detail = null) =>
            results.Add((name, passed, detail));

        PlayerSession NewPlayer(
            string characterId,
            string classId = PlayerClassId,
            int hp = 100,
            int mp = 50) =>
            new(
                $"SES_{Guid.NewGuid():N}",
                characterId,
                classId,
                options.DefaultMapId,
                options.SpawnX,
                options.SpawnY,
                hp,
                options.StartingMaxHp,
                mp,
                options.StartingMaxMp,
                DateTimeOffset.UtcNow);

        // Work order 29 Q4: the catalogue now carries sourced rows for classes the
        // alpha cannot reach. A row is data plus a `sourceRef`, not an executable
        // claim: the engine implements only SELF/DASH/CONE targeting and `/p1/sessions`
        // refuses every class but Minh Kiem, so the castable surface stays exactly the
        // three MK rows asserted further down.
        Check(
            "combat.catalog",
            combatSkills.Count == 7,
            $"count={combatSkills.Count}");

        combatSkills.TryGet("SK-HB-02", out var hb02);
        combatSkills.TryGet("SK-HB-04", out var hb04);
        combatSkills.TryGet("SK-TC-01", out var tc01);
        combatSkills.TryGet("SK-TC-05", out var tc05);
        Check(
            "combat.catalog_foreign_rows_carry_source_numbers",
            hb02 is { ClassId: "CLASS_HUYEN_BUT", CooldownSeconds: 12, ResourceCost: 18, MaxTargets: 1 } &&
            hb04 is { ClassId: "CLASS_HUYEN_BUT", CooldownSeconds: 18, ResourceCost: 28, MaxTargets: 5 } &&
            tc01 is { ClassId: "CLASS_THACH_CHUY", CooldownSeconds: 8, ResourceCost: 14, MaxTargets: 1 } &&
            tc05 is { ClassId: "CLASS_THACH_CHUY", CooldownSeconds: 10, ResourceCost: 12, MaxTargets: 1 },
            "spec:83/89/100/112 CD, MP and target caps");

        Check(
            "combat.catalog_metres_become_wu_at_two_per_unit",
            hb04.RangeWu == 6.0 && tc01.RangeWu == 5.2 && tc05.RangeWu == 8.0 &&
            hb02.RangeWu is null && tc01.AngleDegrees == 60 &&
            hb02.TelegraphSeconds == 0.18 && hb04.TelegraphSeconds == 0.45 &&
            tc01.TelegraphSeconds == 0.25 && tc05.TelegraphSeconds == 0.22,
            "3 m->6 WU, 2,6 m->5,2 WU, 4 m->8 WU; Hanh Cham declares no cast range because source gives none");

        Check(
            "combat.catalog_pvp_is_the_one_sourced_cross_mode_coefficient",
            hb02.Coefficients.Pvp == 0.65 && hb04.Coefficients.Pvp == 0.65 &&
            tc01.Coefficients.Pvp == 0.65 && tc05.Coefficients.Pvp == 0.65 &&
            hb02.Coefficients.Pve == 1.1 && tc01.Coefficients.Pve == 1.7 &&
            tc05.Coefficients.Pve == 1.0 && hb04.Coefficients.Pve == 0.0,
            "GDD:155 fixes PvP at 0,65 server-side; Mua Tinh heals, so it carries no damage coefficient");

        Check(
            "combat.catalog_minh_kiem_surface_unchanged",
            combatSkills.TryGet("SK-MK-01", out _) &&
            combatSkills.TryGet("SK-MK-02", out _) &&
            combatSkills.TryGet("SK-MK-03", out _) &&
            !combatSkills.TryGet("SK-MK-04", out _) &&
            !combatSkills.TryGet("SK-MK-05", out _) &&
            !combatSkills.TryGet("SK-MK-06", out _),
            "MK-04..06 stay out: no stated prepare time, and MK-06 spends Kiem Y the server does not model");

        // Work order 29 Q4 also names "passive", and the only machine-readable source is
        // docs/production/Class_Passive_Production_Data_vi.csv - which the server never
        // read before this loader existed. Loading is not applying: the catalogue is
        // inert, and the damage oracle below (basic 19, MK03 8/10/17) is the proof that
        // no passive changes a hit yet, because those numbers would move if one did.
        var passives = services.GetRequiredService<ClassPassiveCatalog>();
        Check(
            "passive.catalog_forty_rows_across_the_five_classes",
            passives.Count == 40 &&
            passives.SupportedClassIds.All(classId => passives.CountForClass(classId) == 8),
            $"count={passives.Count}");

        Check(
            "passive.catalog_two_branches_of_four_tiers_per_class",
            passives.Rows
                .GroupBy(passive => (passive.ClassId, passive.BranchId))
                .Count() == 10 &&
            passives.Rows
                .GroupBy(passive => (passive.ClassId, passive.BranchId))
                .All(branch => branch.Select(passive => passive.NodeTier).Order().SequenceEqual([1, 2, 3, 4])) &&
            passives.Rows.All(passive => passive.UnlockLevel == passive.NodeTier * 20),
            $"branches={passives.Rows.GroupBy(p => (p.ClassId, p.BranchId)).Count()}");

        passives.TryGet("PAS-MINH_KIEM-KIEM_Y-T4", out var kiemYChainTop);
        Check(
            "passive.catalog_prerequisite_chain_walks_one_branch",
            kiemYChainTop.PrerequisitePassiveId == "PAS-MINH_KIEM-KIEM_Y-T3" &&
            passives.Rows.Where(passive => passive.NodeTier == 1)
                .All(passive => passive.PrerequisitePassiveId is null) &&
            passives.Rows.Where(passive => passive.NodeTier > 1)
                .All(passive => passives.TryGet(passive.PrerequisitePassiveId!, out var parent) &&
                                 parent.ClassId == passive.ClassId &&
                                 parent.BranchId == passive.BranchId &&
                                 parent.NodeTier == passive.NodeTier - 1),
            kiemYChainTop.PrerequisitePassiveId ?? "none");

        // Four of the numbers the Content Bible quotes in prose are here as data, and
        // pinned: this is what let me withdraw "no source" for the Huyen But low-HP
        // ally shield bonus that the skill spec had referenced as "theo bảng nội tại".
        Check(
            "passive.catalog_carries_the_numbers_the_bible_quotes",
            passives.TryGet("PAS-MINH_KIEM-PHAN_CONG-T2", out var thuNhat) &&
            thuNhat.EffectKey == "self_shield_pct" && thuNhat.EffectValue == 4 && thuNhat.EffectUnit == "percent" &&
            passives.TryGet("PAS-HUYEN_BUT-HOI_DONG-T2", out var tinhThuy) &&
            tinhThuy.EffectKey == "low_hp_ally_shield_pct" && tinhThuy.EffectValue == 5 &&
            passives.TryGet("PAS-THACH_CHUY-THE-T1", out var cotThach) &&
            cotThach.EffectKey == "constitution_pct" && cotThach.EffectValue == 3 &&
            passives.TryGet("PAS-HUYEN_BUT-HOI_DONG-T1", out var chiaDong) &&
            chiaDong.EffectKey == "rain_heal_target_bonus" && chiaDong.EffectUnit == "target" &&
            chiaDong.Caps.Count(cap => cap.Kind == PassiveCapKind.HardCap) == 1,
            $"rows={passives.Count}");

        Check(
            "passive.catalog_cap_tokens_classify_and_report_the_rest",
            passives.Rows.SelectMany(passive => passive.Caps).Count() == 37 &&
            passives.Rows.SelectMany(passive => passive.UnparsedCaps).Count() == 10 &&
            passives.Rows.SelectMany(passive => passive.Caps)
                .Count(cap => cap.Kind == PassiveCapKind.ProcRate) == 8 &&
            passives.Rows.SelectMany(passive => passive.Caps)
                .Count(cap => cap.Kind == PassiveCapKind.PvpZero) == 3 &&
            passives.Rows.SelectMany(passive => passive.UnparsedCaps)
                .Any(cap => cap.Equals("không xóa target lock", StringComparison.Ordinal)),
            $"classified={passives.Rows.SelectMany(p => p.Caps).Count()} " +
            $"unparsed={passives.Rows.SelectMany(p => p.UnparsedCaps).Count()}");

        // Rejection fixtures: copy the shipped CSV to a temp docs tree and break one
        // line at a time. The loader must refuse a broken branch chain, an unknown
        // effect unit, and a passive whose approval status is not BASELINE - the last
        // one matters most, because a playtest-balanced number must not load into a
        // server that reports itself as shipped.
        string? PassiveLoadFailure(string linePrefix, string from, string to)
        {
            var root = Path.Combine(Path.GetTempPath(), "p1-passive-" + Guid.NewGuid().ToString("N"));
            try
            {
                var directory = Path.Combine(root, "docs", "production");
                Directory.CreateDirectory(directory);
                var source = File.ReadAllLines(Path.Combine(
                    ClassPassiveCatalogLoader.DiscoverDirectory(AppContext.BaseDirectory),
                    ClassPassiveCatalogLoader.RelativePath));
                var mutated = false;
                for (var line = 0; line < source.Length; line++)
                {
                    if (!source[line].StartsWith(linePrefix, StringComparison.Ordinal) ||
                        !source[line].Contains(from, StringComparison.Ordinal))
                    {
                        continue;
                    }

                    source[line] = source[line].Replace(from, to, StringComparison.Ordinal);
                    mutated = true;
                    break;
                }

                if (!mutated)
                {
                    return "FIXTURE_ANCHOR_MISSING";
                }

                File.WriteAllLines(
                    Path.Combine(directory, Path.GetFileName(ClassPassiveCatalogLoader.RelativePath)),
                    source);

                try
                {
                    ClassPassiveCatalogLoader.Load(root);
                    return "LOADED";
                }
                catch (InvalidOperationException exception)
                {
                    return exception.Message;
                }
            }
            finally
            {
                Directory.Delete(root, recursive: true);
            }
        }

        var brokenChain = PassiveLoadFailure(
            "PAS-MINH_KIEM-KIEM_Y-T4", "PAS-MINH_KIEM-KIEM_Y-T3", "PAS-MINH_KIEM-PHAN_CONG-T1");
        var unknownUnit = PassiveLoadFailure(
            "PAS-HUYEN_BUT-HOI_DONG-T2", "percent", "aura");
        var unapprovedStatus = PassiveLoadFailure(
            "PAS-MINH_KIEM-KIEM_Y-T1", "BASELINE", "PLAYTEST_BALANCED");
        Check(
            "passive.catalog_rejects_a_broken_chain",
            brokenChain is not null && brokenChain.Contains("prerequisite", StringComparison.Ordinal),
            brokenChain ?? "none");
        Check(
            "passive.catalog_rejects_an_unknown_effect_unit",
            unknownUnit is not null && unknownUnit.Contains("effect_unit", StringComparison.Ordinal),
            unknownUnit ?? "none");
        Check(
            "passive.catalog_rejects_a_passive_that_is_not_baseline",
            unapprovedStatus is not null && unapprovedStatus.Contains("status", StringComparison.Ordinal),
            unapprovedStatus ?? "none");

        // Q5 names currency, and docs/production/Currency_Production_Data_vi.csv is its
        // canonical table. The server hard-coded the one id it grants and only guarded
        // arithmetic overflow, so the caps, the character/account split and the fact that
        // nothing is tradeable were all unwritten rules. Loading is not enforcing: turning
        // balance_cap into a refusal needs an error code on the wire, so the catalogue is
        // data plus these structural checks.
        var currencies = services.GetRequiredService<CurrencyCatalog>();
        Check(
            "currency.catalog_sixteen_rows",
            currencies.Count == 16 &&
            currencies.Rows.Select(currency => currency.CurrencyType).Distinct().Count() == 7,
            $"count={currencies.Count}");

        currencies.TryGet("COIN", out var coin);
        Check(
            "currency.catalog_coin_row_matches_the_source",
            coin is { CurrencyType: "SOFT", Tradeable: false, StorageScope: "character", BalanceCap: 2_000_000_000 } &&
            coin.DailyCap.Kind == DailyCapKind.None &&
            coin.WeeklyReset == "none" &&
            coin.Notes.Contains("client never submits balances", StringComparison.Ordinal),
            $"coin={coin?.BalanceCap} daily={coin?.DailyCap.Kind}");

        Check(
            "currency.catalog_no_shipped_currency_is_tradeable",
            currencies.CountWhere(currency => currency.Tradeable) == 0,
            $"tradeable={currencies.CountWhere(c => c.Tradeable)}");

        // The eight account-scoped currencies (all five regional reputations, both merit
        // currencies, the Long Mon medal) cannot be held per character, and the server has
        // no account concept at all - this is the count, recorded rather than invented.
        Check(
            "currency.catalog_scope_split_names_the_missing_account_concept",
            currencies.CountWhere(currency => currency.StorageScope == "character") == 8 &&
            currencies.CountWhere(currency => currency.StorageScope == "account") == 8 &&
            currencies.Rows
                .Where(currency => currency.CurrencyType == "REGIONAL_REPUTATION")
                .All(currency => currency.StorageScope == "account" && currency.BalanceCap == 10_000 &&
                                 currency.DailyCap.Kind == DailyCapKind.Amount && currency.DailyCap.Amount == 200),
            $"character={currencies.CountWhere(c => c.StorageScope == "character")}");

        Check(
            "currency.catalog_keeps_an_unscheduled_cap_visible_instead_of_rounding_it",
            currencies.CountWhere(currency => currency.DailyCap.Kind == DailyCapKind.Amount) == 8 &&
            currencies.CountWhere(currency => currency.DailyCap.Kind == DailyCapKind.None) == 7 &&
            currencies.CountWhere(currency => currency.DailyCap.Kind == DailyCapKind.Unscheduled) == 1 &&
            currencies.Rows
                .Single(currency => currency.DailyCap.Kind == DailyCapKind.Unscheduled)
                .DailyCap.Raw == "per scheduled match",
            $"amount={currencies.CountWhere(c => c.DailyCap.Kind == DailyCapKind.Amount)} " +
            $"none={currencies.CountWhere(c => c.DailyCap.Kind == DailyCapKind.None)}");

        // Every currency the shipped quest rewards pay out has to exist in the table, so a
        // quest cannot name an id that no cap, scope or display name covers.
        var shippedQuests = services.GetRequiredService<IQuestCatalog>();
        var rewardCurrencyIds = shippedQuests.QuestIds
            .Select(questId => shippedQuests.TryGet(questId, out var questDefinition) ? questDefinition : null)
            .Where(questDefinition => questDefinition is not null)
            .SelectMany(questDefinition => questDefinition!.Rewards.Currency)
            .Select(reward => reward.CurrencyId)
            .Distinct(StringComparer.Ordinal)
            .ToList();
        Check(
            "currency.every_reward_currency_id_exists_in_the_catalog",
            rewardCurrencyIds.Count > 0 &&
            rewardCurrencyIds.All(currencyId => currencies.TryGet(currencyId, out _)) &&
            currencies.TryGet(LootCurrencyIds.Coin, out _),
            $"rewards={string.Join("|", rewardCurrencyIds)}");

        var balanceBearingRequests = typeof(InventoryItem).Assembly
            .GetTypes()
            .Where(type => type.Name.EndsWith("Request", StringComparison.Ordinal))
            .SelectMany(type => type.GetProperties(System.Reflection.BindingFlags.Public |
                                                   System.Reflection.BindingFlags.Instance))
            .Where(property => property.Name.Contains("Balance", StringComparison.OrdinalIgnoreCase))
            .Select(property => property.DeclaringType?.Name + "." + property.Name)
            .ToArray();
        Check(
            "currency.no_request_dto_accepts_a_client_submitted_balance",
            balanceBearingRequests.Length == 0,
            string.Join("|", balanceBearingRequests));

        static string Cut(string? message) =>
            message is null ? "none" : message[..Math.Min(90, message.Length)];

        string? CurrencyLoadFailure(string from, string to)
        {
            var root = Path.Combine(Path.GetTempPath(), "p1-currency-" + Guid.NewGuid().ToString("N"));
            try
            {
                var directory = Path.Combine(root, "docs", "production");
                Directory.CreateDirectory(directory);
                var source = File.ReadAllLines(Path.Combine(
                    CurrencyCatalogLoader.DiscoverDirectory(AppContext.BaseDirectory),
                    CurrencyCatalogLoader.RelativePath));
                File.WriteAllLines(
                    Path.Combine(directory, Path.GetFileName(CurrencyCatalogLoader.RelativePath)),
                    source.Select(line => line.Replace(from, to, StringComparison.Ordinal)).ToArray());

                try
                {
                    CurrencyCatalogLoader.Load(root);
                    return "LOADED";
                }
                catch (InvalidOperationException exception)
                {
                    return exception.Message;
                }
            }
            finally
            {
                Directory.Delete(root, recursive: true);
            }
        }

        var badCurrencyType = CurrencyLoadFailure(",SOFT,", ",GOLD,");
        var badBalanceCap = CurrencyLoadFailure("2000000000", "none");
        Check(
            "currency.catalog_rejects_an_unknown_type_and_a_non_numeric_cap",
            badCurrencyType is not null && badCurrencyType.Contains("currency_type", StringComparison.Ordinal) &&
            badBalanceCap is not null && badBalanceCap.Contains("balance_cap", StringComparison.Ordinal),
            $"type='{Cut(badCurrencyType)}' cap='{Cut(badBalanceCap)}'");

        // Q5's gather/craft half lives in docs/production/Life_Sim_Content_Data_vi.csv:
        // five crop plots and six fishing waters with their seed or bait, yield range,
        // grow time, daily cap, season, tool, quality weights, failure rule and the
        // minigame the client must present. Nothing here runs it - the server has no
        // gather loop for it - but the references stop being unverifiable prose.
        var lifeSim = services.GetRequiredService<LifeSimCatalog>();
        Check(
            "lifesim.catalog_eleven_rows",
            lifeSim.Count == 11 && lifeSim.CountOfType("CROP") == 5 && lifeSim.CountOfType("FISH") == 6,
            $"count={lifeSim.Count}");

        var mapBoundsCatalog = services.GetRequiredService<MapBoundsCatalog>();
        var referencedItemIds = lifeSim.Rows
            .SelectMany(entry => new[] { entry.InputItemId, entry.OutputItemId, entry.ToolId }
                .Concat(entry.BaitItemId is null ? [] : [entry.BaitItemId]))
            .Distinct(StringComparer.Ordinal)
            .ToList();
        Check(
            "lifesim.catalog_references_resolve_in_shipped_content",
            referencedItemIds.Count == 14 &&
            referencedItemIds.All(itemId => itemCatalog.TryGet(itemId, out _)) &&
            lifeSim.Rows.All(entry => mapBoundsCatalog.TryResolve(entry.MapId, out _)),
            $"items={referencedItemIds.Count}");

        Check(
            "lifesim.catalog_quality_weights_are_a_full_basis",
            lifeSim.Rows.All(entry => entry.QualityWeights.Sum(weight => weight.Weight) == 10000) &&
            lifeSim.Rows.All(entry => entry.QualityWeights.Count >= 1) &&
            lifeSim.Rows.SelectMany(entry => entry.QualityWeights)
                .Select(weight => weight.Rarity)
                .Distinct(StringComparer.Ordinal)
                .Count() == 3,
            $"weights ok for {lifeSim.Count} rows");

        // The Q3 packet argues the single-lane assumption is provisional. This row is the
        // proof that an approved production table already places content off the lane.
        lifeSim.TryGet("LIFE_FISH_CA_RE", out var offLane);
        Check(
            "lifesim.catalog_keeps_the_one_off_lane_row_off_lane",
            offLane is { XWu: 158, YWu: -3 } &&
            lifeSim.Rows.Count(entry => entry.YWu != 0) == 1,
            $"off-lane y!=0 count={lifeSim.Rows.Count(entry => entry.YWu != 0)}");

        Check(
            "lifesim.catalog_timings_and_daily_caps_follow_their_own_columns",
            lifeSim.Rows.Where(entry => entry.ContentType == "CROP")
                .OrderBy(entry => entry.LevelRequired)
                .Select(entry => entry.ProcessSeconds)
                .SequenceEqual([3600, 7200, 10800, 14400, 21600]) &&
            lifeSim.Rows.Where(entry => entry.ContentType == "CROP")
                .All(entry => entry.InteractionSeconds == 2 && entry.DailyCap == 12) &&
            lifeSim.Rows.Where(entry => entry.ContentType == "FISH")
                .All(entry => entry.InteractionSeconds == 4 && entry.DailyCap == 20 &&
                               entry.ProcessSeconds is >= 30 and <= 90),
            $"crop grow times are monotone in level; fish always 4s and 20/day");

        string? LifeSimLoadFailure(string from, string to)
        {
            var root = Path.Combine(Path.GetTempPath(), "p1-lifesim-" + Guid.NewGuid().ToString("N"));
            try
            {
                var directory = Path.Combine(root, "docs", "production");
                Directory.CreateDirectory(directory);
                var source = File.ReadAllLines(Path.Combine(
                    LifeSimCatalogLoader.DiscoverDirectory(AppContext.BaseDirectory),
                    LifeSimCatalogLoader.RelativePath));
                File.WriteAllLines(
                    Path.Combine(directory, Path.GetFileName(LifeSimCatalogLoader.RelativePath)),
                    source.Select(line => line.Replace(from, to, StringComparison.Ordinal)).ToArray());

                try
                {
                    LifeSimCatalogLoader.Load(root);
                    return "LOADED";
                }
                catch (InvalidOperationException exception)
                {
                    return exception.Message;
                }
            }
            finally
            {
                Directory.Delete(root, recursive: true);
            }
        }

        var badWeightTotal = LifeSimLoadFailure("COMMON:8000", "COMMON:7000");
        var badType = LifeSimLoadFailure(",CROP,", ",MINE,");
        Check(
            "lifesim.catalog_rejects_a_partial_weight_set_and_an_unknown_type",
            badWeightTotal is not null && badWeightTotal.Contains("quality_weights", StringComparison.Ordinal) &&
            badType is not null && badType.Contains("content_type", StringComparison.Ordinal),
            $"weights='{Cut(badWeightTotal)}' type='{Cut(badType)}'");

        // Q7 names weekly arena, rank and reward, and the rotation table already exists in
        // production form. Loading it surfaces what a scheduler would still need - and the
        // first finding is that five of the six bosses have no resolved stats at all.
        var weeklyRotation = services.GetRequiredService<WeeklyBossRotationCatalog>();
        Check(
            "weekly.rotation_six_slots_one_cycle_each",
            weeklyRotation.Count == 6 &&
            weeklyRotation.Rows.Select(slot => slot.CycleIndex).Order().SequenceEqual([1, 2, 3, 4, 5, 6]) &&
            weeklyRotation.Rows.Select(slot => slot.RotationRule).Distinct().Count() == 1 &&
            weeklyRotation.Rows.First().RotationRule.Contains("season_offset", StringComparison.Ordinal),
            $"slots={weeklyRotation.Count}");

        var recordEntityIds = services.GetRequiredService<WorldRecordCatalog>().All
            .SelectMany(record => record.EntityIds)
            .ToHashSet(StringComparer.Ordinal);
        // Every rotation boss must at least exist as a world record, or the scheduler
        // would spawn a name with nothing behind it. Note the deliberate limit of this
        // check: only BOSS_MANG_COT has resolved stats in combat_mob_stats_v1.json today,
        // so the other five would meet the audience's "cannot resolve stats" rule - that
        // gap is reported as a question, not asserted from a gated bundle here.
        Check(
            "weekly.rotation_bosses_exist_as_world_records",
            weeklyRotation.Rows.All(slot => recordEntityIds.Contains(slot.SourceBossId)),
            $"records={weeklyRotation.Rows.Count(slot => recordEntityIds.Contains(slot.SourceBossId))}/" +
            $"{weeklyRotation.Count}");

        Check(
            "weekly.rotation_multipliers_and_caps_are_uniform",
            weeklyRotation.Rows.All(slot => slot.HpMultiplier == 1.35 && slot.DamageMultiplier == 1.1) &&
            weeklyRotation.Rows.Select(slot => slot.WeeklyRewardCap).Distinct().Count() == 1 &&
            weeklyRotation.Rows.All(slot => slot.WeeklyRewardCap == "1/character/week") &&
            weeklyRotation.Rows.All(slot => slot.SpawnXWu == 180 && slot.SpawnYWu == 0) &&
            weeklyRotation.Rows.All(slot => mapBoundsCatalog.TryResolve(slot.SpawnMapId, out _)),
            $"multipliers uniform across {weeklyRotation.Count} slots");

        string? WeeklyLoadFailure(string from, string to)
        {
            var root = Path.Combine(Path.GetTempPath(), "p1-weekly-" + Guid.NewGuid().ToString("N"));
            try
            {
                var directory = Path.Combine(root, "docs", "production");
                Directory.CreateDirectory(directory);
                var source = File.ReadAllLines(Path.Combine(
                    WeeklyBossRotationCatalogLoader.DiscoverDirectory(AppContext.BaseDirectory),
                    WeeklyBossRotationCatalogLoader.RelativePath));
                File.WriteAllLines(
                    Path.Combine(directory, Path.GetFileName(WeeklyBossRotationCatalogLoader.RelativePath)),
                    source.Select(line => line.Replace(from, to, StringComparison.Ordinal)).ToArray());

                try
                {
                    WeeklyBossRotationCatalogLoader.Load(root);
                    return "LOADED";
                }
                catch (InvalidOperationException exception)
                {
                    return exception.Message;
                }
            }
            finally
            {
                Directory.Delete(root, recursive: true);
            }
        }

        var duplicateCycle = WeeklyLoadFailure("TOWER_WK_02,2,", "TOWER_WK_02,1,");
        var badSlotId = WeeklyLoadFailure("TOWER_WK_03,", "tower_wk_03,");
        Check(
            "weekly.rotation_rejects_a_duplicate_cycle_and_a_lowercase_slot",
            duplicateCycle is not null && duplicateCycle.Contains("cycle_index", StringComparison.Ordinal) &&
            badSlotId is not null && badSlotId.Contains("rotation_slot_id", StringComparison.Ordinal),
            $"cycle='{Cut(duplicateCycle)}' slot='{Cut(badSlotId)}'");

        var combatActor = NewPlayer("CHR_SELFCHECK_COMBAT");
        var badSkill = combat.Resolve(
            combatActor, new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-99" });
        Check(
            "combat.invalid_skill_input",
            badSkill.Failure?.Code == P1ErrorCodes.InvalidPayload,
            badSkill.Failure?.Code);

        var wrongClass = NewPlayer(
            "CHR_SELFCHECK_CLASS", classId: "CLASS_LUYEN_TAM");
        var wrongClassCast = combat.Resolve(
            wrongClass, new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-01" });
        Check(
            "combat.class_gate",
            wrongClassCast.Failure?.Code == CombatErrorCodes.SkillNotAvailable,
            wrongClassCast.Failure?.Code);

        // A loaded row for a class no session can hold must still refuse to cast, so
        // "present in the catalogue" never reads as "available in the alpha".
        // The wire vocabulary is deliberately narrower than the content vocabulary,
        // and loading a row must not move it: a client still cannot name a skill
        // outside the alpha subset at all.
        Check(
            "contracts.skill_id_wire_vocabulary_still_alpha_only",
            P1Validation.IsSkillId("SK-MK-01") &&
            P1Validation.IsSkillId("SK-MK-02") &&
            P1Validation.IsSkillId("SK-MK-03") &&
            !P1Validation.IsSkillId("SK-TC-01") &&
            !P1Validation.IsSkillId("SK-HB-02") &&
            !P1Validation.IsSkillId("SK-MK-04") &&
            !P1Validation.IsSkillId("SK-MK-07") &&
            !P1Validation.IsSkillId("sk-MK-01") &&
            !P1Validation.IsSkillId(null),
            "content rows load for four more classes; the request vocabulary is untouched");

        // A loaded row for a class no session can hold is refused before the catalogue is
        // even consulted: v1 validates the id against the alpha wire vocabulary first, so
        // growing the catalogue cannot widen what a client may name. The class gate behind
        // it is the second layer, already proven by combat.class_gate below.
        var foreignSkillActor = NewPlayer("CHR_SELFCHECK_FOREIGN_SKILL");
        var foreignSkillCast = combat.Resolve(
            foreignSkillActor,
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-TC-01" });
        Check(
            "combat.catalog_foreign_class_cast_refused",
            foreignSkillCast.Failure?.Code == P1ErrorCodes.InvalidPayload &&
            foreignSkillCast.Failure?.FieldErrors.Contains("skillId") is true,
            $"{foreignSkillCast.Failure?.Code}/{foreignSkillCast.Failure?.FieldErrors.Count}");

        var staleActor = NewPlayer("CHR_SELFCHECK_STALE");
        staleActor.LastInputSequence = 1;
        var staleCast = combat.Resolve(
            staleActor, new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-01" });
        Check(
            "combat.stale_sequence",
            staleCast.Failure?.Code == P1ErrorCodes.StaleSequence,
            staleCast.Failure?.Code);

        var selfCast = combat.Resolve(
            combatActor, new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-01" });
        Check(
            "combat.self_cast",
            selfCast.Accepted &&
            selfCast.Event?.Payload.TargetId == combatActor.CharacterId &&
            combatActor.Mp == options.StartingMp - 12 &&
            combatActor.LastInputSequence == 1 &&
            combatActor.Revision == 2,
            $"mp={combatActor.Mp} revision={combatActor.Revision}");

        var cooldownCast = combat.Resolve(
            combatActor, new CombatCommand { AimX = 0, AimY = 0, InputSequence = 2, SkillId = "SK-MK-01" });
        Check(
            "combat.cooldown",
            cooldownCast.Failure?.Code == CombatErrorCodes.CooldownActive,
            cooldownCast.Failure?.Code);

        var missingTarget = combat.Resolve(
            NewPlayer("CHR_SELFCHECK_TARGET"),
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-03", TargetId = "TGT_MISSING" });
        Check(
            "combat.target_not_found",
            missingTarget.Failure?.Code == CombatErrorCodes.TargetNotFound,
            missingTarget.Failure?.Code);

        targets.Upsert(new CombatTarget(
            "TGT_SELFCHECK_FAR",
            options.DefaultMapId,
            "OVERWORLD",
            options.SpawnX + 50,
            options.SpawnY,
            Alive: true));
        var farCast = combat.Resolve(
            NewPlayer("CHR_SELFCHECK_RANGE"),
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-02", TargetId = "TGT_SELFCHECK_FAR" });
        Check(
            "combat.out_of_range",
            farCast.Failure?.Code == CombatErrorCodes.OutOfRange,
            farCast.Failure?.Code);

        var worldTargets = services.GetRequiredService<ICombatTargetProvider>();
        var resolvedMob = worldTargets.TryResolve("ENT_MAN_BM_SPAWN_BM_01", out var mobTarget);
        Check(
            "combat.world_target",
            resolvedMob &&
            mobTarget is { MapId: "MAP_BEN_MUA", FloorId: "OVERWORLD", X: 84, IsAlive: true },
            mobTarget?.EntityId);
        Check(
            "combat.world_target_npc_rejected",
            !worldTargets.TryResolve("ENT_MAN_BM_NPC_LYAN", out _));

        var worldRangeCast = combat.Resolve(
            NewPlayer("CHR_SELFCHECK_WORLD_RANGE"),
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-02", TargetId = "ENT_MAN_BM_SPAWN_BM_01" });
        Check(
            "combat.world_target_out_of_range",
            worldRangeCast.Failure?.Code == CombatErrorCodes.OutOfRange,
            worldRangeCast.Failure?.Code);

        var worldConeActor = NewPlayer("CHR_SELFCHECK_WORLD_CONE");
        var worldConeCast = combat.Resolve(
            worldConeActor,
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-03", TargetId = "ENT_MAN_BM_SPAWN_BM_01" });
        Check(
            "combat.world_target_resolves",
            worldConeCast.Accepted && worldConeActor.Mp == 28,
            worldConeCast.Failure?.Code);

        targets.Upsert(new CombatTarget(
            "TGT_SELFCHECK_OTHER_FLOOR",
            options.DefaultMapId,
            "UNDERGROUND",
            options.SpawnX + 1,
            options.SpawnY,
            Alive: true));
        var floorCast = combat.Resolve(
            NewPlayer("CHR_SELFCHECK_FLOOR"),
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-03", TargetId = "TGT_SELFCHECK_OTHER_FLOOR" });
        Check(
            "combat.floor_mismatch",
            floorCast.Failure?.Code == CombatErrorCodes.TargetNotFound,
            floorCast.Failure?.Code);

        var idemActor = NewPlayer("CHR_SELFCHECK_COMBAT_IDEM");
        var idemCommand = new CombatCommand
        {
            AimX = 0,
            AimY = 0,
            InputSequence = 1,
            SkillId = "SK-MK-01"
        };
        var idemFirst = combat.Resolve(idemActor, idemCommand, new string('a', 32));
        var idemReplay = combat.Resolve(idemActor, idemCommand, new string('a', 32));
        Check(
            "combat.idempotency_replay",
            idemFirst.Accepted &&
            idemReplay.Accepted &&
            ReferenceEquals(idemFirst.Event, idemReplay.Event) &&
            idemActor.Mp == 38 &&
            idemActor.Revision == 2,
            $"mp={idemActor.Mp} revision={idemActor.Revision}");

        var idemConflict = combat.Resolve(
            idemActor,
            new CombatCommand
            {
                AimX = 0,
                AimY = 0,
                InputSequence = 2,
                SkillId = "SK-MK-01"
            },
            new string('a', 32));
        Check(
            "combat.idempotency_conflict",
            idemConflict.Failure?.Code == CombatErrorCodes.IdempotencyConflict,
            idemConflict.Failure?.Code);

        

        var noMpCast = combat.Resolve(
            NewPlayer("CHR_SELFCHECK_MP", mp: 0),
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-01" });
        Check(
            "combat.insufficient_resource",
            noMpCast.Failure?.Code == CombatErrorCodes.InsufficientResource,
            noMpCast.Failure?.Code);

        // ─── QOD-16: combat subset domain + entity read-model projection ───

        var configuration = services.GetRequiredService<IConfiguration>();
        var hostEnvironment = services.GetRequiredService<IHostEnvironment>();
        bool Near(double actual, double expected) => Math.Abs(actual - expected) < 1e-9;
        DashMovementService NewDashes(IWorldGeometryService service) =>
            new(service, options, maps);

        var combatDamage = services.GetRequiredService<CombatDamageFeature>();
        Check(
            "combat.damage_gate_off_by_default",
            !combatDamage.Enabled,
            $"enabled={combatDamage.Enabled}");
        var gateBlockedLoad = false;
        try
        {
            _ = combatDamage.MobStats;
        }
        catch (InvalidOperationException)
        {
            gateBlockedLoad = true;
        }

        Check("combat.damage_gate_blocks_load", gateBlockedLoad);

        var enabledCombat = new CombatDamageFeature(
            new P1CombatDamageOptions { Enabled = true },
            configuration,
            hostEnvironment);

        combatSkills.TryGet("SK-MK-01", out var mk01);
        combatSkills.TryGet("SK-MK-02", out var mk02);
        combatSkills.TryGet("SK-MK-03", out var mk03);
        Check(
            "combat.skill_coefficients",
            mk01 is
            {
                TargetingType: CombatTargetingTypes.Self,
                RangeWu: 4.4,
                AngleDegrees: 120,
                MaxTargets: 1,
                TelegraphSeconds: 0.4,
                VfxKey: "VFX/Skill/SK-MK-01"
            } &&
            mk01.Coefficients is { Pve: 1.8, Boss: 1.8, Pvp: 0.65 } &&
            mk02 is
            {
                TargetingType: CombatTargetingTypes.Dash,
                RangeWu: 11,
                AngleDegrees: null,
                MaxTargets: 1,
                TelegraphSeconds: 0.15,
                VfxKey: "VFX/Skill/SK-MK-02"
            } &&
            mk02.Coefficients is { Pve: 1.5, Boss: 1.5, Pvp: 0.65 } &&
            mk03 is
            {
                TargetingType: CombatTargetingTypes.Cone,
                RangeWu: null,
                AngleDegrees: 100,
                MaxTargets: 5,
                TelegraphSeconds: 0.1,
                VfxKey: "VFX/Skill/SK-MK-03"
            } &&
            mk03.Coefficients is { Pve: 1.9, Boss: 1.9, Pvp: 0.65 },
            $"{mk01?.SkillId}/{mk02?.SkillId}/{mk03?.SkillId}");

        var rangeMigration = enabledCombat.RangeMigration;
        Check(
            "combat.skill_range_migration",
            Near(rangeMigration.RangeWuBySkillId["SK-MK-01"], 4.4) &&
            Near(rangeMigration.RangeWuBySkillId["SK-MK-02"], 11.0) &&
            Near(rangeMigration.RangeWuBySkillId["SK-MK-03"], 4.4),
            string.Join(
                ",",
                rangeMigration.RangeWuBySkillId
                    .OrderBy(pair => pair.Key, StringComparer.Ordinal)
                    .Select(pair => $"{pair.Key}={pair.Value}")));

        var mobStats = enabledCombat.MobStats;
        Check(
            "combat.mob_stats_bundle",
            mobStats is
            {
                SchemaVersion: 1,
                BundleId: "COMBAT_MOB_STATS_V1",
                Activation: CombatMobStatLoader.DesignOnlyActivation,
                ReferenceLevel: 5,
                LevelPolicy: "REFERENCE_L5"
            } &&
            mobStats.Archetypes.Count == 3 &&
            mobStats.Bosses.Count == 1,
            $"bundle={mobStats.BundleId} archetypes={mobStats.Archetypes.Count}");

        Check(
            "combat.mob_stats_elite_multipliers",
            mobStats.Elite is { Hp: 6.0, Attack: 1.6, Defense: 1.8 },
            $"{mobStats.Elite.Hp}/{mobStats.Elite.Attack}/{mobStats.Elite.Defense}");

        var carpling = mobStats.Archetypes.First(stats => stats.MobId == "MOB_CARPLING");
        Check(
            "combat.mob_stats_carpling_l5",
            carpling.ReferenceLevel5 is { Hp: 192, Attack: 15, Defense: 4.2 },
            $"{carpling.ReferenceLevel5.Hp}/{carpling.ReferenceLevel5.Attack}/{carpling.ReferenceLevel5.Defense}");

        var shoreStalker = mobStats.Archetypes.First(stats => stats.MobId == "MOB_SHORE_STALKER");
        Check(
            "combat.mob_stats_shore_stalker_l5",
            shoreStalker.ReferenceLevel5 is { Hp: 216, Attack: 23, Defense: 4.8 },
            $"{shoreStalker.ReferenceLevel5.Hp}/{shoreStalker.ReferenceLevel5.Attack}/{shoreStalker.ReferenceLevel5.Defense}");

        var mangCot = mobStats.Bosses.Single();
        Check(
            "combat.mob_stats_boss_blocked",
            mangCot is
            {
                BossId: "BOSS_MANG_COT",
                HpMultiplier: 35,
                AttackMultiplier: 2.0,
                PartyHpMultiplierPerAdditionalPlayer: 0.65,
                ReferenceLevel: 10,
                Activation: "BOSSDATA_BLOCKED"
            } &&
            mangCot.ReferenceStats is { Hp: 12600, Attack: 60, Defense: 10 } &&
            mangCot.Attacks.Count == 3 &&
            mangCot.BlockedReason.Length > 0,
            $"activation={mangCot.Activation} attacks={mangCot.Attacks.Count}");

        var carplingL6 = CombatMobStatLoader.EffectiveAt(mobStats, "MOB_CARPLING", 6);
        Check(
            "combat.mob_stats_level_formula",
            carplingL6.Hp == 211 &&
            Near(carplingL6.Attack, 16.5) &&
            Near(carplingL6.Defense, 4.76),
            $"{carplingL6.Hp}/{carplingL6.Attack}/{carplingL6.Defense}");

        // DEC-022 guard precision: versioned bundle + pure timeline/oracle.
        var guardMitigation = DamageFormula.MitigationMultiplier(10);
        var guardPrecision = enabledCombat.GuardPrecision;
        combatSkills.TryGet("SK-MK-01", out var guardSkill);
        Check(
            "guard.precision_bundle",
            guardPrecision is
            {
                SchemaVersion: 1,
                BundleId: "DESIGN_P1_GUARD_PRECISION_V1",
                DecisionId: "DEC-022",
                Activation: "DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION",
                TickHz: 20
            } &&
            guardPrecision.Guard is
            {
                DurationTicks: 8,
                AngleDegrees: 120,
                RangeWu: 4.4,
                DamageReduction: 0.7,
                MaxConfirmations: 1,
                SwordIntentGain: 2,
                SwordIntentCap: 5
            },
            $"{guardPrecision.DecisionId} tickHz={guardPrecision.TickHz}");

        var gateBlockedGuard = false;
        try
        {
            _ = combatDamage.GuardPrecision;
        }
        catch (InvalidOperationException)
        {
            gateBlockedGuard = true;
        }

        Check("guard.gate_blocks_load", gateBlockedGuard);

        Check(
            "guard.window_boundary",
            GuardTimeline.IsGuardActive(100, 8, 100) &&
            GuardTimeline.IsGuardActive(100, 8, 107) &&
            !GuardTimeline.IsGuardActive(100, 8, 108) &&
            GuardTimeline.GuardEndExclusiveTick(100, 8) ==
            guardPrecision.Oracle.GuardEndExclusiveTick);

        Check(
            "guard.whiff_window",
            GuardTimeline.WhiffStartTick(100, 8) == 108 &&
            GuardTimeline.WhiffEndExclusiveTick(100, 8, 20) == 128 &&
            !GuardTimeline.IsWhiffActive(100, 8, 20, 107) &&
            GuardTimeline.IsWhiffActive(100, 8, 20, 108) &&
            GuardTimeline.IsWhiffActive(100, 8, 20, 127) &&
            !GuardTimeline.IsWhiffActive(100, 8, 20, 128) &&
            guardPrecision.Oracle.WhiffEndExclusiveTick == 128);

        var edgeX = 4.4 * Math.Cos(Math.PI / 3);
        var edgeY = 4.4 * Math.Sin(Math.PI / 3);
        var wideX = 4.4 * Math.Cos(61 * Math.PI / 180);
        var wideY = 4.4 * Math.Sin(61 * Math.PI / 180);
        Check(
            "guard.cone_boundary",
            GuardTimeline.InFront(0, 0, 1, 0, edgeX, edgeY, 4.4, 120) &&
            GuardTimeline.InFront(0, 0, 1, 0, 4.4, 0, 4.4, 120) &&
            !GuardTimeline.InFront(0, 0, 1, 0, 4.41, 0, 4.4, 120) &&
            !GuardTimeline.InFront(0, 0, 1, 0, wideX, wideY, 4.4, 120) &&
            !GuardTimeline.InFront(0, 0, 1, 0, -1, 0, 4.4, 120) &&
            GuardTimeline.InFront(5, 5, 1, 0, 5, 5, 4.4, 120) &&
            !GuardTimeline.InFront(0, 0, 0, 0, 1, 0, 4.4, 120));

        Check(
            "guard.dr_bucket_cap",
            Near(GuardTimeline.CombineReduction(0.7), 0.7) &&
            Near(GuardTimeline.CombineReduction(0.7, 0.2), 0.8) &&
            Near(GuardTimeline.CombineReduction(0.2, 0.2), 0.4) &&
            Near(guardPrecision.Oracle.GuardAndOtherReductionAtCap, 0.8));

        Check(
            "guard.oracle_reduction",
            DamageFormula.FinalDamage(
                30, guardMitigation, 1, 1,
                DamageFormula.DamageReductionMultiplier(0.7)) == 8 &&
            DamageFormula.FinalDamage(
                30, guardMitigation, 1, 1,
                DamageFormula.DamageReductionMultiplier(0.2)) == 21 &&
            DamageFormula.FinalDamage(30, guardMitigation, 1, 1, 1) == 27 &&
            DamageFormula.FinalDamage(
                30, guardMitigation, 1, 1,
                DamageFormula.DamageReductionMultiplier(0.8)) == 5 &&
            guardPrecision.Oracle is
            {
                GuardFinalDamage: 8,
                WhiffFinalDamage: 21,
                OutsideFinalDamage: 27,
                CappedFinalDamage: 5
            });

        var guardSkillPve = guardSkill?.Coefficients.Pve ?? 0;
        var counterRaw = guardPrecision.Oracle.CounterAttack * guardSkillPve;
        Check(
            "guard.counter_oracle",
            guardSkill is not null &&
            Near(guardPrecision.Oracle.CounterPveCoefficient, guardSkill.Coefficients.Pve) &&
            DamageFormula.FinalDamage(counterRaw, guardMitigation, 1, 1, 1) == 32 &&
            DamageFormula.FinalDamage(
                counterRaw, guardMitigation, 1, DamageFormula.CritMultiplier, 1) == 49 &&
            guardPrecision.Oracle is
            {
                CounterNonCritFinalDamage: 32,
                CounterCritFinalDamage: 49
            },
            $"{counterRaw}");

        Check(
            "guard.skill_timing_matches",
            guardSkill is not null &&
            Near(
                guardSkill.TelegraphSeconds,
                guardPrecision.Guard.DurationTicks / (double)guardPrecision.TickHz) &&
            Near(guardSkill.RangeWu!.Value, guardPrecision.Guard.RangeWu) &&
            Near(guardSkill.AngleDegrees!.Value, guardPrecision.Guard.AngleDegrees));

        var impactA = new ImpactOrderKey(
            10, 5, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 0, "ENT_A");
        var impactB = new ImpactOrderKey(
            10, 5, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 0, "ENT_B");
        var impactC = new ImpactOrderKey(
            10, 5, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 1, "ENT_A");
        var impactD = new ImpactOrderKey(
            10, 6, "00000000000000000000000000000000", 0, "ENT_A");
        var impactE = new ImpactOrderKey(
            11, 3, "00000000000000000000000000000000", 0, "ENT_A");
        Check(
            "guard.ordering_deterministic",
            GuardTimeline.CompareImpacts(impactA, impactB) < 0 &&
            GuardTimeline.CompareImpacts(impactB, impactC) < 0 &&
            GuardTimeline.CompareImpacts(impactC, impactD) < 0 &&
            GuardTimeline.CompareImpacts(impactD, impactE) < 0 &&
            GuardTimeline.CompareImpacts(impactE, impactA) > 0);

        Check(
            "guard.confirmation_keys",
            guardPrecision.Ordering.ConfirmationUniqueKey.SequenceEqual(
                new[] { "guardCastId" }, StringComparer.Ordinal) &&
            guardPrecision.Ordering.CounterUniqueKey.SequenceEqual(
                new[] { "guardCastId", "confirmationEventId" }, StringComparer.Ordinal) &&
            guardPrecision.Counter is { DelayTicks: 1, MaxTargets: 1 } &&
            guardPrecision.Whiff is { DurationTicks: 20, DamageReduction: 0.2 });

        // QOD-16 ph2 reliable event read: monotonic cursor, bounded buffer,
        // explicit resync and replay-safe appends.
        var eventStore = new CombatEventStore(new CombatEventStreamOptions
        {
            CapacityPerSession = 4,
            MaxPageSize = 2
        });
        var eventSession = "e2e00000000000000000000000000000";
        CombatEventV2 MakeOutcomeEvent(string eventId, string castId, long tick) =>
            new(
                eventId,
                CombatEventTypesV2.Impact,
                castId,
                "CHR_SELFCHECK_EVENTS",
                "ENT_MAN_BM_SPAWN_BM_01",
                1,
                0,
                "MAP_BEN_MUA#1",
                "OVERWORLD",
                1,
                2,
                tick,
                new DateTimeOffset(2026, 10, 30, 2, 0, 0, TimeSpan.Zero),
                new CombatEventResultV2(true, false, false, 27, 0, 27));

        var appendedEvents = new List<CombatEventV2>();
        for (var index = 1; index <= 3; index++)
        {
            appendedEvents.Add(eventStore.Append(
                eventSession,
                MakeOutcomeEvent(index.ToString("x32"), new string('c', 32), 100 + index)));
        }

        var firstEventPage = eventStore.Read(eventSession, 0, 0);
        Check(
            "eventstore.append_monotonic",
            appendedEvents.Select(item => item.Cursor).SequenceEqual(new long[] { 1, 2, 3 }) &&
            firstEventPage.Events.Select(item => item.Cursor).SequenceEqual(new long[] { 1, 2 }) &&
            firstEventPage.NextCursor == 2 &&
            !firstEventPage.ResyncRequired,
            $"cursors={string.Join(",", appendedEvents.Select(item => item.Cursor))} " +
            $"page={firstEventPage.Events.Count}");

        var sinceFirstEvent = eventStore.Read(eventSession, 1, 10);
        Check(
            "eventstore.read_since_cursor",
            sinceFirstEvent.Events.Select(item => item.Cursor).SequenceEqual(new long[] { 2, 3 }) &&
            sinceFirstEvent.NextCursor == 3,
            $"next={sinceFirstEvent.NextCursor}");

        var upToDatePage = eventStore.Read(eventSession, 3, 0);
        Check(
            "eventstore.read_up_to_date",
            upToDatePage.Events.Count == 0 &&
            upToDatePage.NextCursor == 3 &&
            !upToDatePage.ResyncRequired);

        var replayedEvent = eventStore.Append(
            eventSession, MakeOutcomeEvent(1.ToString("x32"), new string('c', 32), 105));
        Check(
            "eventstore.replay_idempotent",
            replayedEvent.Cursor == 1 &&
            eventStore.Read(eventSession, 2, 0).Events.Select(item => item.Cursor)
                .SequenceEqual(new long[] { 3 }) &&
            eventStore.Read(eventSession, 0, 0).NextCursor == 2,
            $"replayCursor={replayedEvent.Cursor}");

        var invalidEventRejected = false;
        try
        {
            eventStore.Append(
                eventSession,
                MakeOutcomeEvent(new string('f', 32), new string('c', 32), 106) with
                {
                    Type = CombatEventTypesV2.CounterConfirmed
                });
        }
        catch (InvalidOperationException)
        {
            invalidEventRejected = true;
        }

        Check("eventstore.invalid_event_shape", invalidEventRejected);

        for (var index = 4; index <= 6; index++)
        {
            eventStore.Append(
                eventSession,
                MakeOutcomeEvent(index.ToString("x32"), new string('c', 32), 100 + index));
        }

        var overflowPage = eventStore.Read(eventSession, 0, 0);
        Check(
            "eventstore.buffer_overflow",
            overflowPage.ResyncRequired &&
            overflowPage.ResyncReason == CombatEventResyncReasons.BufferOverflow &&
            overflowPage.Events.Count == 0 &&
            overflowPage.NextCursor == 6,
            $"{overflowPage.ResyncReason} next={overflowPage.NextCursor}");

        var retainedPage = eventStore.Read(eventSession, 2, 0);
        Check(
            "eventstore.retained_window_read",
            !retainedPage.ResyncRequired &&
            retainedPage.Events.Select(item => item.Cursor).SequenceEqual(new long[] { 3, 4 }) &&
            retainedPage.NextCursor == 4,
            $"next={retainedPage.NextCursor}");

        var aheadPage = eventStore.Read(eventSession, 99, 0);
        Check(
            "eventstore.cursor_too_old",
            aheadPage.ResyncRequired &&
            aheadPage.ResyncReason == CombatEventResyncReasons.CursorTooOld &&
            aheadPage.Events.Count == 0 &&
            aheadPage.NextCursor == 6);

        Check(
            "eventstore.page_limit",
            eventStore.Read(eventSession, 2, 100).Events.Count == 2 &&
            eventStore.Read(eventSession, 4, 1).Events.Count == 1);

        var otherEventSession = "e2e11111111111111111111111111111";
        var otherEvent = eventStore.Append(
            otherEventSession, MakeOutcomeEvent(new string('a', 32), new string('c', 32), 200));
        Check(
            "eventstore.session_isolation",
            otherEvent.Cursor == 1 &&
            eventStore.Read(otherEventSession, 0, 0).Events.Single().Cursor == 1);

        eventStore.RemoveSession(otherEventSession);
        var freshLifetimeEvent = eventStore.Append(
            otherEventSession, MakeOutcomeEvent(new string('b', 32), new string('c', 32), 210));
        Check(
            "eventstore.session_lifetime_reset",
            freshLifetimeEvent.Cursor == 1 &&
            eventStore.Read(otherEventSession, 0, 0).NextCursor == 1);

        var invalidOptionsRejected = false;
        try
        {
            _ = new CombatEventStore(new CombatEventStreamOptions
            {
                CapacityPerSession = 4,
                MaxPageSize = 5
            });
        }
        catch (InvalidOperationException)
        {
            invalidOptionsRejected = true;
        }

        Check("eventstore.options_validated", invalidOptionsRejected);

        var parallelEventStore = new CombatEventStore(new CombatEventStreamOptions
        {
            CapacityPerSession = 128,
            MaxPageSize = 128
        });
        var parallelEventSession = "e2e22222222222222222222222222222";
        RunBarrierParallel(4, slot =>
        {
            for (var index = 0; index < 25; index++)
            {
                var ordinal = (slot * 25) + index + 1;
                parallelEventStore.Append(
                    parallelEventSession,
                    MakeOutcomeEvent(ordinal.ToString("x32"), new string('d', 32), 300 + ordinal));
            }
        });
        var parallelEventPage = parallelEventStore.Read(parallelEventSession, 0, 0);
        Check(
            "eventstore.parallel_append_monotonic",
            parallelEventPage.Events.Count == 100 &&
            parallelEventPage.Events.Select(item => item.Cursor).Distinct().Count() == 100 &&
            parallelEventPage.Events.Select(item => item.Cursor).SequenceEqual(
                Enumerable.Range(1, 100).Select(value => (long)value)) &&
            parallelEventPage.NextCursor == 100,
            $"count={parallelEventPage.Events.Count} next={parallelEventPage.NextCursor}");

        // QOD-16 ph2 audience policy: AOI 40 WU enter / 48 WU leave hysteresis,
        // same instance/floor/phase, per-caller availability, NPC/boss policy.
        var aoiClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 30, 3, 0, 0, TimeSpan.Zero));
        WorldEntityInstance MakeAoiEntity(
            string entityId,
            string kind,
            string templateId,
            double x,
            string floorId = "OVERWORLD",
            string claimPolicy = WorldEntityClaimPolicies.Shared,
            int respawnSeconds = 0)
        {
            var entity = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = "MAN-TEST-" + entityId,
                Kind = kind,
                TemplateIds = new[] { templateId },
                MapId = options.DefaultMapId,
                FloorId = floorId,
                X = x,
                Y = 0,
                Quantity = 1,
                RespawnSeconds = respawnSeconds,
                ClaimPolicy = claimPolicy
            };
            entity.Initialize();
            return entity;
        }

        var aoiRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog(
                [],
                [
                    MakeAoiEntity(
                        "ENT_SELFCHECK_AOI_EDGE40", WorldEntityKinds.Mob, "MOB_CARPLING", 40),
                    MakeAoiEntity(
                        "ENT_SELFCHECK_AOI_EDGE41", WorldEntityKinds.Mob, "MOB_CARPLING", 41),
                    MakeAoiEntity(
                        "ENT_SELFCHECK_AOI_HYST45", WorldEntityKinds.Mob, "MOB_CARPLING", 45),
                    MakeAoiEntity(
                        "ENT_SELFCHECK_AOI_FLOOR", WorldEntityKinds.Mob, "MOB_CARPLING", 1,
                        "UNDERGROUND"),
                    MakeAoiEntity(
                        "ENT_SELFCHECK_AOI_NPC", WorldEntityKinds.Npc, "NPC_LYAN", 2),
                    MakeAoiEntity(
                        "ENT_SELFCHECK_AOI_BOSS", WorldEntityKinds.Boss, "BOSS_MANG_COT", 3),
                    MakeAoiEntity(
                        "ENT_SELFCHECK_AOI_NODE", WorldEntityKinds.GatherNode,
                        "NODE_BM_ORE_01", 4,
                        claimPolicy: WorldEntityClaimPolicies.PerCharacter,
                        respawnSeconds: 20),
                    MakeAoiEntity(
                        "ENT_SELFCHECK_AOI_SHARED", WorldEntityKinds.Interactable,
                        "OBJ_BM_PACKAGE_01", 5, respawnSeconds: 20)
                ]),
            aoiClock);
        var aoiMobOptions = new MobBehaviorOptions
        {
            AggroRadiusWu = 6,
            LeashRadiusWu = 12,
            AttackRangeWu = 1.2,
            AttackCooldownSeconds = 2,
            MoveSpeedWuPerSecond = 2
        };
        var aoiMobs = new MobLifecycleService(
            aoiRegistry,
            services.GetRequiredService<IWorldGeometryService>(),
            aoiMobOptions,
            aoiClock);
        var aoiClaims = new GatherClaimStore(aoiClock);
        aoiClaims.TryClaim(
            "CHR_SELFCHECK_AOI_A", "ENT_SELFCHECK_AOI_NODE", 20, out _, out _);
        var aoiProjection = new WorldAoiProjectionService(
            aoiRegistry, aoiMobs, enabledCombat, aoiClaims, new MobCombatStateStore());

        var aoiViewerA = NewPlayer("CHR_SELFCHECK_AOI_A");
        aoiViewerA.X = 0;
        aoiViewerA.Y = 0;
        var aoiIdsA = aoiProjection.Project(aoiViewerA)
            .Select(entity => entity.EntityId)
            .ToHashSet(StringComparer.Ordinal);
        Check(
            "aoi.enter_radius",
            aoiIdsA.Contains("ENT_SELFCHECK_AOI_EDGE40") &&
            !aoiIdsA.Contains("ENT_SELFCHECK_AOI_EDGE41") &&
            !aoiIdsA.Contains("ENT_SELFCHECK_AOI_HYST45") &&
            aoiIdsA.Contains("ENT_SELFCHECK_AOI_NPC") &&
            aoiIdsA.Contains("ENT_SELFCHECK_AOI_BOSS") &&
            aoiIdsA.Contains("ENT_SELFCHECK_AOI_NODE") &&
            aoiIdsA.Contains("ENT_SELFCHECK_AOI_SHARED"),
            $"visible={aoiIdsA.Count}");

        Check(
            "aoi.floor_filter",
            !aoiIdsA.Contains("ENT_SELFCHECK_AOI_FLOOR"));

        aoiViewerA.X = 5;
        var aoiIdsNear = aoiProjection.Project(aoiViewerA)
            .Select(entity => entity.EntityId)
            .ToHashSet(StringComparer.Ordinal);
        Check(
            "aoi.hysteresis_enter",
            aoiIdsNear.Contains("ENT_SELFCHECK_AOI_HYST45") &&
            aoiIdsNear.Contains("ENT_SELFCHECK_AOI_EDGE41"),
            $"visible={aoiIdsNear.Count}");

        aoiViewerA.X = 0;
        var aoiIdsBack = aoiProjection.Project(aoiViewerA)
            .Select(entity => entity.EntityId)
            .ToHashSet(StringComparer.Ordinal);
        Check(
            "aoi.hysteresis_keep",
            aoiIdsBack.Contains("ENT_SELFCHECK_AOI_HYST45") &&
            aoiIdsBack.Contains("ENT_SELFCHECK_AOI_EDGE41"),
            $"visible={aoiIdsBack.Count}");

        aoiViewerA.X = -4;
        var aoiIdsFar = aoiProjection.Project(aoiViewerA)
            .Select(entity => entity.EntityId)
            .ToHashSet(StringComparer.Ordinal);
        Check(
            "aoi.hysteresis_leave",
            !aoiIdsFar.Contains("ENT_SELFCHECK_AOI_HYST45") &&
            aoiIdsFar.Contains("ENT_SELFCHECK_AOI_EDGE41") &&
            aoiIdsFar.Contains("ENT_SELFCHECK_AOI_EDGE40"),
            $"visible={aoiIdsFar.Count}");

        aoiProjection.RemoveSession("CHR_SELFCHECK_AOI_A");
        var aoiFreshA = NewPlayer("CHR_SELFCHECK_AOI_A");
        aoiFreshA.X = 0;
        aoiFreshA.Y = 0;
        var aoiFreshPage = aoiProjection.Project(aoiFreshA);
        var aoiFreshIds = aoiFreshPage
            .Select(entity => entity.EntityId)
            .ToHashSet(StringComparer.Ordinal);
        Check(
            "aoi.session_reset",
            !aoiFreshIds.Contains("ENT_SELFCHECK_AOI_HYST45") &&
            aoiFreshIds.Contains("ENT_SELFCHECK_AOI_EDGE40"));

        var aoiViewerB = NewPlayer("CHR_SELFCHECK_AOI_B");
        aoiViewerB.X = 0;
        aoiViewerB.Y = 0;
        var aoiPageB = aoiProjection.Project(aoiViewerB);
        var aoiById = aoiPageB.ToDictionary(
            entity => entity.EntityId, StringComparer.Ordinal);
        Check(
            "aoi.npc_policy",
            aoiById["ENT_SELFCHECK_AOI_NPC"] is
            {
                Kind: WorldEntityKinds.Npc,
                State: WorldEntityStates.Active,
                HealthState: WorldHealthStates.Invulnerable,
                Targetable: false,
                Hp: 0,
                MaxHp: 0,
                LifeId: 1,
                Revision: 1
            });
        Check(
            "aoi.boss_blocked_policy",
            aoiById["ENT_SELFCHECK_AOI_BOSS"] is
            {
                Kind: WorldEntityKinds.Boss,
                HealthState: WorldHealthStates.Blocked,
                Targetable: false,
                Hp: 0,
                MaxHp: 0
            });
        Check(
            "aoi.mob_reference_stats",
            aoiById["ENT_SELFCHECK_AOI_EDGE40"] is
            {
                Kind: WorldEntityKinds.Mob,
                State: MobBehaviorStates.Idle,
                HealthState: WorldHealthStates.Alive,
                Targetable: true,
                Hp: 192,
                MaxHp: 192,
                MapInstanceId: "MAP_BEN_MUA#1",
                Phase: "OPEN_WORLD",
                LifeId: 1
            });
        Check(
            "aoi.availability_per_character",
            aoiById["ENT_SELFCHECK_AOI_NODE"].Availability == WorldAvailability.Available &&
            aoiById["ENT_SELFCHECK_AOI_SHARED"].Availability == WorldAvailability.Available);
        Check(
            "aoi.availability_claimed_cooldown",
            aoiFreshPage
                .First(entity => entity.EntityId == "ENT_SELFCHECK_AOI_NODE")
                .Availability == WorldAvailability.Cooldown);
        Check(
            "aoi.internal_candidates_not_wire",
            aoiRegistry.Count == 8 && aoiPageB.Count == 5,
            $"candidates={aoiRegistry.Count} visible={aoiPageB.Count}");

        // The production shape the integration thread reported: P1:CombatV2 and
        // P1:MobBehavior ON with P1:CombatDamage OFF, so no mob stat bundle
        // exists. ResolveHit skips any target whose max HP it cannot resolve —
        // the cast is accepted and then produces no impact, no miss and no
        // death for that entity — so a row claiming ALIVE/targetable at hp 0
        // advertised a fight the engine silently refuses to resolve. It now
        // follows the boss rule; the behaviour state is unaffected because it is
        // real, and a DEAD mob stays DEAD rather than becoming merely blocked.
        var gateOffMob = MakeAoiEntity(
            "ENT_SELFCHECK_AOI_GATEOFF_MOB", WorldEntityKinds.Mob, "MOB_CARPLING", 10);
        var gateOffDeadMob = MakeAoiEntity(
            "ENT_SELFCHECK_AOI_GATEOFF_DEAD", WorldEntityKinds.Mob, "MOB_CARPLING", 11);
        gateOffDeadMob.Remove(aoiClock.UtcNow);
        var gateOffProjection = new WorldAoiProjectionService(
            new WorldEntityRegistry(
                new WorldEntityCatalog([], [gateOffMob, gateOffDeadMob]), aoiClock),
            aoiMobs,
            combatDamage,
            new GatherClaimStore(aoiClock),
            new MobCombatStateStore());
        var gateOffViewer = NewPlayer("CHR_SELFCHECK_AOI_GATEOFF");
        gateOffViewer.X = 0;
        gateOffViewer.Y = 0;
        var gateOffById = gateOffProjection.Project(gateOffViewer).ToDictionary(
            entity => entity.EntityId, StringComparer.Ordinal);
        Check(
            "aoi.mob_blocked_when_damage_gate_off",
            gateOffById["ENT_SELFCHECK_AOI_GATEOFF_MOB"] is
            {
                Kind: WorldEntityKinds.Mob,
                State: MobBehaviorStates.Idle,
                HealthState: WorldHealthStates.Blocked,
                Targetable: false,
                Hp: 0,
                MaxHp: 0
            },
            $"state={gateOffById["ENT_SELFCHECK_AOI_GATEOFF_MOB"].State} " +
            $"health={gateOffById["ENT_SELFCHECK_AOI_GATEOFF_MOB"].HealthState} " +
            $"targetable={gateOffById["ENT_SELFCHECK_AOI_GATEOFF_MOB"].Targetable}");
        Check(
            "aoi.dead_mob_stays_dead_with_unknown_stats",
            gateOffById["ENT_SELFCHECK_AOI_GATEOFF_DEAD"] is
            {
                HealthState: WorldHealthStates.Dead,
                Targetable: false,
                Hp: 0,
                MaxHp: 0
            });

        // CAM-TOPDOWN-WIDE-20261105 (docs/production/TopDown_Wide_Camera_20261105_vi.md:11,13)
        // makes 64x36 WU the default world view and 48x27 the compact option, while :35
        // forbids touching the server side to match: "the staging build only changes the
        // camera, not the server AOI, reveal, interaction/attack ranges, aggro or grants"
        // and a competitive instance must run one profile for everyone rather than buy
        // vision with a wider screen. That fairness rule only holds while the audience
        // radius already covers the widest box a client can be configured with, so the
        // margin is arithmetic here instead of an assumption someone has to re-derive.
        var wideCornerWu = Math.Sqrt(Math.Pow(64 / 2d, 2) + Math.Pow(36 / 2d, 2));
        var compactCornerWu = Math.Sqrt(Math.Pow(48 / 2d, 2) + Math.Pow(27 / 2d, 2));
        Check(
            "aoi.covers_the_sourced_wide_camera_window",
            wideCornerWu <= WorldAudience.AoiEnterWu &&
            compactCornerWu <= WorldAudience.AoiEnterWu,
            $"wide={wideCornerWu:F3} compact={compactCornerWu:F3} " +
            $"enter={WorldAudience.AoiEnterWu}");
        // The leave ring sits outside the view box, so an entity that is on screen is
        // never dropped while it is still on screen: hysteresis cannot cut a visible
        // actor out of the snapshot.
        Check(
            "aoi.hysteresis_keeps_the_whole_view_box",
            WorldAudience.AoiEnterWu < WorldAudience.AoiLeaveWu &&
            wideCornerWu < WorldAudience.AoiLeaveWu,
            $"leave={WorldAudience.AoiLeaveWu} wide={wideCornerWu:F3}");

        // QOD-16 ph2 v2 combat accept path: cast id, cost/cooldown state and
        // only the events that already occurred (no future impacts).
        var combatV2Store = new CombatEventStore(new CombatEventStreamOptions
        {
            CapacityPerSession = 64,
            MaxPageSize = 64
        });
        var combatV2 = new InMemoryCombatV2Service(
            combatSkills, combatV2Store, new ServerClock());
        var combatV2Actor = NewPlayer("CHR_SELFCHECK_COMBAT_V2");
        var combatV2Session = combatV2Actor.SessionId;
        var basicIntent = new CombatV2Intent(
            CombatV2Actions.BasicAttack, null, null, 1, 1, 0, null);
        var basicCast = combatV2.Resolve(
            combatV2Actor, combatV2Session, basicIntent, new string('a', 32));
        var basicStored = combatV2Store.Read(combatV2Session, 0, 0);
        Check(
            "combatv2.basic_accept",
            basicCast.Accepted &&
            basicCast.Result is
            {
                ActionKind: CombatV2Actions.BasicAttack,
                Mp: 50,
                MpCost: 0,
                NextInputSequence: 1
            } basicResult &&
            basicResult.CastId.Length == 32 &&
            basicResult.Events.SingleOrDefault() is
            {
                Type: CombatEventTypesV2.CastStart,
                Cursor: 1
            } basicStart &&
            basicStart.CastId == basicResult.CastId &&
            basicStored.Events.Single().Cursor == 1 &&
            basicStored.NextCursor == 1,
            basicCast.Failure?.Code);

        var basicReplay = combatV2.Resolve(
            combatV2Actor, combatV2Session, basicIntent, new string('a', 32));
        Check(
            "combatv2.replay_same_cast",
            basicReplay.Accepted &&
            ReferenceEquals(basicReplay.Result, basicCast.Result) &&
            combatV2Store.Read(combatV2Session, 0, 0).NextCursor == 1,
            basicReplay.Failure?.Code);

        Check("combatv2.replay_marker", !basicCast.Replayed && basicReplay.Replayed,
            "Cached accepted receipt cannot be scheduled as a new cast.");
        CombatCommandRaceChecks.Run(combatSkills, id => NewPlayer(id), Check);
        var deadV2Actor = NewPlayer("CHR_V2_DEAD", hp: 0);
        var deadV2Cast = combatV2.Resolve(deadV2Actor, deadV2Actor.SessionId,
            new CombatV2Intent(CombatV2Actions.Skill, "SK-MK-01", null, 1, 1, 0, null), new string('9', 32));
        Check("combatv2.dead_actor_no_cost", deadV2Cast.Failure?.Code == CombatErrorCodes.ActorNotAlive &&
            deadV2Actor.Mp == 50 && deadV2Actor.LastInputSequence == 0 && deadV2Actor.Revision == 1 &&
            combatV2Store.Read(deadV2Actor.SessionId, 0, 100).Events.Count == 0,
            "Dead sources cannot start fresh casts or spend resources.");

        var basicConflict = combatV2.Resolve(
            combatV2Actor, combatV2Session, basicIntent with { AimX = -1 }, new string('a', 32));
        Check(
            "combatv2.replay_conflict",
            basicConflict.Failure?.Code == CombatErrorCodes.IdempotencyConflict,
            basicConflict.Failure?.Code);

        var skillIntent = new CombatV2Intent(
            CombatV2Actions.Skill, "SK-MK-01", null, 2, 1, 0, null);
        var skillCast = combatV2.Resolve(
            combatV2Actor, combatV2Session, skillIntent, new string('b', 32));
        Check(
            "combatv2.skill_accept",
            skillCast.Accepted &&
            skillCast.Result is
            {
                SkillId: "SK-MK-01",
                Mp: 38,
                MpCost: 12,
                NextInputSequence: 2
            } skillResult &&
            skillResult.Events.SingleOrDefault() is { Type: CombatEventTypesV2.CastStart, Cursor: 2 },
            skillCast.Failure?.Code);

        var skillAgain = combatV2.Resolve(
            combatV2Actor, combatV2Session,
            skillIntent with { InputSequence = 3 }, new string('c', 32));
        Check(
            "combatv2.skill_cooldown",
            skillAgain.Failure is { Code: CombatErrorCodes.CooldownActive, Retryable: true },
            skillAgain.Failure?.Code);

        var staleV2Cast = combatV2.Resolve(
            combatV2Actor, combatV2Session,
            basicIntent with { InputSequence = 2 }, new string('d', 32));
        Check(
            "combatv2.stale_sequence",
            staleV2Cast.Failure?.Code == P1ErrorCodes.StaleSequence,
            staleV2Cast.Failure?.Code);

        var poorActor = NewPlayer("CHR_SELFCHECK_COMBAT_V2_POOR", mp: 0);
        var poorCast = combatV2.Resolve(
            poorActor, poorActor.SessionId,
            new CombatV2Intent(CombatV2Actions.Skill, "SK-MK-01", null, 1, 1, 0, null),
            new string('e', 32));
        Check(
            "combatv2.insufficient_mp",
            poorCast.Failure?.Code == CombatErrorCodes.InsufficientResource,
            poorCast.Failure?.Code);

        var otherClassActor = NewPlayer("CHR_SELFCHECK_COMBAT_V2_CLASS", "CLASS_OTHER");
        var otherClassCast = combatV2.Resolve(
            otherClassActor, otherClassActor.SessionId,
            new CombatV2Intent(CombatV2Actions.BasicAttack, null, null, 1, 1, 0, null),
            new string('f', 32));
        Check(
            "combatv2.class_gate",
            otherClassCast.Failure?.Code == CombatErrorCodes.SkillNotAvailable,
            otherClassCast.Failure?.Code);

        var badAction = combatV2.Resolve(
            combatV2Actor, combatV2Session,
            basicIntent with { InputSequence = 9, ActionKind = "HEAVY" }, new string('1', 32));
        var basicWithSkill = combatV2.Resolve(
            combatV2Actor, combatV2Session,
            basicIntent with { InputSequence = 9, SkillId = "SK-MK-01" }, new string('2', 32));
        var badAim = combatV2.Resolve(
            combatV2Actor, combatV2Session,
            basicIntent with { InputSequence = 9, AimX = 2 }, new string('3', 32));
        Check(
            "combatv2.invalid_payload",
            badAction.Failure?.Code == P1ErrorCodes.InvalidPayload &&
            basicWithSkill.Failure?.Code == P1ErrorCodes.InvalidPayload &&
            badAim.Failure?.Code == P1ErrorCodes.InvalidPayload,
            $"{badAction.Failure?.Code}/{basicWithSkill.Failure?.Code}/{badAim.Failure?.Code}");

        combatSkills.TryGet("SK-MK-01", out var onlySkill);
        var narrowV2 = new InMemoryCombatV2Service(
            new CombatSkillCatalog(
                new Dictionary<string, CombatSkillDefinition>(StringComparer.Ordinal)
                {
                    ["SK-MK-01"] = onlySkill!
                }),
            new CombatEventStore(new CombatEventStreamOptions()),
            new ServerClock());
        var narrowActor = NewPlayer("CHR_SELFCHECK_COMBAT_V2_NARROW");
        var unknownSkill = narrowV2.Resolve(
            narrowActor, narrowActor.SessionId,
            new CombatV2Intent(CombatV2Actions.Skill, "SK-MK-02", null, 1, 1, 0, null),
            new string('4', 32));
        Check(
            "combatv2.unknown_skill",
            unknownSkill.Failure?.Code == CombatErrorCodes.UnknownSkill,
            unknownSkill.Failure?.Code);

        // QOD-17 tick engine: impacts resolve on the real tick with the
        // labelled baseline actor stats, life-scoped mob HP, death and kill
        // credit keyed by the death event.
        var tickRecords = services.GetRequiredService<WorldRecordCatalog>();
        var tickClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 30, 4, 0, 0, TimeSpan.Zero));
        WorldEntityInstance MakeTickMob(string entityId, double x)
        {
            var mob = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = "MAN-TEST-" + entityId,
                Kind = WorldEntityKinds.Mob,
                TemplateIds = new[] { "MOB_CARPLING" },
                MapId = options.DefaultMapId,
                FloorId = "OVERWORLD",
                X = x,
                Y = 0,
                Quantity = 1,
                RespawnSeconds = 18
            };
            mob.Initialize();
            return mob;
        }

        if (!questCatalog.TryGet("P00-01", out var tickQuestBase))
        {
            throw new InvalidOperationException("P00-01 must exist for the tick self-check.");
        }

        var tickQuest = tickQuestBase with
        {
            QuestId = "TEST-TICK-01",
            Objectives =
            [
                new QuestObjectiveDefinition(
                    "OBJ_TEST_TICK_KILL", QuestObjectiveTypes.Kill,
                    ["MAN-TEST-ENT_SELFCHECK_TICK_MOB"], 3, options.DefaultMapId)
            ],
            InitialStepId = "STEP_TEST_TICK_KILL",
            PrerequisiteQuestIds = []
        };
        QuestCatalog TickCatalog() => new(
            new Dictionary<string, QuestDefinition>(StringComparer.Ordinal)
            {
                ["TEST-TICK-01"] = tickQuest
            });

        var tickQuestActor = NewPlayer("CHR_SELFCHECK_TICK");
        tickQuestActor.X = 0;
        tickQuestActor.Y = 0;
        var tickQuests = new InMemoryQuestService(
            TickCatalog(), new InMemoryQuestStateStore(), tickRecords, tickClock);
        tickQuests.Accept(tickQuestActor, "TEST-TICK-01");

        var tickRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeTickMob("ENT_SELFCHECK_TICK_MOB", 3)]),
            tickClock);
        var tickEventStore = new CombatEventStore(new CombatEventStreamOptions
        {
            CapacityPerSession = 256,
            MaxPageSize = 256
        });
        var tickStateStore = new MobCombatStateStore();
        var tickGuardWindows = new GuardWindowStore();
        var tickGeometry = services.GetRequiredService<IWorldGeometryService>();
        var tickEngine = new CombatTickEngine(
            tickRegistry,
            enabledCombat,
            combatSkills,
            tickEventStore,
            tickStateStore,
            tickQuests,
            new FixedCombatRolls(hit: true, crit: false),
            tickGuardWindows,
            tickGeometry,
            NewDashes(tickGeometry),
            new ServerClock());

        var basicTickCastId = new string('a', 32);
        Check(
            "tick.schedule",
            tickEngine.Schedule(
                tickQuestActor, tickQuestActor.SessionId, basicTickCastId,
                CombatV2Actions.BasicAttack, null, 1, 0, 100) &&
            !tickEngine.Schedule(
                tickQuestActor, tickQuestActor.SessionId, basicTickCastId,
                CombatV2Actions.BasicAttack, null, 1, 0, 100) &&
            tickEngine.ScheduledCastCount == 1,
            $"scheduled={tickEngine.ScheduledCastCount}");

        tickEngine.Tick(102);
        Check(
            "tick.windup_no_impact",
            (tickStateStore.TryGet("ENT_SELFCHECK_TICK_MOB", 1)?.Hp ?? 192) == 192);

        var basicTickEvents = tickEngine.Tick(103);
        var basicImpact = basicTickEvents.SingleOrDefault(
            combatEvent => combatEvent.Type == CombatEventTypesV2.Impact);
        Check(
            "tick.basic_impact",
            basicImpact is { HitIndex: 0, TargetLifeId: 1 } &&
            basicImpact.Result is { Hit: true, Crit: false, Amount: 19, HpDamage: 19 } &&
            (tickStateStore.TryGet("ENT_SELFCHECK_TICK_MOB", 1)?.Hp ?? 0) == 173,
            $"{basicImpact?.Result?.Amount}");

        tickEngine.Tick(104);
        var tickedTypes = tickEventStore.Read(tickQuestActor.SessionId, 0, 0).Events
            .Select(combatEvent => combatEvent.Type)
            .ToArray();
        Check(
            "tick.end_event",
            tickedTypes.SequenceEqual(
                new[] { CombatEventTypesV2.Impact, CombatEventTypesV2.End },
                StringComparer.Ordinal) &&
            tickEngine.ScheduledCastCount == 0,
            string.Join(",", tickedTypes));

        tickEngine.Schedule(
            tickQuestActor, tickQuestActor.SessionId, new string('b', 32),
            CombatV2Actions.Skill, "SK-MK-03", 1, 0, 200);
        var mk03Hit1 = tickEngine.Tick(202)
            .Single(combatEvent => combatEvent.Type == CombatEventTypesV2.Impact);
        var mk03Hit2 = tickEngine.Tick(205)
            .Single(combatEvent => combatEvent.Type == CombatEventTypesV2.Impact);
        var mk03Hit3 = tickEngine.Tick(208)
            .Single(combatEvent => combatEvent.Type == CombatEventTypesV2.Impact);
        tickEngine.Tick(209);
        Check(
            "tick.mk03_multi_hit",
            mk03Hit1.HitIndex == 0 && mk03Hit1.Result?.Amount == 8 &&
            mk03Hit2.HitIndex == 1 && mk03Hit2.Result?.Amount == 10 &&
            mk03Hit3.HitIndex == 2 && mk03Hit3.Result?.Amount == 17 &&
            (tickStateStore.TryGet("ENT_SELFCHECK_TICK_MOB", 1)?.Hp ?? 0) == 138,
            $"{mk03Hit1.Result?.Amount}/{mk03Hit2.Result?.Amount}/{mk03Hit3.Result?.Amount}");

        // Work order 29 freezes "VFX không quyết định hit". The runtime form of that
        // sentence is two catalogues that differ in exactly one field - the VFX key -
        // resolving the same SK-MK-03 cast into the same three impacts on the same
        // ticks. A grep would only prove nobody reads the key today; this proves the
        // resolution cannot depend on it.
        var variantDefs = new Dictionary<string, CombatSkillDefinition>(StringComparer.Ordinal);
        foreach (var variantId in new[] { "SK-MK-01", "SK-MK-02", "SK-MK-03" })
        {
            combatSkills.TryGet(variantId, out var shippedDefinition);
            variantDefs[variantId] = shippedDefinition with { VfxKey = "VFX/Skill/SK-MK-99" };
        }

        var vfxActor = NewPlayer("CHR_SELFCHECK_VFX_ONLY");
        vfxActor.X = 0;
        vfxActor.Y = 0;
        var vfxQuests = new InMemoryQuestService(
            TickCatalog(), new InMemoryQuestStateStore(), tickRecords, tickClock);
        vfxQuests.Accept(vfxActor, "TEST-TICK-01");
        var vfxRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeTickMob("ENT_SELFCHECK_VFX_MOB", 3)]), tickClock);
        var vfxEventStore = new CombatEventStore(new CombatEventStreamOptions
        {
            CapacityPerSession = 256,
            MaxPageSize = 256
        });
        var vfxStateStore = new MobCombatStateStore();
        var vfxEngine = new CombatTickEngine(
            vfxRegistry,
            enabledCombat,
            new CombatSkillCatalog(variantDefs),
            vfxEventStore,
            vfxStateStore,
            vfxQuests,
            new FixedCombatRolls(hit: true, crit: false),
            new GuardWindowStore(),
            tickGeometry,
            NewDashes(tickGeometry),
            new ServerClock());

        vfxEngine.Schedule(
            vfxActor, vfxActor.SessionId, new string('f', 32),
            CombatV2Actions.Skill, "SK-MK-03", 1, 0, 300);
        var vfxHit1 = vfxEngine.Tick(302)
            .Single(combatEvent => combatEvent.Type == CombatEventTypesV2.Impact);
        var vfxHit2 = vfxEngine.Tick(305)
            .Single(combatEvent => combatEvent.Type == CombatEventTypesV2.Impact);
        var vfxHit3 = vfxEngine.Tick(308)
            .Single(combatEvent => combatEvent.Type == CombatEventTypesV2.Impact);
        Check(
            "tick.vfx_key_cannot_change_the_hit",
            vfxHit1.HitIndex == 0 && vfxHit1.Result?.Amount == 8 &&
            vfxHit2.HitIndex == 1 && vfxHit2.Result?.Amount == 10 &&
            vfxHit3.HitIndex == 2 && vfxHit3.Result?.Amount == 17 &&
            (vfxStateStore.TryGet("ENT_SELFCHECK_VFX_MOB", 1)?.Hp ?? 0) == 157,
            $"{vfxHit1.Result?.Amount}/{vfxHit2.Result?.Amount}/{vfxHit3.Result?.Amount}");

        foreach (var cancelReason in new[] { "DEAD", "MAP", "FLOOR" })
        {
            var cancelledSource = NewPlayer("CHR_CANCEL_" + cancelReason);
            cancelledSource.X = 0; cancelledSource.Y = 0;
            var cancelRegistry = new WorldEntityRegistry(
                new WorldEntityCatalog([], [MakeTickMob("ENT_SELFCHECK_CANCEL_MOB", 3)]), tickClock);
            var cancelHp = new MobCombatStateStore();
            var cancelEngine = new CombatTickEngine(cancelRegistry, enabledCombat, combatSkills,
                new CombatEventStore(new CombatEventStreamOptions()), cancelHp, tickQuests,
                new FixedCombatRolls(hit: true, crit: false),
                new GuardWindowStore(), tickGeometry, NewDashes(tickGeometry), new ServerClock());
            cancelEngine.Schedule(cancelledSource, cancelledSource.SessionId, Guid.NewGuid().ToString("N"),
                CombatV2Actions.BasicAttack, null, 1, 0, 100);
            if (cancelReason == "DEAD") cancelledSource.Hp = 0;
            else if (cancelReason == "MAP") cancelledSource.MapId = "MAP_THANH_LAC";
            else cancelledSource.FloorId = "OTHER_FLOOR";
            var cancelledEvents = cancelEngine.Tick(103);
            Check("tick.cancel_source_" + cancelReason.ToLowerInvariant(),
                cancelledEvents.Count(e => e.Type == CombatEventTypesV2.Cancel) == 1 &&
                cancelledEvents.Count(e => e.Type == CombatEventTypesV2.End) == 1 &&
                !cancelledEvents.Any(e => e.Type is CombatEventTypesV2.Impact or CombatEventTypesV2.Death) &&
                cancelHp.TryGet("ENT_SELFCHECK_CANCEL_MOB", 1) is null && cancelEngine.ScheduledCastCount == 0,
                "Source invalidated before impact; no damage or reward.");
        }

        var missRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeTickMob("ENT_SELFCHECK_TICK_MOB", 3)]),
            tickClock);
        var missStore = new MobCombatStateStore();
        var missEngine = new CombatTickEngine(
            missRegistry, enabledCombat, combatSkills,
            new CombatEventStore(new CombatEventStreamOptions()), missStore,
            tickQuests, new FixedCombatRolls(hit: false, crit: false),
            tickGuardWindows, tickGeometry, NewDashes(tickGeometry), new ServerClock());
        missEngine.Schedule(
            tickQuestActor, "e2e33333333333333333333333333333",
            new string('c', 32), CombatV2Actions.BasicAttack, null, 1, 0, 300);
        var missEvents = missEngine.Tick(303);
        Check(
            "tick.miss",
            missEvents.SingleOrDefault(
                combatEvent => combatEvent.Type == CombatEventTypesV2.Miss)?.Result is
            { Hit: false, Amount: 0, HpDamage: 0 } &&
            (missStore.TryGet("ENT_SELFCHECK_TICK_MOB", 1)?.Hp ?? 192) == 192,
            "miss roll");

        var rangeRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeTickMob("ENT_SELFCHECK_TICK_MOB", 5)]),
            tickClock);
        var rangeEngine = new CombatTickEngine(
            rangeRegistry, enabledCombat, combatSkills,
            new CombatEventStore(new CombatEventStreamOptions()), new MobCombatStateStore(),
            tickQuests, new FixedCombatRolls(hit: true, crit: false),
            tickGuardWindows, tickGeometry, NewDashes(tickGeometry), new ServerClock());
        rangeEngine.Schedule(
            tickQuestActor, "e2e44444444444444444444444444444",
            new string('d', 32), CombatV2Actions.BasicAttack, null, 1, 0, 400);
        var rangeEvents = rangeEngine.Tick(403);
        Check(
            "tick.out_of_range",
            rangeEvents.All(combatEvent => combatEvent.Type != CombatEventTypesV2.Impact),
            string.Join(",", rangeEvents.Select(combatEvent => combatEvent.Type)));

        var behindRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeTickMob("ENT_SELFCHECK_TICK_MOB", -3)]),
            tickClock);
        var behindEngine = new CombatTickEngine(
            behindRegistry, enabledCombat, combatSkills,
            new CombatEventStore(new CombatEventStreamOptions()), new MobCombatStateStore(),
            tickQuests, new FixedCombatRolls(hit: true, crit: false),
            tickGuardWindows, tickGeometry, NewDashes(tickGeometry), new ServerClock());
        behindEngine.Schedule(
            tickQuestActor, "e2e55555555555555555555555555555",
            new string('e', 32), CombatV2Actions.BasicAttack, null, 1, 0, 500);
        var behindEvents = behindEngine.Tick(503);
        Check(
            "tick.behind_no_impact",
            behindEvents.All(combatEvent => combatEvent.Type != CombatEventTypesV2.Impact));

        var deathRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeTickMob("ENT_SELFCHECK_TICK_MOB", 3)]),
            tickClock);
        var deathStore = new MobCombatStateStore();
        var deathActor = NewPlayer("CHR_SELFCHECK_TICK_KILL");
        deathActor.X = 0;
        deathActor.Y = 0;
        var deathQuests = new InMemoryQuestService(
            TickCatalog(), new InMemoryQuestStateStore(), tickRecords, tickClock);
        deathQuests.Accept(deathActor, "TEST-TICK-01");
        var deathKills = new RecordingKillSink();
        var deathEngine = new CombatTickEngine(
            deathRegistry, enabledCombat, combatSkills,
            new CombatEventStore(new CombatEventStreamOptions()), deathStore,
            deathQuests, new FixedCombatRolls(hit: true, crit: false),
            tickGuardWindows, tickGeometry, NewDashes(tickGeometry), new ServerClock(),
            kills: deathKills);

        var deathCount = 0;
        var deathEventIds = new List<string>();
        for (var castIndex = 0; castIndex < 6; castIndex++)
        {
            var startTick = 1000 + (castIndex * 20);
            deathEngine.Schedule(
                deathActor, deathActor.SessionId, castIndex.ToString("x32"),
                CombatV2Actions.Skill, "SK-MK-03", 1, 0, startTick);
            for (var tick = startTick; tick <= startTick + 10; tick++)
            {
                foreach (var combatEvent in deathEngine.Tick(tick))
                {
                    if (combatEvent.Type != CombatEventTypesV2.Death)
                    {
                        continue;
                    }

                    deathCount++;
                    deathEventIds.Add(combatEvent.EventId);
                }
            }
        }

        deathRegistry.TryGet("ENT_SELFCHECK_TICK_MOB", out var deadTickMob);
        var killState = deathQuests.GetState(deathActor.CharacterId, "TEST-TICK-01").State;
        Check(
            "tick.death_once_and_credit",
            deathCount == 1 &&
            deadTickMob.State == WorldEntityStates.Dead &&
            deadTickMob.LifeId == 1 &&
            killState is { State: QuestStates.Active } &&
            killState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_TICK_KILL") == 1,
            $"deaths={deathCount} state={deadTickMob.State} " +
            $"kills={killState?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_TICK_KILL")}");

        tickClock.Advance(TimeSpan.FromSeconds(18));
        var tickRespawnCount = deathRegistry.Update();
        deathRegistry.TryGet("ENT_SELFCHECK_TICK_MOB", out var tickRespawnedMob);
        deathEngine.Schedule(
            deathActor, deathActor.SessionId, new string('f', 32),
            CombatV2Actions.BasicAttack, null, 1, 0, 2000);
        var respawnImpact = deathEngine.Tick(2003)
            .SingleOrDefault(combatEvent => combatEvent.Type == CombatEventTypesV2.Impact);
        var killStateAfterRespawn = deathQuests
            .GetState(deathActor.CharacterId, "TEST-TICK-01").State;
        Check(
            "tick.respawn_new_life",
            tickRespawnCount == 1 &&
            tickRespawnedMob.LifeId == 2 &&
            tickRespawnedMob.State == WorldEntityStates.Alive &&
            respawnImpact is { TargetLifeId: 2, HitIndex: 0 } &&
            (deathStore.TryGet("ENT_SELFCHECK_TICK_MOB", 2)?.Hp ?? 0) == 173 &&
            killStateAfterRespawn?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_TICK_KILL") == 1,
            $"life={tickRespawnedMob.LifeId} hp={deathStore.TryGet("ENT_SELFCHECK_TICK_MOB", 2)?.Hp}");

        // QOD-21 Q2: the quest machines get their credit from this notification, so
        // it must carry exactly the death the engine resolved — one report per
        // resolved kill, the killer the engine charged, the life that ended, and the
        // same event id the killer's combat stream shows. A respawned life that is
        // only hit (not killed) reports nothing.
        Check(
            "tick.kill_sink_reports_authoritative_death",
            deathKills.Kills.Count == 1 &&
            deathEventIds.Count == 1 &&
            deathKills.Kills[0].KillerCharacterId == deathActor.CharacterId &&
            deathKills.Kills[0].EntityId == "ENT_SELFCHECK_TICK_MOB" &&
            deathKills.Kills[0].RecordId == "MAN-TEST-ENT_SELFCHECK_TICK_MOB" &&
            deathKills.Kills[0].LifeId == 1 &&
            deathKills.Kills[0].DeathEventId == deathEventIds[0],
            $"kills={deathKills.Kills.Count} " +
            $"first={deathKills.Kills.FirstOrDefault().EntityId}/" +
            $"{deathKills.Kills.FirstOrDefault().LifeId}");

        // QOD-17 loot: versioned CSV export, one roll per group then weighted
        // SELECT_ONE, deterministic server RNG and dry-run receipts (grant OFF
        // until the mob coin band source exists).
        var lootRecipes = enabledCombat.LootRecipes;
        Check(
            "loot.bundle",
            lootRecipes is
            {
                SchemaVersion: 1,
                BundleId: "LOOT_RECIPE_V1",
                GrantEnabled: false,
                GrantBlockedReason: "COIN_BAND_MISSING"
            } &&
            lootRecipes.Sources.Count == 57 &&
            lootRecipes.MobTemplateToSource.Count == 5 &&
            lootRecipes.MobTemplateToSource["MOB_CARPLING"] == "LT_MOB_CARPLING",
            $"sources={lootRecipes.Sources.Count} mapping={lootRecipes.MobTemplateToSource.Count}");

        var lootGateBlocked = false;
        try
        {
            _ = combatDamage.LootRecipes;
        }
        catch (InvalidOperationException)
        {
            lootGateBlocked = true;
        }

        Check("loot.gate_blocks_load", lootGateBlocked);

        var carplingGroup = lootRecipes.Sources["LT_MOB_CARPLING"].Groups.Single();
        Check(
            "loot.carpling_source",
            carplingGroup is
            {
                GroupId: "MATERIAL_POOL",
                Mode: LootGroupModes.SelectOne,
                ChanceBps: 1200
            } &&
            carplingGroup.Entries.Count == 5 &&
            carplingGroup.Entries.All(entry =>
                entry.QuantityMin == 1 && entry.QuantityMax == 1 && entry.Weight == 1),
            $"{carplingGroup.Entries.Count} entries");

        var passLootroller = new LootRoller(lootRecipes, new FixedLootRolls(0.0));
        var firstLootReceipt = passLootroller.Roll("MOB_CARPLING", new string('a', 32));
        Check(
            "loot.select_one_first",
            firstLootReceipt is
            {
                Granted: false,
                BlockedReason: "COIN_BAND_MISSING",
                SourceId: "LT_MOB_CARPLING"
            } &&
            firstLootReceipt.Groups.Single() is { Passed: true, Quantity: 1 } firstLootGroup &&
            firstLootGroup.EntryId == carplingGroup.Entries[0].EntryId,
            firstLootReceipt.Groups.SingleOrDefault()?.EntryId);

        var lootMissReceipt = new LootRoller(lootRecipes, new FixedLootRolls(0.5))
            .Roll("MOB_CARPLING", "kill-miss");
        Check(
            "loot.chance_miss",
            lootMissReceipt.Groups.Single() is
            {
                Passed: false,
                EntryId: null,
                ItemId: null,
                Quantity: 0
            });

        var lastLootReceipt = new LootRoller(
                lootRecipes, new ChanceThenSelectionRolls(chance: 0.0, selection: 0.999))
            .Roll("MOB_CARPLING", "kill-last");
        Check(
            "loot.select_one_weighted_last",
            lastLootReceipt.Groups.Single() is { Passed: true } lastLootGroup &&
            lastLootGroup.EntryId == carplingGroup.Entries[^1].EntryId,
            lastLootReceipt.Groups.SingleOrDefault()?.EntryId);

        var realLootRoller = new LootRoller(lootRecipes, new LootRngRollSource());
        var realLootA = realLootRoller.Roll("MOB_CARPLING", "kill-deterministic");
        var realLootB = realLootRoller.Roll("MOB_CARPLING", "kill-deterministic");
        Check(
            "loot.roll_deterministic",
            realLootA.Groups.Single().ChanceRoll == realLootB.Groups.Single().ChanceRoll &&
            realLootA.Groups.Single().EntryId == realLootB.Groups.Single().EntryId &&
            realLootA.Groups.Single().Quantity == realLootB.Groups.Single().Quantity &&
            realLootA.Groups.Single().ChanceRoll is >= 0 and < 1);

        var lootLedger = new LootReceiptLedger();
        var recordedReceipt = lootLedger.Record(realLootA);
        var recordedAgainReceipt = lootLedger.Record(realLootB);
        Check(
            "loot.ledger_stable",
            ReferenceEquals(recordedReceipt, recordedAgainReceipt) &&
            lootLedger.TryGet("kill-deterministic", "LT_MOB_CARPLING", out var storedReceipt) &&
            ReferenceEquals(storedReceipt, recordedReceipt) &&
            lootLedger.Count == 1);

        var unknownLootReceipt = passLootroller.Roll("MOB_UNKNOWN", "kill-unknown");
        Check(
            "loot.unsupported_source",
            unknownLootReceipt is { SourceId: null, BlockedReason: "NO_SOURCE", Granted: false } &&
            unknownLootReceipt.Groups.Count == 0);

        Check(
            "loot.grant_off",
            firstLootReceipt.Granted == false &&
            firstLootReceipt.BlockedReason == LootRecipeLoader.CoinBandBlockedReason);

        // QOD-17 manifest spawn groups: members respawn only after the whole
        // group is cleared; partial deaths keep the group down.
        var groupClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 30, 5, 0, 0, TimeSpan.Zero));
        WorldEntityInstance MakeGroupMember(string entityId, int memberIndex)
        {
            var member = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = "MAN-TEST-GROUP",
                Kind = WorldEntityKinds.Mob,
                TemplateIds = new[] { "MOB_CARPLING" },
                MapId = options.DefaultMapId,
                FloorId = "OVERWORLD",
                X = 3,
                Y = 0,
                Quantity = 1,
                RespawnSeconds = 0,
                GroupId = "MAN-TEST-GROUP",
                MemberIndex = memberIndex,
                GroupRespawnSeconds = 10
            };
            member.Initialize();
            return member;
        }

        var groupRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog(
                [],
                [
                    MakeGroupMember("ENT_SELFCHECK_GROUP_1", 1),
                    MakeGroupMember("ENT_SELFCHECK_GROUP_2", 2)
                ]),
            groupClock);
        var groupService = new MobSpawnGroupService(groupRegistry, groupClock);
        groupRegistry.Despawn("ENT_SELFCHECK_GROUP_1");
        var individualGroupRespawn = groupRegistry.Update();
        groupClock.Advance(TimeSpan.FromSeconds(10));
        var partialGroupTick = groupService.Tick();
        groupRegistry.TryGet("ENT_SELFCHECK_GROUP_1", out var partialGroupMember);
        Check(
            "spawn.partial_group_no_respawn",
            individualGroupRespawn == 0 &&
            partialGroupTick == 0 &&
            partialGroupMember.State == WorldEntityStates.Dead,
            $"individual={individualGroupRespawn} group={partialGroupTick} " +
            $"state={partialGroupMember.State}");

        groupRegistry.Despawn("ENT_SELFCHECK_GROUP_2");
        groupClock.Advance(TimeSpan.FromSeconds(9));
        var earlyGroupTick = groupService.Tick();
        groupClock.Advance(TimeSpan.FromSeconds(10));
        var clearedGroupTick = groupService.Tick();
        groupRegistry.TryGet("ENT_SELFCHECK_GROUP_1", out var respawnedGroupMember1);
        groupRegistry.TryGet("ENT_SELFCHECK_GROUP_2", out var respawnedGroupMember2);
        Check(
            "spawn.clear_group_respawn",
            earlyGroupTick == 0 &&
            clearedGroupTick == 2 &&
            respawnedGroupMember1.State == WorldEntityStates.Alive &&
            respawnedGroupMember2.State == WorldEntityStates.Alive &&
            respawnedGroupMember1.LifeId == 2 &&
            respawnedGroupMember2.LifeId == 2,
            $"early={earlyGroupTick} cleared={clearedGroupTick} " +
            $"life={respawnedGroupMember1.LifeId}/{respawnedGroupMember2.LifeId}");

        var spawnRegistry = services.GetRequiredService<WorldEntityRegistry>();
        var registryGroups = new MobSpawnGroupService(
            spawnRegistry, services.GetRequiredService<IServerClock>());
        spawnRegistry.TryGet("ENT_MAN_BM_SPAWN_BM_04_M2", out var mixedGroupMember);
        Check(
            "spawn.real_bundle_composition",
            spawnRegistry.Count == 44 &&
            registryGroups.GroupCount == 8 &&
            registryGroups.MemberCount("MAN-BM-SPAWN_BM_01") == 3 &&
            registryGroups.MemberCount("MAN-BM-SPAWN_BM_02") == 4 &&
            mixedGroupMember is { GroupId: "MAN-BM-SPAWN_BM_04" } &&
            mixedGroupMember.TemplateIds.Single() == "MOB_WATERROOT",
            $"groups={registryGroups.GroupCount} " +
            $"mixed={mixedGroupMember?.TemplateIds.FirstOrDefault()}");

        Check(
            "damage.oracle_raw",
            Near(DamageFormula.RawDamage(20, 0, 1.5, 1, 0), 30),
            $"{DamageFormula.RawDamage(20, 0, 1.5, 1, 0)}");

        var oracleMitigation = DamageFormula.MitigationMultiplier(10);
        Check(
            "damage.oracle_noncrit",
            DamageFormula.FinalDamage(30, oracleMitigation, 1, 1, 1) == 27,
            $"{DamageFormula.FinalDamage(30, oracleMitigation, 1, 1, 1)}");
        Check(
            "damage.oracle_crit",
            DamageFormula.FinalDamage(30, oracleMitigation, 1, DamageFormula.CritMultiplier, 1) == 40,
            $"{DamageFormula.FinalDamage(30, oracleMitigation, 1, DamageFormula.CritMultiplier, 1)}");
        Check("damage.armor_zero", Near(DamageFormula.MitigationMultiplier(0), 1));
        Check(
            "damage.reduction_cap",
            Near(DamageFormula.DamageReductionMultiplier(0.9), 0.2),
            $"{DamageFormula.DamageReductionMultiplier(0.9)}");
        Check(
            "damage.resist_pve_cap",
            Near(DamageFormula.ElementMultiplier(0.7, pvp: false), 0.5) &&
            Near(DamageFormula.ElementMultiplier(0.7, pvp: true), 0.7),
            $"{DamageFormula.ElementMultiplier(0.7, pvp: false)}/{DamageFormula.ElementMultiplier(0.7, pvp: true)}");
        Check(
            "damage.final_min_one",
            DamageFormula.FinalDamage(0.001, 1, 1, 1, 1) == 1);
        Check(
            "damage.hit_clamp",
            Near(DamageFormula.HitProbability(1, 0), 0.98) &&
            Near(DamageFormula.HitProbability(0, 1), 0.05),
            $"{DamageFormula.HitProbability(1, 0)}/{DamageFormula.HitProbability(0, 1)}");
        Check(
            "damage.attribute_derived",
            Near(DamageFormula.AttributeCritChance(5, 0, 1), 0.0525) &&
            Near(DamageFormula.AttributeAccuracy(5, 0), 0.0025) &&
            Near(DamageFormula.AttributeDodge(5, 0, 1), 0.0015));

        var rngSameSeed = CombatRng.Uniform01("CAST_1", "TGT_1", 0);
        var rngRepeat = CombatRng.Uniform01("CAST_1", "TGT_1", 0);
        var rngNextHit = CombatRng.Uniform01("CAST_1", "TGT_1", 1);
        Check(
            "damage.rng_deterministic",
            rngSameSeed == rngRepeat &&
            rngNextHit != rngSameSeed &&
            rngSameSeed is >= 0 and < 1,
            $"hit0={rngSameSeed} hit1={rngNextHit}");

        var registry = services.GetRequiredService<WorldEntityRegistry>();
        var projection = services.GetRequiredService<WorldEntityProjectionService>();
        var projectedGateOff = projection.Project();
        Check(
            "projection.all_entities",
            projectedGateOff.Count == registry.Count && registry.Count == 44,
            $"projected={projectedGateOff.Count} registry={registry.Count}");

        var mobGateOff = projectedGateOff.First(entity => entity.EntityId == "ENT_MAN_BM_SPAWN_BM_01");
        Check(
            "projection.mob_zero_when_gate_off",
            mobGateOff is { Kind: WorldEntityKinds.Mob, Hp: 0, MaxHp: 0, LifeId: 1 },
            $"hp={mobGateOff.Hp}");

        var enabledProjection = new WorldEntityProjectionService(
            registry,
            services.GetRequiredService<MobLifecycleService>(),
            enabledCombat);
        var projected = enabledProjection.Project();

        var npcLyan = projected.First(entity => entity.EntityId == "ENT_MAN_BM_NPC_LYAN");
        Check(
            "projection.npc_invulnerable",
            npcLyan is
            {
                Kind: WorldEntityKinds.Npc,
                Hp: 0,
                MaxHp: 0,
                LifeId: 1,
                Revision: 1,
                State: WorldEntityStates.Active
            },
            $"hp={npcLyan.Hp} state={npcLyan.State}");

        var spawn01 = projected.First(entity => entity.EntityId == "ENT_MAN_BM_SPAWN_BM_01");
        Check(
            "projection.mob_reference_stats",
            spawn01 is
            {
                Kind: WorldEntityKinds.Mob,
                Hp: 192,
                MaxHp: 192,
                LifeId: 1,
                State: MobBehaviorStates.Idle
            },
            $"hp={spawn01.Hp} state={spawn01.State}");

        var spawn07 = projected.First(entity => entity.EntityId == "ENT_MAN_BM_SPAWN_BM_07");
        Check(
            "projection.elite_stats",
            spawn07 is { Kind: WorldEntityKinds.Mob, Hp: 1296, MaxHp: 1296 },
            $"hp={spawn07.Hp}");

        var bossSpawn = projected.First(entity => entity.EntityId == "ENT_MAN_BM_SPAWN_BM_05_QUEST");
        Check(
            "projection.boss_zero_blocked",
            bossSpawn is { Kind: WorldEntityKinds.Boss, Hp: 0, MaxHp: 0 },
            $"hp={bossSpawn.Hp}");

        var lifeIdClock = new ManualServerClock(DateTimeOffset.UtcNow);
        var lifeIdRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog(
                [],
                [MakeFixtureNode("ENT_SELFCHECK_LIFEID_NODE", "MAN-BM-NODE_BM_ORE_01", 21, 60)]),
            lifeIdClock);
        var lifeIdProjection = new WorldEntityProjectionService(
            lifeIdRegistry,
            services.GetRequiredService<MobLifecycleService>(),
            enabledCombat);
        lifeIdRegistry.Despawn("ENT_SELFCHECK_LIFEID_NODE");
        lifeIdClock.Advance(TimeSpan.FromSeconds(60));
        lifeIdRegistry.Update();
        var lifeIdProjected = lifeIdProjection.Project().Single();
        Check(
            "projection.life_id_bump",
            lifeIdProjected is
            {
                State: WorldEntityStates.Available,
                Revision: 3,
                LifeId: 2,
                Hp: 0
            },
            $"state={lifeIdProjected.State} revision={lifeIdProjected.Revision} lifeId={lifeIdProjected.LifeId}");

        Check("quest.catalog", questCatalog.Count == 5, $"count={questCatalog.Count}");
        Check(
            "quest.catalog_ids",
            questCatalog.QuestIds.SequenceEqual(
                new[] { "P00-01", "P00-02", "P00-03", "P00-04", "P00-05" },
                StringComparer.Ordinal),
            string.Join(",", questCatalog.QuestIds));

        var questActor = NewPlayer("CHR_SELFCHECK_QUEST");
        var questInitial = quests.GetState(questActor.CharacterId, "P00-01");
        Check(
            "quest.initial_available",
            questInitial.State?.State == QuestStates.Available,
            questInitial.State?.State);

        var questAccepted = quests.Accept(questActor, "P00-01");
        Check(
            "quest.accept",
            questAccepted.Accepted && questAccepted.State?.State == QuestStates.Active,
            questAccepted.State?.State);

        var eventP1 = new string('a', 32);
        var eventP2 = new string('b', 32);
        var eventP3 = new string('c', 32);

        var progress1 = quests.RecordVerifiedEvent(
            questActor, eventP1, QuestProgressEventTypes.InteractClaim,
            "MAN-BM-OBJ_BM_PACKAGE_01", options.DefaultMapId);
        var progress2 = quests.RecordVerifiedEvent(
            questActor, eventP2, QuestProgressEventTypes.InteractClaim,
            "MAN-BM-OBJ_BM_PACKAGE_02", options.DefaultMapId);
        var progress3 = quests.RecordVerifiedEvent(
            questActor, eventP3, QuestProgressEventTypes.InteractClaim,
            "MAN-BM-OBJ_BM_PACKAGE_03", options.DefaultMapId);
        Check(
            "quest.ready_to_turn_in",
            progress1.SingleOrDefault() is { State: QuestStates.Active, Revision: 3 } p1 &&
            p1.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 1 &&
            progress2.SingleOrDefault() is { State: QuestStates.Active, Revision: 4 } &&
            progress3.SingleOrDefault() is { State: QuestStates.ReadyToTurnIn, Revision: 5 } p3 &&
            p3.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 3,
            progress3.SingleOrDefault()?.State);

        var duplicateProgress = quests.RecordVerifiedEvent(
            questActor, new string('d', 32), QuestProgressEventTypes.InteractClaim,
            "MAN-BM-OBJ_BM_PACKAGE_01", options.DefaultMapId);
        Check(
            "quest.distinct_record_dedupe",
            duplicateProgress.Count == 0,
            duplicateProgress.Count.ToString());

        var inactiveActor = NewPlayer("CHR_SELFCHECK_QUEST_IDLE");
        var inactiveProgress = quests.RecordVerifiedEvent(
            inactiveActor, new string('e', 32), QuestProgressEventTypes.InteractClaim,
            "MAN-BM-OBJ_BM_PACKAGE_01", options.DefaultMapId);
        Check(
            "quest.progress_ignored_when_inactive",
            inactiveProgress.Count == 0,
            inactiveProgress.Count.ToString());

        var questCompleted = quests.TurnIn(questActor, "P00-01");
        Check(
            "quest.completed",
            questCompleted.State?.State == QuestStates.Completed,
            questCompleted.State?.State);

        var reAccept = quests.Accept(questActor, "P00-01");
        Check(
            "quest.invalid_transition",
            reAccept.Failure?.Code == QuestErrorCodes.InvalidTransition,
            reAccept.Failure?.Code);

        var unknownQuest = quests.GetState(questActor.CharacterId, "P99-99");
        Check(
            "quest.unknown_quest",
            unknownQuest.Failure?.Code == QuestErrorCodes.UnknownQuest,
            unknownQuest.Failure?.Code);

        // Q-C: the opening chain exists as a graph, but four of its quests are
        // blocked because the source does not define every field they need. A
        // blocked quest keeps its place (prerequisite/unlock edges) and can never
        // open; each gap names the field and the document that must fill it.
        var blockedDefinitions = questCatalog.QuestIds
            .Select(questId => questCatalog.TryGet(questId, out var definition) ? definition : null)
            .Where(definition => definition is { IsBlocked: true })
            .ToArray();
        Check(
            "quest.blocked_chain_named",
            blockedDefinitions
                .Select(definition => definition!.QuestId)
                .SequenceEqual(
                    new[] { "P00-02", "P00-03", "P00-04", "P00-05" }, StringComparer.Ordinal) &&
            blockedDefinitions.All(definition =>
                definition!.Blocked.Count > 0 &&
                definition.Blocked.All(step =>
                    step.MissingField.Length > 0 &&
                    (step.Source.Contains(".md", StringComparison.OrdinalIgnoreCase) ||
                     step.Source.Contains(".csv", StringComparison.OrdinalIgnoreCase)))),
            string.Join(",", blockedDefinitions.Select(definition => definition!.QuestId)));

        // The actor completed P00-01 just above, so the prerequisite is met —
        // and P00-02 still must not open.
        var chainLockedState = quests.GetState(questActor.CharacterId, "P00-02");
        var chainAccept = questAccept.Accept(
            questActor, "P00-02", "NPC_TA_VAN_KHANH", new string('c', 32));
        Check(
            "quest.blocked_never_available_and_reports_gap",
            chainLockedState.State?.State == QuestStates.Locked &&
            chainAccept.Failure?.Code == QuestAcceptErrorCodes.PrerequisiteNotMet &&
            (chainAccept.Failure.FieldErrors.Contains(
                "activation.blocked.P00_02_RIPPLES", StringComparer.Ordinal)),
            $"{chainLockedState.State?.State}/{string.Join(",", chainAccept.Failure?.FieldErrors ?? [])}");

        QuestDefinition FixtureQuest(
            string questId,
            string[] prerequisites,
            string[] unlocks,
            IReadOnlyList<QuestObjectiveDefinition>? objectives = null,
            string activation = QuestActivations.Active,
            IReadOnlyList<QuestBlockedStep>? blocked = null)
        {
            var objectiveId = "OBJ_" + questId.Replace("-", "_", StringComparison.Ordinal) + "_TALK";
            return new QuestDefinition(
                questId,
                QuestTypes.Main,
                "NPC_LYAN",
                1,
                10,
                prerequisites,
                objectives ?? [new QuestObjectiveDefinition(
                    objectiveId, QuestObjectiveTypes.Talk, ["NPC_LYAN"], 1, options.DefaultMapId)],
                QuestStepIds.FromObjectiveId(objectiveId),
                "NPC_LYAN",
                new QuestRewards([], [], "LEVEL_BAND_BASE"),
                unlocks,
                activation,
                blocked);
        }

        bool ValidatorRejects(WorldRecordCatalog records, params QuestDefinition[] definitions)
        {
            var catalog = definitions.ToDictionary(
                definition => definition.QuestId, StringComparer.Ordinal);
            try
            {
                QuestCatalogValidator.Validate(new QuestCatalog(catalog), records, npcAnchors);
                return false;
            }
            catch (InvalidOperationException)
            {
                return true;
            }
        }

        var shippedRecords = services.GetRequiredService<WorldRecordCatalog>();
        var shippedDefinitions = questCatalog.QuestIds
            .Select(questId => questCatalog.TryGet(questId, out var definition) ? definition : null)
            .Where(definition => definition is not null)
            .Select(definition => definition!)
            .ToArray();
        Check(
            "quest.validator_accepts_the_shipped_chain",
            !ValidatorRejects(shippedRecords, shippedDefinitions),
            "shipped catalog rejected");
        Check(
            "quest.validator_rejects_cycle",
            ValidatorRejects(
                shippedRecords,
                FixtureQuest("Q01-01", ["Q01-02"], ["Q01-02"]),
                FixtureQuest("Q01-02", ["Q01-01"], ["Q01-01"])),
            "cycle accepted");
        Check(
            "quest.validator_rejects_dangling_prerequisite",
            ValidatorRejects(shippedRecords, FixtureQuest("Q01-01", ["Q01-99"], [])),
            "dangling prerequisite accepted");
        Check(
            "quest.validator_rejects_unlock_without_prerequisite",
            ValidatorRejects(
                shippedRecords,
                FixtureQuest("Q01-01", [], ["Q01-02"]),
                FixtureQuest("Q01-02", [], ["Q01-01"])),
            "one-sided unlock accepted");
        Check(
            "quest.validator_rejects_dangling_kill_target",
            ValidatorRejects(
                shippedRecords,
                FixtureQuest(
                    "Q01-01",
                    [],
                    [],
                    [new QuestObjectiveDefinition(
                        "OBJ_Q01_01_KILL",
                        QuestObjectiveTypes.Kill,
                        ["MAN-BM-NO_SUCH_SPAWN"],
                        1,
                        options.DefaultMapId)])),
            "dangling KILL target accepted");
        Check(
            "quest.validator_rejects_blocked_without_gap",
            ValidatorRejects(
                shippedRecords,
                FixtureQuest("Q01-01", [], [], activation: QuestActivations.Blocked)),
            "blocked quest without a named gap accepted");

        // Q-C2: a narrative node is only visible when the character's own quest
        // state matches its condition, and entering it is the only thing that can
        // set a flag or progress a talk objective. Only a text key leaves the
        // server; the server never composes prose.
        var narrative = services.GetRequiredService<NarrativeService>();
        var narrativeCatalog = services.GetRequiredService<NarrativeNodeCatalog>();
        var narrativeActor = NewPlayer("CHR_SELFCHECK_NARRATIVE");
        var narrativeOffer = narrative.Offer(narrativeActor, "P00-01");
        var clueBeforeActive = narrative.Enter(
            narrativeActor, "P00-01", "NPC_LYAN", "DLG_P00_01_CLUE");
        var wrongSpeaker = narrative.Enter(
            narrativeActor, "P00-01", "NPC_TA_VAN_KHANH", "DLG_P00_01_OFFER");
        var enteredOffer = narrative.Enter(
            narrativeActor, "P00-01", "NPC_LYAN", "DLG_P00_01_OFFER");
        Check(
            "narrative.reveal_gate_follows_quest_state",
            narrative.PartyPolicy == PartyPolicies.SoloOnly &&
            narrativeOffer is { Entered: true, Node.NodeId: "DLG_P00_01_OFFER" } &&
            narrativeOffer.Node.TextKey == "DLG_P00_01_OFFER_TEXT" &&
            clueBeforeActive.ErrorCode == NarrativeErrorCodes.NotRevealed &&
            wrongSpeaker.ErrorCode == NarrativeErrorCodes.WrongSpeaker &&
            enteredOffer is { Entered: true, NextNodeId: "DLG_P00_01_CLUE" },
            $"{narrativeOffer.Node?.NodeId}/{clueBeforeActive.ErrorCode}/{enteredOffer.NextNodeId}");

        Check(
            "narrative.catalog_choices_and_flags",
            narrativeCatalog.Count == 229 &&
            narrativeCatalog.Flags.SetEquals(new[] { "C3_05_COUNCIL_ONLY", "C3_05_PUBLISHED" }) &&
            narrativeCatalog.TryGet("DLG_C3_05_CHOICE", out var choiceNode) &&
            choiceNode.Choices.Count == 2 &&
            choiceNode.Choices.Select(choice => choice.Flag).SequenceEqual(
                new[] { "C3_05_PUBLISHED", "C3_05_COUNCIL_ONLY" }, StringComparer.Ordinal),
            $"nodes={narrativeCatalog.Count}");

        var flagStore = new NarrativeFlagStore();
        for (var flagIndex = 0; flagIndex < NarrativeFlagStore.Capacity + 4; flagIndex++)
        {
            flagStore.Set("CHR_SELFCHECK_FLAGS", $"FLAG_{flagIndex}");
        }

        Check(
            "narrative.flags_are_bounded",
            flagStore.For("CHR_SELFCHECK_FLAGS").Count == NarrativeFlagStore.Capacity,
            $"flags={flagStore.For("CHR_SELFCHECK_FLAGS").Count}");

        // Q-D: the level transaction is real (thresholds from the shipped 100-row
        // table, multi-level, capped) while the quest XP amount has no source yet,
        // so the shipped rule resolves nothing and the receipt stays applied:false.
        var xpTable = services.GetRequiredService<LevelProgressionTable>();
        var scriptedXp = new ExperienceService(xpTable, new FixedQuestXpRule(400));
        var xpActor = NewPlayer("CHR_SELFCHECK_XP");
        var xpApplied = scriptedXp.TryApply(
            xpActor, new QuestXpRequest("TEST_RULE", 1, false), out var xpGrant, out _);
        var hugeXp = new ExperienceService(xpTable, new FixedQuestXpRule(50_000_000));
        var cappedActor = NewPlayer("CHR_SELFCHECK_XP_CAP");
        hugeXp.TryApply(cappedActor, new QuestXpRequest("TEST_RULE", 1, false), out _, out _);
        var unresolved = new ExperienceService(xpTable, new UnresolvedQuestXpRules())
            .TryApply(
                xpActor, new QuestXpRequest("LEVEL_BAND_BASE", 1, false), out _, out var unresolvedRule);
        Check(
            "xp.transaction_levels_and_caps",
            xpApplied && xpTable.At(1).XpToNext == 175 &&
            xpActor is { Level: 2, TotalXp: 400 } &&
            xpActor.UnspentPoints == xpTable.At(2).AllocatablePointsTotal &&
            xpGrant is { LevelsGained: 1 } &&
            cappedActor.Level == xpTable.MaxLevel &&
            cappedActor.UnspentPoints == xpTable.At(cappedActor.Level).AllocatablePointsTotal &&
            !unresolved && unresolvedRule == "LEVEL_BAND_BASE" && xpActor.TotalXp == 400,
            $"level={xpActor.Level} cap={cappedActor.Level} rule={unresolvedRule}");

        // Q-E: a death grants at most once, a roll-only bundle grants nothing,
        // and a new life of the same entity is a new death.
        var grantService = new LootGrantService(
            services.GetRequiredService<IInventoryService>(), new LootGrantLedger());
        var grantActor = NewPlayer("CHR_SELFCHECK_LOOT");
        var rollOnly = grantService.Grant(
            grantActor, new string('d', 32), 1, grantEnabled: false,
            "COIN_BAND_MISSING", [new LootGrantItem("POT-HP-01", 1)]);
        var grantedDeath = new string('e', 32);
        var grantedOnce = grantService.Grant(
            grantActor, grantedDeath, 1, grantEnabled: true, null,
            [new LootGrantItem("POT-HP-01", 2)]);
        var grantedReplay = grantService.Grant(
            grantActor, grantedDeath, 1, grantEnabled: true, null,
            [new LootGrantItem("POT-HP-01", 2)]);
        var secondLife = grantService.Grant(
            grantActor, grantedDeath, 2, grantEnabled: true, null,
            [new LootGrantItem("POT-HP-01", 1)]);
        Check(
            "loot.grant_once_per_death_and_off_by_source",
            !rollOnly.Granted && rollOnly.BlockedReason == "COIN_BAND_MISSING" &&
            grantedOnce is { Granted: true, Replayed: false } &&
            grantedReplay is { Granted: true, Replayed: true } &&
            secondLife is { Granted: true, Replayed: false, LifeId: 2 },
            $"{rollOnly.BlockedReason}/{grantedReplay.Replayed}/{secondLife.LifeId}");

        Check(
            "npc.registry",
            npcAnchors.Count > 0 &&
            npcAnchors.TryResolve("NPC_LYAN", options.DefaultMapId, out var lyanAnchor) &&
            lyanAnchor.X == 42 &&
            lyanAnchor.Y == 0,
            $"count={npcAnchors.Count}");

        var worldEntities = services.GetRequiredService<WorldEntityRegistry>();
        Check("world.registry", worldEntities.Count == 44, $"count={worldEntities.Count}");

        var npcEntity = worldEntities.TryGet("ENT_MAN_BM_NPC_LYAN", out var foundNpc)
            ? foundNpc
            : null;
        Check(
            "world.npc_entity",
            npcEntity is { Kind: WorldEntityKinds.Npc, State: WorldEntityStates.Active } &&
            npcEntity.X == 42 &&
            npcEntity.Y == 0,
            npcEntity?.Kind);

        var mobEntity = worldEntities.TryGet("ENT_MAN_BM_SPAWN_BM_01", out var foundMob)
            ? foundMob
            : null;
        Check(
            "world.mob_entity",
            mobEntity is
            {
                Kind: WorldEntityKinds.Mob,
                State: WorldEntityStates.Alive,
                Quantity: 1,
                RespawnSeconds: 0,
                GroupId: "MAN-BM-SPAWN_BM_01",
                MemberIndex: 1,
                GroupRespawnSeconds: 18
            } &&
            mobEntity.X == 84,
            mobEntity?.Kind);

        var worldCatalog = services.GetRequiredService<WorldEntityCatalog>();
        var manualClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 0, 0, 0, TimeSpan.Zero));
        var manualWorld = new WorldEntityRegistry(worldCatalog, manualClock);

        Check("world.despawn_unknown", !manualWorld.Despawn("ENT_MISSING"));

        var despawned = manualWorld.Despawn("ENT_MAN_BM_SPAWN_BM_01") &&
                        manualWorld.TryGet("ENT_MAN_BM_SPAWN_BM_01", out var deadMob) &&
                        deadMob.State == WorldEntityStates.Dead &&
                        deadMob.Revision == 2;
        Check("world.despawn_mob", despawned);

        var groupMembersCleared =
            manualWorld.Despawn("ENT_MAN_BM_SPAWN_BM_01_M2") &&
            manualWorld.Despawn("ENT_MAN_BM_SPAWN_BM_01_M3");
        Check("world.group_cleared", groupMembersCleared);

        var beforeRespawn = manualWorld.Update();
        Check(
            "world.respawn_wait",
            beforeRespawn == 0 &&
            manualWorld.TryGet("ENT_MAN_BM_SPAWN_BM_01", out var waitingMob) &&
            waitingMob.State == WorldEntityStates.Dead,
            $"respawned={beforeRespawn}");

        var groupRespawnService = new MobSpawnGroupService(manualWorld, manualClock);
        var earlyGroupRespawn = groupRespawnService.Tick();
        manualClock.Advance(TimeSpan.FromSeconds(18));
        var individualMobRespawn = manualWorld.Update();
        var respawned = groupRespawnService.Tick();
        manualWorld.TryGet("ENT_MAN_BM_SPAWN_BM_01_M2", out var revivedMember2);
        Check(
            "world.respawn",
            earlyGroupRespawn == 0 &&
            individualMobRespawn == 0 &&
            respawned == 3 &&
            manualWorld.TryGet("ENT_MAN_BM_SPAWN_BM_01", out var revivedMob) &&
            revivedMob.State == WorldEntityStates.Alive &&
            revivedMob.Revision == 3 &&
            revivedMember2.LifeId == 2,
            $"individual={individualMobRespawn} group={respawned}");

        Check("world.despawn_npc_rejected", !manualWorld.Despawn("ENT_MAN_BM_NPC_LYAN"));

        var nodeCleared = manualWorld.Despawn("ENT_MAN_BM_NODE_BM_ORE_01") &&
                          manualWorld.TryGet("ENT_MAN_BM_NODE_BM_ORE_01", out var node) &&
                          node.State == WorldEntityStates.Depleted;
        Check("world.node_lifecycle", nodeCleared);

        var startNpcOk = questCatalog.TryGet("P00-01", out var p0001) &&
                         string.Equals(p0001.StartNpcId, "NPC_LYAN", StringComparison.Ordinal);
        Check("quest.start_npc", startNpcOk, p0001?.StartNpcId);

        var accepter = NewPlayer("CHR_SELFCHECK_ACCEPT");
        accepter.X = 42;
        accepter.Y = 0;
        var accepted = questAccept.Accept(
            accepter, "P00-01", "NPC_LYAN", new string('a', 32));
        Check(
            "quest_accept.success",
            accepted.Accepted &&
            accepted.State?.State == QuestStates.Active &&
            accepted.State.Revision == 2,
            accepted.Failure?.Code ?? $"state={accepted.State?.State}");

        var replayed = questAccept.Accept(
            accepter, "P00-01", "NPC_LYAN", new string('a', 32));
        Check(
            "quest_accept.replay",
            replayed.Accepted && replayed.State?.Revision == 2,
            replayed.Failure?.Code);

        var keyConflict = questAccept.Accept(
            accepter, "P00-01", "NPC_TA_VAN_KHANH", new string('a', 32));
        Check(
            "quest_accept.idempotency_conflict",
            keyConflict.Failure?.Code == QuestAcceptErrorCodes.IdempotencyConflict,
            keyConflict.Failure?.Code);

        var secondAccept = questAccept.Accept(
            accepter, "P00-01", "NPC_LYAN", new string('b', 32));
        Check(
            "quest_accept.invalid_transition",
            secondAccept.Failure?.Code == QuestErrorCodes.InvalidTransition,
            secondAccept.Failure?.Code);

        var farActor = NewPlayer("CHR_SELFCHECK_ACCEPT_FAR");
        var tooFar = questAccept.Accept(
            farActor, "P00-01", "NPC_LYAN", new string('c', 32));
        Check(
            "quest_accept.out_of_range",
            tooFar.Failure?.Code == QuestAcceptErrorCodes.OutOfRange && tooFar.Failure.Retryable,
            tooFar.Failure?.Code);

        var wrongNpc = questAccept.Accept(
            NewPlayer("CHR_SELFCHECK_ACCEPT_NPC"),
            "P00-01", "NPC_TA_VAN_KHANH", new string('d', 32));
        Check(
            "quest_accept.npc_mismatch",
            wrongNpc.Failure?.Code == QuestAcceptErrorCodes.NpcMismatch,
            wrongNpc.Failure?.Code);

        var highLevel = NewPlayer("CHR_SELFCHECK_ACCEPT_LEVEL");
        highLevel.X = 42;
        highLevel.Level = 11;
        var levelGate = questAccept.Accept(
            highLevel, "P00-01", "NPC_LYAN", new string('e', 32));
        Check(
            "quest_accept.level_band",
            levelGate.Failure?.Code == QuestAcceptErrorCodes.PrerequisiteNotMet,
            levelGate.Failure?.Code);

        var missingQuest = questAccept.Accept(
            NewPlayer("CHR_SELFCHECK_ACCEPT_UNKNOWN"),
            "P99-99", "NPC_LYAN", new string('f', 32));
        Check(
            "quest_accept.unknown_quest",
            missingQuest.Failure?.Code == QuestErrorCodes.QuestNotFound,
            missingQuest.Failure?.Code);

        MapPolygon Rect(double x1, double y1, double x2, double y2) =>
            new("OVERWORLD",
            [
                new TopologyPoint(x1, y1),
                new TopologyPoint(x2, y1),
                new TopologyPoint(x2, y2),
                new TopologyPoint(x1, y2)
            ]);

        maps.TryResolve(options.DefaultMapId, out var topologyBounds);
        var reviewedTopology = new MapTopologyBundle
        {
            MapId = options.DefaultMapId,
            LayoutVersion = 1,
            BundleVersion = 2,
            ReviewState = TopologyReviewStates.Reviewed,
            IsReviewed = true,
            Bounds = topologyBounds,
            FloorIds = ["OVERWORLD"],
            WalkablePolygons = [Rect(30, -10, 60, 10)],
            BlockedPolygons = [Rect(45, -10, 46, 10), Rect(52, 2, 54, 4)],
            Placements = [new TopologyPlacement(
                "MAN-BM-NPC_LYAN", "NPC_LYAN", "OVERWORLD", 42, 0)]
        };
        var geometry = new WorldGeometryService(
            new WorldGeometryCatalog([reviewedTopology]));

        var clearLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 35, 0, 42, 0);
        Check("los.clear", clearLine.Status == LineOfSightStatus.Allowed, clearLine.Reason);

        var wallLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 50, 0, 42, 0);
        Check("los.wall", wallLine.Status == LineOfSightStatus.Blocked, wallLine.Reason);

        var endpointInWall = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 45.5, 0, 42, 0);
        Check(
            "los.endpoint_in_wall",
            endpointInWall.Status == LineOfSightStatus.Blocked,
            endpointInWall.Reason);

        var holeLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 50, 3, 56, 3);
        Check("los.hole", holeLine.Status == LineOfSightStatus.Blocked, holeLine.Reason);

        var cornerLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 50, 4, 58, 4);
        Check(
            "los.corner_touch",
            cornerLine.Status == LineOfSightStatus.Blocked,
            cornerLine.Reason);

        var sweepClear = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 35, 0, 38, 0, 0.6);
        Check("sweep.clear", sweepClear.Status == LineOfSightStatus.Allowed, sweepClear.Reason);

        var sweepWall = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 46.5, 0, 42, 0, 0.6);
        Check("sweep.wall", sweepWall.Status == LineOfSightStatus.Blocked, sweepWall.Reason);

        var sweepBigStep = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 35, 0, 50, 0, 0.6);
        Check(
            "sweep.big_step",
            sweepBigStep.Status == LineOfSightStatus.Blocked,
            sweepBigStep.Reason);

        var sweepHole = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 50, 3, 56, 3, 0.6);
        Check("sweep.hole", sweepHole.Status == LineOfSightStatus.Blocked, sweepHole.Reason);

        var sweepCorner = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 50, 4, 58, 4, 0.6);
        Check(
            "sweep.corner_touch",
            sweepCorner.Status == LineOfSightStatus.Blocked,
            sweepCorner.Reason);

        var sweepFloor = geometry.CheckWalkSegment(
            options.DefaultMapId, "UNDERGROUND", 35, 0, 38, 0, 0.6);
        Check("sweep.floor", sweepFloor.Status == LineOfSightStatus.Blocked, sweepFloor.Reason);

        var sweepNonfiniteRadius = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 35, 0, 38, 0, double.NaN);
        Check(
            "sweep.nonfinite_radius",
            sweepNonfiniteRadius.Status == LineOfSightStatus.Blocked,
            sweepNonfiniteRadius.Reason);

        var sweepFootprint = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 50, 4.5, 58, 4.5, 0.6);
        Check(
            "sweep.footprint_blocked",
            sweepFootprint.Status == LineOfSightStatus.Blocked &&
            sweepFootprint.Reason == "footprint",
            sweepFootprint.Reason);

        var sweepNarrow = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 50, 4.5, 58, 4.5, 0.1);
        Check(
            "sweep.footprint_small_allowed",
            sweepNarrow.Status == LineOfSightStatus.Allowed,
            sweepNarrow.Reason);

        var floorLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "UNDERGROUND", 35, 0, 42, 0);
        Check("los.floor", floorLine.Status == LineOfSightStatus.Blocked, floorLine.Reason);

        var nonfiniteLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", double.NaN, 0, 42, 0);
        Check(
            "los.nonfinite",
            nonfiniteLine.Status == LineOfSightStatus.Blocked,
            nonfiniteLine.Reason);

        var outsideLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 20, 0, 42, 0);
        Check(
            "los.outside_walkable",
            outsideLine.Status == LineOfSightStatus.Blocked,
            outsideLine.Reason);

        var shippedGeometry = services.GetRequiredService<IWorldGeometryService>();
        var notEnforced = shippedGeometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 35, 0, 42, 0);
        Check(
            "los.not_enforced_without_reviewed_bundle",
            notEnforced.Status == LineOfSightStatus.NotEnforced,
            notEnforced.Reason?.ToString());

        WorldEntityInstance MakeFixtureMob(
            string entityId, double x, double y, string templateId = "MOB_CARPLING")
        {
            var mob = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = "MAN-TEST-" + entityId,
                Kind = WorldEntityKinds.Mob,
                TemplateIds = new[] { templateId },
                MapId = options.DefaultMapId,
                FloorId = "OVERWORLD",
                X = x,
                Y = y,
                Quantity = 1,
                RespawnSeconds = 18
            };
            mob.Initialize();
            return mob;
        }

        var mobClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 1, 0, 0, TimeSpan.Zero));
        var mobOptions = new MobBehaviorOptions
        {
            AggroRadiusWu = 6,
            LeashRadiusWu = 12,
            AttackRangeWu = 1.2,
            AttackCooldownSeconds = 2,
            MoveSpeedWuPerSecond = 2,
            TelegraphSeconds = 0.45,
            RecoverySeconds = 0.5
        };
        MobAttackService NewMobAttacks(WorldEntityRegistry registry, CombatDamageFeature feature) =>
            new(registry, feature, mobOptions, new GuardDefenseService(
                new GuardWindowStore(), feature, new CombatEventStore(new CombatEventStreamOptions())),
                new PlayerLifeLedger());
        MobLifecycleEvent Impact(string entityId, string targetCharacterId) =>
            new(entityId, MobBehaviorStates.Telegraph, MobBehaviorStates.Attack,
                mobClock.UtcNow, targetCharacterId);
        int ImpactCount(IReadOnlyList<MobLifecycleEvent> lifecycleEvents) =>
            lifecycleEvents.Count(lifecycle =>
                lifecycle.ToState == MobBehaviorStates.Attack);

        var mobRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeFixtureMob("ENT_SELFCHECK_MOB", 43, 0)]),
            mobClock);
        var mobAi = new MobLifecycleService(mobRegistry, geometry, mobOptions, mobClock);
        var mobAttacks = NewMobAttacks(mobRegistry, enabledCombat);
        var prey = NewPlayer("CHR_SELFCHECK_PREY");
        prey.X = 44;
        prey.Y = 0;

        var aggroTick = mobAi.Tick([prey]);
        Check(
            "mob.aggro",
            aggroTick.Any(lifecycle =>
                lifecycle.FromState == MobBehaviorStates.Idle &&
                lifecycle.ToState == MobBehaviorStates.Aggro),
            string.Join(",", aggroTick.Select(lifecycle => lifecycle.ToState)));

        // One acquisition edge per tick: AGGRO on the first tick, then CHASE and
        // the telegraph it walks into. Impact therefore lands 0.45s after the
        // telegraph opens, never on the tick that opened it.
        mobClock.Advance(TimeSpan.FromSeconds(0.05));
        var openTick = mobAi.Tick([prey]);
        Check(
            "mob.telegraph_opens",
            mobAi.GetState("ENT_SELFCHECK_MOB") == MobBehaviorStates.Telegraph &&
            openTick.Any(lifecycle =>
                lifecycle.FromState == MobBehaviorStates.Aggro &&
                lifecycle.ToState == MobBehaviorStates.Chase) &&
            openTick.Any(lifecycle =>
                lifecycle.FromState == MobBehaviorStates.Chase &&
                lifecycle.ToState == MobBehaviorStates.Telegraph) &&
            ImpactCount(openTick) == 0,
            mobAi.GetState("ENT_SELFCHECK_MOB"));

        mobClock.Advance(TimeSpan.FromSeconds(0.30));
        var holdingTick = mobAi.Tick([prey]);
        Check(
            "mob.telegraph_holds",
            mobAi.GetState("ENT_SELFCHECK_MOB") == MobBehaviorStates.Telegraph &&
            ImpactCount(holdingTick) == 0,
            mobAi.GetState("ENT_SELFCHECK_MOB"));

        mobClock.Advance(TimeSpan.FromSeconds(0.30));
        var attackTick = mobAi.Tick([prey]);
        var impactOrder = attackTick
            .Where(lifecycle => lifecycle.FromState == MobBehaviorStates.Telegraph ||
                                lifecycle.ToState == MobBehaviorStates.Recover)
            .Select(lifecycle => $"{lifecycle.FromState}>{lifecycle.ToState}")
            .ToArray();
        Check(
            "mob.attack",
            mobAi.GetState("ENT_SELFCHECK_MOB") == MobBehaviorStates.Recover &&
            impactOrder.SequenceEqual(
                new[] { "TELEGRAPH>ATTACK", "ATTACK>RECOVER" }, StringComparer.Ordinal),
            string.Join(",", impactOrder));

        var firstImpact = mobAttacks.ApplyImpacts(attackTick, [prey], mobClock.Tick);
        Check(
            "mob.damage_lands",
            firstImpact.Count == 1 &&
            firstImpact[0] is { Applied: true, AttackId: "BITE", Damage: 10, HpBefore: 100, HpAfter: 90 } &&
            prey.Hp == 90,
            firstImpact.Count == 1 ? firstImpact[0].ToString() : "no resolution");

        // Art Bible §12 CARPLING attack 15 x BITE 0,8 = 12 raw; Rules §2 floor
        // (12 * 100 / (100 + armor 10)) = 10.
        Check(
            "mob.damage_revision_bumps",
            prey.Revision == 2,
            $"revision={prey.Revision}");

        mobClock.Advance(TimeSpan.FromSeconds(0.30));
        var recoveryTick = mobAi.Tick([prey]);
        Check(
            "mob.recovery_holds",
            mobAi.GetState("ENT_SELFCHECK_MOB") == MobBehaviorStates.Recover &&
            recoveryTick.All(lifecycle => lifecycle.ToState != MobBehaviorStates.Telegraph),
            mobAi.GetState("ENT_SELFCHECK_MOB"));

        mobClock.Advance(TimeSpan.FromSeconds(0.30));
        var recoverTick = mobAi.Tick([prey]);
        Check(
            "mob.recovery_ends_to_chase",
            mobAi.GetState("ENT_SELFCHECK_MOB") == MobBehaviorStates.Chase &&
            recoverTick.Any(lifecycle =>
                lifecycle.FromState == MobBehaviorStates.Recover &&
                lifecycle.ToState == MobBehaviorStates.Chase),
            mobAi.GetState("ENT_SELFCHECK_MOB"));

        var cooldownTick = mobAi.Tick([prey]);
        Check(
            "mob.attack_cooldown",
            ImpactCount(cooldownTick) == 0 &&
            cooldownTick.All(lifecycle => lifecycle.ToState != MobBehaviorStates.Telegraph),
            "impact fired during cooldown");

        mobClock.Advance(TimeSpan.FromSeconds(1.50));
        var readyTick = mobAi.Tick([prey]);
        Check(
            "mob.telegraph_repeats_after_cooldown",
            mobAi.GetState("ENT_SELFCHECK_MOB") == MobBehaviorStates.Telegraph &&
            readyTick.Any(lifecycle =>
                lifecycle.FromState == MobBehaviorStates.Chase &&
                lifecycle.ToState == MobBehaviorStates.Telegraph),
            mobAi.GetState("ENT_SELFCHECK_MOB"));

        mobClock.Advance(TimeSpan.FromSeconds(0.60));
        var secondAttackTick = mobAi.Tick([prey]);
        var secondImpact = mobAttacks.ApplyImpacts(secondAttackTick, [prey], mobClock.Tick);
        Check(
            "mob.damage_second_impact",
            secondImpact.Count == 1 && secondImpact[0].Damage == 10 && prey.Hp == 80,
            $"hp={prey.Hp}");

        var whiffClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 5, 0, 0, TimeSpan.Zero));
        var whiffRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeFixtureMob("ENT_SELFCHECK_WHIFF_MOB", 43, 0)]),
            whiffClock);
        var whiffAi = new MobLifecycleService(whiffRegistry, geometry, mobOptions, whiffClock);
        var whiffAttacks = NewMobAttacks(whiffRegistry, enabledCombat);
        var runner = NewPlayer("CHR_SELFCHECK_RUNNER");
        runner.X = 44;
        runner.Y = 0;
        whiffAi.Tick([runner]);
        whiffAi.Tick([runner]);
        // The telegraph only opens while the target is in range; the player
        // escapes during the read window, and the mob holds its ground.
        runner.X = 44.6;
        whiffClock.Advance(TimeSpan.FromSeconds(0.60));
        var whiffTick = whiffAi.Tick([runner]);
        var whiffImpact = whiffAttacks.ApplyImpacts(whiffTick, [runner], whiffClock.Tick);
        Check(
            "mob.impact_whiffs_out_of_range",
            ImpactCount(whiffTick) == 1 &&
            whiffImpact.Count == 1 &&
            !whiffImpact[0].Applied &&
            whiffImpact[0].BlockedReason == MobAttackBlockedReasons.OutOfRangeAtImpact &&
            runner.Hp == 100,
            whiffImpact.Count == 1 ? whiffImpact[0].BlockedReason : "no resolution");

        var telegraphCancelClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 6, 0, 0, TimeSpan.Zero));
        var telegraphCancelRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeFixtureMob("ENT_SELFCHECK_CANCEL_MOB", 43, 0)]),
            telegraphCancelClock);
        var telegraphCancelAi = new MobLifecycleService(
            telegraphCancelRegistry, geometry, mobOptions, telegraphCancelClock);
        var telegraphCancelAttacks = NewMobAttacks(telegraphCancelRegistry, enabledCombat);
        var bait = NewPlayer("CHR_SELFCHECK_BAIT");
        bait.X = 44;
        bait.Y = 0;
        telegraphCancelAi.Tick([bait]);
        telegraphCancelClock.Advance(TimeSpan.FromSeconds(0.05));
        telegraphCancelAi.Tick([bait]);
        // Past the impact deadline, but with no target: the pending impact is
        // cancelled, so the mob never swings.
        telegraphCancelClock.Advance(TimeSpan.FromSeconds(0.60));
        var telegraphCancelTick = telegraphCancelAi.Tick([]);
        telegraphCancelClock.Advance(TimeSpan.FromSeconds(1));
        var afterTelegraphCancelTick = telegraphCancelAi.Tick([]);
        Check(
            "mob.telegraph_cancel_on_lost_target",
            telegraphCancelAi.GetState("ENT_SELFCHECK_CANCEL_MOB") == MobBehaviorStates.Idle &&
            telegraphCancelTick.Any(lifecycle =>
                lifecycle.FromState == MobBehaviorStates.Telegraph &&
                lifecycle.ToState == MobBehaviorStates.Return) &&
            ImpactCount(telegraphCancelTick) == 0 &&
            ImpactCount(afterTelegraphCancelTick) == 0 &&
            telegraphCancelAttacks.ApplyImpacts(afterTelegraphCancelTick, [], telegraphCancelClock.Tick).Count == 0 &&
            bait.Hp == 100,
            telegraphCancelAi.GetState("ENT_SELFCHECK_CANCEL_MOB"));

        var gateOffAttacks = NewMobAttacks(mobRegistry, combatDamage);
        var gateOffImpact = gateOffAttacks.ApplyImpacts(
            [Impact("ENT_SELFCHECK_MOB", prey.CharacterId)], [prey], mobClock.Tick);
        Check(
            "mob.damage_gate_off",
            gateOffImpact.Count == 1 &&
            !gateOffImpact[0].Applied &&
            gateOffImpact[0].BlockedReason == MobAttackBlockedReasons.GateOff &&
            prey.Hp == 80,
            gateOffImpact.Count == 1 ? gateOffImpact[0].BlockedReason : "no resolution");

        var oracleRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([],
            [
                MakeFixtureMob("ENT_SELFCHECK_WATERROOT", 43, 0, "MOB_WATERROOT"),
                MakeFixtureMob("ENT_SELFCHECK_STALKER_ELITE", 43, 0, "MOB_SHORE_STALKER_ELITE"),
                MakeFixtureMob("ENT_SELFCHECK_MOSS_BEAST", 43, 0, "MOB_MOSS_BEAST")
            ]),
            mobClock);
        var oracleAttacks = NewMobAttacks(oracleRegistry, enabledCombat);
        var waterrootPrey = NewPlayer("CHR_SELFCHECK_WATERROOT_PREY");
        waterrootPrey.X = 43.5;
        var elitePrey = NewPlayer("CHR_SELFCHECK_ELITE_PREY");
        elitePrey.X = 43.5;
        var unknownPrey = NewPlayer("CHR_SELFCHECK_UNKNOWN_PREY");
        unknownPrey.X = 43.5;
        var oracleImpacts = oracleAttacks.ApplyImpacts(
            [
                Impact("ENT_SELFCHECK_WATERROOT", waterrootPrey.CharacterId),
                Impact("ENT_SELFCHECK_STALKER_ELITE", elitePrey.CharacterId),
                Impact("ENT_SELFCHECK_MOSS_BEAST", unknownPrey.CharacterId)
            ],
            [waterrootPrey, elitePrey, unknownPrey], mobClock.Tick);
        Check(
            "mob.damage_waterroot_basic_move",
            waterrootPrey.Hp == 82 &&
            oracleImpacts.Single(resolution =>
                resolution.EntityId == "ENT_SELFCHECK_WATERROOT") is
                { Damage: 18, AttackId: "VINE" },
            $"hp={waterrootPrey.Hp}");
        Check(
            "mob.damage_elite_scaling",
            elitePrey.Hp == 67 &&
            oracleImpacts.Single(resolution =>
                resolution.EntityId == "ENT_SELFCHECK_STALKER_ELITE") is
                { Damage: 33, AttackId: "POUNCE" },
            $"hp={elitePrey.Hp}");
        var unknownResolution = oracleImpacts.Single(resolution =>
            resolution.EntityId == "ENT_SELFCHECK_MOSS_BEAST");
        Check(
            "mob.damage_unknown_template",
            unknownPrey.Hp == 100 &&
            !unknownResolution.Applied &&
            unknownResolution.BlockedReason == MobAttackBlockedReasons.UnknownTemplate,
            $"hp={unknownPrey.Hp}");

        var downedPrey = NewPlayer("CHR_SELFCHECK_DOWNED_PREY", hp: 0);
        downedPrey.X = 44;
        downedPrey.Y = 0;
        var downedTick = mobAi.Tick([downedPrey]);
        var downedImpact = mobAttacks.ApplyImpacts(
            [Impact("ENT_SELFCHECK_MOB", downedPrey.CharacterId)], [downedPrey], mobClock.Tick);
        var downedResolution = downedImpact.Single();
        Check(
            "mob.downed_target_untouched",
            ImpactCount(downedTick) == 0 &&
            !downedResolution.Applied &&
            downedResolution.BlockedReason == MobAttackBlockedReasons.TargetDown,
            downedResolution.BlockedReason);

        var wallClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 2, 0, 0, TimeSpan.Zero));
        var wallRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeFixtureMob("ENT_SELFCHECK_WALL_MOB", 43, 0)]),
            wallClock);
        var wallAi = new MobLifecycleService(wallRegistry, geometry, mobOptions, wallClock);
        var blockedPrey = NewPlayer("CHR_SELFCHECK_BLOCKED_PREY");
        blockedPrey.X = 47.5;
        blockedPrey.Y = 0;
        wallAi.Tick([blockedPrey]);
        Check(
            "mob.los_blocks_aggro",
            wallAi.GetState("ENT_SELFCHECK_WALL_MOB") == MobBehaviorStates.Idle,
            wallAi.GetState("ENT_SELFCHECK_WALL_MOB"));

        var leashOptions = new MobBehaviorOptions
        {
            AggroRadiusWu = 20,
            LeashRadiusWu = 12,
            AttackRangeWu = 1.2,
            AttackCooldownSeconds = 2,
            MoveSpeedWuPerSecond = 2
        };
        var leashClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 3, 0, 0, TimeSpan.Zero));
        var leashRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeFixtureMob("ENT_SELFCHECK_LEASH_MOB", 32, 0)]),
            leashClock);
        var leashAi = new MobLifecycleService(
            leashRegistry, geometry, leashOptions, leashClock);
        var farPrey = NewPlayer("CHR_SELFCHECK_FAR_PREY");
        farPrey.X = 44.5;
        farPrey.Y = 0;
        leashAi.Tick([farPrey]);
        Check(
            "mob.leash_return",
            leashAi.GetState("ENT_SELFCHECK_LEASH_MOB") == MobBehaviorStates.Return,
            leashAi.GetState("ENT_SELFCHECK_LEASH_MOB"));

        var floorPrey = NewPlayer("CHR_SELFCHECK_FLOOR_PREY");
        floorPrey.X = 44;
        floorPrey.Y = 0;
        floorPrey.FloorId = "UNDERGROUND";
        var floorClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 4, 0, 0, TimeSpan.Zero));
        var floorRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeFixtureMob("ENT_SELFCHECK_FLOOR_MOB", 43, 0)]),
            floorClock);
        var floorAi = new MobLifecycleService(floorRegistry, geometry, mobOptions, floorClock);
        floorAi.Tick([floorPrey]);
        Check(
            "mob.floor_ignored",
            floorAi.GetState("ENT_SELFCHECK_FLOOR_MOB") == MobBehaviorStates.Idle,
            floorAi.GetState("ENT_SELFCHECK_FLOOR_MOB"));

        // Q-B5: the telegraph read model. A client deciding "lean back or eat it"
        // needs the committed frame, its target and its reach in ticks — the
        // state name alone is not a read window.
        var telegraphClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 30, 2, 0, 0, TimeSpan.Zero));
        var telegraphRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeFixtureMob("ENT_SELFCHECK_READ_MOB", 43, 0)]),
            telegraphClock);
        var telegraphAi = new MobLifecycleService(
            telegraphRegistry, geometry, mobOptions, telegraphClock);
        var telegraphReads = new MobTelegraphProjection(
            telegraphAi, Options.Create(mobOptions), telegraphClock);
        var readPrey = NewPlayer("CHR_SELFCHECK_READ_PREY");
        readPrey.X = 44;
        readPrey.Y = 0;
        // Two different questions: "is there anything to read about this mob"
        // and "is a swing committed right now". The acquisition states are
        // readable too, so the helpers must not be conflated.
        MobTelegraphReading? ReadEngaged() =>
            telegraphReads.Project(telegraphRegistry.All)
                .FirstOrDefault(reading => reading.State != MobBehaviorStates.Idle);
        MobTelegraphReading? ReadTelegraph() =>
            telegraphReads.Project(telegraphRegistry.All)
                .FirstOrDefault(reading => reading.State == MobBehaviorStates.Telegraph);

        Check(
            "telegraph.idle_has_nothing_to_read",
            telegraphReads.Project(telegraphRegistry.All).Count == 0,
            string.Join(",", telegraphReads.Project(telegraphRegistry.All)
                .Select(reading => reading.State)));

        MobTelegraphReading? committed = null;
        for (var step = 0; step < 12 && committed is null; step++)
        {
            telegraphAi.Tick([readPrey]);
            committed = ReadTelegraph();
            if (committed is null)
            {
                telegraphClock.Advance(TimeSpan.FromSeconds(0.05));
            }
        }

        Check(
            "telegraph.reading_carries_target_timing_and_reach",
            committed is { State: MobBehaviorStates.Telegraph, ImpactInTicks: 9, RangeWu: 1.2 } &&
            committed.AngleDegrees is null &&
            committed.LifeId > 0 &&
            committed.EntityId == "ENT_SELFCHECK_READ_MOB" &&
            committed.TargetCharacterId == readPrey.CharacterId &&
            committed.ImpactAtUtc == telegraphClock.UtcNow.AddSeconds(0.45),
            committed is null ? "never telegraphed" : $"{committed.State}/{committed.ImpactInTicks}");

        telegraphClock.Advance(TimeSpan.FromSeconds(0.1));
        var counting = ReadTelegraph();
        Check(
            "telegraph.countdown_moves_with_the_server_clock",
            counting?.ImpactInTicks == 7 && counting?.State == MobBehaviorStates.Telegraph,
            $"{counting?.ImpactInTicks}");

        // Out of *attack* range while still acquired does not un-commit the
        // swing: the impact frame still happens and only the damage check knows
        // it will whiff, so the client has to keep drawing it. 44,6 stays inside
        // the open area — the reviewed fixture's wall starts at 45, and stepping
        // the prey behind it would drop the target for line of sight instead.
        readPrey.X = 44.6;
        telegraphClock.Advance(TimeSpan.FromSeconds(0.3));
        telegraphAi.Tick([readPrey]);
        var escaped = ReadTelegraph();
        Check(
            "telegraph.stays_committed_when_the_target_leaves_range",
            escaped?.State == MobBehaviorStates.Telegraph &&
            escaped.ImpactInTicks == 1 &&
            escaped.TargetCharacterId == readPrey.CharacterId,
            $"{escaped?.State}/{escaped?.ImpactInTicks}");

        telegraphClock.Advance(TimeSpan.FromSeconds(0.05));
        telegraphAi.Tick([readPrey]);
        var recovered = ReadEngaged();
        Check(
            "telegraph_after_impact_reads_recovery_and_cooldown",
            recovered?.State == MobBehaviorStates.Recover &&
            recovered.ImpactInTicks is null &&
            recovered.RecoverInTicks == 10 &&
            recovered.NextAttackInTicks == 40,
            $"{recovered?.State}/{recovered?.RecoverInTicks}/{recovered?.NextAttackInTicks}");

        readPrey.X = 300;
        telegraphClock.Advance(TimeSpan.FromSeconds(0.55));
        telegraphAi.Tick([readPrey]);
        var dropped = telegraphReads.Project(telegraphRegistry.All);
        var droppedReading = dropped.Count > 0 ? dropped[0] : null;
        Check(
            "telegraph_lost_target_reports_no_committed_frame",
            dropped.Count == 1 &&
            droppedReading!.ImpactInTicks is null &&
            droppedReading.RecoverInTicks is null &&
            droppedReading.TargetCharacterId is null,
            $"count={dropped.Count}/{droppedReading?.State}/{droppedReading?.ImpactInTicks}");

        // ─── DEC-022: guard window, whiff buff and counter runtime ───

        var guardClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 30, 1, 0, 0, TimeSpan.Zero));
        var guardRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([],
            [
                MakeFixtureMob("ENT_SELFCHECK_GUARD_MOB", 41, 0),
                MakeFixtureMob("ENT_SELFCHECK_GUARD_MOB2", 40.9, 0.6),
                MakeFixtureMob("ENT_SELFCHECK_GUARD_MOB3", 41.1, 0.2)
            ]),
            guardClock);
        var guardWindows = new GuardWindowStore();
        var guardEvents = new CombatEventStore(new CombatEventStreamOptions
        {
            CapacityPerSession = 256,
            MaxPageSize = 256
        });
        var guardDefense = new GuardDefenseService(guardWindows, enabledCombat, guardEvents);
        var guardAttacks = new MobAttackService(
            guardRegistry, enabledCombat, mobOptions, guardDefense, new PlayerLifeLedger());
        var guardStates = new MobCombatStateStore();
        var guardEngine = new CombatTickEngine(
            guardRegistry, enabledCombat, combatSkills, guardEvents, guardStates,
            tickQuests, new FixedCombatRolls(hit: true, crit: false),
            guardWindows, geometry, NewDashes(geometry), new ServerClock());
        var guardMissEngine = new CombatTickEngine(
            guardRegistry, enabledCombat, combatSkills, guardEvents, guardStates,
            tickQuests, new FixedCombatRolls(hit: false, crit: false),
            guardWindows, geometry, NewDashes(geometry), new ServerClock());

        MobLifecycleEvent GuardImpact(string entityId, PlayerSession victim) =>
            new(entityId, MobBehaviorStates.Telegraph, MobBehaviorStates.Attack,
                guardClock.UtcNow, victim.CharacterId);
        int CountEvent(string sessionId, string type) => guardEvents
            .Read(sessionId, 0, 256).Events
            .Count(stored => stored.Type == type);
        PlayerSession NewGuardHero(string suffix, int hp = 100)
        {
            var hero = NewPlayer("CHR_SELFCHECK_GUARD_" + suffix, hp: hp);
            hero.X = 40;
            hero.Y = 0;
            return hero;
        }

        var hero1 = NewGuardHero("ONE");
        var policyCastId = new string('f', 32);
        guardEngine.Schedule(
            hero1, hero1.SessionId, policyCastId, CombatV2Actions.Skill, "SK-MK-01",
            1, 0, startTick: 0);
        var policyWindow = guardWindows.Find(hero1.CharacterId);
        Check(
            "guard.window_opens_on_accept",
            policyWindow is not null &&
            policyWindow.GuardCastId == policyCastId &&
            policyWindow is
            {
                CastStartTick: 0,
                GuardEndExclusiveTick: 8,
                WhiffEndExclusiveTick: 28,
                CounterCoefficient: 1.8,
                AttackSnapshot: 20
            } &&
            guardWindows.Count == 1,
            policyWindow is null ? "no window" : $"{policyWindow.GuardEndExclusiveTick}");

        Check(
            "guard.front_hit_inside_window",
            guardDefense.EvaluateIncoming(hero1.CharacterId, 7, 41, 0)
                is { Phase: GuardPhases.Guard, DamageReduction: 0.7, FrontHit: true, CounterEligible: true },
            guardDefense.EvaluateIncoming(hero1.CharacterId, 7, 41, 0).Phase);
        Check(
            "guard.back_hit_gets_no_reduction",
            guardDefense.EvaluateIncoming(hero1.CharacterId, 5, 39, 0)
                is { Phase: GuardPhases.Guard, DamageReduction: 0, FrontHit: false, CounterEligible: false },
            "behind hit reduced");
        Check(
            "guard.range_edge_is_inclusive",
            guardDefense.EvaluateIncoming(hero1.CharacterId, 5, 44.4, 0).FrontHit &&
            !guardDefense.EvaluateIncoming(hero1.CharacterId, 5, 44.5, 0).FrontHit,
            "4.4 WU edge");
        Check(
            "guard.angle_edge_is_inclusive",
            guardDefense.EvaluateIncoming(hero1.CharacterId, 5, 41, 1.7320508075688772).FrontHit &&
            !guardDefense.EvaluateIncoming(hero1.CharacterId, 5, 41, 1.8).FrontHit,
            "60 degree edge");
        Check(
            "guard.window_end_is_exclusive_whiff_starts",
            guardDefense.EvaluateIncoming(hero1.CharacterId, 8, 41, 0)
                is { Phase: GuardPhases.Whiff, DamageReduction: 0.2, CounterEligible: false },
            guardDefense.EvaluateIncoming(hero1.CharacterId, 8, 41, 0).Phase);

        // The guard cast itself has no impacts, so its END lands at start+2 while
        // the whiff buff still has 20 ticks to live (DEC-022 §4).
        var guardEndEvents = guardEngine.Tick(2);
        var whiffResolutions = guardAttacks.ApplyImpacts(
            [GuardImpact("ENT_SELFCHECK_GUARD_MOB2", hero1)], [hero1], 20);
        Check(
            "guard.cast_end_keeps_whiff",
            guardEndEvents.Any(stored => stored.Type == CombatEventTypesV2.End) &&
            whiffResolutions.Single() is { Applied: true, Damage: 8, GuardPhase: GuardPhases.Whiff } &&
            hero1.Hp == 92 &&
            hero1.SwordIntent == 0 &&
            CountEvent(hero1.SessionId, CombatEventTypesV2.CounterConfirmed) == 0,
            whiffResolutions.Single().Damage.ToString());

        var expiredResolutions = guardAttacks.ApplyImpacts(
            [GuardImpact("ENT_SELFCHECK_GUARD_MOB2", hero1)], [hero1], 30);
        Check(
            "guard.whiff_expires_full_damage",
            guardDefense.EvaluateIncoming(hero1.CharacterId, 28, 41, 0).Phase == GuardPhases.Expired &&
            expiredResolutions.Single() is { Damage: 10, GuardPhase: GuardPhases.Expired } &&
            hero1.Hp == 82,
            expiredResolutions.Single().Damage.ToString());

        var hero2 = NewGuardHero("TWO");
        var counterCastId = new string('e', 32);
        guardEngine.Schedule(
            hero2, hero2.SessionId, counterCastId, CombatV2Actions.Skill, "SK-MK-01",
            1, 0, startTick: 0);
        var twoHits = guardAttacks.ApplyImpacts(
            [
                GuardImpact("ENT_SELFCHECK_GUARD_MOB", hero2),
                GuardImpact("ENT_SELFCHECK_GUARD_MOB2", hero2)
            ],
            [hero2],
            tick: 5);
        var counterWindow = guardWindows.Find(hero2.CharacterId);
        Check(
            "guard.two_hits_one_confirmation_one_counter",
            twoHits.Count == 2 &&
            twoHits.All(resolution => resolution.Damage == 3) &&
            hero2.Hp == 94 &&
            counterWindow is { ConfirmationCount: 1 } &&
            hero2.SwordIntent == 2 &&
            twoHits[0].Confirmation is not null &&
            twoHits[1].Confirmation is null &&
            CountEvent(hero2.SessionId, CombatEventTypesV2.CounterConfirmed) == 1,
            $"hp={hero2.Hp} intent={hero2.SwordIntent}");
        Check(
            "guard.counter_reserved_for_next_tick",
            counterWindow is { CounterTick: 6, CounterResolved: false } &&
            counterWindow.CounterSourceEntityId == "ENT_SELFCHECK_GUARD_MOB",
            counterWindow?.CounterTick?.ToString() ?? "none");

        var counterEvents = guardEngine.Tick(6);
        var counterImpact = counterEvents.SingleOrDefault(
            stored => stored.Type == CombatEventTypesV2.Impact);
        Check(
            "guard.counter_impact_next_tick",
            counterImpact is { HitIndex: 0 } &&
            counterImpact.CastId == counterCastId &&
            counterImpact.Result is { Hit: true, Crit: false, Amount: 34, HpDamage: 34 } &&
            counterWindow is { CounterOutcome: "DAMAGE" } &&
            (guardStates.TryGet("ENT_SELFCHECK_GUARD_MOB", 1)?.Hp ?? 0) == 158 &&
            counterEvents.Count(stored => stored.Type == CombatEventTypesV2.Impact) == 1 &&
            counterImpact.TargetId == "ENT_SELFCHECK_GUARD_MOB",
            counterImpact?.Result?.Amount.ToString() ?? "no impact");
        Check(
            "guard.counter_pays_no_extra_resource_and_resolves_once",
            hero2.SwordIntent == 2 &&
            !guardEngine.Tick(6).Any(stored => stored.Type == CombatEventTypesV2.Impact) &&
            (guardStates.TryGet("ENT_SELFCHECK_GUARD_MOB", 1)?.Hp ?? 0) == 158,
            "counter resolved twice");

        var hero3 = NewGuardHero("THREE");
        var cancelCastId = new string('d', 32);
        guardEngine.Schedule(
            hero3, hero3.SessionId, cancelCastId, CombatV2Actions.Skill, "SK-MK-01",
            1, 0, startTick: 10);
        guardAttacks.ApplyImpacts(
            [GuardImpact("ENT_SELFCHECK_GUARD_MOB", hero3)], [hero3], tick: 11);
        var cancelWindow = guardWindows.Find(hero3.CharacterId);
        // The confirmed source steps out of the cone before the counter lands:
        // the counter cancels, keeps the committed cost and never retargets.
        guardRegistry.TryGet("ENT_SELFCHECK_GUARD_MOB", out var counterSource);
        counterSource.MoveTo(60, 0);
        var mpBeforeCancel = hero3.Mp;
        var intentBeforeCancel = hero3.SwordIntent;
        var cancelEvents = guardEngine.Tick(12);
        counterSource.MoveTo(41, 0);
        Check(
            "guard.counter_cancelled_keeps_cost_no_retarget",
            cancelWindow is
            {
                CounterTick: 12,
                CounterResolved: true,
                ConfirmationCount: 1,
                CounterOutcome: "OUT_OF_RANGE_OR_CONE"
            } &&
            cancelEvents.Any(stored => stored.Type == CombatEventTypesV2.Cancel) &&
            !cancelEvents.Any(stored => stored.Type == CombatEventTypesV2.Impact) &&
            hero3.Mp == mpBeforeCancel &&
            hero3.SwordIntent == intentBeforeCancel &&
            guardStates.TryGet("ENT_SELFCHECK_GUARD_MOB", 1)?.Hp == 158,
            cancelWindow?.CounterOutcome ?? "none");

        var hero5 = NewGuardHero("MISS");
        guardMissEngine.Schedule(
            hero5, hero5.SessionId, new string('b', 32), CombatV2Actions.Skill, "SK-MK-01",
            1, 0, startTick: 40);
        guardMissEngine.Tick(41);
        var missResolutions = guardAttacks.ApplyImpacts(
            [GuardImpact("ENT_SELFCHECK_GUARD_MOB", hero5)], [hero5], tick: 41);
        var missWindow = guardWindows.Find(hero5.CharacterId);
        var mobHpBeforeMiss = guardStates.TryGet("ENT_SELFCHECK_GUARD_MOB", 1)?.Hp ?? 0;
        var counterMissEvents = guardMissEngine.Tick(42);
        Check(
            "guard.counter_miss_no_refund_no_damage",
            missResolutions.Single().Confirmation is not null &&
            counterMissEvents.Any(stored => stored.Type == CombatEventTypesV2.Miss) &&
            missWindow is { CounterOutcome: "MISS" } &&
            (guardStates.TryGet("ENT_SELFCHECK_GUARD_MOB", 1)?.Hp ?? 0) == mobHpBeforeMiss &&
            hero5.Mp == 50,
            missWindow?.CounterOutcome ?? "none");

        var hero4 = NewGuardHero("DOWN", hp: 3);
        guardEngine.Schedule(
            hero4, hero4.SessionId, new string('c', 32), CombatV2Actions.Skill, "SK-MK-01",
            1, 0, startTick: 20);
        var lethalResolutions = guardAttacks.ApplyImpacts(
            [GuardImpact("ENT_SELFCHECK_GUARD_MOB", hero4)], [hero4], tick: 21);
        var downTick = guardEngine.Tick(22);
        Check(
            "guard.defender_death_clears_resource_no_confirmation",
            hero4.Hp == 0 &&
            hero4.SwordIntent == 0 &&
            lethalResolutions.Single().Damage == 3 &&
            lethalResolutions.Single().Confirmation is null &&
            guardWindows.Find(hero4.CharacterId) is null &&
            CountEvent(hero4.SessionId, CombatEventTypesV2.CounterConfirmed) == 0 &&
            lethalResolutions.Single().GuardWindowCastId == new string('c', 32) &&
            lethalResolutions.Single().DamageReduction == 0.7,
            $"hp={hero4.Hp} intent={hero4.SwordIntent}");
        // A down defender's own cast is cancelled once, and nothing of it lands.
        Check(
            "guard.down_defender_cast_cancels_once",
            downTick.Count(stored => stored.Type == CombatEventTypesV2.Cancel) == 1 &&
            downTick.Count(stored => stored.Type == CombatEventTypesV2.End) == 1 &&
            !downTick.Any(stored =>
                stored.Type is CombatEventTypesV2.Impact or CombatEventTypesV2.Death) &&
            !guardEngine.Tick(23).Any(stored =>
                stored.Type is CombatEventTypesV2.Cancel or CombatEventTypesV2.Impact) &&
            guardWindows.Find(hero4.CharacterId) is null,
            string.Join(",", downTick.Select(stored => stored.Type)));

        var hero6 = NewGuardHero("REFRESH");
        guardEngine.Schedule(
            hero6, hero6.SessionId, new string('1', 32), CombatV2Actions.Skill, "SK-MK-01",
            1, 0, startTick: 50);
        var refreshCastId = new string('2', 32);
        guardEngine.Schedule(
            hero6, hero6.SessionId, refreshCastId, CombatV2Actions.Skill, "SK-MK-01",
            2, 0, startTick: 51);
        var refreshWindow = guardWindows.Find(hero6.CharacterId);
        Check(
            "guard.refresh_replaces_window_without_stacking",
            refreshWindow is not null &&
            refreshWindow.GuardCastId == refreshCastId &&
            refreshWindow.CastStartTick == 51 &&
            guardDefense.EvaluateIncoming(hero6.CharacterId, 55, 41, 0).DamageReduction == 0.7);
        var refreshResolutions = guardAttacks.ApplyImpacts(
            [GuardImpact("ENT_SELFCHECK_GUARD_MOB", hero6)], [hero6], tick: 55);
        Check(
            "guard.refresh_confirmation_belongs_to_new_window",
            refreshResolutions.Single() is { Damage: 3 } &&
            refreshResolutions.Single().Confirmation?.GuardCastId == refreshCastId,
            refreshResolutions.Single().Confirmation?.GuardCastId ?? "none");

        var hero8 = NewGuardHero("LETHAL");
        var lethalMobId = "ENT_SELFCHECK_GUARD_MOB3";
        guardStates.ApplyDamage(lethalMobId, lifeId: 1, maxHp: 192, damage: 158, actorId: hero8.CharacterId);
        guardEngine.Schedule(
            hero8, hero8.SessionId, new string('3', 32), CombatV2Actions.Skill, "SK-MK-01",
            1, 0, startTick: 60);
        guardAttacks.ApplyImpacts(
            [GuardImpact(lethalMobId, hero8)], [hero8], tick: 61);
        var deathEvents = guardEngine.Tick(62);
        Check(
            "guard.counter_lethal_hit_death_once",
            deathEvents.Count(stored => stored.Type == CombatEventTypesV2.Death) == 1 &&
            guardRegistry.TryGet(lethalMobId, out var killedMob) &&
            killedMob.State == WorldEntityStates.Dead &&
            guardWindows.Find(hero8.CharacterId) is { ConfirmationCount: 1 },
            string.Join(",", deathEvents.Select(stored => stored.Type)));

        var hero7 = NewGuardHero("GATEOFF");
        var gateOffWindows = new GuardWindowStore();
        var gateOffDefense = new GuardDefenseService(
            gateOffWindows, combatDamage, new CombatEventStore(new CombatEventStreamOptions()));
        var gateOffEngine = new CombatTickEngine(
            guardRegistry, combatDamage, combatSkills,
            new CombatEventStore(new CombatEventStreamOptions()), new MobCombatStateStore(),
            tickQuests, new FixedCombatRolls(hit: true, crit: false),
            gateOffWindows, geometry, NewDashes(geometry), new ServerClock());
        gateOffEngine.Schedule(
            hero7, hero7.SessionId, new string('9', 32), CombatV2Actions.Skill, "SK-MK-01",
            1, 0, startTick: 70);
        Check(
            "guard.gate_off_never_opens_window",
            gateOffWindows.Count == 0 &&
            gateOffWindows.Find(hero7.CharacterId) is null &&
            gateOffDefense.EvaluateIncoming(hero7.CharacterId, 71, 41, 0)
                is { Phase: GuardPhases.None, DamageReduction: 0 },
            $"windows={gateOffWindows.Count}");

        // DEC-022 §3: a source that dies after the confirmation keeps the
        // confirmation and the resource, but the reserved counter cancels.
        var hero9 = NewGuardHero("SOURCEDOWN");
        guardEngine.Schedule(
            hero9, hero9.SessionId, new string('4', 32), CombatV2Actions.Skill, "SK-MK-01",
            1, 0, startTick: 80);
        var sourceDownResolutions = guardAttacks.ApplyImpacts(
            [GuardImpact("ENT_SELFCHECK_GUARD_MOB", hero9)], [hero9], tick: 81);
        var sourceDownWindow = guardWindows.Find(hero9.CharacterId);
        guardRegistry.Despawn("ENT_SELFCHECK_GUARD_MOB");
        var sourceDownEvents = guardEngine.Tick(82);
        Check(
            "guard.counter_source_death_after_confirm_cancels",
            sourceDownResolutions.Single().Confirmation is not null &&
            sourceDownWindow is { ConfirmationCount: 1, CounterTick: 82, CounterResolved: true } &&
            hero9.SwordIntent == 2 &&
            sourceDownEvents.Any(stored => stored.Type == CombatEventTypesV2.Cancel) &&
            !sourceDownEvents.Any(stored => stored.Type == CombatEventTypesV2.Impact) &&
            sourceDownWindow.CounterOutcome is "SOURCE_NOT_ALIVE" or "SOURCE_NEW_LIFE",
            sourceDownWindow?.CounterOutcome ?? "none");

        // DEC-022 §3: the counter re-runs line of sight at its own tick; walking
        // behind cover cancels it instead of hitting through the wall.
        var hero10 = NewPlayer("CHR_SELFCHECK_GUARD_BLOCKED");
        hero10.X = 43;
        hero10.Y = 0;
        guardEngine.Schedule(
            hero10, hero10.SessionId, new string('5', 32), CombatV2Actions.Skill, "SK-MK-01",
            -1, 0, startTick: 90);
        guardRegistry.TryGet("ENT_SELFCHECK_GUARD_MOB3", out var coveringMob);
        coveringMob.ForceRespawn();
        coveringMob.MoveTo(42.5, 0);
        var blockedHpBefore = guardStates.Ensure(
            "ENT_SELFCHECK_GUARD_MOB3", coveringMob.LifeId, 192).Hp;
        var blockedResolutions = guardAttacks.ApplyImpacts(
            [GuardImpact("ENT_SELFCHECK_GUARD_MOB3", hero10)], [hero10], tick: 91);
        hero10.X = 46.5;
        var blockedEvents = guardEngine.Tick(92);
        Check(
            "guard.counter_los_block_cancels",
            blockedResolutions.Single() is { Damage: 3, Confirmation: not null } &&
            blockedEvents.Any(stored => stored.Type == CombatEventTypesV2.Cancel) &&
            !blockedEvents.Any(stored => stored.Type == CombatEventTypesV2.Impact) &&
            guardWindows.Find(hero10.CharacterId) is { CounterOutcome: "LOS_BLOCKED" } &&
            guardStates.TryGet("ENT_SELFCHECK_GUARD_MOB3", coveringMob.LifeId)?.Hp == blockedHpBefore,
            guardWindows.Find(hero10.CharacterId)?.CounterOutcome ?? "none");

        // QREV-02: a coalesced timer callback can skip the tick a reserved
        // counter was due on. Overdue work must stay eligible, resolve exactly
        // once in deadline order, and be stamped with the tick that actually
        // processed it instead of a backdated one.
        var lateClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 30, 2, 0, 0, TimeSpan.Zero));
        var lateRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([],
            [
                MakeFixtureMob("ENT_SELFCHECK_LATE_MOB_A", 41, 0),
                MakeFixtureMob("ENT_SELFCHECK_LATE_MOB_B", 41, 0.4)
            ]),
            lateClock);
        var lateWindows = new GuardWindowStore();
        var lateEvents = new CombatEventStore(new CombatEventStreamOptions
        {
            CapacityPerSession = 256,
            MaxPageSize = 256
        });
        var lateDefense = new GuardDefenseService(lateWindows, enabledCombat, lateEvents);
        var lateAttacks = new MobAttackService(
            lateRegistry, enabledCombat, mobOptions, lateDefense, new PlayerLifeLedger());
        var lateStates = new MobCombatStateStore();
        var lateEngine = new CombatTickEngine(
            lateRegistry, enabledCombat, combatSkills, lateEvents, lateStates,
            tickQuests, new FixedCombatRolls(hit: true, crit: false),
            lateWindows, geometry, NewDashes(geometry), new ServerClock());
        var lateHeroA = NewGuardHero("LATE_A");
        var lateHeroB = NewGuardHero("LATE_B");
        lateEngine.Schedule(
            lateHeroA, lateHeroA.SessionId, new string('6', 32), CombatV2Actions.Skill,
            "SK-MK-01", 1, 0, startTick: 0);
        lateEngine.Schedule(
            lateHeroB, lateHeroB.SessionId, new string('7', 32), CombatV2Actions.Skill,
            "SK-MK-01", 1, 0, startTick: 0);
        MobLifecycleEvent LateImpact(string entityId, PlayerSession victim) =>
            new(entityId, MobBehaviorStates.Telegraph, MobBehaviorStates.Attack,
                lateClock.UtcNow, victim.CharacterId);
        lateAttacks.ApplyImpacts(
            [LateImpact("ENT_SELFCHECK_LATE_MOB_A", lateHeroA)], [lateHeroA], tick: 1);
        lateAttacks.ApplyImpacts(
            [LateImpact("ENT_SELFCHECK_LATE_MOB_B", lateHeroB)], [lateHeroB], tick: 2);
        var overdueQueue = lateWindows.PendingCounters(4);
        Check(
            "tick.counter_overdue_stays_eligible_in_deadline_order",
            overdueQueue.Count == 2 &&
            overdueQueue[0].CounterTick == 2 &&
            overdueQueue[1].CounterTick == 3 &&
            overdueQueue.All(state => !state.CounterResolved),
            $"pending={overdueQueue.Count}");

        var catchUpEvents = lateEngine.Tick(10);
        var catchUpImpacts = catchUpEvents
            .Where(stored => stored.Type == CombatEventTypesV2.Impact)
            .ToArray();
        var catchUpAgain = lateEngine.Tick(10);
        Check(
            "tick.counter_catchup_resolves_once_at_processed_tick",
            catchUpImpacts.Length == 2 &&
            catchUpImpacts[0].ActorId == lateHeroA.CharacterId &&
            catchUpImpacts[1].ActorId == lateHeroB.CharacterId &&
            catchUpImpacts.All(stored => stored.ServerTick == 10) &&
            !catchUpAgain.Any(stored => stored.Type == CombatEventTypesV2.Impact) &&
            lateWindows.PendingCounters(10).Count == 0 &&
            lateStates.TryGet("ENT_SELFCHECK_LATE_MOB_A", 1)?.Hp == 158 &&
            lateStates.TryGet("ENT_SELFCHECK_LATE_MOB_B", 1)?.Hp == 158,
            string.Join(",", catchUpImpacts.Select(stored => stored.ActorId)));

        // QREV-04: basic and MK03 impacts re-run line of sight at the impact
        // tick, on the reviewed synthetic bundle only. Production topology stays
        // SYNTHETIC_TEST_ONLY and answers NotEnforced, which is not a wall test.
        var losRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([],
            [
                MakeFixtureMob("ENT_SELFCHECK_WALL_MOB_EAST", 46.5, 0),
                MakeFixtureMob("ENT_SELFCHECK_WALL_MOB_WEST", 42.5, 0)
            ]),
            lateClock);
        var losEngine = new CombatTickEngine(
            losRegistry, enabledCombat, combatSkills,
            new CombatEventStore(new CombatEventStreamOptions
            {
                CapacityPerSession = 256,
                MaxPageSize = 256
            }),
            new MobCombatStateStore(), tickQuests,
            new FixedCombatRolls(hit: true, crit: false),
            new GuardWindowStore(), geometry, NewDashes(geometry), new ServerClock());
        var losCaster = NewPlayer("CHR_SELFCHECK_LOS_CASTER");
        losCaster.X = 43.5;
        losCaster.Y = 0;
        losEngine.Schedule(
            losCaster, losCaster.SessionId, new string('8', 32),
            CombatV2Actions.BasicAttack, null, 1, 0, startTick: 0);
        losEngine.Schedule(
            losCaster, losCaster.SessionId, new string('a', 32),
            CombatV2Actions.BasicAttack, null, -1, 0, startTick: 0);
        var losTickEvents = losEngine.Tick(3);
        var losImpacts = losTickEvents
            .Where(stored => stored.Type == CombatEventTypesV2.Impact)
            .ToArray();
        Check(
            "tick.impact_blocked_by_cover_on_reviewed_bundle",
            losImpacts.Length == 1 &&
            losImpacts[0].TargetId == "ENT_SELFCHECK_WALL_MOB_WEST" &&
            losImpacts[0].Result is { Amount: 19, HpDamage: 19 } &&
            losEngine.Tick(4).Any(stored => stored.Type == CombatEventTypesV2.End),
            string.Join(",", losImpacts.Select(stored => stored.TargetId)));

        var shippedLos = services.GetRequiredService<IWorldGeometryService>()
            .CheckLineOfSight(options.DefaultMapId, "OVERWORLD", 43.5, 0, 46.5, 0);
        Check(
            "tick.impact_not_blocked_when_geometry_unreviewed",
            shippedLos.Status == LineOfSightStatus.NotEnforced,
            shippedLos.Status.ToString());

        // QREV-05: refreshes and impacts race on the same defender. One impact is
        // one critical section, so the window that paid the reduction is always
        // the window that owns the confirmation, and no window pays twice.
        var raceRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeFixtureMob("ENT_SELFCHECK_RACE_MOB", 41, 0)]),
            lateClock);
        var raceWindows = new GuardWindowStore();
        var raceEvents = new CombatEventStore(new CombatEventStreamOptions
        {
            CapacityPerSession = 512,
            MaxPageSize = 512
        });
        var raceEngine = new CombatTickEngine(
            raceRegistry, enabledCombat, combatSkills, raceEvents, new MobCombatStateStore(),
            tickQuests, new FixedCombatRolls(hit: true, crit: false),
            raceWindows, geometry, NewDashes(geometry), new ServerClock());
        var raceAttacks = new MobAttackService(
            raceRegistry, enabledCombat, mobOptions,
            new GuardDefenseService(raceWindows, enabledCombat, raceEvents),
            new PlayerLifeLedger());
        var raceHero = NewGuardHero("RACE");
        var raceResolutions = new System.Collections.Concurrent.ConcurrentBag<MobAttackResolution>();
        RunBarrierParallel(8, index =>
        {
            if (index % 2 == 0)
            {
                raceEngine.Schedule(
                    raceHero, raceHero.SessionId, index.ToString("x32"),
                    CombatV2Actions.Skill, "SK-MK-01", 1, 0, startTick: 0);
                return;
            }

            raceResolutions.Add(raceAttacks.ApplyImpacts(
                [new MobLifecycleEvent(
                    "ENT_SELFCHECK_RACE_MOB",
                    MobBehaviorStates.Telegraph,
                    MobBehaviorStates.Attack,
                    lateClock.UtcNow,
                    raceHero.CharacterId)],
                [raceHero],
                tick: 1).Single());
        });

        var raceList = raceResolutions.ToArray();
        var raceConfirmed = raceList
            .Select(resolution => resolution.Confirmation?.GuardCastId)
            .Where(castId => castId is not null)
            .Distinct(StringComparer.Ordinal)
            .ToArray();
        var raceConfirmationEvents = raceEvents
            .Read(raceHero.SessionId, 0, 512).Events
            .Count(stored => stored.Type == CombatEventTypesV2.CounterConfirmed);
        Check(
            "guard.impact_never_mixes_two_windows",
            raceList.Length == 4 &&
            raceList.All(resolution => resolution.Applied) &&
            raceList.All(resolution =>
                resolution.DamageReduction is 0 or 0.7 &&
                resolution.Damage == (resolution.DamageReduction > 0 ? 3 : 10)) &&
            raceList.All(resolution =>
                resolution.Confirmation is null ||
                resolution.Confirmation.GuardCastId == resolution.GuardWindowCastId) &&
            raceConfirmed.Length == raceConfirmationEvents &&
            raceHero.SwordIntent == Math.Min(5, 2 * raceConfirmed.Length) &&
            raceHero.Hp == 100 - raceList.Sum(resolution => resolution.Damage),
            $"confirmed={raceConfirmed.Length} events={raceConfirmationEvents} intent={raceHero.SwordIntent}");

        // Q-B: SK-MK-02 Tầm Long is swept movement, not a claim of a completed
        // dash. On the unreviewed production bundle the sweep is NotEnforced, so
        // the dash runs its canonical 11 WU (= 5,5 m) and that is reported as
        // Complete, never as proof that walls work.
        var dashHero = NewPlayer("CHR_SELFCHECK_DASH_OPEN");
        dashHero.X = 33;
        dashHero.Y = 0;
        var dashEngine = new CombatTickEngine(
            new WorldEntityRegistry(new WorldEntityCatalog([], []), lateClock),
            enabledCombat, combatSkills,
            new CombatEventStore(new CombatEventStreamOptions { CapacityPerSession = 256, MaxPageSize = 256 }),
            new MobCombatStateStore(), tickQuests, new FixedCombatRolls(hit: true, crit: false),
            new GuardWindowStore(), tickGeometry, NewDashes(tickGeometry), new ServerClock());
        var openDashCast = new string('1', 32);
        dashEngine.Schedule(
            dashHero, dashHero.SessionId, openDashCast, CombatV2Actions.Skill, "SK-MK-02",
            1, 0, startTick: 0);
        dashEngine.Tick(6);
        var openDashPosition = dashHero.X;
        var openDashEvents = dashEngine.Tick(7);
        var openDash = dashEngine.DashLedger.Find(openDashCast);
        Check(
            "dash.unenforced_geometry_runs_full_range",
            openDashPosition == 33 &&
            openDash is { AchievedWu: 11, StopReason: DashStopReasons.Complete, AppliedTick: 7 } &&
            dashHero.X == 44 && dashHero.Y == 0 &&
            !openDashEvents.Any(stored =>
                stored.Type is CombatEventTypesV2.Impact or CombatEventTypesV2.Miss),
            openDash?.StopReason ?? "no resolution");
        var openEndEvents = dashEngine.Tick(8);
        Check(
            "dash_ends_the_tick_after_it_moved",
            !openDashEvents.Any(stored => stored.Type == CombatEventTypesV2.End) &&
            openEndEvents.Count(stored => stored.Type == CombatEventTypesV2.End) == 1 &&
            openEndEvents.Single(stored => stored.Type == CombatEventTypesV2.End).ServerTick == 8,
            string.Join(",", openEndEvents.Select(stored => $"{stored.Type}@{stored.ServerTick}")));

        // On the reviewed synthetic bundle the same dash stops in front of the
        // 45–46 wall instead of teleporting the actor through it.
        var wallDashHero = NewPlayer("CHR_SELFCHECK_DASH_WALL");
        wallDashHero.X = 43.5;
        wallDashHero.Y = 0;
        var wallDashEngine = new CombatTickEngine(
            new WorldEntityRegistry(new WorldEntityCatalog([], []), lateClock),
            enabledCombat, combatSkills,
            new CombatEventStore(new CombatEventStreamOptions { CapacityPerSession = 256, MaxPageSize = 256 }),
            new MobCombatStateStore(), tickQuests, new FixedCombatRolls(hit: true, crit: false),
            new GuardWindowStore(), geometry, NewDashes(geometry), new ServerClock());
        var wallDashCast = new string('2', 32);
        wallDashEngine.Schedule(
            wallDashHero, wallDashHero.SessionId, wallDashCast, CombatV2Actions.Skill,
            "SK-MK-02", 1, 0, startTick: 0);
        wallDashEngine.Tick(7);
        var wallDash = wallDashEngine.DashLedger.Find(wallDashCast);
        Check(
            "dash_stops_short_of_reviewed_wall",
            wallDash is not null &&
            wallDash.StopReason == DashStopReasons.BlockedByGeometry &&
            wallDash.AchievedWu > 0.2 && wallDash.AchievedWu < 1.1 &&
            wallDashHero.X < 44.5 && wallDashHero.X > 43.5 && wallDashHero.Y == 0 &&
            wallDash.RequestedWu == 11,
            wallDash is null ? "no resolution" : $"{wallDash.AchievedWu}/{wallDash.StopReason}");
        var revisionBeforeSecond = wallDashHero.Revision;
        var secondDashCast = new string('3', 32);
        wallDashEngine.Schedule(
            wallDashHero, wallDashHero.SessionId, secondDashCast, CombatV2Actions.Skill,
            "SK-MK-02", 1, 0, startTick: 20);
        wallDashEngine.Tick(27);
        var secondDash = wallDashEngine.DashLedger.Find(secondDashCast);
        Check(
            "dash_blocked_at_start_reports_no_travel",
            secondDash is not null &&
            secondDash.AchievedWu < 0.05 &&
            secondDash.StopReason is DashStopReasons.ZeroDistance or DashStopReasons.BlockedByGeometry &&
            wallDashHero.X == wallDash?.X &&
            wallDashHero.Revision == revisionBeforeSecond,
            secondDash is null ? "no resolution" : $"{secondDash.AchievedWu}/{secondDash.StopReason}");

        // A dash that is scheduled and then invalidated moves nobody and is
        // cancelled once; the committed MP/cooldown are never refunded.
        var deadDashHero = NewPlayer("CHR_SELFCHECK_DASH_DEAD");
        deadDashHero.X = 33;
        deadDashHero.Y = 0;
        var deadDashEngine = new CombatTickEngine(
            new WorldEntityRegistry(new WorldEntityCatalog([], []), lateClock),
            enabledCombat, combatSkills,
            new CombatEventStore(new CombatEventStreamOptions { CapacityPerSession = 256, MaxPageSize = 256 }),
            new MobCombatStateStore(), tickQuests, new FixedCombatRolls(hit: true, crit: false),
            new GuardWindowStore(), tickGeometry, NewDashes(tickGeometry), new ServerClock());
        var deadDashCast = new string('4', 32);
        deadDashEngine.Schedule(
            deadDashHero, deadDashHero.SessionId, deadDashCast, CombatV2Actions.Skill,
            "SK-MK-02", 1, 0, startTick: 0);
        var mpBeforeDeath = deadDashHero.Mp;
        deadDashHero.Hp = 0;
        var deadDashEvents = deadDashEngine.Tick(7);
        Check(
            "dash_cancelled_when_actor_down_before_movement",
            deadDashHero.X == 33 &&
            deadDashEngine.DashLedger.Find(deadDashCast) is null &&
            deadDashHero.Mp == mpBeforeDeath &&
            deadDashEvents.Count(stored => stored.Type == CombatEventTypesV2.Cancel) == 1 &&
            deadDashEvents.Count(stored => stored.Type == CombatEventTypesV2.End) == 1 &&
            !deadDashEvents.Any(stored => stored.Type == CombatEventTypesV2.Impact),
            string.Join(",", deadDashEvents.Select(stored => stored.Type)));

        var dashLedger = new DashLedger();
        for (var ledgerIndex = 0; ledgerIndex < 600; ledgerIndex++)
        {
            dashLedger.Record(new DashResolution(
                ledgerIndex.ToString("x32"), "CHR_LEDGER", ledgerIndex, 11, 11, 0, 0,
                DashStopReasons.Complete, 1));
        }

        Check(
            "dash_ledger_is_bounded",
            dashLedger.Count == DashLedger.Capacity &&
            dashLedger.Find(87.ToString("x32")) is null &&
            dashLedger.Find(88.ToString("x32")) is not null &&
            dashLedger.Find(599.ToString("x32")) is { AchievedWu: 11 },
            $"count={dashLedger.Count}");

        // Q-B: status read model. A client that lost its event cursor (or
        // reconnected after the buffer rolled over) still has to be able to ask
        // what is active. Nothing here is on the wire yet.
        var statusHero = NewGuardHero("STATUS");
        var statusWindows = new GuardWindowStore();
        var statusDashes = NewDashes(geometry);
        var statusCommands = new InMemoryCombatV2Service(
            combatSkills,
            new CombatEventStore(new CombatEventStreamOptions
            {
                CapacityPerSession = 256,
                MaxPageSize = 256
            }),
            new ServerClock());
        var statusEngine = new CombatTickEngine(
            guardRegistry, enabledCombat, combatSkills, guardEvents, guardStates,
            tickQuests, new FixedCombatRolls(hit: true, crit: false),
            statusWindows, geometry, statusDashes, new ServerClock());
        var statusProjection = new CombatStatusProjection(
            statusWindows, statusCommands, statusDashes);
        var statusAttacks = new MobAttackService(
            guardRegistry, enabledCombat, mobOptions,
            new GuardDefenseService(statusWindows, enabledCombat, guardEvents),
            new PlayerLifeLedger());
        var statusAccept = statusCommands.Resolve(
            statusHero, statusHero.SessionId,
            new CombatV2Intent(CombatV2Actions.Skill, "SK-MK-01", null, 1, 1, 0, null),
            new string('6', 32));
        var statusCastId = new string('7', 32);
        statusEngine.Schedule(
            statusHero, statusHero.SessionId, statusCastId, CombatV2Actions.Skill, "SK-MK-01",
            1, 0, startTick: 0);
        statusEngine.Schedule(
            statusHero, statusHero.SessionId, new string('8', 31) + "a",
            CombatV2Actions.Skill, "SK-MK-02", 1, 0, startTick: 0);
        statusAttacks.ApplyImpacts(
            [GuardImpact("ENT_SELFCHECK_GUARD_MOB2", statusHero)], [statusHero], tick: 1);
        var guardingStatus = statusProjection.Project(
            statusHero, tick: 1, nowUtc: guardClock.UtcNow);
        Check(
            "status.guard_phase_counter_and_cooldown",
            statusAccept.Accepted &&
            guardingStatus is
            {
                GuardPhase: GuardPhases.Guard,
                CounterReserved: true,
                CounterTick: 2,
                SwordIntent: 2,
                Hp: 97,
                Mp: 38,
                LastDash: null
            } &&
            guardingStatus.GuardCastId == statusCastId &&
            guardingStatus.GuardEndExclusiveTick == 8 &&
            guardingStatus.WhiffEndExclusiveTick == 28 &&
            guardingStatus.CounterSourceEntityId == "ENT_SELFCHECK_GUARD_MOB2" &&
            guardingStatus.Cooldowns.Single(cooldown => cooldown.ActionKey == "SK-MK-01").Active &&
            statusEngine.Tick(2).Any(stored => stored.Type == CombatEventTypesV2.Impact),
            $"{guardingStatus.GuardPhase}/{guardingStatus.Cooldowns.Count}");

        var resolvedStatus = statusProjection.Project(
            statusHero, tick: 3, nowUtc: guardClock.UtcNow);
        Check(
            "status_reports_resolved_counter_and_keeps_cooldown",
            resolvedStatus is { CounterReserved: false, CounterOutcome: "DAMAGE", Mp: 38 } &&
            resolvedStatus.Cooldowns.Any(cooldown => cooldown.ActionKey == "SK-MK-01"),
            resolvedStatus.CounterOutcome ?? "none");

        // The dash of the same hero is visible without any event replay.
        statusEngine.Tick(7);
        var dashStatus = statusProjection.Project(
            statusHero, tick: 8, nowUtc: guardClock.UtcNow);
        Check(
            "status_carries_last_dash_outcome_without_events",
            dashStatus.LastDash is { StopReason: DashStopReasons.BlockedByGeometry } &&
            dashStatus.LastDash.AchievedWu > 4.0 && dashStatus.LastDash.AchievedWu < 4.45 &&
            dashStatus.LastDash.X < 44.5 &&
            dashStatus.GuardPhase == GuardPhases.Expired &&
            dashStatus.Hp == 97,
            dashStatus.LastDash?.StopReason ?? "no dash");

        // The earlier guard fixtures live in their own store, so the same
        // projection is pointed at it to read whiff and closed-window states.
        var guardStatus = new CombatStatusProjection(
            guardWindows, statusCommands, statusDashes);
        var whiffStatus = guardStatus.Project(hero1, tick: 20, nowUtc: guardClock.UtcNow);
        var expiredStatus = guardStatus.Project(hero1, tick: 40, nowUtc: guardClock.UtcNow);
        var downStatus = guardStatus.Project(hero4, tick: 21, nowUtc: guardClock.UtcNow);
        Check(
            "status_tracks_whiff_expiry_and_closed_window",
            whiffStatus.GuardPhase == GuardPhases.Whiff &&
            expiredStatus.GuardPhase == GuardPhases.Expired &&
            downStatus is { GuardPhase: GuardPhases.None, SwordIntent: 0, CounterReserved: false },
            $"{whiffStatus.GuardPhase}/{expiredStatus.GuardPhase}/{downStatus.GuardPhase}");

        // Q-B3: return from a downed state. Server-owned anchor only, one apply
        // per idempotency key, and the previous life's cast, guard window and
        // reserved counter all cleaned up as events rather than silently dropped.
        var returnSessions = new InMemorySessionStore();
        var returnWindows = new GuardWindowStore();
        var returnEvents = new CombatEventStore(new CombatEventStreamOptions
        {
            CapacityPerSession = 256,
            MaxPageSize = 256
        });
        var returnStates = new MobCombatStateStore();
        var returnEngine = new CombatTickEngine(
            guardRegistry, enabledCombat, combatSkills, returnEvents, returnStates,
            tickQuests, new FixedCombatRolls(hit: true, crit: false),
            returnWindows, geometry, NewDashes(geometry), new ServerClock());
        // One ledger for the whole return fixture: the mob attack that ends the
        // life and the return that starts the next one have to look at the same
        // per-character state, which is how the composition root wires it. The
        // clock is manual because the approved cooldown is measured in ticks.
        var returnLives = new PlayerLifeLedger();
        var returnClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 30, 3, 0, 0, TimeSpan.Zero));
        var returnAttacks = new MobAttackService(
            guardRegistry, enabledCombat, mobOptions,
            new GuardDefenseService(returnWindows, enabledCombat, returnEvents),
            returnLives);
        DeathReturnService NewDeathReturn(int restoreHp) => new(
            returnSessions, maps, options,
            new DeathReturnOptions { Enabled = true, RestoreHpFixture = restoreHp },
            returnWindows, returnEngine, returnLives, returnClock, null);
        var deathReturnService = NewDeathReturn(0);
        var downHero = NewGuardHero("RETURN");
        returnSessions.Add(downHero);
        var downCastId = new string('9', 31) + "a";
        returnEngine.Schedule(
            downHero, downHero.SessionId, downCastId, CombatV2Actions.Skill, "SK-MK-01",
            1, 0, startTick: 0);
        returnAttacks.ApplyImpacts(
            [GuardImpact("ENT_SELFCHECK_GUARD_MOB2", downHero)], [downHero], tick: 1);
        var revisionBeforeReturn = downHero.Revision;
        var intentBeforeReturn = downHero.SwordIntent;
        downHero.Hp = 0;
        // The registered service is the one the composition root builds with the
        // shipped appsettings, so this also proves the gate defaults OFF on boot.
        var wiredDeathReturn = services.GetRequiredService<DeathReturnService>();
        var disabledReturn = wiredDeathReturn
            .ReturnToAnchor(downHero.SessionId, new string('9', 31) + "0");
        var aliveKey = new string('9', 31) + "b";
        downHero.Hp = 100;
        var aliveReturn = deathReturnService.ReturnToAnchor(downHero.SessionId, aliveKey);
        var badKeyReturn = deathReturnService.ReturnToAnchor(downHero.SessionId, "not-a-key");
        downHero.Hp = 0;
        Check(
            "death_return.gate_off_and_refuses_alive_and_bad_key",
            wiredDeathReturn.Enabled == false &&
            services.GetRequiredService<DeathReturnOptions>() is { Enabled: false } &&
            disabledReturn.ErrorCode == DeathReturnErrorCodes.Disabled &&
            aliveReturn.ErrorCode == DeathReturnErrorCodes.NotDowned &&
            badKeyReturn.ErrorCode == DeathReturnErrorCodes.InvalidKey &&
            downHero.X == 40 && downHero.Y == 0 &&
            downHero.Revision == revisionBeforeReturn &&
            disabledReturn is { InflightCastsCancelled: 0, ReservedCountersCancelled: 0 } &&
            aliveReturn is { InflightCastsCancelled: 0, ReservedCountersCancelled: 0 },
            $"{disabledReturn.ErrorCode}/{aliveReturn.ErrorCode}/{badKeyReturn.ErrorCode}");

        var unknownMapHero = NewGuardHero("RETURN_NOMAP");
        unknownMapHero.MapId = "MAP_NOT_IN_BOUNDS";
        unknownMapHero.Hp = 0;
        returnSessions.Add(unknownMapHero);
        var unknownSessionReturn = deathReturnService
            .ReturnToAnchor("SES_DOES_NOT_EXIST", new string('9', 31) + "c");
        var unknownMapReturn = deathReturnService
            .ReturnToAnchor(unknownMapHero.SessionId, new string('9', 31) + "d");
        Check(
            "death_return.unknown_session_and_map_do_not_move_anyone",
            unknownSessionReturn.ErrorCode == DeathReturnErrorCodes.UnknownSession &&
            unknownMapReturn.ErrorCode == DeathReturnErrorCodes.UnknownMap &&
            unknownMapHero.X == 40 && unknownMapHero.Y == 0 &&
            returnEngine.ScheduledCastCount == 1,
            $"{unknownSessionReturn.ErrorCode}/{unknownMapReturn.ErrorCode}");

        var deathKey = new string('9', 32);
        var firstReturn = deathReturnService.ReturnToAnchor(downHero.SessionId, deathKey);
        var afterReturnEvents = returnEvents.Read(downHero.SessionId, 0, 256).Events;
        var returnWindow = returnWindows.FindAny(downHero.CharacterId);
        var lateTickEvents = returnEngine.Tick(2);
        Check(
            "death_return.clears_cast_window_and_counter_once",
            firstReturn is { Applied: true, Replayed: false, ErrorCode: null, Hp: 0 } &&
            firstReturn is { InflightCastsCancelled: 1, ReservedCountersCancelled: 1 } &&
            firstReturn.SessionId == downHero.SessionId &&
            firstReturn.Revision == revisionBeforeReturn + 1 &&
            firstReturn.X == options.SpawnX && firstReturn.Y == options.SpawnY &&
            downHero.X == options.SpawnX && downHero.Y == options.SpawnY &&
            returnEngine.ScheduledCastCount == 0 &&
            returnWindows.Find(downHero.CharacterId) is null &&
            downHero.SwordIntent == 0 &&
            intentBeforeReturn == 2 &&
            returnWindow is { CounterResolved: true, CounterOutcome: "RETURNED_TO_ANCHOR" } &&
            afterReturnEvents.Count(stored => stored.Type == CombatEventTypesV2.Cancel) == 2 &&
            afterReturnEvents.Count(stored => stored.Type == CombatEventTypesV2.End) == 1 &&
            lateTickEvents.Count == 0,
            $"{firstReturn.ErrorCode}/{firstReturn.InflightCastsCancelled}/" +
            $"{firstReturn.ReservedCountersCancelled}/{lateTickEvents.Count}");

        var replayReturn = deathReturnService.ReturnToAnchor(downHero.SessionId, deathKey);
        var otherHero = NewGuardHero("RETURN_OTHER");
        otherHero.Hp = 0;
        returnSessions.Add(otherHero);
        var stolenKeyReturn = deathReturnService.ReturnToAnchor(otherHero.SessionId, deathKey);
        var eventsAfterReplay = returnEvents.Read(downHero.SessionId, 0, 256).Events.Count;
        Check(
            "death_return_replays_the_recorded_answer",
            replayReturn is { Applied: false, Replayed: true } &&
            replayReturn.Revision == firstReturn.Revision &&
            replayReturn.X == firstReturn.X && replayReturn.Y == firstReturn.Y &&
            downHero.Revision == firstReturn.Revision &&
            downHero.X == options.SpawnX &&
            stolenKeyReturn.ErrorCode == DeathReturnErrorCodes.KeyConflict &&
            stolenKeyReturn.Applied == false &&
            otherHero.X == 40 && otherHero.Y == 0 &&
            returnEvents.Read(downHero.SessionId, 0, 256).Events.Count == eventsAfterReplay,
            $"{replayReturn.Replayed}/{stolenKeyReturn.ErrorCode}");

        // Reconnect case (work order 30 item 1): the receipt follows the character, not
        // the session. A second session for the same character that presents the key the
        // first one committed gets the recorded snapshot back and moves nobody - the new
        // actor stays exactly where it is, which is why the decision tells a client to
        // fresh-read the world instead of reading a receipt as current state.
        var reconnectService = NewDeathReturn(0);
        var reconnectFirst = NewPlayer("CHR_SELFCHECK_RETURN_RECONNECT", hp: 0);
        returnSessions.Add(reconnectFirst);
        var reconnectApplied = reconnectService.ReturnToAnchor(
            reconnectFirst.SessionId, "c" + new string('0', 31));
        var reconnectSecond = NewPlayer("CHR_SELFCHECK_RETURN_RECONNECT", hp: 0);
        returnSessions.Add(reconnectSecond);
        var reconnectSecondX = reconnectSecond.X;
        var reconnectReplay = reconnectService.ReturnToAnchor(
            reconnectSecond.SessionId, "c" + new string('0', 31));
        Check(
            "death_return.a_reconnected_session_replaying_the_old_key_gets_the_receipt",
            reconnectApplied is { Applied: true } &&
            reconnectReplay is { Applied: false, Replayed: true } &&
            reconnectReplay.Hp == reconnectApplied.Hp &&
            reconnectSecond.Hp == 0 &&
            reconnectSecond.X == reconnectSecondX,
            $"applied={reconnectApplied.Applied}/{reconnectApplied.Hp} replay={reconnectReplay.Applied}/{reconnectReplay.Replayed}/{reconnectReplay.Hp} newActor={reconnectSecond.Hp}@{reconnectSecond.X}");

        // Two clients racing one key must produce one return, not two moves and
        // two revision bumps.
        var racedHero = NewGuardHero("RETURN_RACE");
        racedHero.Hp = 0;
        returnSessions.Add(racedHero);
        var racedService = NewDeathReturn(options.StartingMaxHp);
        var racedResults = new System.Collections.Concurrent.ConcurrentBag<DeathReturnResult>();
        RunBarrierParallel(4, _ => racedResults.Add(
            racedService.ReturnToAnchor(racedHero.SessionId, new string('9', 31) + "e")));
        var racedApplied = racedResults.Count(result => result.Applied && !result.Replayed);
        var racedReplayed = racedResults.Count(result => result.Replayed);
        Check(
            "death_return.one_key_applies_once_under_contention",
            racedApplied == 1 && racedReplayed == 3 &&
            racedHero.X == options.SpawnX && racedHero.Revision == 2 &&
            racedResults.All(result => result.Revision == racedHero.Revision),
            $"applied={racedApplied} replayed={racedReplayed} x={racedHero.X}");

        // A configured restore value is the only thing that refills HP, and a
        // returned actor is no longer downed: a second key cannot farm returns.
        racedHero.Hp = 0;
        racedHero.X = 40;
        var refilledReturn = racedService.ReturnToAnchor(
            racedHero.SessionId, new string('9', 31) + "0");
        var secondKeyReturn = racedService.ReturnToAnchor(
            racedHero.SessionId, new string('9', 31) + "f");
        Check(
            "death_return.restores_only_the_configured_fixture_value",
            refilledReturn is { Applied: true } &&
            refilledReturn.Hp == options.StartingMaxHp &&
            racedHero.Hp == options.StartingMaxHp &&
            refilledReturn.Revision == 3 &&
            secondKeyReturn.ErrorCode == DeathReturnErrorCodes.NotDowned &&
            racedHero.X == options.SpawnX,
            $"{refilledReturn.Hp}/{secondKeyReturn.ErrorCode}");

        var ledgerService = NewDeathReturn(0);
        string ledgerFirstSession = string.Empty;
        string ledgerFirstKey = string.Empty;
        for (var ledgerIndex = 0; ledgerIndex < 300; ledgerIndex++)
        {
            var ledgerHero = NewPlayer("CHR_SELFCHECK_RETURN_" + ledgerIndex, hp: 0);
            returnSessions.Add(ledgerHero);
            ledgerService.ReturnToAnchor(
                ledgerHero.SessionId, ledgerIndex.ToString("x32"));
            if (ledgerIndex == 0)
            {
                ledgerFirstSession = ledgerHero.SessionId;
                ledgerFirstKey = ledgerIndex.ToString("x32");
            }
        }

        Check(
            "death_return_keeps_every_receipt_whose_life_is_still_current",
            ledgerService.LedgerCount == 300 &&
            ledgerService.ReceiptsHeldPastBound == 44 &&
            ledgerService.ReturnToAnchor(ledgerFirstSession, ledgerFirstKey)
                is { Applied: false, Replayed: true },
            $"count={ledgerService.LedgerCount} held={ledgerService.ReceiptsHeldPastBound}");

        // DEC-DEATH-RETURN-20261105 answers the six packet questions, and the
        // approved shape is owned by three numbers the fixture does not have: the
        // anchor and the HP formula and the cooldown all come from the design, and
        // the receipt answers a death the damage path actually recorded.
        var returnAlphaRules = services.GetRequiredService<AlphaDesign>().DeathReturn;
        var alphaReturnService = new DeathReturnService(
            returnSessions, maps, options,
            new DeathReturnOptions { Enabled = true },
            returnWindows, returnEngine, returnLives, returnClock, returnAlphaRules);
        var alphaHero = NewGuardHero("RETURN_ALPHA");
        returnSessions.Add(alphaHero);
        var alphaLifeBefore = returnLives.LifeVersion(alphaHero.CharacterId);
        var alphaRevisionBefore = alphaHero.Revision;
        var alphaMpBefore = alphaHero.Mp;
        // One reference hit does not end a 100-HP life, so the fixture drops the
        // actor to the edge and lets the shipped damage commit cross it: the
        // point under test is that the death record comes from that commit.
        alphaHero.Hp = 1;
        returnAttacks.ApplyImpacts(
            [GuardImpact("ENT_SELFCHECK_GUARD_MOB2", alphaHero)], [alphaHero], tick: 3);
        var alphaDeath = returnLives.LatestDeath(alphaHero.CharacterId);
        Check(
            "death_return.damage_path_records_the_death_it_answers",
            alphaHero.Hp == 0 &&
            alphaDeath is not null &&
            alphaDeath.CharacterId == alphaHero.CharacterId &&
            alphaDeath.LifeVersion == alphaLifeBefore &&
            alphaDeath.DeathRevision == alphaHero.Revision &&
            alphaHero.Revision == alphaRevisionBefore + 1 &&
            alphaDeath.DeathEventId == PlayerLifeLedger.DeathEventIdFor(
                alphaHero.CharacterId, alphaLifeBefore, alphaHero.Revision),
            $"death={alphaDeath?.DeathEventId} life={alphaLifeBefore} " +
            $"revision={alphaRevisionBefore}->{alphaHero.Revision}");

        var alphaDeathId = alphaDeath!.DeathEventId;
        var alphaReturn = alphaReturnService.ReturnToAnchor(
            alphaHero.SessionId, new string('9', 31) + "1");
        Check(
            "death_return.alpha_shape_uses_the_design_anchor_formula_and_clock",
            returnAlphaRules is
            {
                MapId: "MAP_BEN_MUA", AnchorX: 18, AnchorY: 0,
                NewDeathReturnCooldownSeconds: 3, XpPenalty: 0, CurrencyPenalty: 0,
                DurabilityPenalty: 0
            } &&
            alphaReturnService.CooldownTicks == 60 &&
            alphaReturn is { Applied: true, Replayed: false, ErrorCode: null } &&
            alphaReturn.X == returnAlphaRules.AnchorX &&
            alphaReturn.Y == returnAlphaRules.AnchorY &&
            alphaHero.X == returnAlphaRules.AnchorX &&
            // max(1, ceil(currentEffectiveMaxHp * 0.5)) with the fixture's 100.
            alphaReturn.Hp == 50 && alphaHero.Hp == 50 &&
            // restoreMp keeps the absolute value: nothing refills MP.
            alphaReturn.Mp == alphaMpBefore && alphaHero.Mp == alphaMpBefore &&
            alphaReturn.MaxHp == alphaHero.MaxHp &&
            alphaReturn.DeathEventId == alphaDeathId &&
            alphaReturn.NewLifeVersion == alphaLifeBefore + 1 &&
            returnLives.LifeVersion(alphaHero.CharacterId) == alphaLifeBefore + 1 &&
            alphaReturn.NextReturnAllowedAtTick == returnClock.Tick + 60,
            $"hp={alphaReturn.Hp}/{alphaReturn.MaxHp} mp={alphaReturn.Mp} " +
            $"x={alphaReturn.X},{alphaReturn.Y} life={alphaReturn.NewLifeVersion} " +
            $"until={alphaReturn.NextReturnAllowedAtTick}");

        // A second death inside the window is refused, and a committed replay of
        // the first key still answers whatever the actor looks like now.
        var alphaCooldownStartTick = returnClock.Tick;
        // The first return moved the actor to the anchor, out of the mob's
        // attack reach, so walk them back before ending the next life.
        alphaHero.X = 40;
        alphaHero.Y = 0;
        alphaHero.Hp = 1;
        returnAttacks.ApplyImpacts(
            [GuardImpact("ENT_SELFCHECK_GUARD_MOB2", alphaHero)], [alphaHero], tick: 4);
        var alphaSecondDeath = returnLives.LatestDeath(alphaHero.CharacterId);
        var cooldownPosition = alphaHero.X;
        var cooldownReturn = alphaReturnService.ReturnToAnchor(
            alphaHero.SessionId, new string('9', 31) + "2");
        var replayInCooldown = alphaReturnService.ReturnToAnchor(
            alphaHero.SessionId, new string('9', 31) + "1");
        Check(
            "death_return.cooldown_refuses_a_new_death_and_replay_answers_first",
            alphaSecondDeath is { LifeVersion: 2 } &&
            alphaSecondDeath!.DeathEventId != alphaDeathId &&
            cooldownReturn is
            {
                Applied: false,
                Replayed: false,
                ErrorCode: DeathReturnErrorCodes.Cooldown
            } &&
            cooldownReturn.NextReturnAllowedAtTick == alphaCooldownStartTick + 60 &&
            cooldownReturn.Hp == 0 &&
            alphaHero.X == cooldownPosition &&
            replayInCooldown is { Applied: false, Replayed: true } &&
            replayInCooldown.Hp == alphaReturn.Hp &&
            replayInCooldown.X == alphaReturn.X &&
            replayInCooldown.NextReturnAllowedAtTick ==
                alphaReturn.NextReturnAllowedAtTick &&
            alphaHero.Revision == alphaSecondDeath!.DeathRevision,
            $"code={cooldownReturn.ErrorCode} life={alphaSecondDeath?.LifeVersion} " +
            $"replay={replayInCooldown.Replayed}@{replayInCooldown.Hp}");

        returnClock.Advance(TimeSpan.FromSeconds(3.05));
        var afterCooldownReturn = alphaReturnService.ReturnToAnchor(
            alphaHero.SessionId, new string('9', 31) + "3");
        Check(
            "death_return.cooldown_expires_on_the_server_tick",
            afterCooldownReturn is { Applied: true, Replayed: false, Hp: 50 } &&
            afterCooldownReturn.DeathEventId == alphaSecondDeath!.DeathEventId &&
            afterCooldownReturn.NewLifeVersion == 3 &&
            afterCooldownReturn.NextReturnAllowedAtTick == returnClock.Tick + 60,
            $"code={afterCooldownReturn.ErrorCode} " +
            $"life={afterCooldownReturn.NewLifeVersion}");

        // Reconnect retention: the decision says the life state belongs to the
        // character, never to the session, so a fresh session for the same actor
        // continues the same numbering instead of starting at 1.
        var reconnectHero = NewGuardHero("RETURN_ALPHA");
        returnSessions.Add(reconnectHero);
        var reconnectReturn = alphaReturnService.ReturnToAnchor(
            reconnectHero.SessionId, new string('9', 31) + "4");
        Check(
            "death_return.life_state_follows_the_character_not_the_session",
            reconnectHero.CharacterId == alphaHero.CharacterId &&
            reconnectHero.SessionId != alphaHero.SessionId &&
            reconnectReturn.SessionId == reconnectHero.SessionId &&
            reconnectReturn.NewLifeVersion == 3 &&
            reconnectReturn.DeathEventId == alphaSecondDeath!.DeathEventId &&
            reconnectReturn.ErrorCode == DeathReturnErrorCodes.NotDowned &&
            returnLives.LifeVersion(reconnectHero.CharacterId) ==
                reconnectReturn.NewLifeVersion,
            $"sessions={reconnectHero.SessionId != alphaHero.SessionId} " +
            $"life={reconnectReturn.NewLifeVersion}");

        var validatorAlphaFixture = false;
        var validatorAlphaZero = false;
        var validatorFixtureWithoutAlpha = false;
        try
        {
            DeathReturnOptionsValidator.Validate(
                new DeathReturnOptions { Enabled = true, RestoreHpFixture = 50 },
                options, alphaProfileEnabled: true);
        }
        catch (InvalidOperationException)
        {
            validatorAlphaFixture = true;
        }

        try
        {
            DeathReturnOptionsValidator.Validate(
                new DeathReturnOptions { Enabled = true, RestoreHpFixture = 0 },
                options, alphaProfileEnabled: true);
            validatorAlphaZero = true;
        }
        catch (InvalidOperationException)
        {
        }

        try
        {
            DeathReturnOptionsValidator.Validate(
                new DeathReturnOptions { Enabled = true, RestoreHpFixture = 50 },
                options, alphaProfileEnabled: false);
            validatorFixtureWithoutAlpha = true;
        }
        catch (InvalidOperationException)
        {
        }

        Check(
            "death_return.validator_refuses_a_fixture_under_the_alpha_profile",
            validatorAlphaFixture && validatorAlphaZero && validatorFixtureWithoutAlpha,
            $"alphaFixture={validatorAlphaFixture} alphaZero={validatorAlphaZero} " +
            $"fixtureWithoutAlpha={validatorFixtureWithoutAlpha}");

        var idA = PlayerLifeLedger.DeathEventIdFor("CHR_X", 1, 12);
        var idSameLife = PlayerLifeLedger.DeathEventIdFor("CHR_X", 2, 12);
        var idSameRevision = PlayerLifeLedger.DeathEventIdFor("CHR_X", 1, 13);
        var idOtherCharacter = PlayerLifeLedger.DeathEventIdFor("CHR_Y", 1, 12);
        Check(
            "player_life.death_event_id_is_canonical_and_derived",
            System.Text.RegularExpressions.Regex.IsMatch(idA, @"^PDEATH_[0-9a-f]{64}$") &&
            idA == PlayerLifeLedger.DeathEventIdFor("CHR_X", 1, 12) &&
            idA != idSameLife && idA != idSameRevision && idA != idOtherCharacter &&
            idSameLife != idSameRevision,
            $"id={idA.Length}");

        // Work order 30 item 1: churn of unrelated deaths must not cost a live character
        // its life identity. 300 characters die and none is returned; the two first
        // tracked still have to answer their own death with the same derived id and the
        // same life number, and the ledger has to report how far past the bound it grew
        // instead of silently dropping them (the old rule renumbered an evicted character
        // at 1, so its next death minted a fresh identity for the same life).
        var churnLedger = new PlayerLifeLedger();
        var churnFirstDeath = churnLedger.RecordDamageCommit(
            "CHR_CHURN_FIRST", 100, 0, 11, DateTimeOffset.UnixEpoch);
        var churnSecondDeath = churnLedger.RecordDamageCommit(
            "CHR_CHURN_SECOND", 100, 0, 12, DateTimeOffset.UnixEpoch);
        for (var churnIndex = 0; churnIndex < 300; churnIndex++)
        {
            churnLedger.RecordDamageCommit(
                $"CHR_CHURN_{churnIndex:D3}", 100, 0, churnIndex + 100, DateTimeOffset.UnixEpoch);
        }

        var churnSurvived = churnLedger.LatestDeath("CHR_CHURN_FIRST");
        Check(
            "lifecycle.churn_of_300_other_deaths_keeps_a_downed_characters_death_identity",
            churnFirstDeath is not null && churnSecondDeath is not null &&
            churnSurvived is not null &&
            churnSurvived.DeathEventId == churnFirstDeath.DeathEventId &&
            churnLedger.LifeVersion("CHR_CHURN_FIRST") == 1 &&
            churnLedger.LifeVersion("CHR_CHURN_SECOND") == 1 &&
            churnLedger.TrackedCharacters == 302 &&
            churnLedger.PinnedCharacters == 302 &&
            churnLedger.CapacityExceededBy == 46,
            $"tracked={churnLedger.TrackedCharacters} pinned={churnLedger.PinnedCharacters} " +
            $"exceeded={churnLedger.CapacityExceededBy} " +
            $"firstLife={churnLedger.LifeVersion("CHR_CHURN_FIRST")} " +
            $"idKept={churnSurvived?.DeathEventId == churnFirstDeath?.DeathEventId}");

        // The other half of the rule: reclaiming happens only where nothing is owed. Once
        // 46 of those lives are closed by a committed return, the next character is
        // absorbed by reclaiming one closed entry, the tracked count stops growing, and
        // the overflow counter stays where it was. Pinned lands on 257, not on the bound:
        // the newcomer is itself a downed character, so one closed entry left and one
        // pinned entry arrived in the same insert.
        for (var churnIndex = 0; churnIndex < 46; churnIndex++)
        {
            churnLedger.RecordResurrectionCommit($"CHR_CHURN_{churnIndex:D3}", 0, 100);
        }

        churnLedger.RecordDamageCommit(
            "CHR_CHURN_NEWCOMER", 100, 0, 999, DateTimeOffset.UnixEpoch);
        Check(
            "lifecycle.only_a_closed_life_is_reclaimable_so_the_bound_holds_again",
            churnLedger.TrackedCharacters == 302 &&
            churnLedger.PinnedCharacters == 257 &&
            churnLedger.CapacityExceededBy == 46 &&
            churnLedger.LatestDeath("CHR_CHURN_000") is null &&
            churnLedger.LatestDeath("CHR_CHURN_045") is not null &&
            churnLedger.LatestDeath("CHR_CHURN_NEWCOMER") is not null,
            $"tracked={churnLedger.TrackedCharacters} pinned={churnLedger.PinnedCharacters} " +
            $"exceeded={churnLedger.CapacityExceededBy} " +
            $"reclaimedOldestClosed={churnLedger.LatestDeath("CHR_CHURN_000") is null} " +
            $"newestClosedKept={churnLedger.LatestDeath("CHR_CHURN_045") is not null}");

        var ledgerNoDoubleRecord = new PlayerLifeLedger();
        var repeatAt = returnClock.UtcNow;
        var repeatFirst = ledgerNoDoubleRecord.RecordDamageCommit(
            "CHR_REPEAT", 10, 0, 7, repeatAt);
        var repeatSecond = ledgerNoDoubleRecord.RecordDamageCommit(
            "CHR_REPEAT", 0, 0, 8, repeatAt);
        var repeatHeal = ledgerNoDoubleRecord.RecordResurrectionCommit(
            "CHR_REPEAT", 0, 50);
        var repeatAfterHeal = ledgerNoDoubleRecord.RecordDamageCommit(
            "CHR_REPEAT", 50, 0, 9, repeatAt);
        Check(
            "player_life.one_transition_one_record_and_one_life_advance",
            repeatFirst is { LifeVersion: 1, DeathRevision: 7 } &&
            repeatSecond is null &&
            repeatHeal == 2 &&
            ledgerNoDoubleRecord.LifeVersion("CHR_REPEAT") == 2 &&
            repeatAfterHeal is { LifeVersion: 2, DeathRevision: 9 } &&
            repeatAfterHeal!.DeathEventId != repeatFirst!.DeathEventId,
            $"first={repeatFirst?.DeathEventId} second={repeatSecond?.DeathEventId}");

        // The non-death half of the same rule: a window belongs to the instance it
        // opened on, so an actor who changes map with no hit and no cast in
        // flight must not keep one open — the read model would report GUARD/WHIFF
        // forever and the whiff reward would survive an instance change.
        var sweepHero = NewGuardHero("SWEEP");
        returnSessions.Add(sweepHero);
        var sweepWindows = new GuardWindowStore();
        var sweepEngine = new CombatTickEngine(
            guardRegistry, enabledCombat, combatSkills, returnEvents, returnStates,
            tickQuests, new FixedCombatRolls(hit: true, crit: false),
            sweepWindows, geometry, NewDashes(geometry), new ServerClock());
        sweepEngine.Schedule(
            sweepHero, sweepHero.SessionId, new string('8', 31) + "f",
            CombatV2Actions.Skill, "SK-MK-01", 1, 0, startTick: 0);
        var sweepCastEvents = sweepEngine.Tick(12);
        sweepHero.MapId = "MAP_KHO_CUA_LUYEN";
        var sweepMapEvents = sweepEngine.Tick(13);
        var sweepProjection = new CombatStatusProjection(
            sweepWindows, statusCommands, statusDashes);
        Check(
            "guard.window_closes_on_map_change_without_a_hit",
            sweepCastEvents.Any(stored => stored.Type == CombatEventTypesV2.End) &&
            sweepEngine.ScheduledCastCount == 0 &&
            sweepWindows.Find(sweepHero.CharacterId) is null &&
            sweepWindows.FindAny(sweepHero.CharacterId) is
            {
                EndReason: GuardWindowEndReasons.MapOrFloorChange,
                WhiffGranted: false
            } &&
            sweepMapEvents.Count == 0 &&
            sweepProjection.Project(sweepHero, tick: 13, nowUtc: guardClock.UtcNow).GuardPhase
                == GuardPhases.None,
            $"{sweepWindows.FindAny(sweepHero.CharacterId)?.EndReason}/" +
            $"{sweepProjection.Project(sweepHero, tick: 13, nowUtc: guardClock.UtcNow).GuardPhase}");

        var losAccept = new InMemoryQuestAcceptService(
            questCatalog, quests, npcAnchors, geometry,
            services.GetRequiredService<QuestAcceptOptions>(),
            services.GetRequiredService<QuestXpSnapshotStore>());

        var blockedActor = NewPlayer("CHR_SELFCHECK_LOS_BLOCKED");
        blockedActor.X = 46.5;
        blockedActor.Y = 0;
        var blockedAccept = losAccept.Accept(
            blockedActor, "P00-01", "NPC_LYAN", new string('1', 31) + "0");
        Check(
            "quest_accept.los_blocked",
            blockedAccept.Failure?.Code == QuestAcceptErrorCodes.OutOfRange &&
            blockedAccept.Failure.Retryable,
            blockedAccept.Failure?.Code);

        var blockedState = quests.GetState(blockedActor.CharacterId, "P00-01").State;
        Check(
            "quest_accept.los_blocked_state",
            blockedState is { State: QuestStates.Available, Revision: 1 },
            blockedState?.State);

        var clearActor = NewPlayer("CHR_SELFCHECK_LOS_CLEAR");
        clearActor.X = 38;
        clearActor.Y = 0;
        var clearAccept = losAccept.Accept(
            clearActor, "P00-01", "NPC_LYAN", new string('2', 31) + "0");
        Check(
            "quest_accept.los_allowed",
            clearAccept.Accepted && clearAccept.State?.State == QuestStates.Active,
            clearAccept.Failure?.Code);

        var worldRecords = services.GetRequiredService<WorldRecordCatalog>();
        Check("world.records", worldRecords.Count == 352, $"count={worldRecords.Count}");
        Check(
            "world.records_resolve_target",
            worldRecords.TryResolveTarget("OBJ_BM_PACKAGE_01", options.DefaultMapId, out var packageRecord) &&
            packageRecord.RecordId == "MAN-BM-OBJ_BM_PACKAGE_01" &&
            packageRecord.RecordType == WorldEntityKinds.Interactable &&
            worldRecords.TryResolveTarget(
                "MAN-BM-OBJ_BM_PACKAGE_02", options.DefaultMapId, out _),
            packageRecord?.RecordId);

        WorldEntityInstance MakeFixtureInteractable(
            string entityId,
            string recordId,
            double x,
            int respawnSeconds,
            string claimPolicy = WorldEntityClaimPolicies.Shared)
        {
            var interactable = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = recordId,
                Kind = WorldEntityKinds.Interactable,
                TemplateIds = new[] { "OBJ_BM_PACKAGE_01" },
                MapId = options.DefaultMapId,
                FloorId = "OVERWORLD",
                X = x,
                Y = 0,
                Quantity = 1,
                RespawnSeconds = respawnSeconds,
                ClaimPolicy = claimPolicy
            };
            interactable.Initialize();
            return interactable;
        }

        WorldEntityInstance MakeFixtureNpc(string entityId)
        {
            var npc = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = "MAN-BM-NPC_LYAN",
                Kind = WorldEntityKinds.Npc,
                TemplateIds = new[] { "NPC_LYAN" },
                MapId = options.DefaultMapId,
                FloorId = "OVERWORLD",
                X = 42,
                Y = 0,
                Quantity = 1,
                RespawnSeconds = 0
            };
            npc.Initialize();
            return npc;
        }

        var interactClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 5, 0, 0, TimeSpan.Zero));
        var interactRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog(
                [],
                [
                    MakeFixtureInteractable(
                        "ENT_SELFCHECK_PKG_1", "MAN-BM-OBJ_BM_PACKAGE_01", 36, 20),
                    MakeFixtureInteractable(
                        "ENT_SELFCHECK_PKG_2", "MAN-BM-OBJ_BM_PACKAGE_02", 44, 20),
                    MakeFixtureInteractable(
                        "ENT_SELFCHECK_PKG_3", "MAN-BM-OBJ_BM_PACKAGE_03", 52, 20),
                    MakeFixtureNpc("ENT_SELFCHECK_NPC")
                ]),
            interactClock);
        var interactStates = new InMemoryQuestStateStore();
        var interactQuests = new InMemoryQuestService(
            questCatalog, interactStates, worldRecords, interactClock);
        var interactInventory = new InMemoryInventoryService(new InMemoryInventoryStateStore());
        var fixedRoller = new FixedYieldRoller(2);
        var interactOptions = new InteractionOptions
        {
            Enabled = true,
            MaxInteractionDistanceWu = 5,
            AssumedProfessionLevel = 1
        };
        var interactions = new InMemoryInteractionService(
            interactRegistry,
            worldRecords,
            interactQuests,
            interactInventory,
            services.GetRequiredService<IWorldGeometryService>(),
            interactClock,
            fixedRoller,
            new GatherClaimStore(interactClock),
            interactOptions);

        var interactActor = NewPlayer("CHR_SELFCHECK_INTERACT");
        interactActor.X = 36;
        interactActor.Y = 0;
        var interactAccepted = interactQuests.Accept(interactActor, "P00-01");
        Check(
            "interact.quest_accepted",
            interactAccepted.Accepted && interactAccepted.State?.State == QuestStates.Active,
            interactAccepted.Failure?.Code);

        var badTargetShape = interactions.Interact(
            interactActor, "not-an-entity", new string('0', 32));
        Check(
            "interact.invalid_payload",
            badTargetShape.Failure?.Code == P1ErrorCodes.InvalidPayload,
            badTargetShape.Failure?.Code);

        var missingInteractTarget = interactions.Interact(
            interactActor, "ENT_SELFCHECK_MISSING", new string('1', 31) + "a");
        Check(
            "interact.target_not_found",
            missingInteractTarget.Failure?.Code == InteractionErrorCodes.TargetNotFound,
            missingInteractTarget.Failure?.Code);

        var npcTarget = interactions.Interact(
            interactActor, "ENT_SELFCHECK_NPC", new string('1', 31) + "b");
        Check(
            "interact.invalid_target",
            npcTarget.Failure?.Code == InteractionErrorCodes.InvalidTarget,
            npcTarget.Failure?.Code);

        var collect1 = interactions.Interact(
            interactActor, "ENT_SELFCHECK_PKG_1", new string('1', 31) + "c");
        Check(
            "interact.collect_package",
            collect1.Accepted &&
            collect1.Result is
            {
                Kind: WorldEntityKinds.Interactable,
                Outcome: "collected",
                TargetState: WorldEntityStates.Depleted,
                RecordId: "MAN-BM-OBJ_BM_PACKAGE_01",
                Yield: null,
                RespawnAtUtc: not null
            } &&
            collect1.Result.QuestUpdates.SingleOrDefault() is
            {
                State: QuestStates.Active,
                Revision: 3
            } collect1Quest &&
            collect1Quest.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 1,
            collect1.Failure?.Code ?? collect1.Result?.TargetState);

        var collect1Replay = interactions.Interact(
            interactActor, "ENT_SELFCHECK_PKG_1", new string('1', 31) + "c");
        Check(
            "interact.idempotency_replay",
            collect1Replay.Accepted && ReferenceEquals(collect1Replay.Result, collect1.Result),
            collect1Replay.Failure?.Code);

        var collectConflict = interactions.Interact(
            interactActor, "ENT_SELFCHECK_PKG_2", new string('1', 31) + "c");
        Check(
            "interact.idempotency_conflict",
            collectConflict.Failure?.Code == InteractionErrorCodes.IdempotencyConflict,
            collectConflict.Failure?.Code);

        var collectDepleted = interactions.Interact(
            interactActor, "ENT_SELFCHECK_PKG_1", new string('1', 31) + "d");
        Check(
            "interact.target_depleted",
            collectDepleted.Failure?.Code == InteractionErrorCodes.TargetNotAvailable,
            collectDepleted.Failure?.Code);

        var farInteractor = NewPlayer("CHR_SELFCHECK_INTERACT_FAR");
        var farCollect = interactions.Interact(
            farInteractor, "ENT_SELFCHECK_PKG_3", new string('1', 31) + "e");
        Check(
            "interact.out_of_range",
            farCollect.Failure is
            {
                Code: InteractionErrorCodes.OutOfRange,
                Retryable: true
            },
            farCollect.Failure?.Code);

        interactActor.X = 44;
        var collect2 = interactions.Interact(
            interactActor, "ENT_SELFCHECK_PKG_2", new string('2', 31) + "a");
        Check(
            "interact.collect_second",
            collect2.Accepted &&
            collect2.Result!.QuestUpdates.SingleOrDefault() is
            {
                State: QuestStates.Active,
                Revision: 4
            },
            collect2.Failure?.Code);

        interactActor.X = 52;
        var collect3 = interactions.Interact(
            interactActor, "ENT_SELFCHECK_PKG_3", new string('3', 31) + "a");
        Check(
            "interact.ready_to_turn_in",
            collect3.Accepted &&
            collect3.Result!.QuestUpdates.SingleOrDefault() is
            {
                State: QuestStates.ReadyToTurnIn,
                Revision: 5
            } collect3Quest &&
            collect3Quest.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 3,
            collect3.Failure?.Code ?? collect3.Result?.QuestUpdates.SingleOrDefault()?.State);

        var interactTurnIn = interactQuests.TurnIn(interactActor, "P00-01");
        Check(
            "interact.turn_in_completed",
            interactTurnIn.Accepted &&
            interactTurnIn.State is { State: QuestStates.Completed, Revision: 6 },
            interactTurnIn.Failure?.Code ?? interactTurnIn.State?.State);

        interactClock.Advance(TimeSpan.FromSeconds(20));
        var sharedRespawn = interactRegistry.Update();
        Check("interact.respawn_shared", sharedRespawn == 3, $"respawned={sharedRespawn}");

        var dedupeActor = NewPlayer("CHR_SELFCHECK_DEDUPE");
        dedupeActor.X = 36;
        dedupeActor.Y = 0;
        interactQuests.Accept(dedupeActor, "P00-01");
        var dedupe1 = interactions.Interact(
            dedupeActor, "ENT_SELFCHECK_PKG_1", new string('4', 31) + "a");
        interactClock.Advance(TimeSpan.FromSeconds(20));
        interactRegistry.Update();
        var dedupe2 = interactions.Interact(
            dedupeActor, "ENT_SELFCHECK_PKG_1", new string('5', 31) + "a");
        var dedupeState = interactQuests.GetState(dedupeActor.CharacterId, "P00-01").State;
        Check(
            "interact.distinct_record_dedupe",
            dedupe1.Accepted &&
            dedupe2.Accepted &&
            dedupe2.Result!.QuestUpdates.Count == 0 &&
            dedupeState is { State: QuestStates.Active } &&
            dedupeState.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 1,
            $"{dedupe2.Failure?.Code} updates={dedupe2.Result?.QuestUpdates.Count}");

        // Production Rules §5: P00-01 packages are per-character claims — two
        // characters collect all three at the same time without waiting for a
        // global respawn, and the shared registry state never leaves AVAILABLE.
        var packageClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 6, 0, 0, TimeSpan.Zero));
        var packageRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog(
                [],
                [
                    MakeFixtureInteractable(
                        "ENT_SELFCHECK_PKG1", "MAN-BM-OBJ_BM_PACKAGE_01", 36, 20,
                        WorldEntityClaimPolicies.PerCharacter),
                    MakeFixtureInteractable(
                        "ENT_SELFCHECK_PKG2", "MAN-BM-OBJ_BM_PACKAGE_02", 44, 20,
                        WorldEntityClaimPolicies.PerCharacter),
                    MakeFixtureInteractable(
                        "ENT_SELFCHECK_PKG3", "MAN-BM-OBJ_BM_PACKAGE_03", 52, 20,
                        WorldEntityClaimPolicies.PerCharacter)
                ]),
            packageClock);
        var packageQuests = new InMemoryQuestService(
            questCatalog, new InMemoryQuestStateStore(), worldRecords, packageClock);
        var packageInteractions = new InMemoryInteractionService(
            packageRegistry,
            worldRecords,
            packageQuests,
            new InMemoryInventoryService(new InMemoryInventoryStateStore()),
            services.GetRequiredService<IWorldGeometryService>(),
            packageClock,
            fixedRoller,
            new GatherClaimStore(packageClock),
            interactOptions);

        var packageActorA = NewPlayer("CHR_SELFCHECK_PACKAGE_A");
        var packageActorB = NewPlayer("CHR_SELFCHECK_PACKAGE_B");
        packageQuests.Accept(packageActorA, "P00-01");
        packageQuests.Accept(packageActorB, "P00-01");

        var packageTargets = new[]
        {
            ("ENT_SELFCHECK_PKG1", 36.0),
            ("ENT_SELFCHECK_PKG2", 44.0),
            ("ENT_SELFCHECK_PKG3", 52.0)
        };
        var packageOutcomes = new InteractionOutcome?[packageTargets.Length, 2];
        using (var packageBarrier = new Barrier(2))
        {
            RunBarrierParallel(2, index =>
            {
                var session = index == 0 ? packageActorA : packageActorB;
                var keyStem = index == 0 ? 'a' : 'b';
                for (var step = 0; step < packageTargets.Length; step++)
                {
                    session.X = packageTargets[step].Item2;
                    session.Y = 0;
                    packageBarrier.SignalAndWait();
                    packageOutcomes[step, index] = packageInteractions.Interact(
                        session,
                        packageTargets[step].Item1,
                        $"{keyStem}{step}{new string('0', 30)}");
                }
            });
        }

        var packageAccepted = packageOutcomes
            .Cast<InteractionOutcome?>()
            .Count(outcome => outcome is { Accepted: true });
        var packageStateA = packageQuests.GetState(packageActorA.CharacterId, "P00-01").State;
        var packageStateB = packageQuests.GetState(packageActorB.CharacterId, "P00-01").State;
        Check(
            "interact.package_per_character_parallel",
            packageAccepted == 6 &&
            packageStateA is { State: QuestStates.ReadyToTurnIn } &&
            packageStateB is { State: QuestStates.ReadyToTurnIn } &&
            packageStateA.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 3 &&
            packageStateB.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 3,
            $"accepted={packageAccepted}/6 a={packageStateA?.State} b={packageStateB?.State}");

        packageRegistry.TryGet("ENT_SELFCHECK_PKG1", out var packageEntity);
        Check(
            "interact.package_state_stays_available",
            packageEntity.State == WorldEntityStates.Available &&
            packageRegistry.Update() == 0,
            packageEntity.State);

        packageActorA.X = 36;
        packageActorA.Y = 0;
        var packageReclaim = packageInteractions.Interact(
            packageActorA, "ENT_SELFCHECK_PKG1", new string('7', 32));
        Check(
            "interact.package_per_character_window",
            packageReclaim.Failure?.Code == InteractionErrorCodes.TargetNotAvailable,
            packageReclaim.Failure?.Code);

        packageClock.Advance(TimeSpan.FromSeconds(20));
        var packageReclaimAfterWindow = packageInteractions.Interact(
            packageActorA, "ENT_SELFCHECK_PKG1", new string('8', 32));
        Check(
            "interact.package_per_character_respawn",
            packageReclaimAfterWindow.Accepted &&
            packageReclaimAfterWindow.Result!.QuestUpdates.Count == 0 &&
            packageQuests.GetState(packageActorA.CharacterId, "P00-01").State is
            {
                State: QuestStates.ReadyToTurnIn
            },
            packageReclaimAfterWindow.Failure?.Code);

        // Progress dedupe scope: unique(actor, quest, objective, event-or-record)
        // — state is per character + quest, so the objective scope keeps two
        // valid objectives that reference the same record independent.
        if (!questCatalog.TryGet("P00-01", out var dedupeBaseQuest))
        {
            throw new InvalidOperationException("P00-01 must exist for the dedupe self-check.");
        }

        QuestDefinition MakeSyntheticQuest(
            string questId, params QuestObjectiveDefinition[] objectives) =>
            dedupeBaseQuest with
            {
                QuestId = questId,
                Objectives = objectives,
                InitialStepId = QuestStepIds.FromObjectiveId(objectives[0].ObjectiveId),
                PrerequisiteQuestIds = []
            };

        var syntheticDefinitions = new Dictionary<string, QuestDefinition>(StringComparer.Ordinal)
        {
            ["TEST-DEDUPE-01"] = MakeSyntheticQuest(
                "TEST-DEDUPE-01",
                new QuestObjectiveDefinition(
                    "OBJ_TEST_SHARE_A", QuestObjectiveTypes.Collect,
                    ["MAN-BM-OBJ_BM_PACKAGE_01"], 1, options.DefaultMapId),
                new QuestObjectiveDefinition(
                    "OBJ_TEST_SHARE_B", QuestObjectiveTypes.Collect,
                    ["MAN-BM-OBJ_BM_PACKAGE_01", "MAN-BM-OBJ_BM_PACKAGE_02"], 2,
                    options.DefaultMapId)),
            ["TEST-SEQ-01"] = MakeSyntheticQuest(
                "TEST-SEQ-01",
                new QuestObjectiveDefinition(
                    "OBJ_TEST_SEQ_A", QuestObjectiveTypes.Collect,
                    ["MAN-BM-OBJ_BM_PACKAGE_01"], 1, options.DefaultMapId),
                new QuestObjectiveDefinition(
                    "OBJ_TEST_SEQ_B", QuestObjectiveTypes.Collect,
                    ["MAN-BM-OBJ_BM_PACKAGE_03"], 1, options.DefaultMapId)),
            ["TEST-KILL-01"] = MakeSyntheticQuest(
                "TEST-KILL-01",
                new QuestObjectiveDefinition(
                    "OBJ_TEST_KILL_A", QuestObjectiveTypes.Kill,
                    ["MAN-BM-SPAWN_BM_01"], 2, options.DefaultMapId),
                new QuestObjectiveDefinition(
                    "OBJ_TEST_KILL_B", QuestObjectiveTypes.Kill,
                    ["MAN-BM-SPAWN_BM_01"], 2, options.DefaultMapId))
        };
        var syntheticQuests = new InMemoryQuestService(
            new QuestCatalog(syntheticDefinitions),
            new InMemoryQuestStateStore(),
            worldRecords,
            interactClock);
        var dedupeScopeActor = NewPlayer("CHR_SELFCHECK_DEDUPE_SCOPE");

        syntheticQuests.Accept(dedupeScopeActor, "TEST-DEDUPE-01");
        syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('a', 32),
            QuestProgressEventTypes.InteractClaim, "MAN-BM-OBJ_BM_PACKAGE_01",
            options.DefaultMapId);
        var sharedRecordState = syntheticQuests.GetState(
            dedupeScopeActor.CharacterId, "TEST-DEDUPE-01").State;
        Check(
            "quest.dedupe_two_objectives_share_record",
            sharedRecordState is { State: QuestStates.Active } &&
            sharedRecordState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_A") == 1 &&
            sharedRecordState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_B") == 1,
            $"{sharedRecordState?.State} " +
            $"a={sharedRecordState?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_A")} " +
            $"b={sharedRecordState?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_B")}");

        var duplicateEvent = syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('b', 32),
            QuestProgressEventTypes.InteractClaim, "MAN-BM-OBJ_BM_PACKAGE_01",
            options.DefaultMapId);
        var duplicateState = syntheticQuests.GetState(
            dedupeScopeActor.CharacterId, "TEST-DEDUPE-01").State;
        Check(
            "quest.dedupe_duplicate_event",
            duplicateEvent.Count == 0 &&
            duplicateState?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_A") == 1 &&
            duplicateState?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_B") == 1,
            $"updates={duplicateEvent.Count}");

        syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('c', 32),
            QuestProgressEventTypes.InteractClaim, "MAN-BM-OBJ_BM_PACKAGE_02",
            options.DefaultMapId);
        var secondRecordState = syntheticQuests.GetState(
            dedupeScopeActor.CharacterId, "TEST-DEDUPE-01").State;
        Check(
            "quest.dedupe_second_record",
            secondRecordState is { State: QuestStates.ReadyToTurnIn } &&
            secondRecordState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_B") == 2,
            secondRecordState?.State);

        syntheticQuests.Accept(dedupeScopeActor, "TEST-SEQ-01");
        syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('d', 32),
            QuestProgressEventTypes.InteractClaim, "MAN-BM-OBJ_BM_PACKAGE_01",
            options.DefaultMapId);
        var sequentialState = syntheticQuests.GetState(
            dedupeScopeActor.CharacterId, "TEST-SEQ-01").State;
        Check(
            "quest.dedupe_sequential_step_guard",
            sequentialState is { State: QuestStates.Active } &&
            sequentialState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SEQ_A") == 1 &&
            sequentialState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SEQ_B") == 0,
            $"{sequentialState?.State} " +
            $"b={sequentialState?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SEQ_B")}");

        syntheticQuests.Accept(dedupeScopeActor, "TEST-KILL-01");
        syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('e', 32),
            QuestProgressEventTypes.Kill, "MAN-BM-SPAWN_BM_01", options.DefaultMapId);
        var killFirst = syntheticQuests.GetState(
            dedupeScopeActor.CharacterId, "TEST-KILL-01").State;
        var killReplay = syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('e', 32),
            QuestProgressEventTypes.Kill, "MAN-BM-SPAWN_BM_01", options.DefaultMapId);
        syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('f', 32),
            QuestProgressEventTypes.Kill, "MAN-BM-SPAWN_BM_01", options.DefaultMapId);
        var killSecond = syntheticQuests.GetState(
            dedupeScopeActor.CharacterId, "TEST-KILL-01").State;
        Check(
            "quest.dedupe_kill_event_scope",
            killFirst?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_KILL_A") == 1 &&
            killFirst?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_KILL_B") == 1 &&
            killReplay.Count == 0 &&
            killSecond is { State: QuestStates.ReadyToTurnIn } &&
            killSecond.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_KILL_A") == 2 &&
            killSecond.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_KILL_B") == 2,
            $"{killSecond?.State} " +
            $"a={killSecond?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_KILL_A")} " +
            $"b={killSecond?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_KILL_B")}");

        var losInteractions = new InMemoryInteractionService(
            new WorldEntityRegistry(
                new WorldEntityCatalog(
                    [],
                    [
                        MakeFixtureInteractable(
                            "ENT_SELFCHECK_LOS_BLOCKED", "MAN-BM-OBJ_BM_PACKAGE_01", 46.5, 60),
                        MakeFixtureInteractable(
                            "ENT_SELFCHECK_LOS_CLEAR", "MAN-BM-OBJ_BM_PACKAGE_01", 40, 60)
                    ]),
                interactClock),
            worldRecords,
            interactQuests,
            interactInventory,
            geometry,
            interactClock,
            fixedRoller,
            new GatherClaimStore(interactClock),
            interactOptions);

        var losBlockedActor = NewPlayer("CHR_SELFCHECK_INTERACT_LOS");
        losBlockedActor.X = 44;
        losBlockedActor.Y = 0;
        var losBlocked = losInteractions.Interact(
            losBlockedActor, "ENT_SELFCHECK_LOS_BLOCKED", new string('6', 31) + "a");
        Check(
            "interact.los_blocked",
            losBlocked.Failure is
            {
                Code: InteractionErrorCodes.OutOfRange,
                Retryable: true
            },
            losBlocked.Failure?.Code);

        losBlockedActor.X = 36;
        var losClear = losInteractions.Interact(
            losBlockedActor, "ENT_SELFCHECK_LOS_CLEAR", new string('7', 31) + "a");
        Check(
            "interact.los_allowed",
            losClear.Accepted &&
            losClear.Result is { Outcome: "collected", TargetState: WorldEntityStates.Depleted },
            losClear.Failure?.Code);

        WorldEntityInstance MakeFixtureNode(
            string entityId,
            string recordId,
            double x,
            int respawnSeconds)
        {
            var node = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = recordId,
                Kind = WorldEntityKinds.GatherNode,
                TemplateIds = new[] { "NODE_BM_ORE_01" },
                MapId = options.DefaultMapId,
                FloorId = "OVERWORLD",
                X = x,
                Y = 0,
                Quantity = 1,
                RespawnSeconds = respawnSeconds
            };
            node.Initialize();
            return node;
        }

        var gatherInteractions = new InMemoryInteractionService(
            new WorldEntityRegistry(
                new WorldEntityCatalog(
                    [],
                    [
                        MakeFixtureNode("ENT_SELFCHECK_NODE_ORE", "MAN-BM-NODE_BM_ORE_01", 21, 60),
                        MakeFixtureNode("ENT_SELFCHECK_NODE_T2", "MAN-BM-NODE_BM_HERB_02", 132, 120)
                    ]),
                interactClock),
            worldRecords,
            interactQuests,
            interactInventory,
            services.GetRequiredService<IWorldGeometryService>(),
            interactClock,
            fixedRoller,
            new GatherClaimStore(interactClock),
            interactOptions);

        var gatherer1 = NewPlayer("CHR_SELFCHECK_GATHER_1");
        gatherer1.X = 21;
        gatherer1.Y = 0;
        var gather1 = gatherInteractions.Interact(
            gatherer1, "ENT_SELFCHECK_NODE_ORE", new string('8', 31) + "a");
        Check(
            "interact.gather_claim",
            gather1.Accepted &&
            gather1.Result is
            {
                Kind: WorldEntityKinds.GatherNode,
                Outcome: "gathered",
                TargetState: WorldEntityStates.Available,
                RecordId: "MAN-BM-NODE_BM_ORE_01",
                RespawnAtUtc: not null
            } &&
            gather1.Result.Yield is { ItemId: "MAT-ORE-01", Quantity: 2 },
            gather1.Failure?.Code ?? gather1.Result?.Outcome);

        var gather1Inventory = interactInventory.GetSnapshot(gatherer1.CharacterId);
        Check(
            "interact.gather_inventory",
            gather1Inventory.InventoryRevision == 1 &&
            gather1Inventory.Items.Single() is
            {
                TemplateId: "MAT-ORE-01",
                Stack: 2,
                Location: InventoryLocations.Bag
            },
            $"revision={gather1Inventory.InventoryRevision} items={gather1Inventory.Items.Count}");

        var gather1Replay = gatherInteractions.Interact(
            gatherer1, "ENT_SELFCHECK_NODE_ORE", new string('8', 31) + "a");
        Check(
            "interact.gather_replay_no_double",
            gather1Replay.Accepted && ReferenceEquals(gather1Replay.Result, gather1.Result) &&
            interactInventory.GetSnapshot(gatherer1.CharacterId).Items.Count == 1,
            gather1Replay.Failure?.Code);

        var gather1Cooldown = gatherInteractions.Interact(
            gatherer1, "ENT_SELFCHECK_NODE_ORE", new string('9', 31) + "a");
        Check(
            "interact.gather_shard_cooldown",
            gather1Cooldown.Failure?.Code == InteractionErrorCodes.TargetNotAvailable &&
            interactInventory.GetSnapshot(gatherer1.CharacterId).Items.Count == 1,
            gather1Cooldown.Failure?.Code);

        var gatherer2 = NewPlayer("CHR_SELFCHECK_GATHER_2");
        gatherer2.X = 21;
        gatherer2.Y = 0;
        var gather2 = gatherInteractions.Interact(
            gatherer2, "ENT_SELFCHECK_NODE_ORE", new string('a', 32));
        Check(
            "interact.gather_shard_other_character",
            gather2.Accepted &&
            interactInventory.GetSnapshot(gatherer2.CharacterId).Items.Count == 1 &&
            interactInventory.GetSnapshot(gatherer1.CharacterId).Items.Count == 1,
            gather2.Failure?.Code);

        interactClock.Advance(TimeSpan.FromSeconds(60));
        var gather1Again = gatherInteractions.Interact(
            gatherer1, "ENT_SELFCHECK_NODE_ORE", new string('b', 32));
        Check(
            "interact.gather_respawn_per_character",
            gather1Again.Accepted &&
            interactInventory.GetSnapshot(gatherer1.CharacterId) is
            {
                InventoryRevision: 2,
                Items: { Count: 2 }
            },
            $"{gather1Again.Failure?.Code} revision={interactInventory.GetSnapshot(gatherer1.CharacterId).InventoryRevision}");

        var professionActor = NewPlayer("CHR_SELFCHECK_GATHER_GATE");
        professionActor.X = 132;
        professionActor.Y = 0;
        var professionGate = gatherInteractions.Interact(
            professionActor, "ENT_SELFCHECK_NODE_T2", new string('c', 32));
        Check(
            "interact.profession_gate",
            professionGate.Failure?.Code == InteractionErrorCodes.ProfessionLevelInsufficient &&
            interactInventory.GetSnapshot(professionActor.CharacterId).Items.Count == 0,
            professionGate.Failure?.Code);

        // ─── barrier-coordinated concurrency + failure injection (QOD-A) ───

        var raceInventory = new InMemoryInventoryService(new InMemoryInventoryStateStore());
        var raceInteractions = new InMemoryInteractionService(
            new WorldEntityRegistry(
                new WorldEntityCatalog(
                    [],
                    [
                        MakeFixtureNode("ENT_SELFCHECK_RACE_NODE", "MAN-BM-NODE_BM_ORE_01", 21, 60),
                        MakeFixtureInteractable(
                            "ENT_SELFCHECK_RACE_PKG", "MAN-BM-OBJ_BM_PACKAGE_01", 36, 20)
                    ]),
                interactClock),
            worldRecords,
            interactQuests,
            raceInventory,
            services.GetRequiredService<IWorldGeometryService>(),
            interactClock,
            fixedRoller,
            new GatherClaimStore(interactClock),
            interactOptions);

        // Same key, same payload in parallel: both requests must replay the
        // winner's stored result — one interactionId, one yield.
        var raceActor = NewPlayer("CHR_SELFCHECK_RACE_GATHER");
        raceActor.X = 21;
        raceActor.Y = 0;
        var sameKeyRace = Guid.NewGuid().ToString("N");
        var sameKeyRaceOutcomes = new InteractionOutcome[2];
        RunBarrierParallel(2, index =>
        {
            sameKeyRaceOutcomes[index] = raceInteractions.Interact(
                raceActor, "ENT_SELFCHECK_RACE_NODE", sameKeyRace);
        });
        var sameKeyRaceAccepted = sameKeyRaceOutcomes.Count(outcome => outcome.Accepted);
        var sameKeyRaceIds = sameKeyRaceOutcomes
            .Where(outcome => outcome.Accepted)
            .Select(outcome => outcome.Result!.InteractionId)
            .Distinct()
            .Count();
        Check(
            "interact.parallel_same_key_single_result",
            sameKeyRaceAccepted == 2 &&
            sameKeyRaceIds == 1 &&
            ReferenceEquals(sameKeyRaceOutcomes[0].Result, sameKeyRaceOutcomes[1].Result) &&
            raceInventory.GetSnapshot(raceActor.CharacterId).Items.Count == 1,
            $"accepted={sameKeyRaceAccepted} distinctIds={sameKeyRaceIds} " +
            $"codes={string.Join(",", sameKeyRaceOutcomes.Select(o => o.Failure?.Code ?? "ok"))}");

        // Two different keys, same character/node in parallel: exactly one
        // claim wins, the other gets the per-character cooldown.
        var twoKeyActor = NewPlayer("CHR_SELFCHECK_RACE_2KEY");
        twoKeyActor.X = 21;
        twoKeyActor.Y = 0;
        var twoKeyOutcomes = new InteractionOutcome[2];
        RunBarrierParallel(2, index =>
        {
            twoKeyOutcomes[index] = raceInteractions.Interact(
                twoKeyActor, "ENT_SELFCHECK_RACE_NODE", Guid.NewGuid().ToString("N"));
        });
        var twoKeyAccepted = twoKeyOutcomes.Count(outcome => outcome.Accepted);
        var twoKeyCooldown = twoKeyOutcomes.Count(outcome =>
            !outcome.Accepted &&
            outcome.Failure?.Code == InteractionErrorCodes.TargetNotAvailable);
        Check(
            "interact.parallel_two_keys_single_grant",
            twoKeyAccepted == 1 && twoKeyCooldown == 1 &&
            raceInventory.GetSnapshot(twoKeyActor.CharacterId).Items.Count == 1,
            $"accepted={twoKeyAccepted} " +
            $"codes={string.Join(",", twoKeyOutcomes.Select(o => o.Failure?.Code ?? "ok"))}");

        // Two characters claim the same node in parallel: per-character
        // shards mean both win independently.
        var shardA = NewPlayer("CHR_SELFCHECK_SHARD_A");
        shardA.X = 21;
        shardA.Y = 0;
        var shardB = NewPlayer("CHR_SELFCHECK_SHARD_B");
        shardB.X = 21;
        shardB.Y = 0;
        var shardActors = new[] { shardA, shardB };
        var shardOutcomes = new InteractionOutcome[2];
        RunBarrierParallel(2, index =>
        {
            shardOutcomes[index] = raceInteractions.Interact(
                shardActors[index], "ENT_SELFCHECK_RACE_NODE", Guid.NewGuid().ToString("N"));
        });
        Check(
            "interact.parallel_two_characters_independent",
            shardOutcomes.All(outcome => outcome.Accepted) &&
            raceInventory.GetSnapshot(shardA.CharacterId).Items.Count == 1 &&
            raceInventory.GetSnapshot(shardB.CharacterId).Items.Count == 1,
            $"codes={string.Join(",", shardOutcomes.Select(o => o.Failure?.Code ?? "ok"))}");

        // Two characters race for one shared INTERACTABLE: the registry's
        // atomic check-and-set lets exactly one collect.
        var pkgA = NewPlayer("CHR_SELFCHECK_RACE_PKG_A");
        pkgA.X = 36;
        pkgA.Y = 0;
        var pkgB = NewPlayer("CHR_SELFCHECK_RACE_PKG_B");
        pkgB.X = 36;
        pkgB.Y = 0;
        var pkgActors = new[] { pkgA, pkgB };
        var pkgOutcomes = new InteractionOutcome[2];
        RunBarrierParallel(2, index =>
        {
            pkgOutcomes[index] = raceInteractions.Interact(
                pkgActors[index], "ENT_SELFCHECK_RACE_PKG", Guid.NewGuid().ToString("N"));
        });
        var pkgAccepted = pkgOutcomes.Count(outcome => outcome.Accepted);
        var pkgDepleted = pkgOutcomes.Count(outcome =>
            !outcome.Accepted &&
            outcome.Failure?.Code == InteractionErrorCodes.TargetNotAvailable);
        Check(
            "interact.parallel_shared_interactable_single_claim",
            pkgAccepted == 1 && pkgDepleted == 1,
            $"accepted={pkgAccepted} " +
            $"codes={string.Join(",", pkgOutcomes.Select(o => o.Failure?.Code ?? "ok"))}");

        // Failure after the reservation: the claim is released by token, the
        // node stays claimable and the retry grants exactly once.
        var failInventory = new InMemoryInventoryService(new InMemoryInventoryStateStore());
        var raceFailOnceInventory = new FailOnceInventoryDecorator(failInventory);
        var failInteractions = new InMemoryInteractionService(
            new WorldEntityRegistry(
                new WorldEntityCatalog(
                    [],
                    [MakeFixtureNode("ENT_SELFCHECK_FAIL_NODE", "MAN-BM-NODE_BM_ORE_01", 21, 60)]),
                interactClock),
            worldRecords,
            interactQuests,
            raceFailOnceInventory,
            services.GetRequiredService<IWorldGeometryService>(),
            interactClock,
            fixedRoller,
            new GatherClaimStore(interactClock),
            interactOptions);

        var failGatherer = NewPlayer("CHR_SELFCHECK_GATHER_FAIL");
        failGatherer.X = 21;
        failGatherer.Y = 0;
        var failedGather = failInteractions.Interact(
            failGatherer, "ENT_SELFCHECK_FAIL_NODE", Guid.NewGuid().ToString("N"));
        Check(
            "interact.fail_after_reserve_rejected",
            !failedGather.Accepted &&
            failedGather.Failure is
            {
                Code: InteractionErrorCodes.TargetNotAvailable,
                Retryable: true
            } &&
            failInventory.GetSnapshot(failGatherer.CharacterId).Items.Count == 0,
            failedGather.Failure?.Code);

        var retriedGather = failInteractions.Interact(
            failGatherer, "ENT_SELFCHECK_FAIL_NODE", Guid.NewGuid().ToString("N"));
        Check(
            "interact.fail_after_reserve_retry_grants_once",
            retriedGather.Accepted &&
            failInventory.GetSnapshot(failGatherer.CharacterId) is { Items: { Count: 1 } },
            retriedGather.Failure?.Code);

        var inventoryActor = NewPlayer("CHR_SELFCHECK_INVENTORY");
        var emptyInventory = inventory.GetSnapshot(inventoryActor.CharacterId);
        Check(
            "inventory.empty",
            emptyInventory.InventoryRevision == 0 && emptyInventory.Items.Count == 0,
            $"revision={emptyInventory.InventoryRevision}");

        var granted = inventory.Apply(inventoryActor, new InventoryMutation
        {
            AddItems =
            [
                new ItemGrant
                {
                    TemplateId = "EQ-MK-CHEST-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Bag,
                    Durability = 100
                }
            ],
            CurrencyDeltas = [new CurrencyDelta { CurrencyId = "COIN", Amount = 20 }]
        });
        Check(
            "inventory.grant",
            granted.IsSuccess &&
            granted.Snapshot!.InventoryRevision == 1 &&
            granted.Snapshot.Items.Count == 1 &&
            granted.Snapshot.Currencies.Single().Amount == 20,
            granted.ErrorCode ?? $"revision={granted.Snapshot?.InventoryRevision}");

        // Q5 audit (owner ask on #87): the reward coat serialized durability 0.
        // The canonical catalog states a durability for every equipment row
        // (`Item_Rarity_Variant_Catalog_vi.csv`, column `durability` = 100 for
        // EQ-MK-CHEST-T1-R-COMMON) and leaves the cell blank only for consumables,
        // so 0 was an uninitialized field, not "non-durable". A grant that names no
        // durability now takes the source; an explicit number still wins; a blank
        // source cell stays 0 because that is what the row says, not a default.
        var durabilityActor = NewPlayer("CHR_SELFCHECK_DURABILITY");
        var durabilityGrant = inventory.Apply(durabilityActor, new InventoryMutation
        {
            AddItems =
            [
                new ItemGrant
                {
                    TemplateId = "EQ-MK-CHEST-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Bag
                },
                new ItemGrant
                {
                    TemplateId = "POT-HP-01",
                    Stack = 1,
                    Location = InventoryLocations.Bag
                },
                new ItemGrant
                {
                    TemplateId = "EQ-MK-HAT-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Bag,
                    Durability = 7
                },
                new ItemGrant
                {
                    TemplateId = "UNKNOWN_TEMPLATE_X",
                    Stack = 1,
                    Location = InventoryLocations.Bag
                }
            ]
        });
        Check(
            "inventory.grant_durability_comes_from_the_catalog",
            durabilityGrant.IsSuccess &&
            durabilityGrant.Snapshot!.Items.Single(item =>
                item.TemplateId == "EQ-MK-CHEST-T1-R-COMMON").Durability == 100 &&
            durabilityGrant.Snapshot.Items.Single(item =>
                item.TemplateId == "POT-HP-01").Durability == 0 &&
            durabilityGrant.Snapshot.Items.Single(item =>
                item.TemplateId == "EQ-MK-HAT-T1-R-COMMON").Durability == 7 &&
            durabilityGrant.Snapshot.Items.Single(item =>
                item.TemplateId == "UNKNOWN_TEMPLATE_X").Durability == 0 &&
            itemCatalog.TryGet("EQ-MK-CHEST-T1-R-COMMON", out var chestEntry) &&
            chestEntry.Durability == 100 &&
            itemCatalog.TryGet("POT-HP-01", out var potionEntry) &&
            potionEntry.Durability is null,
            $"grant={durabilityGrant.ErrorCode} items=" +
            string.Join(
                "|",
                (durabilityGrant.Snapshot?.Items ?? []).Select(item =>
                    $"{item.TemplateId}:{item.Durability}")));

        // DEC-023 §2 publishes a four-number no-gear oracle and two one-item oracles.
        // The aggregation is deliberately not wired into combat - an accepted equip
        // still moves only the inventory - but the rules land now, so the day gear does
        // apply cannot quietly count weapon_power twice, invent a key for an unknown
        // label, or heal somebody by changing a maximum.
        var noGear = PlayerStatAggregation.Derive([]);
        Check(
            "stats.dec023_level_one_no_gear_oracle",
            noGear.HpMax == 198 && noGear.MpMax == 102 &&
            noGear.PhysicalAttack == 20 && noGear.Armor == 10,
            $"hp={noGear.HpMax} mp={noGear.MpMax} attack={noGear.PhysicalAttack} armor={noGear.Armor}");

        itemCatalog.TryGet("EQ-MK-WEAPON-T1-R-COMMON", out var oracleSword);
        itemCatalog.TryGet("EQ-MK-HAT-T1-R-COMMON", out var oracleHat);
        var sword = PlayerStatAggregation.Resolve(oracleSword);
        var hat = PlayerStatAggregation.Resolve(oracleHat);
        var swordOnly = PlayerStatAggregation.Derive([sword]);
        var hatOnly = PlayerStatAggregation.Derive([hat]);
        Check(
            "stats.dec023_one_item_oracles_are_38_and_14_not_50_and_16",
            sword.WeaponAttack == 12 && sword.Strength == 2 &&
            sword.Conflicts.Count == 0 && sword.UnsupportedLabels.Count == 0 &&
            swordOnly.PhysicalAttack == 38 &&
            hat.Armor == 2 && hat.Vitality == 1 && hat.Conflicts.Count == 0 &&
            hatOnly.Armor == 14 && hatOnly.HpMax == 212,
            $"sword.attack={swordOnly.PhysicalAttack} hat.hp={hatOnly.HpMax} hat.armor={hatOnly.Armor}");

        // The alias rule gets a teeth test: two disagreeing columns contribute nothing
        // and name the row, instead of summing (the 50 §2 rejects), taking max, or
        // dropping whichever column is less convenient.
        var conflicting = PlayerStatAggregation.Resolve(new ItemCatalogEntry(
            "EQ-TEST-CONFLICT", ItemCatalog.WeaponCategory, "WEAPON", "Kiếm", "CLASS_MINH_KIEM",
            1, "Thường", 1, null, "12", null, StatLabels.WeaponPowerPhysical, "9", null, null));
        Check(
            "stats.alias_conflict_contributes_nothing_and_names_the_row",
            conflicting.WeaponAttack == 0 &&
            conflicting.Conflicts.Count == 1 &&
            conflicting.Conflicts[0].Contains("EQ-TEST-CONFLICT", StringComparison.Ordinal) &&
            conflicting.Conflicts[0].Contains("weapon_power/primary_stat", StringComparison.Ordinal) &&
            conflicting.UnsupportedLabels.Count == 0 &&
            conflicting.UnsupportedValues.Count == 0,
            string.Join(" / ", conflicting.Conflicts));

        var unknownLabel = PlayerStatAggregation.Resolve(new ItemCatalogEntry(
            "EQ-TEST-UNKNOWN", ItemCatalog.ArmorCategory, "CHEST", "Áo", "CLASS_MINH_KIEM",
            1, "Thường", 1, null, null, null, "Chí mạng", "5", null, null));
        Check(
            "stats.unknown_stat_label_is_reported_not_invented",
            unknownLabel.UnsupportedLabels.SequenceEqual(["Chí mạng"]) &&
            unknownLabel.IsEmpty &&
            unknownLabel.Conflicts.Count == 0,
            string.Join(" / ", unknownLabel.UnsupportedLabels));

        // §6 leaves the rounding rule for fractional and percentage gear open, and the
        // shipped catalog is full of them (90 fractional weapon_power, 635 fractional
        // armor, 1628/1565 modifier strings). Refusing is the only honest reading until
        // somebody rules on it, so a fractional row must contribute zero and say so.
        var fractional = PlayerStatAggregation.Resolve(new ItemCatalogEntry(
            "EQ-TEST-FRACTION", ItemCatalog.ArmorCategory, "CHEST", "Áo", "CLASS_MINH_KIEM",
            1, "Tinh", 1, null, null, "1.1", StatLabels.ArmorLabel, "1.1", "HP hồi", "0.5%"));
        Check(
            "stats.fraction_and_percent_cells_are_refused_not_rounded",
            fractional.Armor == 0 &&
            fractional.IsEmpty &&
            fractional.Conflicts.Count == 0 &&
            fractional.UnsupportedValues.Count == 2 &&
            fractional.UnsupportedValues[0].Contains("1.1", StringComparison.Ordinal) &&
            fractional.UnsupportedLabels.SequenceEqual(["HP hồi"]),
            string.Join(" / ", fractional.UnsupportedValues));

        Check(
            "stats.max_change_clamps_and_never_heals",
            PlayerStatAggregation.ClampAfterMaxChange(210, 198) == 198 &&
            PlayerStatAggregation.ClampAfterMaxChange(198, 216) == 198 &&
            PlayerStatAggregation.ClampAfterMaxChange(0, 216) == 0 &&
            PlayerStatAggregation.ClampAfterMaxChange(150, 198) == 150,
            "210/216 losing an +18 hat -> 198/198, putting it back keeps 198, a dead actor stays at 0");

        var equipped = inventory.Apply(inventoryActor, new InventoryMutation
        {
            ExpectedRevision = 1,
            AddItems =
            [
                new ItemGrant
                {
                    TemplateId = "EQ-MK-CHEST-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Equipped,
                    Slot = "CHEST",
                    Durability = 100
                }
            ]
        });
        Check(
            "inventory.equip",
            equipped.IsSuccess &&
            equipped.Snapshot!.InventoryRevision == 2 &&
            equipped.Snapshot.Items.Count == 2,
            equipped.ErrorCode ?? $"revision={equipped.Snapshot?.InventoryRevision}");

        var slotClash = inventory.Apply(inventoryActor, new InventoryMutation
        {
            ExpectedRevision = 2,
            AddItems =
            [
                new ItemGrant
                {
                    TemplateId = "EQ-MK-CHEST-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Equipped,
                    Slot = "CHEST",
                    Durability = 100
                }
            ]
        });
        Check(
            "inventory.slot_occupied",
            slotClash.ErrorCode == InventoryErrorCodes.SlotOccupied,
            slotClash.ErrorCode);

        var missingItem = inventory.Apply(inventoryActor, new InventoryMutation
        {
            RemoveItems = [new ItemRemoval { InstanceId = "ITM_SELFCHECK_MISSING", Stack = 1 }]
        });
        Check(
            "inventory.item_not_found",
            missingItem.ErrorCode == InventoryErrorCodes.ItemNotFound,
            missingItem.ErrorCode);

        var overdraw = inventory.Apply(inventoryActor, new InventoryMutation
        {
            CurrencyDeltas = [new CurrencyDelta { CurrencyId = "COIN", Amount = -1000 }]
        });
        Check(
            "inventory.insufficient_currency",
            overdraw.ErrorCode == InventoryErrorCodes.InsufficientCurrency,
            overdraw.ErrorCode);

        var staleWrite = inventory.Apply(inventoryActor, new InventoryMutation
        {
            ExpectedRevision = 1,
            CurrencyDeltas = [new CurrencyDelta { CurrencyId = "COIN", Amount = 1 }]
        });
        Check(
            "inventory.revision_conflict",
            staleWrite.ErrorCode == InventoryErrorCodes.RevisionConflict && staleWrite.Retryable,
            staleWrite.ErrorCode);

        Check(
            "inventory.rejections_do_not_mutate",
            inventory.GetSnapshot(inventoryActor.CharacterId).InventoryRevision == 2,
            inventory.GetSnapshot(inventoryActor.CharacterId).InventoryRevision.ToString());

        var bagItem = inventory.GetSnapshot(inventoryActor.CharacterId)
            .Items.Single(item => item.Location == InventoryLocations.Bag);
        var removed = inventory.Apply(inventoryActor, new InventoryMutation
        {
            RemoveItems = [new ItemRemoval { InstanceId = bagItem.InstanceId, Stack = 1 }]
        });
        Check(
            "inventory.remove",
            removed.IsSuccess &&
            removed.Snapshot!.Items.Count == 1 &&
            removed.Snapshot.InventoryRevision == 3,
            removed.ErrorCode ?? $"revision={removed.Snapshot?.InventoryRevision}");

        // ─── QOD-21 Q1a: approved alpha profile ingest ────────

        var alphaRecords = services.GetRequiredService<WorldRecordCatalog>();
        var alphaDesign = services.GetRequiredService<AlphaDesign>();
        var alphaOptions = services.GetRequiredService<AlphaProfileOptions>();

        Check(
            "alpha.profile_loaded",
            alphaDesign.DecisionId == "DESIGN-BM-ALPHA-20261103" &&
            alphaDesign.Status.StartsWith(
                "APPROVED_FOR_IMPLEMENTATION", StringComparison.Ordinal) &&
            !alphaDesign.DefaultEnabled &&
            !alphaOptions.Enabled &&
            alphaDesign.OverlayRecords.Count == 7 &&
            alphaDesign.Inventory.BagSlots == 100 &&
            alphaDesign.Inventory.EquipmentSlots.Count == 12 &&
            alphaDesign.Boss.MaxHp == 1200 &&
            alphaDesign.Boss.Moves.Count == 3 &&
            alphaDesign.DeathReturn.AnchorX == 18 &&
            alphaDesign.DeathReturn.AnchorY == 0,
            $"{alphaDesign.DecisionId} overlays={alphaDesign.OverlayRecords.Count} " +
            $"enabled={alphaOptions.Enabled}");

        Check(
            "alpha.overlay_bounds",
            maps.TryResolve(alphaDesign.Scope.MapId, out var alphaBounds) &&
            alphaDesign.OverlayRecords.All(record =>
                alphaBounds.Contains(record.X, record.Y)),
            alphaDesign.Scope.MapId);

        bool AlphaRejects(AlphaDesign mutated)
        {
            try
            {
                AlphaProfileValidator.Validate(mutated, maps, npcAnchors, alphaRecords);
                return false;
            }
            catch (InvalidOperationException)
            {
                return true;
            }
        }

        var badOverlay = new[] { alphaDesign.OverlayRecords[0] with { X = 9999 } }
            .Concat(alphaDesign.OverlayRecords.Skip(1))
            .ToArray();
        Check(
            "alpha.rejects_out_of_bounds_overlay",
            AlphaRejects(alphaDesign with { OverlayRecords = badOverlay }),
            "x=9999 must fail");

        Check(
            "alpha.rejects_wrong_bag",
            AlphaRejects(alphaDesign with
            {
                Inventory = alphaDesign.Inventory with { BagSlots = 99 }
            }),
            "bag 99 must fail");

        Check(
            "alpha.rejects_missing_boss_move",
            AlphaRejects(alphaDesign with
            {
                Boss = alphaDesign.Boss with
                {
                    Moves = alphaDesign.Boss.Moves
                        .Where(move => move.Id != "C")
                        .ToArray()
                }
            }),
            "A+B only must fail");

        Check(
            "alpha.rejects_wrong_death_anchor",
            AlphaRejects(alphaDesign with
            {
                DeathReturn = alphaDesign.DeathReturn with { AnchorX = 0 }
            }),
            "anchor 0 must fail");

        Check(
            "alpha.rejects_unapproved_status",
            AlphaRejects(alphaDesign with { Status = "DRAFT" }),
            "DRAFT must fail");

        Check(
            "alpha.rejects_default_enabled",
            AlphaRejects(alphaDesign with { DefaultEnabled = true }),
            "defaultEnabled=true must fail");

        // ─── QOD-21 Q1b: alpha overlay merge into the runtime catalogs ────

        var alphaBaseEntities = services.GetRequiredService<WorldEntityCatalog>();
        Check(
            "alpha.overlay_gate_off_records",
            alphaRecords.Count == 352 &&
            alphaDesign.OverlayRecords.All(overlay => !alphaRecords.TryGet(overlay.RecordId, out _)),
            $"base={alphaRecords.Count}");
        Check(
            "alpha.overlay_gate_off_entities",
            alphaBaseEntities.Count == 44 &&
            alphaDesign.OverlayRecords.All(overlay =>
                alphaBaseEntities.Entities.All(entity =>
                    !string.Equals(entity.EntityId, overlay.EntityId, StringComparison.Ordinal))),
            $"base={alphaBaseEntities.Count}");

        var alphaMergedRecords = AlphaOverlayMerger.MergeRecords(
            alphaRecords, alphaDesign, maps);
        var alphaMergedEntities = AlphaOverlayMerger.MergeEntities(
            alphaBaseEntities, alphaDesign, maps);

        Check(
            "alpha.overlay_merge_records",
            alphaMergedRecords.Count == 359 &&
            alphaDesign.OverlayRecords.All(overlay =>
                alphaMergedRecords.TryGet(overlay.RecordId, out var record) &&
                record.MapId == "MAP_BEN_MUA" &&
                record.X == overlay.X &&
                record.Y == overlay.Y &&
                record.EntityIds.Count == 1 &&
                record.EntityIds[0] == overlay.EntityId &&
                record.RespawnSeconds == 0 &&
                record.Gather is null &&
                record.DesignState == $"ALPHA_OVERLAY:{alphaDesign.DecisionId}"),
            $"merged={alphaMergedRecords.Count}");

        var alphaRippleRecord = alphaMergedRecords.TryGet(
            "ALPHA-BM-RIPPLE-01", out var ripple01) ? ripple01 : null;
        var alphaVillagerRecord = alphaMergedRecords.TryGet(
            "ALPHA-BM-VILLAGER-01", out var villager01) ? villager01 : null;
        var alphaWaveRecord = alphaMergedRecords.TryGet(
            "ALPHA-BM-WAVE-TRAINING", out var wave01) ? wave01 : null;
        var alphaFragmentRecord = alphaMergedRecords.TryGet(
            "ALPHA-BM-FRAGMENT", out var fragment01) ? fragment01 : null;
        Check(
            "alpha.overlay_merge_record_kinds",
            alphaRippleRecord?.RecordType == "INTERACTABLE" &&
            alphaVillagerRecord?.RecordType == "RESCUE_INTERACTABLE" &&
            alphaWaveRecord?.RecordType == "QUEST_HAZARD" &&
            alphaFragmentRecord?.Condition.Contains(
                "boss kill committed", StringComparison.Ordinal) == true,
            $"ripple={alphaRippleRecord?.RecordType} " +
            $"villager={alphaVillagerRecord?.RecordType} " +
            $"wave={alphaWaveRecord?.RecordType}");

        var alphaResolvedRipple = alphaMergedRecords.TryResolveTarget(
            "ALPHA_OBJ_BM_RIPPLE_02", "MAP_BEN_MUA", out var resolvedRipple)
            ? resolvedRipple
            : null;
        Check(
            "alpha.overlay_merge_resolve",
            alphaResolvedRipple?.RecordId == "ALPHA-BM-RIPPLE-02" &&
            !alphaMergedRecords.TryResolveTarget(
                "ALPHA_OBJ_BM_RIPPLE_02", "MAP_THANH_LAC", out _),
            alphaResolvedRipple?.RecordId ?? "unresolved");

        Check(
            "alpha.overlay_merge_entities",
            alphaMergedEntities.Count == 50 &&
            alphaMergedEntities.Templates.Count == 28 &&
            alphaDesign.OverlayRecords
                .Where(overlay => AlphaOverlayMerger.HasRuntimeEntity(overlay.Kind))
                .All(overlay =>
                {
                    var entity = alphaMergedEntities.Entities.SingleOrDefault(candidate =>
                        string.Equals(candidate.EntityId, overlay.EntityId, StringComparison.Ordinal));
                    return entity is
                    {
                        Kind: WorldEntityKinds.Interactable,
                        MapId: "MAP_BEN_MUA",
                        FloorId: "OVERWORLD",
                        Quantity: 1,
                        RespawnSeconds: 0,
                        ClaimPolicy: WorldEntityClaimPolicies.PerCharacter,
                        State: WorldEntityStates.Available,
                        Revision: 1,
                        LifeId: 1
                    } &&
                    entity.RecordId == overlay.RecordId &&
                    entity.X == overlay.X &&
                    entity.Y == overlay.Y &&
                    entity.TemplateIds.Count == 1 &&
                    entity.TemplateIds[0] == overlay.EntityId &&
                    alphaMergedEntities.Templates.Any(template =>
                        template.TemplateId == overlay.EntityId &&
                        template.Kind == WorldEntityKinds.Interactable);
                }) &&
            alphaMergedEntities.Entities.All(entity =>
                !string.Equals(entity.EntityId, "ALPHA_WAVE_BM_TRAINING", StringComparison.Ordinal)),
            $"entities={alphaMergedEntities.Count} templates={alphaMergedEntities.Templates.Count}");

        var alphaMergedRegistry = new WorldEntityRegistry(
            alphaMergedEntities, services.GetRequiredService<IServerClock>());
        var alphaFragmentEntity = alphaMergedRegistry.TryGet(
            "ALPHA_OBJ_BM_FRAGMENT", out var fragmentEntity) ? fragmentEntity : null;
        Check(
            "alpha.overlay_registry_ready",
            alphaFragmentEntity is { State: WorldEntityStates.Available } &&
            !alphaMergedRegistry.TryGet("ALPHA_WAVE_BM_TRAINING", out _),
            alphaFragmentEntity?.State ?? "missing");

        bool AlphaOverlayRecordRejects(AlphaDesign mutated)
        {
            try
            {
                AlphaOverlayMerger.MergeRecords(alphaRecords, mutated, maps);
                return false;
            }
            catch (InvalidOperationException)
            {
                return true;
            }
        }

        bool AlphaOverlayEntityRejects(AlphaDesign mutated)
        {
            try
            {
                AlphaOverlayMerger.MergeEntities(alphaBaseEntities, mutated, maps);
                return false;
            }
            catch (InvalidOperationException)
            {
                return true;
            }
        }

        Check(
            "alpha.overlay_rejects_base_entity_collision",
            AlphaOverlayEntityRejects(alphaDesign with
            {
                OverlayRecords = new[] { alphaDesign.OverlayRecords[0] with
                {
                    EntityId = "ENT_MAN_BM_FISHING_LINH"
                } }.Concat(alphaDesign.OverlayRecords.Skip(1)).ToArray()
            }),
            "entityId must not collide with a world entity");

        Check(
            "alpha.overlay_rejects_non_alpha_record_prefix",
            AlphaOverlayRecordRejects(alphaDesign with
            {
                OverlayRecords = new[] { alphaDesign.OverlayRecords[0] with
                {
                    RecordId = "BM-RIPPLE-01"
                } }.Concat(alphaDesign.OverlayRecords.Skip(1)).ToArray()
            }),
            "recordId must keep the ALPHA- prefix");

        Check(
            "alpha.overlay_rejects_bad_kind",
            AlphaOverlayRecordRejects(alphaDesign with
            {
                OverlayRecords = new[] { alphaDesign.OverlayRecords[0] with
                {
                    Kind = "NPC"
                } }.Concat(alphaDesign.OverlayRecords.Skip(1)).ToArray()
            }),
            "kind NPC must fail");

        Check(
            "alpha.overlay_rejects_duplicate_record",
            AlphaOverlayRecordRejects(alphaDesign with
            {
                OverlayRecords = new[] { alphaDesign.OverlayRecords[0],
                    alphaDesign.OverlayRecords[0] with { EntityId = "ALPHA_OBJ_BM_RIPPLE_99" } }
                    .Concat(alphaDesign.OverlayRecords.Skip(1)).ToArray()
            }),
            "duplicate recordId must fail");

        // ─── QOD-21 Q1c: alpha quest pack merge ────────

        var alphaEnvironment = services.GetRequiredService<IHostEnvironment>();
        var alphaOverlayQuests = QuestCatalogLoader.Load(
            AlphaQuestCatalogMerger.DiscoverOverlayDirectory(
                alphaEnvironment.ContentRootPath));
        var alphaMergedQuests = AlphaQuestCatalogMerger.Merge(
            questCatalog, alphaOverlayQuests);

        Check(
            "alpha.quest_gate_off_catalog",
            questCatalog.Count == 5 &&
            !questCatalog.TryGet("C1-01", out _),
            $"base={questCatalog.Count}");

        Check(
            "alpha.quest_merge_catalog",
            alphaMergedQuests.Count == 6 &&
            alphaMergedQuests.QuestIds.SequenceEqual(
                new[] { "C1-01", "P00-01", "P00-02", "P00-03", "P00-04", "P00-05" },
                StringComparer.Ordinal),
            $"merged={alphaMergedQuests.Count}");

        var alphaP00_02 = alphaMergedQuests.TryGet("P00-02", out var alphaP2)
            ? alphaP2
            : null;
        Check(
            "alpha.quest_p00_02",
            alphaP00_02 is
            {
                IsBlocked: false,
                StartNpcId: "NPC_TA_VAN_KHANH",
                TurnInNpcId: "NPC_TA_VAN_KHANH",
                MinLevel: 1,
                MaxLevel: 10
            } &&
            alphaP00_02.Objectives.Count == 2 &&
            alphaP00_02.Objectives[0].Type == QuestObjectiveTypes.Interact &&
            alphaP00_02.Objectives[0].Count == 3 &&
            alphaP00_02.Objectives[0].TargetIds.SequenceEqual(
                new[] { "ALPHA-BM-RIPPLE-01", "ALPHA-BM-RIPPLE-02", "ALPHA-BM-RIPPLE-03" },
                StringComparer.Ordinal) &&
            alphaP00_02.Objectives[1].Type == QuestObjectiveTypes.Kill &&
            alphaP00_02.Objectives[1].Count == 4 &&
            alphaP00_02.Objectives[1].TargetIds.SequenceEqual(
                new[] { "MOB_CARPLING" }, StringComparer.Ordinal) &&
            alphaP00_02.Unlocks.SequenceEqual(new[] { "P00-03" }, StringComparer.Ordinal) &&
            alphaP00_02.Rewards.ItemIds.SequenceEqual(
                new[] { "POT-HP-01" }, StringComparer.Ordinal),
            $"activation={alphaP00_02?.Activation}");

        var alphaP00_03 = alphaMergedQuests.TryGet("P00-03", out var alphaP3)
            ? alphaP3
            : null;
        Check(
            "alpha.quest_p00_03",
            alphaP00_03 is
            {
                IsBlocked: false,
                StartNpcId: "NPC_LYAN",
                TurnInNpcId: "NPC_LYAN"
            } &&
            alphaP00_03.Objectives.Count == 3 &&
            alphaP00_03.Objectives[0].Type == QuestObjectiveTypes.Interact &&
            alphaP00_03.Objectives[0].Count == 2 &&
            alphaP00_03.Objectives[0].TargetIds.SequenceEqual(
                new[] { "ALPHA-BM-VILLAGER-01", "ALPHA-BM-VILLAGER-02" },
                StringComparer.Ordinal) &&
            alphaP00_03.Objectives[1].Type == QuestObjectiveTypes.Kill &&
            alphaP00_03.Objectives[1].Count == 3 &&
            alphaP00_03.Objectives[1].TargetIds.SequenceEqual(
                new[] { "MOB_WATERROOT" }, StringComparer.Ordinal) &&
            alphaP00_03.Objectives[2].Type == QuestObjectiveTypes.Interact &&
            alphaP00_03.Objectives[2].Count == 1 &&
            alphaP00_03.Objectives[2].TargetIds.SequenceEqual(
                new[] { "ALPHA-BM-WAVE-TRAINING" }, StringComparer.Ordinal) &&
            alphaP00_03.Unlocks.SequenceEqual(new[] { "P00-04" }, StringComparer.Ordinal),
            $"objectives={alphaP00_03?.Objectives.Count}");

        var alphaP00_04 = alphaMergedQuests.TryGet("P00-04", out var alphaP4)
            ? alphaP4
            : null;
        Check(
            "alpha.quest_p00_04",
            alphaP00_04 is
            {
                IsBlocked: false,
                StartNpcId: "NPC_TA_VAN_KHANH",
                TurnInNpcId: "NPC_TA_VAN_KHANH"
            } &&
            alphaP00_04.Objectives.Count == 2 &&
            alphaP00_04.Objectives.All(objective =>
                objective.Type == QuestObjectiveTypes.Kill && objective.Count == 3) &&
            alphaP00_04.Objectives[0].TargetIds.SequenceEqual(
                new[] { "MAN-BM-WAVE_BM_ESCORT_A" }, StringComparer.Ordinal) &&
            alphaP00_04.Objectives[1].TargetIds.SequenceEqual(
                new[] { "MAN-BM-WAVE_BM_ESCORT_B" }, StringComparer.Ordinal) &&
            alphaP00_04.Rewards.Currency.Count == 1 &&
            alphaP00_04.Rewards.Currency[0].CurrencyId == "COIN" &&
            alphaP00_04.Rewards.Currency[0].Amount == 30,
            $"objectives={alphaP00_04?.Objectives.Count}");

        var alphaP00_05 = alphaMergedQuests.TryGet("P00-05", out var alphaP5)
            ? alphaP5
            : null;
        Check(
            "alpha.quest_p00_05",
            alphaP00_05 is
            {
                IsBlocked: false,
                StartNpcId: "NPC_TA_VAN_KHANH",
                TurnInNpcId: "NPC_TA_VAN_KHANH"
            } &&
            alphaP00_05.OrderedObjectives &&
            alphaP00_05.Objectives.Count == 3 &&
            alphaP00_05.Objectives[0].Type == QuestObjectiveTypes.Boss &&
            alphaP00_05.Objectives[0].TargetIds.SequenceEqual(
                new[] { "MAN-BM-SPAWN_BM_05_QUEST" }, StringComparer.Ordinal) &&
            alphaP00_05.Objectives[1].Type == QuestObjectiveTypes.Interact &&
            alphaP00_05.Objectives[1].TargetIds.SequenceEqual(
                new[] { "ALPHA-BM-FRAGMENT" }, StringComparer.Ordinal) &&
            alphaP00_05.Objectives[2].Type == QuestObjectiveTypes.Talk &&
            alphaP00_05.Objectives[2].TargetIds.SequenceEqual(
                new[] { "NPC_CLASS_TRIAL" }, StringComparer.Ordinal) &&
            alphaP00_05.Unlocks.SequenceEqual(new[] { "C1-01" }, StringComparer.Ordinal) &&
            alphaP00_05.Rewards.ItemIds.SequenceEqual(
                new[] { "EQ-MK-WEAPON-T1-R-COMMON" }, StringComparer.Ordinal),
            $"ordered={alphaP00_05?.OrderedObjectives}");

        var alphaC1_01 = alphaMergedQuests.TryGet("C1-01", out var alphaC1)
            ? alphaC1
            : null;
        Check(
            "alpha.quest_c1_01",
            alphaC1_01 is
            {
                IsBlocked: false,
                QuestType: QuestTypes.Main,
                StartNpcId: "NPC_LYAN",
                TurnInNpcId: "NPC_LYAN",
                MinLevel: 11,
                MaxLevel: 20
            } &&
            alphaC1_01.PrerequisiteQuestIds.SequenceEqual(
                new[] { "P00-05" }, StringComparer.Ordinal) &&
            alphaC1_01.Objectives.Count == 2 &&
            alphaC1_01.Objectives[0].Type == QuestObjectiveTypes.Talk &&
            alphaC1_01.Objectives[0].Count == 3 &&
            alphaC1_01.Objectives[0].MapId == "MAP_THANH_LAC" &&
            alphaC1_01.Objectives[0].TargetIds.SequenceEqual(
                new[] { "NPC_GUARD_CAPTAIN", "NPC_HA_MAC", "NPC_MASTER_MINH_KIEM" },
                StringComparer.Ordinal) &&
            alphaC1_01.Objectives[1].Type == QuestObjectiveTypes.Talk &&
            alphaC1_01.Objectives[1].TargetIds.SequenceEqual(
                new[] { "NPC_CLASS_TRIAL" }, StringComparer.Ordinal) &&
            alphaC1_01.Rewards.Currency.Count == 1 &&
            alphaC1_01.Rewards.Currency[0].CurrencyId == "COIN" &&
            alphaC1_01.Rewards.Currency[0].Amount == 80 &&
            alphaC1_01.Unlocks.Count == 0,
            $"band={alphaC1_01?.MinLevel}..{alphaC1_01?.MaxLevel}");

        var alphaQuestValidationPassed = true;
        string? alphaQuestValidationError = null;
        try
        {
            QuestCatalogValidator.Validate(
                alphaMergedQuests, alphaMergedRecords, npcAnchors);
        }
        catch (InvalidOperationException exception)
        {
            alphaQuestValidationPassed = false;
            alphaQuestValidationError = exception.Message;
        }

        Check(
            "alpha.quest_merge_validates",
            alphaQuestValidationPassed,
            alphaQuestValidationError);

        Dictionary<string, QuestDefinition> AlphaOverlayDefinitions() =>
            alphaOverlayQuests.QuestIds.ToDictionary(
                questId => questId,
                questId => alphaOverlayQuests.TryGet(questId, out var definition)
                    ? definition
                    : throw new InvalidOperationException($"missing overlay quest {questId}"),
                StringComparer.Ordinal);

        bool AlphaQuestMergeRejects(QuestCatalog overlay)
        {
            try
            {
                AlphaQuestCatalogMerger.Merge(questCatalog, overlay);
                return false;
            }
            catch (InvalidOperationException)
            {
                return true;
            }
        }

        var blockedOverlayDefinitions = AlphaOverlayDefinitions();
        blockedOverlayDefinitions["P00-02"] = blockedOverlayDefinitions["P00-02"] with
        {
            Activation = QuestActivations.Blocked,
            BlockedSteps = [new QuestBlockedStep("X", "turnInNpcId", "design.md")]
        };
        Check(
            "alpha.quest_rejects_blocked_overlay",
            AlphaQuestMergeRejects(new QuestCatalog(blockedOverlayDefinitions)),
            "a BLOCKED alpha definition must fail");

        var missingPackDefinitions = AlphaOverlayDefinitions();
        missingPackDefinitions.Remove("C1-01");
        Check(
            "alpha.quest_rejects_missing_pack_quest",
            AlphaQuestMergeRejects(new QuestCatalog(missingPackDefinitions)),
            "a pack without C1-01 must fail");

        var extraPackDefinitions = AlphaOverlayDefinitions();
        extraPackDefinitions["P00-06"] = extraPackDefinitions["P00-02"] with
        {
            QuestId = "P00-06"
        };
        Check(
            "alpha.quest_rejects_unknown_pack_quest",
            AlphaQuestMergeRejects(new QuestCatalog(extraPackDefinitions)),
            "an id outside the design pack must fail");

        // Q1c runtime: the merged P00-05 semantics are exercised on fixtures.
        // BOSS objectives credit only kills of the quest-boss record (the tick
        // engine already emits KILL with source.RecordId, so a
        // MAN-BM-SPAWN_BM_05_QUEST death reaches the objective), and
        // orderedObjectives holds every later objective closed until the first
        // incomplete one completes (boss before fragment before class-confirm).

        QuestDefinition AlphaOrderedFixture(string questId, bool ordered) =>
            new(
                questId,
                QuestTypes.Main,
                "NPC_TA_VAN_KHANH",
                1,
                10,
                [],
                [
                    new QuestObjectiveDefinition(
                        "OBJ_BOSS_FIXTURE", QuestObjectiveTypes.Boss,
                        ["MAN-BM-SPAWN_BM_05_QUEST"], 1, options.DefaultMapId),
                    new QuestObjectiveDefinition(
                        "OBJ_FRAGMENT_FIXTURE", QuestObjectiveTypes.Interact,
                        ["ALPHA-BM-FRAGMENT"], 1, options.DefaultMapId)
                ],
                QuestStepIds.FromObjectiveId("OBJ_BOSS_FIXTURE"),
                "NPC_TA_VAN_KHANH",
                new QuestRewards([], [], "LEVEL_BAND_BASE"),
                [],
                OrderedObjectives: ordered);

        var alphaRuntimeQuests = new InMemoryQuestService(
            new QuestCatalog(
                new Dictionary<string, QuestDefinition>
                {
                    ["ALPHA-ORDER-01"] = AlphaOrderedFixture("ALPHA-ORDER-01", ordered: true),
                    ["ALPHA-FREE-01"] = AlphaOrderedFixture("ALPHA-FREE-01", ordered: false)
                }),
            new InMemoryQuestStateStore(),
            alphaMergedRecords,
            interactClock);

        var alphaBossActor = NewPlayer("CHR_SELFCHECK_ALPHA_BOSS");
        alphaRuntimeQuests.Accept(alphaBossActor, "ALPHA-ORDER-01");
        var bossEventId = new string('f', 32);
        var fragmentEventId = new string('a', 32);
        var nonKillBossEvent = alphaRuntimeQuests.RecordVerifiedEvent(
            alphaBossActor, fragmentEventId, QuestProgressEventTypes.InteractClaim,
            "MAN-BM-SPAWN_BM_05_QUEST", options.DefaultMapId);
        var bossKill = alphaRuntimeQuests.RecordVerifiedEvent(
            alphaBossActor, bossEventId, QuestProgressEventTypes.Kill,
            "MAN-BM-SPAWN_BM_05_QUEST", options.DefaultMapId);
        var bossReplay = alphaRuntimeQuests.RecordVerifiedEvent(
            alphaBossActor, bossEventId, QuestProgressEventTypes.Kill,
            "MAN-BM-SPAWN_BM_05_QUEST", options.DefaultMapId);
        var bossState = alphaRuntimeQuests.GetState(
            alphaBossActor.CharacterId, "ALPHA-ORDER-01").State;
        Check(
            "alpha.quest_boss_credits_only_kills",
            nonKillBossEvent.Count == 0 &&
            bossKill.Count == 1 &&
            bossReplay.Count == 0 &&
            bossState is { State: QuestStates.Active } &&
            bossState.ObjectiveCounters.GetValueOrDefault("OBJ_BOSS_FIXTURE") == 1 &&
            bossState.ObjectiveCounters.GetValueOrDefault("OBJ_FRAGMENT_FIXTURE") == 0,
            $"nonKill={nonKillBossEvent.Count} kill={bossKill.Count} " +
            $"replay={bossReplay.Count} boss={bossState?.ObjectiveCounters.GetValueOrDefault("OBJ_BOSS_FIXTURE")}");

        var alphaOrderActor = NewPlayer("CHR_SELFCHECK_ALPHA_ORDER");
        alphaRuntimeQuests.Accept(alphaOrderActor, "ALPHA-ORDER-01");
        var orderStateBefore = alphaRuntimeQuests.GetState(
            alphaOrderActor.CharacterId, "ALPHA-ORDER-01").State;
        var earlyFragment = alphaRuntimeQuests.RecordVerifiedEvent(
            alphaOrderActor, fragmentEventId, QuestProgressEventTypes.InteractClaim,
            "ALPHA-BM-FRAGMENT", options.DefaultMapId);
        var orderStateAfter = alphaRuntimeQuests.GetState(
            alphaOrderActor.CharacterId, "ALPHA-ORDER-01").State;
        Check(
            "alpha.quest_ordered_holds_later_objective",
            earlyFragment.Count == 0 &&
            orderStateBefore is { State: QuestStates.Active } &&
            orderStateAfter is { State: QuestStates.Active } &&
            orderStateAfter.Revision == orderStateBefore!.Revision &&
            orderStateAfter.ObjectiveCounters.GetValueOrDefault("OBJ_BOSS_FIXTURE") == 0 &&
            orderStateAfter.ObjectiveCounters.GetValueOrDefault("OBJ_FRAGMENT_FIXTURE") == 0,
            $"changed={earlyFragment.Count} revision={orderStateAfter?.Revision}");

        var inOrderKill = alphaRuntimeQuests.RecordVerifiedEvent(
            alphaOrderActor, bossEventId, QuestProgressEventTypes.Kill,
            "MAN-BM-SPAWN_BM_05_QUEST", options.DefaultMapId);
        var inOrderFragment = alphaRuntimeQuests.RecordVerifiedEvent(
            alphaOrderActor, new string('b', 32), QuestProgressEventTypes.InteractClaim,
            "ALPHA-BM-FRAGMENT", options.DefaultMapId);
        var orderDone = alphaRuntimeQuests.GetState(
            alphaOrderActor.CharacterId, "ALPHA-ORDER-01").State;
        Check(
            "alpha.quest_ordered_completes_in_order",
            inOrderKill.Count == 1 &&
            inOrderFragment.Count == 1 &&
            orderDone is { State: QuestStates.ReadyToTurnIn } &&
            orderDone.ObjectiveCounters.GetValueOrDefault("OBJ_BOSS_FIXTURE") == 1 &&
            orderDone.ObjectiveCounters.GetValueOrDefault("OBJ_FRAGMENT_FIXTURE") == 1,
            $"{orderDone?.State}");

        var alphaFreeActor = NewPlayer("CHR_SELFCHECK_ALPHA_FREE");
        alphaRuntimeQuests.Accept(alphaFreeActor, "ALPHA-FREE-01");
        var freeFragment = alphaRuntimeQuests.RecordVerifiedEvent(
            alphaFreeActor, fragmentEventId, QuestProgressEventTypes.InteractClaim,
            "ALPHA-BM-FRAGMENT", options.DefaultMapId);
        var freeState = alphaRuntimeQuests.GetState(
            alphaFreeActor.CharacterId, "ALPHA-FREE-01").State;
        Check(
            "alpha.quest_unordered_accepts_any_order",
            freeFragment.Count == 1 &&
            freeState is { State: QuestStates.Active } &&
            freeState.ObjectiveCounters.GetValueOrDefault("OBJ_BOSS_FIXTURE") == 0 &&
            freeState.ObjectiveCounters.GetValueOrDefault("OBJ_FRAGMENT_FIXTURE") == 1,
            $"changed={freeFragment.Count} fragment={freeState?.ObjectiveCounters.GetValueOrDefault("OBJ_FRAGMENT_FIXTURE")}");

        // Q1c runtime: the training-wave trial (DESIGN-BM-ALPHA-20261103
        // questRules.P00-03.waveTrial) as a domain-only 20 Hz machine behind
        // P1:AlphaProfile. The sourced rect (140,-2)-(148,2), windup 1,2 s
        // (24 ticks), cooldown 6 s (120 ticks) and raw damage 12 come from the
        // design; the hazard record ALPHA-BM-WAVE-TRAINING has no runtime
        // entity, so the dodge credit is an INTERACT_CLAIM verified event the
        // machine records itself. The dash has no iframe, so an iframe escape
        // is unsupported by design.

        var waveRecording = new RecordingQuestService();
        var waveCombatOn = new CombatDamageFeature(
            new P1CombatDamageOptions { Enabled = true },
            services.GetRequiredService<IConfiguration>(),
            services.GetRequiredService<IHostEnvironment>());
        var waveCombatOff = new CombatDamageFeature(
            new P1CombatDamageOptions { Enabled = false },
            services.GetRequiredService<IConfiguration>(),
            services.GetRequiredService<IHostEnvironment>());
        var waveTrial = new AlphaWaveTrialService(
            alphaDesign, waveRecording, waveCombatOn, new PlayerLifeLedger());
        var waveTrialNoDamage = new AlphaWaveTrialService(
            alphaDesign, waveRecording, waveCombatOff, new PlayerLifeLedger());

        // Enter at tick 1000 (cycle opens, impact 1024), leave during the
        // warning, and be outside at the impact frame: one dodge credit.
        var waveActor = NewPlayer("CHR_SELFCHECK_ALPHA_WAVE");
        waveActor.X = 144;
        waveActor.Y = 0;
        var waveOpen = waveTrial.Tick([waveActor], 1000);
        waveActor.X = 130;
        waveTrial.Tick([waveActor], 1005);
        var waveCredit = waveTrial.Tick([waveActor], 1024);
        Check(
            "alpha.wave_trial_dodge_credits",
            waveOpen.Count == 0 &&
            waveCredit.Count == 1 &&
            waveCredit[0].Outcome == WaveTrialOutcomes.Credit &&
            waveCredit[0].Damage == 0 &&
            waveActor.Hp == 100 &&
            waveRecording.Events.Count == 1 &&
            waveRecording.Events[0].RecordId == "ALPHA-BM-WAVE-TRAINING" &&
            waveRecording.Events[0].EventType == QuestProgressEventTypes.InteractClaim &&
            waveRecording.Events[0].MapId == options.DefaultMapId,
            $"{waveCredit.FirstOrDefault()?.Outcome} hp={waveActor.Hp} events={waveRecording.Events.Count}");

        // Standing back inside during the 120-tick cooldown starts nothing;
        // once the cooldown expires the trial retriggers and a second dodge
        // credits again.
        waveActor.X = 144;
        var waveCooldownBlock = waveTrial.Tick([waveActor], 1030);
        waveTrial.Tick([waveActor], 1144);
        waveActor.X = 130;
        var waveSecondCredit = waveTrial.Tick([waveActor], 1168);
        Check(
            "alpha.wave_trial_cooldown_and_retry",
            waveCooldownBlock.Count == 0 &&
            waveSecondCredit.Count == 1 &&
            waveSecondCredit[0].Outcome == WaveTrialOutcomes.Credit &&
            waveRecording.Events.Count == 2,
            $"{waveSecondCredit.FirstOrDefault()?.Outcome} events={waveRecording.Events.Count}");

        // Staying inside through the whole warning resolves a raw-damage hit
        // on the impact tick, not before, and moves HP and the session
        // revision exactly once.
        var waveHitActor = NewPlayer("CHR_SELFCHECK_ALPHA_WAVE_HIT");
        waveHitActor.X = 144;
        waveHitActor.Y = 0;
        var waveHitOpen = waveTrial.Tick([waveHitActor], 2000);
        var waveHitEarly = waveTrial.Tick([waveHitActor], 2023);
        var waveHit = waveTrial.Tick([waveHitActor], 2024);
        Check(
            "alpha.wave_trial_hit_raw_damage",
            waveHitOpen.Count == 0 &&
            waveHitEarly.Count == 0 &&
            waveHit.Count == 1 &&
            waveHit[0].Outcome == WaveTrialOutcomes.Hit &&
            waveHit[0].Damage == 12 &&
            waveHit[0].HpBefore == 100 &&
            waveHit[0].HpAfter == 88 &&
            waveHitActor.Hp == 88 &&
            waveHitActor.Revision == 2 &&
            waveRecording.Events.Count == 2,
            $"{waveHit.FirstOrDefault()?.Outcome} hp={waveHitActor.Hp} rev={waveHitActor.Revision}");

        // With P1:CombatDamage off the same impact resolves blocked: no HP, no
        // revision, but the cooldown still runs so the trial stays retryable.
        var waveGatedActor = NewPlayer("CHR_SELFCHECK_ALPHA_WAVE_GATED");
        waveGatedActor.X = 144;
        waveGatedActor.Y = 0;
        waveTrialNoDamage.Tick([waveGatedActor], 3000);
        var waveGated = waveTrialNoDamage.Tick([waveGatedActor], 3024);
        Check(
            "alpha.wave_trial_hit_damage_gated",
            waveGated.Count == 1 &&
            waveGated[0].Outcome == WaveTrialOutcomes.DamageBlocked &&
            waveGated[0].Damage == 0 &&
            waveGatedActor.Hp == 100 &&
            waveGatedActor.Revision == 1,
            $"{waveGated.FirstOrDefault()?.Outcome} hp={waveGatedActor.Hp}");

        // Leaving the map mid-warning cancels with no credit and no cooldown,
        // so returning can open a fresh cycle immediately.
        var waveLeaveActor = NewPlayer("CHR_SELFCHECK_ALPHA_WAVE_LEAVE");
        waveLeaveActor.X = 144;
        waveLeaveActor.Y = 0;
        waveTrial.Tick([waveLeaveActor], 4000);
        waveLeaveActor.MapId = "MAP_THANH_LAC";
        var waveLeave = waveTrial.Tick([waveLeaveActor], 4010);
        waveLeaveActor.MapId = options.DefaultMapId;
        waveTrial.Tick([waveLeaveActor], 4020);
        waveLeaveActor.X = 130;
        var waveLeaveCredit = waveTrial.Tick([waveLeaveActor], 4044);
        Check(
            "alpha.wave_trial_cancel_on_map_leave",
            waveLeave.Count == 1 &&
            waveLeave[0].Outcome == WaveTrialOutcomes.Cancelled &&
            waveLeave[0].Damage == 0 &&
            waveLeaveCredit.Count == 1 &&
            waveLeaveCredit[0].Outcome == WaveTrialOutcomes.Credit &&
            waveRecording.Events.Count == 3,
            $"{waveLeave.FirstOrDefault()?.Outcome}/{waveLeaveCredit.FirstOrDefault()?.Outcome}");

        // Leaving and re-entering before the impact is still inside at the
        // impact frame: the hit lands.
        var waveReenterActor = NewPlayer("CHR_SELFCHECK_ALPHA_WAVE_REENTER");
        waveReenterActor.X = 144;
        waveReenterActor.Y = 0;
        waveTrial.Tick([waveReenterActor], 5000);
        waveReenterActor.X = 130;
        waveTrial.Tick([waveReenterActor], 5010);
        waveReenterActor.X = 144;
        var waveReenterHit = waveTrial.Tick([waveReenterActor], 5024);
        Check(
            "alpha.wave_trial_reentry_hits",
            waveReenterHit.Count == 1 &&
            waveReenterHit[0].Outcome == WaveTrialOutcomes.Hit &&
            waveReenterHit[0].Damage == 12 &&
            waveReenterActor.Hp == 88,
            $"{waveReenterHit.FirstOrDefault()?.Outcome} hp={waveReenterActor.Hp}");

        // A downed actor never opens a cycle; dying mid-warning cancels it
        // with no damage and no credit.
        var waveDownActor = NewPlayer("CHR_SELFCHECK_ALPHA_WAVE_DOWN", hp: 0);
        waveDownActor.X = 144;
        waveDownActor.Y = 0;
        var waveDownSkip = waveTrial.Tick([waveDownActor], 6000);
        var waveDieActor = NewPlayer("CHR_SELFCHECK_ALPHA_WAVE_DIE");
        waveDieActor.X = 144;
        waveDieActor.Y = 0;
        waveTrial.Tick([waveDieActor], 7000);
        waveDieActor.Hp = 0;
        var waveDieCancel = waveTrial.Tick([waveDieActor], 7010);
        Check(
            "alpha.wave_trial_downed_and_death",
            waveDownSkip.Count == 0 &&
            waveDieCancel.Count == 1 &&
            waveDieCancel[0].Outcome == WaveTrialOutcomes.Cancelled &&
            waveDieCancel[0].Damage == 0 &&
            waveRecording.Events.Count == 3,
            $"{waveDieCancel.FirstOrDefault()?.Outcome} events={waveRecording.Events.Count}");

        // The rectangle belongs to Bến Mưa: the same position on another map
        // never triggers.
        var waveForeignActor = NewPlayer("CHR_SELFCHECK_ALPHA_WAVE_FOREIGN");
        waveForeignActor.MapId = "MAP_THANH_LAC";
        waveForeignActor.X = 144;
        waveForeignActor.Y = 0;
        var waveForeignSkip = waveTrial.Tick([waveForeignActor], 8000);
        Check(
            "alpha.wave_trial_foreign_map",
            waveForeignSkip.Count == 0 &&
            waveForeignActor.Hp == 100,
            $"resolutions={waveForeignSkip.Count}");

        // Without the QUEST_HAZARD overlay record the machine is inert: no
        // fabricated record id, no damage, no credit.
        var waveNoHazardDesign = alphaDesign with
        {
            OverlayRecords = alphaDesign.OverlayRecords
                .Where(record => !string.Equals(
                    record.Kind, "QUEST_HAZARD", StringComparison.Ordinal))
                .ToArray()
        };
        var waveInert = new AlphaWaveTrialService(
            waveNoHazardDesign, waveRecording, waveCombatOn, new PlayerLifeLedger());
        var waveInertActor = NewPlayer("CHR_SELFCHECK_ALPHA_WAVE_INERT");
        waveInertActor.X = 144;
        waveInertActor.Y = 0;
        var waveInertSkip = waveInert.Tick([waveInertActor], 9000);
        Check(
            "alpha.wave_trial_inert_without_hazard_record",
            waveInertSkip.Count == 0 &&
            waveInertActor.Hp == 100 &&
            waveRecording.Events.Count == 3,
            $"resolutions={waveInertSkip.Count} hp={waveInertActor.Hp}");

        // ─── QOD-21 Q3: the alpha loot payout switch ────

        // DESIGN-BM-Q3-20261104 `loot`: effectiveGrant is AlphaProfile.Enabled AND
        // explicit private alpha AND P1:AlphaLoot:GrantEnabled, off means a dry-run
        // that is never paid later, and the roll happens once per kill key.
        var lootProfileOff = new AlphaProfileOptions { Enabled = false };
        var lootProfileOn = new AlphaProfileOptions { Enabled = true };
        var lootFlagOff = new AlphaLootOptions { GrantEnabled = false };
        var lootFlagOn = new AlphaLootOptions { GrantEnabled = true };
        var lootRoller = new LootRoller(
            enabledCombat.LootRecipes, new LootRngRollSource());
        var lootLevel = new Func<int>(() => 5);
        var lootMob = new WorldEntityInstance
        {
            EntityId = "ENT_SELFCHECK_LOOT_MOB",
            RecordId = "MAN-SELFCHECK-LOOT",
            Kind = WorldEntityKinds.Mob,
            TemplateIds = new[] { "MOB_CARPLING" },
            MapId = alphaDesign.Scope.MapId,
            FloorId = "OVERWORLD",
            X = 84,
            Y = 0,
            Quantity = 1,
            RespawnSeconds = 0,
            GroupId = "MAN-BM-SPAWN_BM_01",
            MemberIndex = 1
        };
        lootMob.Initialize();
        var lootActor = NewPlayer("CHR_SELFCHECK_ALPHA_LOOT");

        // One ledger shared by the three switches: a death recorded while the
        // payout was off must keep that answer after it is turned on.
        var alphaLootGrantLedger = new LootGrantLedger();
        var lootOffProduction = new LootGrantService(
            services.GetRequiredService<IInventoryService>(), alphaLootGrantLedger,
            new AlphaLootGrantPolicy(alphaDesign, lootProfileOff, lootFlagOff),
            enabledCombat, new LootReceiptLedger());
        var lootOffAlpha = new LootGrantService(
            services.GetRequiredService<IInventoryService>(), alphaLootGrantLedger,
            new AlphaLootGrantPolicy(alphaDesign, lootProfileOn, lootFlagOff),
            enabledCombat, new LootReceiptLedger());
        var lootOnAlpha = new LootGrantService(
            services.GetRequiredService<IInventoryService>(), alphaLootGrantLedger,
            new AlphaLootGrantPolicy(alphaDesign, lootProfileOn, lootFlagOn),
            enabledCombat, new LootReceiptLedger());

        var blockedProductionDeath = new string('a', 32);
        var blockedAlphaDeath = new string('b', 32);
        var productionBlock = lootOffProduction.OnMobDeath(
            lootActor, lootMob, "MOB_CARPLING", lootLevel, blockedProductionDeath, 1);
        var alphaDryRun = lootOffAlpha.OnMobDeath(
            lootActor, lootMob, "MOB_CARPLING", lootLevel, blockedAlphaDeath, 1);
        // Turning the flag on afterwards must not reach back for that death.
        var afterFlagOn = lootOnAlpha.OnMobDeath(
            lootActor, lootMob, "MOB_CARPLING", lootLevel, blockedAlphaDeath, 1);
        var paidDeath = new string('c', 32);
        var paidOnce = lootOnAlpha.OnMobDeath(
            lootActor, lootMob, "MOB_CARPLING", lootLevel, paidDeath, 1);
        var paidReplay = lootOnAlpha.OnMobDeath(
            lootActor, lootMob, "MOB_CARPLING", lootLevel, paidDeath, 1);

        var lootValidatorRejected = false;
        try
        {
            AlphaLootPolicy.Validate(lootFlagOn, lootProfileOff, alphaDesign);
        }
        catch (InvalidOperationException)
        {
            lootValidatorRejected = true;
        }

        var rollKey = LootRollKeys.For(
            lootRoller.ProfileVersion, lootActor.CharacterId, paidDeath, 1,
            "MAN-BM-SPAWN_BM_01");

        Check(
            "alpha.loot_grant_requires_profile_and_own_flag",
            alphaDesign.Loot.DefaultGrantEnabled == false &&
            alphaDesign.Loot.NoLiveRerollOnRetry &&
            alphaDesign.Loot.InclusiveIntegers &&
            alphaDesign.Loot.CoinMinExpression == "mobLevel" &&
            alphaDesign.Loot.CoinMaxExpression == "2*mobLevel" &&
            alphaDesign.Loot.RollOnceKey.SequenceEqual(
                new[] { "profileVersion", "characterId", "deathEventId", "lifeId", "groupId" }) &&
            string.Equals(alphaDesign.Status,
                "APPROVED_FOR_IMPLEMENTATION_PRIVATE_ALPHA_NOT_PLAYTEST_BALANCED",
                StringComparison.Ordinal) &&
            !alphaDesign.DefaultEnabled &&
            !productionBlock.Granted &&
            productionBlock.BlockedReason == LootGrantPolicies.SourceShortReason &&
            !alphaDryRun.Granted &&
            alphaDryRun.BlockedReason == LootGrantPolicies.DryRunReason &&
            !afterFlagOn.Granted &&
            afterFlagOn.BlockedReason == LootGrantPolicies.DryRunReason &&
            paidOnce.Granted &&
            paidOnce.Coin >= 5 && paidOnce.Coin <= 10 &&
            paidReplay.Replayed && paidReplay.Coin == paidOnce.Coin &&
            lootValidatorRejected &&
            rollKey == string.Concat(
                lootRoller.ProfileVersion, "|", lootActor.CharacterId, "|", paidDeath,
                "|1|MAN-BM-SPAWN_BM_01"),
            $"prod={productionBlock.BlockedReason} dry={alphaDryRun.BlockedReason} " +
            $"backfill={afterFlagOn.Granted}/{afterFlagOn.BlockedReason} " +
            $"coin={paidOnce.Coin} replay={paidReplay.Replayed}/{paidReplay.Coin}");

        // ─── QOD-21 Q3: alpha quest XP valued at the accepted level ────

        // DESIGN-BM-Q3-20261104 `xp`: nextLevelXp(L) = 100 + 50L + 25L², grant =
        // floor(nextLevelXp * numerator / 100), normal 25 / boss 55, snapshotted at
        // QUEST_ACCEPT_COMMIT. The decision ships three worked levels and the
        // resolver is pinned to all six numbers, not to one of them.
        var xpRules = new AlphaQuestXpRules(alphaDesign.Progression);
        var xpNormal = new long?[4];
        var xpBoss = new long?[4];
        for (var level = 1; level <= 3; level++)
        {
            xpNormal[level] = xpRules.Resolve(new QuestXpRequest("LEVEL_BAND_BASE", level, false));
            xpBoss[level] = xpRules.Resolve(new QuestXpRequest("LEVEL_BAND_BASE", level, true));
        }

        var xpUnknownRule = xpRules.Resolve(new QuestXpRequest("SOME_OTHER_RULE", 1, false));
        var xpWithoutSnapshot = xpRules.Resolve(new QuestXpRequest("LEVEL_BAND_BASE", 0, false));
        var xpZeroRules = new AlphaQuestXpRules(alphaDesign.Progression with
        {
            NormalQuestXpNumerator = 0,
            BossQuestXpNumerator = 0
        });
        var xpZero = xpZeroRules.Resolve(new QuestXpRequest("LEVEL_BAND_BASE", 1, false));
        var xpFormulaGuard = false;
        try
        {
            _ = new AlphaQuestXpRules(alphaDesign.Progression with { XpToNext = "ceil(99+50*L)" });
        }
        catch (InvalidOperationException)
        {
            xpFormulaGuard = true;
        }

        // The snapshot, not the current level, decides the payout: accept at 1,
        // reach 5 while doing the quest, and the reward is still the level-1 value.
        var xpSnapshots = services.GetRequiredService<QuestXpSnapshotStore>();
        var xpSnapshotActor = NewPlayer("CHR_SELFCHECK_XP_SNAPSHOT");
        xpSnapshotActor.Level = 1;
        xpSnapshots.RecordAccept(xpSnapshotActor.CharacterId, "P00-02", 1);
        var xpSnapshotHasLevel = xpSnapshots.TryGetAcceptedLevel(
            xpSnapshotActor.CharacterId, "P00-02", out var xpStoredLevel);
        xpSnapshotActor.Level = 5;
        var xpSnapshotService = new ExperienceService(
            services.GetRequiredService<LevelProgressionTable>(), xpRules);
        var xpSnapshotApplied = xpSnapshotService.TryApply(
            xpSnapshotActor,
            new QuestXpRequest("LEVEL_BAND_BASE", xpStoredLevel, false),
            out var xpSnapshotGrant,
            out _);
        var xpSnapshotDelta = xpSnapshotGrant!.TotalXpAfter - xpSnapshotGrant.TotalXpBefore;
        var xpNoSnapshot = xpSnapshots.TryGetAcceptedLevel(
            "CHR_SELFCHECK_XP_NEVER_ACCEPTED", "P00-02", out _);
        // With the profile off — which is how the self-check runs — the shipped
        // container must still refuse to value LEVEL_BAND_BASE at all.
        var xpGateOffRule = services.GetRequiredService<IQuestXpRule>();
        var xpGateOffResolved = xpGateOffRule.Resolve(new QuestXpRequest("LEVEL_BAND_BASE", 1, true));

        Check(
            "alpha.xp_accept_snapshot_oracle",
            alphaDesign.Progression.NormalQuestXpNumerator == 25 &&
            alphaDesign.Progression.BossQuestXpNumerator == 55 &&
            alphaDesign.Progression.Denominator == 100 &&
            alphaDesign.Progression.AcceptSnapshot &&
            xpNormal[1] == 43 && xpNormal[2] == 75 && xpNormal[3] == 118 &&
            xpBoss[1] == 96 && xpBoss[2] == 165 && xpBoss[3] == 261 &&
            xpUnknownRule is null &&
            xpWithoutSnapshot is null &&
            xpZero == 0 &&
            xpFormulaGuard &&
            xpSnapshotHasLevel && xpStoredLevel == 1 &&
            xpSnapshotApplied && xpSnapshotDelta == 43 &&
            xpSnapshotActor.TotalXp == 43 &&
            !xpNoSnapshot &&
            xpGateOffRule is UnresolvedQuestXpRules && xpGateOffResolved is null,
            $"L1={xpNormal[1]}/{xpBoss[1]} L2={xpNormal[2]}/{xpBoss[2]} " +
            $"L3={xpNormal[3]}/{xpBoss[3]} snapshot={xpSnapshotDelta} " +
            $"level={xpSnapshotActor.Level} gateOff={xpGateOffRule.GetType().Name}");

        // The snapshot is written by the real accept service at its commit point,
        // and an idempotent replay returns the recorded answer without re-reading
        // the (now different) level.
        var xpAcceptActor = NewPlayer("CHR_SELFCHECK_XP_ACCEPT");
        xpAcceptActor.X = 42;
        xpAcceptActor.Y = 0;
        xpAcceptActor.Level = 3;
        var xpFirstAccept = questAccept.Accept(
            xpAcceptActor, "P00-01", "NPC_LYAN", new string('c', 32)).Accepted;
        var xpAcceptSnapshot = xpSnapshots.TryGetAcceptedLevel(
            xpAcceptActor.CharacterId, "P00-01", out var xpAcceptedLevel);
        xpAcceptActor.Level = 7;
        var xpReplayAccept = questAccept.Accept(
            xpAcceptActor, "P00-01", "NPC_LYAN", new string('c', 32)).Accepted;
        var xpAfterReplay = xpSnapshots.TryGetAcceptedLevel(
            xpAcceptActor.CharacterId, "P00-01", out var xpReplayedLevel);

        Check(
            "alpha.xp_snapshot_written_at_accept_commit",
            xpFirstAccept && xpAcceptSnapshot && xpAcceptedLevel == 3 &&
            xpReplayAccept && xpAfterReplay && xpReplayedLevel == 3,
            $"accepted={xpFirstAccept} level={xpAcceptedLevel} replay={xpReplayedLevel}");

        // ─── Q1c: P00-04 escort checkpoint machine ────

        // Domain-only 20 Hz machine behind P1:AlphaProfile. Sourced values:
        // NPC_LYAN, speed 3 wu/s (0,15 wu per tick), followRange 12,
        // waypoints (42,0)->(80,0)->(120,0), checkpoint waves
        // MAN-BM-WAVE_BM_ESCORT_A (MOB_CARPLING x3 at x=80) and
        // MAN-BM-WAVE_BM_ESCORT_B (MOB_WATERROOT x3 at x=120). The machine
        // holds the shared wave members dead until a checkpoint commits,
        // pauses the NPC while its wave is active, restores the NPC to the
        // last committed checkpoint on a wipe (resetting an in-progress wave
        // with new life IDs, never a cleared one), and re-holds cleared-wave
        // respawns so the wave cannot be farmed.

        WorldEntityInstance EscortWaveMember(
            string entityId,
            string recordId,
            string templateId,
            double x,
            int memberIndex)
        {
            var member = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = recordId,
                Kind = WorldEntityKinds.Mob,
                TemplateIds = new[] { templateId },
                MapId = alphaDesign.Scope.MapId,
                FloorId = "OVERWORLD",
                X = x,
                Y = 0,
                Quantity = 1,
                RespawnSeconds = 0,
                GroupId = recordId,
                MemberIndex = memberIndex,
                GroupRespawnSeconds = 30
            };
            member.Initialize();
            return member;
        }

        var escortWaveA1 = EscortWaveMember(
            "ENT_SELFCHECK_ESCORT_A_1", "MAN-BM-WAVE_BM_ESCORT_A", "MOB_CARPLING", 80, 1);
        var escortWaveA2 = EscortWaveMember(
            "ENT_SELFCHECK_ESCORT_A_2", "MAN-BM-WAVE_BM_ESCORT_A", "MOB_CARPLING", 80, 2);
        var escortWaveA3 = EscortWaveMember(
            "ENT_SELFCHECK_ESCORT_A_3", "MAN-BM-WAVE_BM_ESCORT_A", "MOB_CARPLING", 80, 3);
        var escortWaveB1 = EscortWaveMember(
            "ENT_SELFCHECK_ESCORT_B_1", "MAN-BM-WAVE_BM_ESCORT_B", "MOB_WATERROOT", 120, 1);
        var escortWaveB2 = EscortWaveMember(
            "ENT_SELFCHECK_ESCORT_B_2", "MAN-BM-WAVE_BM_ESCORT_B", "MOB_WATERROOT", 120, 2);
        var escortWaveB3 = EscortWaveMember(
            "ENT_SELFCHECK_ESCORT_B_3", "MAN-BM-WAVE_BM_ESCORT_B", "MOB_WATERROOT", 120, 3);
        var escortQuestStub = new EscortQuestStub();
        var escortClock = new ServerClock();
        var escortRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog(
                [],
                [
                    escortWaveA1, escortWaveA2, escortWaveA3,
                    escortWaveB1, escortWaveB2, escortWaveB3
                ]),
            escortClock);
        var escort = new AlphaEscortService(alphaDesign, escortQuestStub, escortRegistry);

        List<EscortResolution> TickEscort(
            AlphaEscortService service,
            PlayerSession player,
            long from,
            long to)
        {
            var all = new List<EscortResolution>();
            for (var t = from; t <= to; t++)
            {
                all.AddRange(service.Tick([player], t));
            }

            return all;
        }

        // The NPC only walks within followRange of the owner, so walking
        // phases keep the owner pinned to the NPC position each tick.
        List<EscortResolution> WalkEscortWith(
            AlphaEscortService service,
            PlayerSession player,
            long from,
            long to)
        {
            var all = new List<EscortResolution>();
            for (var t = from; t <= to; t++)
            {
                all.AddRange(service.Tick([player], t));
                if (service.TryGetNpcPosition(player.CharacterId, out var npcX, out _))
                {
                    player.X = npcX;
                }
            }

            return all;
        }

        // The escort credits only the kill notification the combat engine
        // produces, so the fixture resolves a death the way the engine does —
        // despawn the member, then report it with the event id the killer's
        // combat stream carries. The returned notification can be handed over
        // again to prove a replay cannot double-count.
        var escortKillSequence = 0L;
        CombatMobKill KillEscortWaveMember(
            AlphaEscortService service,
            WorldEntityRegistry registry,
            WorldEntityInstance member,
            string recordId,
            string killerCharacterId)
        {
            var lifeId = member.LifeId;
            registry.Despawn(member.EntityId);
            escortKillSequence++;
            var kill = new CombatMobKill(
                killerCharacterId,
                member.EntityId,
                recordId,
                lifeId,
                $"{escortKillSequence:x32}");
            ((ICombatKillSink)service).OnMobKilled(kill);
            return kill;
        }

        // With no owner at all the machine still holds every wave member dead:
        // the waves only exist after their checkpoint commits ("khi Ly An qua
        // x=80/120" in the world records).
        var escortBootHold = escort.Tick([], 1);
        Check(
            "alpha.escort_holds_waves_at_boot",
            escortBootHold.Count == 0 &&
            escortWaveA1.State == WorldEntityStates.Dead &&
            escortWaveA2.State == WorldEntityStates.Dead &&
            escortWaveA3.State == WorldEntityStates.Dead &&
            escortWaveB1.State == WorldEntityStates.Dead &&
            escortWaveB2.State == WorldEntityStates.Dead &&
            escortWaveB3.State == WorldEntityStates.Dead,
            $"a1={escortWaveA1.State} b1={escortWaveB1.State}");

        // Golden path with a 20-tick out-of-range pause: the creation tick
        // already moves, so 38 wu at 0,15 wu per tick is 254 movement ticks
        // (1 at start + 253 walking), and the x=80 commit lands exactly 20
        // ticks late (tick 1273), proving the speed and the followRange wait.
        escortQuestStub.Set("CHR_SELFCHECK_ESCORT_MAIN", QuestStates.Active);
        var escortOwner = NewPlayer("CHR_SELFCHECK_ESCORT_MAIN");
        escortOwner.X = 42;
        escortOwner.Y = 0;
        var escortStarted = TickEscort(escort, escortOwner, 1000, 1000);
        escortOwner.X = 20;
        TickEscort(escort, escortOwner, 1001, 1020);
        escortOwner.X = 42;
        var escortEarlyCommit = WalkEscortWith(escort, escortOwner, 1021, 1272);
        var escortCommit80 = WalkEscortWith(escort, escortOwner, 1273, 1273);
        Check(
            "alpha.escort_starts_and_moves_with_follow_range",
            escortStarted.Count == 1 &&
            escortStarted[0].Outcome == EscortOutcomes.Started &&
            escortStarted[0].NpcX == 42 &&
            escortEarlyCommit.All(r => r.Outcome != EscortOutcomes.CheckpointCommitted) &&
            escortCommit80.Count == 2 &&
            escortCommit80[0].Outcome == EscortOutcomes.CheckpointCommitted &&
            escortCommit80[0].Detail == "80" &&
            escortCommit80[1].Outcome == EscortOutcomes.WaveActivated &&
            escortCommit80[1].Detail == "MAN-BM-WAVE_BM_ESCORT_A",
            $"{escortStarted.FirstOrDefault()?.Outcome} " +
            $"{escortCommit80.Select(r => r.Outcome + ":" + r.Detail).FirstOrDefault()}");

        // The commit spawns wave A with fresh life IDs and the NPC waits at
        // the checkpoint while the wave is active.
        var escortPaused80 = TickEscort(escort, escortOwner, 1274, 1290);
        var escortX80Found = escort.TryGetNpcPosition(
            escortOwner.CharacterId, out double escortX80, out _);
        Check(
            "alpha.escort_checkpoint_80_commits_and_spawns_wave_a",
            escortWaveA1.State == WorldEntityStates.Alive &&
            escortWaveA1.LifeId == 2 &&
            escortWaveA2.LifeId == 2 &&
            escortWaveA3.LifeId == 2 &&
            escortPaused80.All(r => r.Outcome != EscortOutcomes.CheckpointCommitted) &&
            escortX80Found &&
            escortX80 == 80,
            $"a1={escortWaveA1.State}/{escortWaveA1.LifeId} npc={escortX80}");

        // Two of three credited deaths do not clear the wave, and replaying one of
        // them adds no credit (the same death event id is the same key). The third
        // kill clears it and the NPC resumes on the tick that reports the clear.
        KillEscortWaveMember(
            escort,
            escortRegistry,
            escortWaveA1,
            "MAN-BM-WAVE_BM_ESCORT_A",
            escortOwner.CharacterId);
        var escortKillA2 = KillEscortWaveMember(
            escort,
            escortRegistry,
            escortWaveA2,
            "MAN-BM-WAVE_BM_ESCORT_A",
            escortOwner.CharacterId);
        ((ICombatKillSink)escort).OnMobKilled(escortKillA2);
        var escortTwoKills = TickEscort(escort, escortOwner, 1300, 1300);
        KillEscortWaveMember(
            escort,
            escortRegistry,
            escortWaveA3,
            "MAN-BM-WAVE_BM_ESCORT_A",
            escortOwner.CharacterId);
        var escortWaveACleared = TickEscort(escort, escortOwner, 1301, 1301);
        var escortXAfterAFound = escort.TryGetNpcPosition(
            escortOwner.CharacterId, out double escortXAfterA, out _);
        Check(
            "alpha.escort_wave_a_clears_then_resumes",
            escortTwoKills.All(r => r.Outcome != EscortOutcomes.WaveCleared) &&
            escortWaveACleared.Count == 1 &&
            escortWaveACleared[0].Outcome == EscortOutcomes.WaveCleared &&
            escortWaveACleared[0].Detail == "MAN-BM-WAVE_BM_ESCORT_A" &&
            escortXAfterAFound &&
            escortXAfterA > 80,
            $"{escortWaveACleared.FirstOrDefault()?.Outcome} npc={escortXAfterA}");

        // Wipe mid-segment: the NPC restores to the last committed checkpoint
        // and the cleared wave stays dead (not farmable); reviving resumes
        // the walk from the checkpoint.
        WalkEscortWith(escort, escortOwner, 1302, 1340);
        escortOwner.Hp = 0;
        var escortWipeMidWalk = TickEscort(escort, escortOwner, 1341, 1341);
        escortOwner.Hp = 100;
        escortOwner.X = 80;
        var escortWipeHold = TickEscort(escort, escortOwner, 1342, 1342);
        Check(
            "alpha.escort_wipe_restores_checkpoint",
            escortWipeMidWalk.Count == 1 &&
            escortWipeMidWalk[0].Outcome == EscortOutcomes.Wiped &&
            escortWipeMidWalk[0].Detail == "checkpoint=80" &&
            escortWipeMidWalk[0].NpcX == 80 &&
            escortWaveA1.State == WorldEntityStates.Dead &&
            escortWaveA2.State == WorldEntityStates.Dead &&
            escortWaveA3.State == WorldEntityStates.Dead &&
            escortWipeHold.All(r => r.Outcome != EscortOutcomes.WaveActivated),
            $"{escortWipeMidWalk.FirstOrDefault()?.Detail} a1={escortWaveA1.State}");

        // The MobSpawnGroupService would respawn a cleared group after 30 s;
        // the machine re-holds the members dead on the next tick so the
        // completed checkpoint cannot be farmed.
        escortWaveA1.ForceRespawn();
        escortWaveA2.ForceRespawn();
        escortWaveA3.ForceRespawn();
        var escortFarmBlock = TickEscort(escort, escortOwner, 1343, 1343);
        Check(
            "alpha.escort_completed_wave_not_farmable",
            escortFarmBlock.All(r => r.Outcome != EscortOutcomes.WaveActivated) &&
            escortWaveA1.State == WorldEntityStates.Dead &&
            escortWaveA2.State == WorldEntityStates.Dead &&
            escortWaveA3.State == WorldEntityStates.Dead,
            $"a1={escortWaveA1.State} outcomes={escortFarmBlock.Count}");

        // Second segment: 40 wu is 267 movement ticks from the 1342 resume
        // (the 1343 farm tick also moves), so the x=120 commit lands at tick
        // 1608 (1342 + 266).
        WalkEscortWith(escort, escortOwner, 1344, 1607);
        var escortCommit120 = WalkEscortWith(escort, escortOwner, 1608, 1608);
        Check(
            "alpha.escort_checkpoint_120_and_wave_b",
            escortCommit120.Count == 2 &&
            escortCommit120[0].Outcome == EscortOutcomes.CheckpointCommitted &&
            escortCommit120[0].Detail == "120" &&
            escortCommit120[1].Outcome == EscortOutcomes.WaveActivated &&
            escortCommit120[1].Detail == "MAN-BM-WAVE_BM_ESCORT_B" &&
            escortWaveB1.State == WorldEntityStates.Alive &&
            escortWaveB1.LifeId == 2,
            $"{escortCommit120.Select(r => r.Outcome + ":" + r.Detail).FirstOrDefault()} " +
            $"b1={escortWaveB1.State}/{escortWaveB1.LifeId}");

        // Wipe mid-wave: one of three credited deaths down, the wipe restores the
        // NPC to 120 and re-activates the pending wave. Only the member that is
        // actually dead is re-spawned (fresh life ID); the ones still fighting keep
        // their lives, and the instance's credit set resets to zero either way, so
        // the fight restarts from the beginning without disturbing a life that is
        // still in play.
        KillEscortWaveMember(
            escort,
            escortRegistry,
            escortWaveB1,
            "MAN-BM-WAVE_BM_ESCORT_B",
            escortOwner.CharacterId);
        TickEscort(escort, escortOwner, 1609, 1609);
        escortOwner.Hp = 0;
        var escortWipeMidWave = TickEscort(escort, escortOwner, 1610, 1610);
        escortOwner.Hp = 100;
        Check(
            "alpha.escort_wipe_mid_wave_resets_lives",
            escortWipeMidWave.Count == 2 &&
            escortWipeMidWave.Any(r => r.Outcome == EscortOutcomes.Wiped &&
                r.NpcX == 120 && r.Detail == "checkpoint=120") &&
            escortWipeMidWave.Any(r => r.Outcome == EscortOutcomes.WaveActivated &&
                r.Detail == "MAN-BM-WAVE_BM_ESCORT_B") &&
            escortWaveB1.State == WorldEntityStates.Alive &&
            escortWaveB1.LifeId == 3 &&
            escortWaveB2.State == WorldEntityStates.Alive &&
            escortWaveB2.LifeId == 2 &&
            escortWaveB3.State == WorldEntityStates.Alive &&
            escortWaveB3.LifeId == 2,
            $"b1={escortWaveB1.State}/{escortWaveB1.LifeId} b2={escortWaveB2.LifeId}");

        // The refight: the reset lives have to be killed again — the credit the
        // previous generation earned is gone — and the third kill completes the
        // escort at the final waypoint.
        KillEscortWaveMember(
            escort,
            escortRegistry,
            escortWaveB1,
            "MAN-BM-WAVE_BM_ESCORT_B",
            escortOwner.CharacterId);
        KillEscortWaveMember(
            escort,
            escortRegistry,
            escortWaveB2,
            "MAN-BM-WAVE_BM_ESCORT_B",
            escortOwner.CharacterId);
        var escortResetPartial = TickEscort(escort, escortOwner, 1611, 1611);
        KillEscortWaveMember(
            escort,
            escortRegistry,
            escortWaveB3,
            "MAN-BM-WAVE_BM_ESCORT_B",
            escortOwner.CharacterId);
        var escortCompleted = TickEscort(escort, escortOwner, 1612, 1612);
        Check(
            "alpha.escort_completes_after_wave_b",
            escortResetPartial.All(r => r.Outcome != EscortOutcomes.WaveCleared) &&
            escortCompleted.Any(r => r.Outcome == EscortOutcomes.WaveCleared &&
                r.Detail == "MAN-BM-WAVE_BM_ESCORT_B") &&
            escortCompleted.Any(r => r.Outcome == EscortOutcomes.Completed &&
                r.NpcX == 120 && r.NpcY == 0),
            string.Join(",", escortCompleted.Select(r => r.Outcome)));

        // The instance ends when the quest leaves ACTIVE and the cleared
        // waves go back under hold.
        escortQuestStub.Set("CHR_SELFCHECK_ESCORT_MAIN", QuestStates.Completed);
        var escortEnded = TickEscort(escort, escortOwner, 1613, 1613);
        Check(
            "alpha.escort_ends_when_quest_leaves_active",
            escortEnded.Count == 1 &&
            escortEnded[0].Outcome == EscortOutcomes.Ended &&
            escortEnded[0].Detail == QuestStates.Completed &&
            escortWaveB1.State == WorldEntityStates.Dead &&
            escortWaveB2.State == WorldEntityStates.Dead &&
            escortWaveB3.State == WorldEntityStates.Dead,
            $"{escortEnded.FirstOrDefault()?.Outcome} b1={escortWaveB1.State}");

        // A player without the quest never opens an instance and nothing
        // spawns.
        var escortStranger = NewPlayer("CHR_SELFCHECK_ESCORT_STRANGER");
        escortStranger.X = 42;
        escortStranger.Y = 0;
        var escortStrangerTick = TickEscort(escort, escortStranger, 2000, 2100);
        Check(
            "alpha.escort_ignores_player_without_quest",
            escortStrangerTick.Count == 0 &&
            !escort.TryGetNpcPosition(escortStranger.CharacterId, out _, out _) &&
            escortWaveA1.State == WorldEntityStates.Dead,
            $"outcomes={escortStrangerTick.Count}");

        // Owner-specific instances: two owners, one in range and one far
        // away; only the in-range NPC walks, so no second clone moves.
        var escortTwoStub = new EscortQuestStub();
        escortTwoStub.Set("CHR_SELFCHECK_ESCORT_TWO_A", QuestStates.Active);
        escortTwoStub.Set("CHR_SELFCHECK_ESCORT_TWO_B", QuestStates.Active);
        var escortTwoRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog(
                [],
                [
                    escortWaveA1, escortWaveA2, escortWaveA3,
                    escortWaveB1, escortWaveB2, escortWaveB3
                ]),
            escortClock);
        var escortTwo = new AlphaEscortService(alphaDesign, escortTwoStub, escortTwoRegistry);
        var escortOwnerA = NewPlayer("CHR_SELFCHECK_ESCORT_TWO_A");
        escortOwnerA.X = 42;
        escortOwnerA.Y = 0;
        var escortOwnerB = NewPlayer("CHR_SELFCHECK_ESCORT_TWO_B");
        escortOwnerB.X = 10;
        escortOwnerB.Y = 0;
        List<EscortResolution> escortTwoA = [];
        List<EscortResolution> escortTwoB = [];
        for (var t = 3000; t <= 3254; t++)
        {
            var twoResolutions = escortTwo.Tick([escortOwnerA, escortOwnerB], t);
            escortTwoA.AddRange(twoResolutions.Where(r =>
                string.Equals(r.CharacterId, "CHR_SELFCHECK_ESCORT_TWO_A", StringComparison.Ordinal)));
            escortTwoB.AddRange(twoResolutions.Where(r =>
                string.Equals(r.CharacterId, "CHR_SELFCHECK_ESCORT_TWO_B", StringComparison.Ordinal)));
            if (escortTwo.TryGetNpcPosition("CHR_SELFCHECK_ESCORT_TWO_A", out var twoAx, out _))
            {
                escortOwnerA.X = twoAx;
            }
        }

        var escortBxFound = escortTwo.TryGetNpcPosition(
            "CHR_SELFCHECK_ESCORT_TWO_B", out double escortBx, out _);
        Check(
            "alpha.escort_owner_specific_instances",
            escortTwoA.Any(r => r.Outcome == EscortOutcomes.CheckpointCommitted) &&
            escortTwoB.Count == 1 &&
            escortTwoB[0].Outcome == EscortOutcomes.Started &&
            escortBxFound &&
            escortBx == 42,
            $"a={escortTwoA.Count} b={escortTwoB.Count} bx={escortBx}");

        // Without the wave entities in the registry the machine reaches the first
        // checkpoint and then stops: activation fails with a diagnostic naming the
        // wave and how many actors it ships, and the escort neither fabricates a
        // spawn nor walks on to "complete" a run it never fought.
        var escortInertRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], []),
            escortClock);
        var escortInertStub = new EscortQuestStub();
        escortInertStub.Set("CHR_SELFCHECK_ESCORT_INERT", QuestStates.Active);
        var escortInert = new AlphaEscortService(alphaDesign, escortInertStub, escortInertRegistry);
        var escortInertOwner = NewPlayer("CHR_SELFCHECK_ESCORT_INERT");
        escortInertOwner.X = 42;
        escortInertOwner.Y = 0;
        List<EscortResolution> escortInertResolutions = [];
        for (var t = 4000; t <= 4700; t++)
        {
            escortInertResolutions.AddRange(escortInert.Tick([escortInertOwner], t));
            if (escortInert.TryGetNpcPosition(escortInertOwner.CharacterId, out var inertX, out _))
            {
                escortInertOwner.X = inertX;
            }
        }

        Check(
            "alpha.escort_missing_wave_blocks_instead_of_completing",
            escortInertResolutions.Any(r => r.Outcome == EscortOutcomes.CheckpointCommitted &&
                r.Detail == "80") &&
            escortInertResolutions.Count(r =>
                r.Outcome == EscortOutcomes.WaveActivationFailed) == 1 &&
            escortInertResolutions.Single(r =>
                r.Outcome == EscortOutcomes.WaveActivationFailed).Detail ==
                "wave MAN-BM-WAVE_BM_ESCORT_A ships 0 of 3 required MOB_CARPLING actors" &&
            escortInertResolutions.All(r => r.Outcome != EscortOutcomes.WaveActivated &&
                r.Outcome != EscortOutcomes.WaveCleared &&
                r.Outcome != EscortOutcomes.CheckpointCommitted ||
                r.Detail == "80") &&
            escortInertResolutions.All(r => r.Outcome != EscortOutcomes.Completed) &&
            escortInert.TryGetNpcPosition(escortInertOwner.CharacterId, out var inertHeld, out _) &&
            inertHeld == 80,
            $"outcomes={string.Join(",", escortInertResolutions.Select(r => r.Outcome))}");

        // ─── QOD-21 Q2: escort credit authority across two owners ────

        // One wave group, two owners. The content ships a single shared group per
        // wave, so the machine has to prove three things: an owner is only ever
        // credited for the kills its own cast landed, one owner's wipe never
        // re-spawns (and therefore never resets) the generation the other owner is
        // fighting, and a deferred activation says so instead of walking on.
        var escortIsoStub = new EscortQuestStub();
        escortIsoStub.Set("CHR_SELFCHECK_ESCORT_ISO_A", QuestStates.Active);
        escortIsoStub.Set("CHR_SELFCHECK_ESCORT_ISO_B", QuestStates.Active);
        var escortIsoM1 = EscortWaveMember(
            "ENT_SELFCHECK_ESCORT_ISO_1", "MAN-BM-WAVE_BM_ESCORT_A", "MOB_CARPLING", 80, 1);
        var escortIsoM2 = EscortWaveMember(
            "ENT_SELFCHECK_ESCORT_ISO_2", "MAN-BM-WAVE_BM_ESCORT_A", "MOB_CARPLING", 80, 2);
        var escortIsoM3 = EscortWaveMember(
            "ENT_SELFCHECK_ESCORT_ISO_3", "MAN-BM-WAVE_BM_ESCORT_A", "MOB_CARPLING", 80, 3);
        var escortIsoRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [escortIsoM1, escortIsoM2, escortIsoM3]),
            escortClock);
        var escortIso = new AlphaEscortService(alphaDesign, escortIsoStub, escortIsoRegistry);
        var escortIsoOwnerA = NewPlayer("CHR_SELFCHECK_ESCORT_ISO_A");
        escortIsoOwnerA.X = 42;
        escortIsoOwnerA.Y = 0;
        var escortIsoOwnerB = NewPlayer("CHR_SELFCHECK_ESCORT_ISO_B");
        escortIsoOwnerB.X = 42;
        escortIsoOwnerB.Y = 0;
        List<EscortResolution> escortIsoA = [];
        List<EscortResolution> escortIsoB = [];
        for (var t = 5000; t <= 5270; t++)
        {
            var isoRound = escortIso.Tick([escortIsoOwnerA, escortIsoOwnerB], t);
            escortIsoA.AddRange(isoRound.Where(r =>
                string.Equals(r.CharacterId, "CHR_SELFCHECK_ESCORT_ISO_A", StringComparison.Ordinal)));
            escortIsoB.AddRange(isoRound.Where(r =>
                string.Equals(r.CharacterId, "CHR_SELFCHECK_ESCORT_ISO_B", StringComparison.Ordinal)));
            if (escortIso.TryGetNpcPosition(escortIsoOwnerA.CharacterId, out var isoAx, out _))
            {
                escortIsoOwnerA.X = isoAx;
            }

            if (escortIso.TryGetNpcPosition(escortIsoOwnerB.CharacterId, out var isoBx, out _))
            {
                escortIsoOwnerB.X = isoBx;
            }
        }

        Check(
            "alpha.escort_two_owners_join_one_shared_wave",
            escortIsoA.Count(r => r.Outcome == EscortOutcomes.WaveActivated) == 1 &&
            escortIsoB.Count(r => r.Outcome == EscortOutcomes.WaveActivated) == 1 &&
            escortIsoM1.State == WorldEntityStates.Alive &&
            escortIsoM1.LifeId == 2 &&
            escortIsoM2.LifeId == 2 &&
            escortIsoM3.LifeId == 2 &&
            escortIsoA.All(r => r.Outcome != EscortOutcomes.WaveActivationFailed) &&
            escortIsoB.All(r => r.Outcome != EscortOutcomes.WaveActivationFailed),
            $"a={string.Join(",", escortIsoA.Select(r => r.Outcome))} " +
            $"m1={escortIsoM1.LifeId}");

        // Owner A kills one member and then dies. Its wipe re-activation must not
        // touch the group owner B is still fighting: the same lives, the same dead
        // member, and A reports the deferral instead of completing.
        KillEscortWaveMember(
            escortIso,
            escortIsoRegistry,
            escortIsoM1,
            "MAN-BM-WAVE_BM_ESCORT_A",
            escortIsoOwnerA.CharacterId);
        escortIsoOwnerA.Hp = 0;
        var escortIsoWipeRound = escortIso.Tick([escortIsoOwnerA, escortIsoOwnerB], 5300);
        escortIsoOwnerA.Hp = 100;
        Check(
            "alpha.escort_wipe_does_not_respawn_another_owners_wave",
            escortIsoWipeRound.Any(r =>
                r.CharacterId == "CHR_SELFCHECK_ESCORT_ISO_A" &&
                r.Outcome == EscortOutcomes.Wiped) &&
            escortIsoWipeRound.Any(r =>
                r.CharacterId == "CHR_SELFCHECK_ESCORT_ISO_A" &&
                r.Outcome == EscortOutcomes.WaveActivationFailed &&
                r.Detail ==
                    "wave MAN-BM-WAVE_BM_ESCORT_A is held by another owner's active fight") &&
            escortIsoWipeRound.All(r =>
                r.CharacterId != "CHR_SELFCHECK_ESCORT_ISO_B" ||
                (r.Outcome != EscortOutcomes.Wiped &&
                 r.Outcome != EscortOutcomes.WaveActivationFailed &&
                 r.Outcome != EscortOutcomes.WaveCleared)) &&
            escortIsoM1.State == WorldEntityStates.Dead &&
            escortIsoM1.LifeId == 2 &&
            escortIsoM2.State == WorldEntityStates.Alive &&
            escortIsoM2.LifeId == 2 &&
            escortIsoM3.State == WorldEntityStates.Alive &&
            escortIsoM3.LifeId == 2,
            $"round={string.Join(",", escortIsoWipeRound.Select(r => r.Outcome))} " +
            $"m1={escortIsoM1.State}/{escortIsoM1.LifeId}");

        // The world's own group respawn brings the dead member back under a fresh
        // life; both owners re-arm onto it (activation is no longer deferred). Owner
        // B then kills all three. Only B's instance clears — the credit key names the
        // instance of the character the engine reported as the killer.
        escortIsoM1.ForceRespawn();
        var escortIsoRespawnRound = escortIso.Tick([escortIsoOwnerA, escortIsoOwnerB], 5301);
        KillEscortWaveMember(
            escortIso, escortIsoRegistry, escortIsoM1,
            "MAN-BM-WAVE_BM_ESCORT_A", escortIsoOwnerB.CharacterId);
        KillEscortWaveMember(
            escortIso, escortIsoRegistry, escortIsoM2,
            "MAN-BM-WAVE_BM_ESCORT_A", escortIsoOwnerB.CharacterId);
        KillEscortWaveMember(
            escortIso, escortIsoRegistry, escortIsoM3,
            "MAN-BM-WAVE_BM_ESCORT_A", escortIsoOwnerB.CharacterId);
        var escortIsoBClearRound = escortIso.Tick([escortIsoOwnerA, escortIsoOwnerB], 5302);
        Check(
            "alpha.escort_kill_credit_is_owner_scoped",
            escortIsoRespawnRound.Count(r => r.Outcome == EscortOutcomes.WaveActivated) == 1 &&
            escortIsoRespawnRound.Single(r => r.Outcome == EscortOutcomes.WaveActivated)
                .CharacterId == "CHR_SELFCHECK_ESCORT_ISO_A" &&
            escortIsoM1.LifeId == 3 &&
            escortIsoBClearRound.Count(r => r.Outcome == EscortOutcomes.WaveCleared) == 1 &&
            escortIsoBClearRound.Single(r => r.Outcome == EscortOutcomes.WaveCleared)
                .CharacterId == "CHR_SELFCHECK_ESCORT_ISO_B" &&
            escortIso.TryGetNpcPosition("CHR_SELFCHECK_ESCORT_ISO_A", out var isoAStill, out _) &&
            isoAStill == 80 &&
            escortIso.TryGetNpcPosition("CHR_SELFCHECK_ESCORT_ISO_B", out var isoBAfter, out _) &&
            isoBAfter > 80,
            $"respawn={string.Join(",", escortIsoRespawnRound.Select(r => r.Outcome))} " +
            $"clear={string.Join(",", escortIsoBClearRound.Select(r => r.Outcome))} " +
            $"m1={escortIsoM1.LifeId}");

        // ─── QOD-21 Q3: the v2 slot vocabulary beside the frozen v1 five ────

        // The twelve tokens are the contract the clients bind to, so both directions
        // of the side-by-side rule are pinned: the design list and the implemented
        // list are one source of truth, every token is reachable from a canonical
        // catalog slot label, and the collapse onto v1's five tokens never invents a
        // v1 name for something v1 cannot say.
        InventoryV2Slots.ValidateAgainstDesign(alphaDesign.Inventory.EquipmentSlots);
        InventoryV2Slots.ValidateLabelMap();
        var v2HatCollapses = InventoryV2Slots.CollapseToV1(InventoryV2Slots.Hat, out var v2HatV1);
        var v2RingCollapses = InventoryV2Slots.CollapseToV1(InventoryV2Slots.RingLeft, out var v2RingV1);
        var v2LegsCollapses = InventoryV2Slots.CollapseToV1(InventoryV2Slots.Legs, out var v2LegsV1);
        var v2GlovesCollapses = InventoryV2Slots.CollapseToV1(InventoryV2Slots.Gloves, out _);
        var v2LabelResolves = InventoryV2Slots.TryResolveLabel(
            ItemCatalog.ArmorCategory, "Quần", out var v2LegsSlot);
        var v2WeaponResolves = InventoryV2Slots.TryResolveLabel(
            ItemCatalog.WeaponCategory, "Cung", out var v2WeaponSlot);
        var v2SealResolves = InventoryV2Slots.TryResolveLabel(
            ItemCatalog.AccessoryCategory, "Ấn hộ mệnh", out var v2SealSlot);
        var v2NonEquipmentRejected = !InventoryV2Slots.TryResolveLabel(
            "TIÊU HAO", "Nón", out _);
        var v2UnknownLabelRejected = !InventoryV2Slots.TryResolveLabel(
            ItemCatalog.ArmorCategory, "Khiên", out _);
        var v2OrderGuard = false;
        try
        {
            InventoryV2Slots.ValidateAgainstDesign(
                alphaDesign.Inventory.EquipmentSlots.Reverse().ToList());
        }
        catch (InvalidOperationException)
        {
            v2OrderGuard = true;
        }

        var v2Unsupported = new InventoryV2UnsupportedItem
        {
            InstanceId = "ITM_SELFCHECK_V2_ORPHAN",
            TemplateId = "EQ-MK-CHEST-T1-R-COMMON",
            SourceSlot = "RING_S",
            Reason = InventoryV2UnsupportedReasons.UnmappedSlot
        };
        var v2Snapshot = new InventorySnapshotV2
        {
            SlotSpec = alphaDesign.Inventory.WireMigration,
            InventoryRevision = 4,
            BagSlots = alphaDesign.Inventory.BagSlots,
            Slots = InventoryV2Slots.All.Select(slot => new InventoryV2SlotEntry
            {
                SlotId = slot,
                Item = slot switch
                {
                    InventoryV2Slots.Legs => new InventoryItemV2
                    {
                        InstanceId = "ITM_SELFCHECK_V2_LEGS",
                        TemplateId = "EQ-MK-LEGS-T1-R-COMMON",
                        Stack = 1,
                        Location = "EQUIPPED",
                        SlotId = InventoryV2Slots.Legs,
                        Durability = 0,
                        Version = 1
                    },
                    InventoryV2Slots.RingLeft => new InventoryItemV2
                    {
                        InstanceId = "ITM_SELFCHECK_V2_RING_L",
                        TemplateId = "EQ-MK-RING_L-T1-R-COMMON",
                        Stack = 1,
                        Location = "EQUIPPED",
                        SlotId = InventoryV2Slots.RingLeft,
                        Durability = 0,
                        Version = 1
                    },
                    _ => null
                }
            }).ToList(),
            Bag =
            [
                new InventoryItemV2
                {
                    InstanceId = "ITM_SELFCHECK_V2_POTION",
                    TemplateId = "POT-HP-01",
                    Stack = 5,
                    Location = "BAG",
                    SlotId = null,
                    Durability = 0,
                    Version = 1
                }
            ],
            Unsupported = [v2Unsupported],
            Currencies = [new InventoryCurrency { CurrencyId = "COIN", Amount = 80 }]
        };
        var v2Wire = JsonSerializer.Serialize(v2Snapshot, P1Json.Options);
        var v2RoundTrip = JsonSerializer.Deserialize<InventorySnapshotV2>(v2Wire, P1Json.Options);
        Check(
            "alpha.inventory_v2_slots_beside_v1_five",
            InventoryV2Slots.All.Count == 12 &&
            InventoryV2Slots.All.Distinct(StringComparer.Ordinal).Count() == 12 &&
            InventoryV2Slots.All.SequenceEqual(
                alphaDesign.Inventory.EquipmentSlots, StringComparer.Ordinal) &&
            alphaDesign.Inventory.BagSlots == 100 &&
            alphaDesign.Inventory.SchemaVersion == 2 &&
            string.Equals(alphaDesign.Inventory.WireMigration,
                "V2_SIDE_BY_SIDE_KEEP_V1_FIVE_SLOT_CONTRACT", StringComparison.Ordinal) &&
            v2HatCollapses && v2HatV1 == EquipmentSlots.Hat &&
            v2RingCollapses && v2RingV1 == EquipmentSlots.Accessory &&
            !v2LegsCollapses && v2LegsV1.Length == 0 &&
            !v2GlovesCollapses &&
            v2LabelResolves && v2LegsSlot == InventoryV2Slots.Legs &&
            v2WeaponResolves && v2WeaponSlot == InventoryV2Slots.Weapon &&
            v2SealResolves && v2SealSlot == InventoryV2Slots.Seal &&
            v2NonEquipmentRejected &&
            v2UnknownLabelRejected &&
            v2OrderGuard &&
            v2RoundTrip is not null &&
            v2RoundTrip.Slots.Count == 12 &&
            v2RoundTrip.Slots.Count(entry => entry.Item is null) == 10 &&
            v2RoundTrip.Bag.Count == 1 &&
            v2RoundTrip.Bag[0].SlotId is null &&
            v2RoundTrip.Unsupported.Count == 1 &&
            v2RoundTrip.Unsupported[0].Reason == InventoryV2UnsupportedReasons.UnmappedSlot &&
            v2RoundTrip.Unsupported[0].SourceSlot == "RING_S" &&
            v2RoundTrip.Slots.Single(entry => entry.SlotId == InventoryV2Slots.RingLeft)
                .Item?.TemplateId == "EQ-MK-RING_L-T1-R-COMMON",
            $"collapse={v2HatV1}/{v2RingV1}/{v2LegsV1} roundTrip={v2RoundTrip?.Slots.Count} " +
            $"empty={v2RoundTrip?.Slots.Count(e => e.Item is null)} order={v2OrderGuard}");

        // ─── QOD-21 Q2: the P00-05 Mãng Cốt encounter machine ────

        // The real encounter on the 20 Hz loop: the arena gate, the telegraph
        // → impact → recovery timeline per sourced move shape, the C→B→A
        // priority with no overlap, the phase thresholds evaluated at the
        // impact frame, the phase guard, the wipe countdown with a fresh life
        // and the quest-instance holds (world-event boss disabled, trial NPC
        // visibility window).
        WorldEntityInstance BossWorldEntity(string entityId, string recordId)
        {
            var boss = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = recordId,
                Kind = WorldEntityKinds.Boss,
                TemplateIds = new[] { "BOSS_MANG_COT" },
                MapId = alphaDesign.Scope.MapId,
                FloorId = "OVERWORLD",
                X = 178,
                Y = 0,
                Quantity = 1,
                RespawnSeconds = 0
            };
            boss.Initialize();
            return boss;
        }

        var bossClock = new ServerClock();
        (AlphaBossEncounterService Service, BossEncounterQuestStub Quest,
            WorldEntityInstance QuestBoss, WorldEntityInstance EventBoss) NewBossFixture(
                bool damageGateOn)
        {
            var questBoss = BossWorldEntity(
                "ENT_SELFCHECK_BOSS_QUEST", alphaDesign.QuestRules.P00_05_BossRecordId);
            var eventBoss = BossWorldEntity(
                "ENT_SELFCHECK_BOSS_EVENT", alphaDesign.QuestRules.P00_05_WorldEventRecordIdDisabled);
            var registry = new WorldEntityRegistry(
                new WorldEntityCatalog([], [questBoss, eventBoss]), bossClock);
            var stub = new BossEncounterQuestStub();
            var feature = damageGateOn ? enabledCombat : combatDamage;
            var service = new AlphaBossEncounterService(
                alphaDesign,
                stub,
                registry,
                feature,
                new GuardDefenseService(
                    new GuardWindowStore(),
                    feature,
                    new CombatEventStore(new CombatEventStreamOptions())),
                new PlayerLifeLedger());
            return (service, stub, questBoss, eventBoss);
        }

        List<BossEncounterResolution> TickBoss(
            AlphaBossEncounterService service,
            PlayerSession player,
            long from,
            long to)
        {
            var all = new List<BossEncounterResolution>();
            for (var t = from; t <= to; t++)
            {
                all.AddRange(service.Tick([player], t));
            }

            return all;
        }

        PlayerSession NewArenaOwner(string characterId, double x, int hp = 4000)
        {
            var owner = NewPlayer(characterId, hp: hp);
            owner.X = x;
            owner.Y = 0;
            return owner;
        }

        // Registration needs the quest active AND the owner inside the ring.
        var (bossService, bossQuest, bossQuestEntity, bossEventEntity) =
            NewBossFixture(damageGateOn: true);
        bossQuest.Set("CHR_SELFCHECK_BOSS_MAIN", QuestStates.Active);
        var bossOwner = NewArenaOwner("CHR_SELFCHECK_BOSS_MAIN", 181);
        var bossRegistered = TickBoss(bossService, bossOwner, 5000, 5000);
        var bossOpenState = bossService.TryGetState("CHR_SELFCHECK_BOSS_MAIN", out var bossOpen);
        Check(
            "alpha.boss_registers_and_opens_move_c",
            bossRegistered.Count == 2 &&
            bossRegistered[0].Outcome == BossEncounterOutcomeCodes.Registered &&
            bossRegistered[0].Detail == "life=1" &&
            bossRegistered[1].Outcome == BossEncounterOutcomeCodes.Telegraph &&
            bossRegistered[1].Detail == "C" &&
            bossOpenState &&
            bossOpen.Status == "OPEN" &&
            bossOpen.Phase == 1 &&
            bossOpen.BossHp == 1200 &&
            bossOpen.BossMaxHp == 1200 &&
            bossOpen.ActiveMoveId == "C" &&
            bossOpen.ActiveMoveState == "TELEGRAPH" &&
            bossQuestEntity.State == WorldEntityStates.Alive,
            $"{string.Join(",", bossRegistered.Select(r => r.Outcome + ":" + (r.Detail ?? "-")))}");

        // The world-event record at the same coordinate is a different entity and
        // must survive another player's quest instance: instance scoping, not a
        // global despawn, is what keeps the quest boss and the world boss apart.
        var bossHoldTicks = TickBoss(bossService, bossOwner, 5001, 5001);
        bossEventEntity.ForceRespawn();
        TickBoss(bossService, bossOwner, 5002, 5002);
        Check(
            "alpha.boss_leaves_world_event_boss_untouched",
            bossHoldTicks.Count == 0 &&
            bossEventEntity.State == WorldEntityStates.Alive &&
            bossQuestEntity.State == WorldEntityStates.Alive,
            $"outcomes={bossHoldTicks.Count} event={bossEventEntity.State} " +
            $"quest={bossQuestEntity.State}");

        // Move C (Vòng Bọt, ANNULUS 3–7 WU, windup 1.0 s = 20 ticks) lands at
        // tick 5020; with the damage gate off the frame still commits but pays
        // nothing, the same rule as the mob impacts.
        var (bossGateService, bossGateQuest, _, _) = NewBossFixture(damageGateOn: false);
        bossGateQuest.Set("CHR_SELFCHECK_BOSS_GATE", QuestStates.Active);
        var bossGateOwner = NewArenaOwner("CHR_SELFCHECK_BOSS_GATE", 181);
        var bossGateFrames = TickBoss(bossGateService, bossGateOwner, 5000, 5020);
        Check(
            "alpha.boss_damage_gate_off_blocks_impact",
            bossGateFrames.Any(r => r.Outcome == BossEncounterOutcomeCodes.ImpactBlocked &&
                r.Detail == $"C:{MobAttackBlockedReasons.GateOff}" && r.Damage == 0) &&
            bossGateOwner.Hp == 4000,
            $"{string.Join(",", bossGateFrames.Select(r => r.Outcome))}");

        // The full C→B→A cycle against one stationary owner inside every shape:
        // C 24×1.3 → 28, B 24×1.5 → 32, A 24×1.2 → 26 against armor 10, one
        // revision bump per landed impact, and the impacts only ever open after
        // the previous move's recovery (no overlap).
        var bossImpacts = TickBoss(bossService, bossOwner, 5001, 5110);
        var bossLanded = bossImpacts
            .Where(r => r.Outcome == BossEncounterOutcomeCodes.Impact)
            .Select(r => $"{r.Detail}={r.Damage}")
            .ToArray();
        Check(
            "alpha.boss_impacts_stationary_owner_in_move_order",
            bossLanded.SequenceEqual(new[] { "C=28", "B=32", "A=26" }) &&
            bossImpacts.Where(r => r.Outcome == BossEncounterOutcomeCodes.Telegraph)
                .Select(r => r.Detail).SequenceEqual(new[] { "B", "A" }) &&
            bossOwner.Hp == 4000 - 28 - 32 - 26 &&
            bossOwner.Revision == 4,
            string.Join(",", bossLanded) + $" hp={bossOwner.Hp} rev={bossOwner.Revision}");

        // Out at 9 WU the owner is inside the ring but outside the annulus
        // (outer 7) and outside the cone (8): those frames dodge, while the
        // telegraph-start-locked circle (r 4 on the position held at telegraph
        // start) still lands because nobody moved.
        var (bossDodgeService, bossDodgeQuest, _, _) = NewBossFixture(damageGateOn: true);
        bossDodgeQuest.Set("CHR_SELFCHECK_BOSS_DODGE", QuestStates.Active);
        var bossDodgeOwner = NewArenaOwner("CHR_SELFCHECK_BOSS_DODGE", 187);
        var bossDodgeFrames = TickBoss(bossDodgeService, bossDodgeOwner, 5000, 5110);
        Check(
            "alpha.boss_out_of_shape_frames_are_dodged",
            bossDodgeFrames.Any(r => r.Outcome == BossEncounterOutcomeCodes.ImpactBlocked &&
                r.Detail == "C:DODGED") &&
            bossDodgeFrames.Any(r => r.Outcome == BossEncounterOutcomeCodes.ImpactBlocked &&
                r.Detail == "A:DODGED") &&
            bossDodgeFrames.Any(r => r.Outcome == BossEncounterOutcomeCodes.Impact &&
                r.Detail == "B" && r.Damage == 32) &&
            bossDodgeOwner.Hp == 4000 - 32,
            $"{string.Join(",", bossDodgeFrames
                .Where(r => r.Outcome == BossEncounterOutcomeCodes.Impact ||
                            r.Outcome == BossEncounterOutcomeCodes.ImpactBlocked)
                .Select(r => r.Detail))}");

        // Damage before phase: HP dragged to 710 (60% of 1200) before the first
        // frame flips the fight to phase 2 at that frame. The 20-tick phase
        // guard then holds the next telegraph, and the recovery the boss needs
        // before that is the source's 1.0 s shortened by the phase-2 multiplier
        // 0.8 → 16 ticks, so the guard (until local tick 40) is what releases
        // move B at tick 5040.
        var (bossPhaseService, bossPhaseQuest, _, _) = NewBossFixture(damageGateOn: true);
        bossPhaseQuest.Set("CHR_SELFCHECK_BOSS_PHASE", QuestStates.Active);
        var bossPhaseOwner = NewArenaOwner("CHR_SELFCHECK_BOSS_PHASE", 181);
        TickBoss(bossPhaseService, bossPhaseOwner, 5000, 5000);
        bossPhaseService.ApplyBossDamage("CHR_SELFCHECK_BOSS_PHASE", 490, 5000);
        var bossPhaseFrames = TickBoss(bossPhaseService, bossPhaseOwner, 5001, 5020);
        var bossHeldFrames = TickBoss(bossPhaseService, bossPhaseOwner, 5021, 5039);
        var bossReleasedFrames = TickBoss(bossPhaseService, bossPhaseOwner, 5040, 5045);
        var bossPhaseChanged = bossPhaseFrames
            .Where(r => r.Outcome == BossEncounterOutcomeCodes.PhaseChanged)
            .ToArray();
        Check(
            "alpha.boss_phase_two_guard_and_recovery",
            bossPhaseChanged.Length == 1 &&
            bossPhaseChanged[0].Detail == "Two" &&
            bossPhaseChanged[0].Phase == 2 &&
            bossPhaseChanged[0].BossHp == 710 &&
            bossHeldFrames.All(r => r.Outcome != BossEncounterOutcomeCodes.Telegraph) &&
            bossReleasedFrames.Count(r => r.Outcome == BossEncounterOutcomeCodes.Telegraph) == 1 &&
            bossReleasedFrames.Single(r => r.Outcome == BossEncounterOutcomeCodes.Telegraph).Detail == "B",
            $"{string.Join(",", bossPhaseFrames.Select(r => r.Outcome + ":" + (r.Detail ?? "-")))} " +
            $"held={string.Join(",", bossHeldFrames.Select(r => r.Outcome))} " +
            $"released={string.Join(",", bossReleasedFrames.Select(r => r.Outcome))}");

        // One transition per frame: 350 HP is already past the 30% line, yet a
        // phase-1 fight only steps to 2 at the first frame and reaches 3 at the
        // next one.
        var (bossStepService, bossStepQuest, _, _) = NewBossFixture(damageGateOn: true);
        bossStepQuest.Set("CHR_SELFCHECK_BOSS_STEP", QuestStates.Active);
        var bossStepOwner = NewArenaOwner("CHR_SELFCHECK_BOSS_STEP", 181);
        TickBoss(bossStepService, bossStepOwner, 5000, 5000);
        bossStepService.ApplyBossDamage("CHR_SELFCHECK_BOSS_STEP", 850, 5000);
        var bossStepFrames = TickBoss(bossStepService, bossStepOwner, 5001, 5070);
        var bossStepPhases = bossStepFrames
            .Where(r => r.Outcome == BossEncounterOutcomeCodes.PhaseChanged)
            .Select(r => r.Detail)
            .ToArray();
        Check(
            "alpha.boss_one_phase_transition_per_frame",
            bossStepPhases.SequenceEqual(new[] { "Two", "Three" }) &&
            bossStepFrames.First(r => r.Outcome == BossEncounterOutcomeCodes.PhaseChanged)
                .Detail == "Two",
            string.Join(",", bossStepPhases));

        // A killing hit ends the fight inside its own tick: DEFEATED once, the
        // boss despawned, and no further frames for that owner.
        var bossDefeat = bossPhaseService.ApplyBossDamage(
            "CHR_SELFCHECK_BOSS_PHASE", 710, 5046);
        var bossDefeatTick = TickBoss(bossPhaseService, bossPhaseOwner, 5047, 5060);
        var bossDefeatState = bossPhaseService.TryGetState(
            "CHR_SELFCHECK_BOSS_PHASE", out var bossDefeatSnapshot);
        Check(
            "alpha.boss_defeat_reports_once_and_stops",
            bossDefeat.Count == 1 &&
            bossDefeat[0].Outcome == BossEncounterOutcomeCodes.Defeated &&
            bossDefeatTick.Count == 0 &&
            bossDefeatState &&
            bossDefeatSnapshot.Status == "DEFEATED" &&
            bossDefeatSnapshot.BossHp == 0,
            $"{string.Join(",", bossDefeat.Select(r => r.Outcome))} " +
            $"{bossDefeatSnapshot.Status}");

        // NPC_CLASS_TRIAL only appears after the boss is down AND the fragment
        // is claimed; it closes again the moment the instance ends (turn-in),
        // which the same tick that drops ACTIVE reports as ENDED.
        var bossTrialNoFragment = bossPhaseService.IsTrialNpcVisible("CHR_SELFCHECK_BOSS_PHASE");
        bossPhaseQuest.Set("CHR_SELFCHECK_BOSS_PHASE", QuestStates.Active, fragment: 1);
        var bossTrialVisible = bossPhaseService.IsTrialNpcVisible("CHR_SELFCHECK_BOSS_PHASE");
        bossPhaseQuest.Set("CHR_SELFCHECK_BOSS_PHASE", QuestStates.Completed, fragment: 1);
        var bossEnded = TickBoss(bossPhaseService, bossPhaseOwner, 5061, 5061);
        var bossTrialAfterTurnIn = bossPhaseService.IsTrialNpcVisible("CHR_SELFCHECK_BOSS_PHASE");
        Check(
            "alpha.boss_trial_npc_visibility_window",
            !bossTrialNoFragment &&
            bossTrialVisible &&
            !bossTrialAfterTurnIn &&
            bossEnded.Count == 1 &&
            bossEnded[0].Outcome == BossEncounterOutcomeCodes.Ended,
            $"noFragment={bossTrialNoFragment} visible={bossTrialVisible} " +
            $"afterTurnIn={bossTrialAfterTurnIn} ended={bossEnded.FirstOrDefault()?.Outcome}");

        // The quest leaving ACTIVE while the fight is still open ends the
        // instance and the boss goes back under despawn hold.
        var (bossEndService, bossEndQuest, bossEndQuestBoss, _) = NewBossFixture(damageGateOn: true);
        bossEndQuest.Set("CHR_SELFCHECK_BOSS_END", QuestStates.Active);
        var bossEndOwner = NewArenaOwner("CHR_SELFCHECK_BOSS_END", 181);
        TickBoss(bossEndService, bossEndOwner, 5000, 5000);
        bossEndQuest.Set("CHR_SELFCHECK_BOSS_END", QuestStates.ReadyToTurnIn);
        var bossEndFrames = TickBoss(bossEndService, bossEndOwner, 5001, 5001);
        Check(
            "alpha.boss_ends_when_quest_leaves_active",
            bossEndFrames.Count == 1 &&
            bossEndFrames[0].Outcome == BossEncounterOutcomeCodes.Ended &&
            bossEndFrames[0].Detail == QuestStates.ReadyToTurnIn &&
            !bossEndService.TryGetState("CHR_SELFCHECK_BOSS_END", out _) &&
            bossEndQuestBoss.State == WorldEntityStates.Alive,
            $"{bossEndFrames.FirstOrDefault()?.Outcome} " +
            $"boss={bossEndQuestBoss.State}");

        // Wipe: ten seconds (200 ticks) without a live target inside the ring
        // refills the boss, returns it to phase 1 and costs no loot; the owner
        // coming back is a fresh attempt on a NEW life, never a replay.
        var (bossWipeService, bossWipeQuest, bossWipeQuestBoss, _) =
            NewBossFixture(damageGateOn: true);
        bossWipeQuest.Set("CHR_SELFCHECK_BOSS_WIPE", QuestStates.Active);
        var bossWipeOwner = NewArenaOwner("CHR_SELFCHECK_BOSS_WIPE", 181);
        TickBoss(bossWipeService, bossWipeOwner, 5000, 5000);
        bossWipeOwner.X = 240;
        var bossWipeEarly = TickBoss(bossWipeService, bossWipeOwner, 5001, 5200);
        var bossWipeAt = TickBoss(bossWipeService, bossWipeOwner, 5201, 5201);
        bossWipeOwner.X = 181;
        var bossRedo = TickBoss(bossWipeService, bossWipeOwner, 5202, 5202);
        var bossWipeState = bossWipeService.TryGetState("CHR_SELFCHECK_BOSS_WIPE", out var bossWipe);
        Check(
            "alpha.boss_wipe_resets_and_restarts_on_a_new_life",
            bossWipeEarly.All(r => r.Outcome != BossEncounterOutcomeCodes.Wiped) &&
            bossWipeAt.Count == 1 &&
            bossWipeAt[0].Outcome == BossEncounterOutcomeCodes.Wiped &&
            bossWipeAt[0].Detail == "life=2" &&
            bossWipeAt[0].BossHp == 1200 &&
            bossRedo.Count == 2 &&
            bossRedo[0].Outcome == BossEncounterOutcomeCodes.Registered &&
            bossRedo[0].Detail == "life=2" &&
            bossWipeQuestBoss.State == WorldEntityStates.Alive &&
            bossWipeQuestBoss.LifeId == 1 &&
            bossWipeState &&
            bossWipe.BossLifeId == 2 &&
            bossWipe.Phase == 1,
            $"{bossWipeAt.FirstOrDefault()?.Outcome}:{bossWipeAt.FirstOrDefault()?.Detail} " +
            $"redo={string.Join(",", bossRedo.Select(r => r.Outcome))}");

        // Outside the ring nothing opens at all: no instance, no state, no
        // telegraph, and the world-event boss is left alone.
        var (bossIdleService, _, bossIdleEvent, _) = NewBossFixture(damageGateOn: true);
        var bossIdleOwner = NewArenaOwner("CHR_SELFCHECK_BOSS_IDLE", 195);
        var bossIdle = TickBoss(bossIdleService, bossIdleOwner, 5000, 5020);
        Check(
            "alpha.boss_never_opens_outside_the_arena",
            bossIdle.Count == 0 &&
            !bossIdleService.TryGetState("CHR_SELFCHECK_BOSS_IDLE", out _) &&
            bossIdleEvent.State == WorldEntityStates.Alive,
            $"outcomes={bossIdle.Count} event={bossIdleEvent.State}");

        // questRules.P00-05.phaseNpcOverride: the same actor moves to (182,4)
        // for as long as the instance is held, and only for its owner.
        var bossPhaseNpc = bossService.TryGetPhaseNpcPosition(
            "CHR_SELFCHECK_BOSS_MAIN", out double bossNpcX, out double bossNpcY);
        var bossNpcOther = bossService.TryGetPhaseNpcPosition("CHR_NOBODY", out _, out _);
        Check(
            "alpha.boss_phase_npc_override_is_owner_specific",
            bossPhaseNpc &&
            bossNpcX == 182 &&
            bossNpcY == 4 &&
            !bossNpcOther,
            $"npc=({bossNpcX},{bossNpcY}) other={bossNpcOther}");

        // The tick engine resolves player casts only against `MOB` entities, so
        // the quest boss is only strikable through the alpha bridge once an owner
        // has registered an encounter. This proves all three: with no instance the
        // boss is not a target; after registration the same cast lands and drains
        // the encounter's HP; and the killing cast emits DEATH and credits the
        // P00-05 BOSS objective with the death-event key (no new event types).
        var bossIntStub = new BossEncounterQuestStub();
        bossIntStub.Set("CHR_SELFCHECK_BOSS_INT", QuestStates.Active);
        var bossIntBoss = BossWorldEntity(
            "ENT_SELFCHECK_BOSS_INT", alphaDesign.QuestRules.P00_05_BossRecordId);
        var bossIntRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [bossIntBoss]), bossClock);
        var bossIntEncounter = new AlphaBossEncounterService(
            alphaDesign,
            bossIntStub,
            bossIntRegistry,
            enabledCombat,
            new GuardDefenseService(
                new GuardWindowStore(),
                enabledCombat,
                new CombatEventStore(new CombatEventStreamOptions())),
            new PlayerLifeLedger());
        var bossIntEngine = new CombatTickEngine(
            bossIntRegistry,
            enabledCombat,
            combatSkills,
            new CombatEventStore(new CombatEventStreamOptions { CapacityPerSession = 512, MaxPageSize = 512 }),
            new MobCombatStateStore(),
            bossIntStub,
            new FixedCombatRolls(hit: true, crit: false),
            new GuardWindowStore(),
            tickGeometry,
            NewDashes(tickGeometry),
            new ServerClock(),
            bosses: bossIntEncounter);
        var bossIntOwner = NewPlayer("CHR_SELFCHECK_BOSS_INT", hp: 500);
        bossIntOwner.X = 181;
        bossIntOwner.Y = 0;

        // Cast before the encounter is registered: the boss is a `BOSS`, so the
        // mob path ignores it and the bridge reports no live target. Count only
        // events that struck the boss (the cast still emits its own END).
        var bossPreStrikes = 0;
        bossIntEngine.Schedule(
            bossIntOwner, "SES_BOSS_INT", "0000000000000000000000000000a000",
            CombatV2Actions.BasicAttack, null, -1, 0, 10000);
        for (var t = 10000L; t <= 10005; t++)
        {
            bossPreStrikes += bossIntEngine.Tick(t).Count(evt =>
                string.Equals(evt.TargetId, bossIntBoss.EntityId, StringComparison.Ordinal));
        }

        bossIntEncounter.Tick([bossIntOwner], 10010);
        var bossCastImpacts = 0;
        var bossDeathEvents = 0;
        var bossRounds = 0;
        var bossKilled = false;
        while (!bossKilled && bossRounds < 80)
        {
            var start = 11000 + bossRounds * 10;
            bossIntEngine.Schedule(
                bossIntOwner, "SES_BOSS_INT", $"{bossRounds:x32}",
                CombatV2Actions.BasicAttack, null, -1, 0, start);
            for (var t = start; t <= start + 5; t++)
            {
                foreach (var evt in bossIntEngine.Tick(t))
                {
                    if (!string.Equals(evt.TargetId, bossIntBoss.EntityId, StringComparison.Ordinal))
                    {
                        continue;
                    }

                    if (string.Equals(evt.Type, CombatEventTypesV2.Impact, StringComparison.Ordinal))
                    {
                        bossCastImpacts++;
                    }
                    else if (string.Equals(evt.Type, CombatEventTypesV2.Death, StringComparison.Ordinal))
                    {
                        bossDeathEvents++;
                        bossKilled = true;
                    }
                }
            }

            bossRounds++;
        }

        var bossIntState = bossIntEncounter.TryGetState("CHR_SELFCHECK_BOSS_INT", out var bossIntSnapshot);
        Check(
            "alpha.boss_cast_kill_credits_objective_through_bridge",
            bossPreStrikes == 0 &&
            bossIntState &&
            bossIntSnapshot.Status == "DEFEATED" &&
            bossIntSnapshot.BossHp == 0 &&
            bossCastImpacts == 67 &&
            bossDeathEvents == 1 &&
            bossIntBoss.State == WorldEntityStates.Alive &&
            bossIntStub.VerifiedEvents.Any(e =>
                e.EventType == QuestProgressEventTypes.Kill &&
                e.RecordId == alphaDesign.QuestRules.P00_05_BossRecordId),
            $"pre={bossPreStrikes} impacts={bossCastImpacts} deaths={bossDeathEvents} " +
            $"hp={bossIntSnapshot.BossHp} state={bossIntSnapshot.Status}");

        // Two owners fighting the same record template on one shared anchor must
        // never share mutable state: A's damage, defeat and wipe leave B's HP, life,
        // revision, status and snapshot identity exactly as they were.
        var (bossIsoService, bossIsoQuest, _, _) = NewBossFixture(damageGateOn: true);
        bossIsoQuest.Set("CHR_SELFCHECK_BOSS_ISO_A", QuestStates.Active);
        bossIsoQuest.Set("CHR_SELFCHECK_BOSS_ISO_B", QuestStates.Active);
        var bossIsoA = NewArenaOwner("CHR_SELFCHECK_BOSS_ISO_A", 181);
        var bossIsoB = NewArenaOwner("CHR_SELFCHECK_BOSS_ISO_B", 184);
        bossIsoService.Tick([bossIsoA, bossIsoB], 5000);
        var bossIsoBBefore = bossIsoService.TryGetSnapshot(
            "CHR_SELFCHECK_BOSS_ISO_B", 5000, out var bossIsoBPinned);
        bossIsoService.ApplyBossDamage("CHR_SELFCHECK_BOSS_ISO_A", 1190, 5001);
        bossIsoService.ApplyBossDamage("CHR_SELFCHECK_BOSS_ISO_A", 10, 5002);
        bossIsoA.X = 300;
        // Both owners stay in the roster (dropping one would legitimately end its
        // instance), so only A's own state may move.
        for (var t = 5003; t <= 5210; t++)
        {
            bossIsoService.Tick([bossIsoA, bossIsoB], t);
        }
        var bossIsoAa = bossIsoService.TryGetSnapshot(
            "CHR_SELFCHECK_BOSS_ISO_A", 5210, out var bossIsoASnap);
        var bossIsoBb = bossIsoService.TryGetSnapshot(
            "CHR_SELFCHECK_BOSS_ISO_B", 5211, out var bossIsoBSnap);
        // Strict round-trip under the P1 JSON options: the wire DTO must serialize
        // and deserialize with no unmapped member, so a client binding the shipped
        // contract sees exactly these fields.
        var bossIsoWire = JsonSerializer.Serialize(bossIsoBSnap, P1Json.Options);
        var bossIsoRoundTrip =
            JsonSerializer.Deserialize<EncounterSnapshotV1>(bossIsoWire, P1Json.Options);
        Check(
            "alpha.boss_two_owner_attempts_are_isolated",
            bossIsoBBefore &&
            bossIsoAa &&
            bossIsoBb &&
            bossIsoASnap.Status == "DEFEATED" &&
            bossIsoASnap.BossHp == 0 &&
            bossIsoASnap.BossLifeId == 1 &&
            bossIsoBSnap.Status == "OPEN" &&
            bossIsoBSnap.BossHp == 1200 &&
            bossIsoBSnap.BossLifeId == 1 &&
            // B's own fight keeps advancing on its own tick budget, so only the
            // fields A could have leaked into must be pinned.
            bossIsoBSnap.BossRevision >= bossIsoBPinned.BossRevision &&
            bossIsoBSnap.Phase == bossIsoBPinned.Phase &&
            bossIsoBSnap.EncounterId == bossIsoBPinned.EncounterId &&
            bossIsoASnap.EncounterId != bossIsoBSnap.EncounterId &&
            !bossIsoBSnap.RegisteredCharacterIds.Contains("CHR_SELFCHECK_BOSS_ISO_A") &&
            bossIsoRoundTrip is not null &&
            bossIsoRoundTrip.EncounterId == bossIsoBSnap.EncounterId &&
            bossIsoRoundTrip.BossHp == bossIsoBSnap.BossHp &&
            bossIsoRoundTrip.Arena.CenterXWu == bossIsoBSnap.Arena.CenterXWu &&
            bossIsoRoundTrip.SafePads.Count == bossIsoBSnap.SafePads.Count &&
            bossIsoRoundTrip.MoveCooldownRemainingTicks.C ==
                bossIsoBSnap.MoveCooldownRemainingTicks.C,
            $"a={bossIsoASnap.Status}/{bossIsoASnap.BossHp} " +
            $"b={bossIsoBSnap.Status}/{bossIsoBSnap.BossHp}/{bossIsoBSnap.BossRevision}");

        // The approved read model: stable opaque id, one registered character, a
        // locked cone facing that is normalized, deadlines that agree with the tick
        // they were read on, per-move cooldowns, pads that only apply in phase 3,
        // the same-actor phase NPC and a revision that moves only with real state.
        var (bossSnapService, bossSnapQuest, _, _) = NewBossFixture(damageGateOn: true);
        bossSnapQuest.Set("CHR_SELFCHECK_BOSS_SNAP", QuestStates.Active);
        var bossSnapOwner = NewArenaOwner("CHR_SELFCHECK_BOSS_SNAP", 181);
        TickBoss(bossSnapService, bossSnapOwner, 5000, 5000);
        var bossSnapOnce = bossSnapService.TryGetSnapshot(
            "CHR_SELFCHECK_BOSS_SNAP", 5005, out var bossSnapA);
        var bossSnapAgain = bossSnapService.TryGetSnapshot(
            "CHR_SELFCHECK_BOSS_SNAP", 5006, out var bossSnapB);
        var bossSnapFacingLength = Math.Sqrt(
            (bossSnapA.ActiveMove?.Shape.FacingX ?? 0) * (bossSnapA.ActiveMove?.Shape.FacingX ?? 0) +
            (bossSnapA.ActiveMove?.Shape.FacingY ?? 0) * (bossSnapA.ActiveMove?.Shape.FacingY ?? 0));
        // Move C opens first (priority), so the first frame is an annulus: it must
        // carry no cone fields at all. Drive to move A's telegraph to read the cone
        // facing the client needs, and check it is a normalized direction vector.
        TickBoss(bossSnapService, bossSnapOwner, 5001, 5087);
        var bossSnapConeOk = bossSnapService.TryGetSnapshot(
            "CHR_SELFCHECK_BOSS_SNAP", 5088, out var bossSnapCone);
        var bossConeFacing = bossSnapCone.ActiveMove?.Shape;
        var bossConeFacingLength = Math.Sqrt(
            (bossConeFacing?.FacingX ?? 0) * (bossConeFacing?.FacingX ?? 0) +
            (bossConeFacing?.FacingY ?? 0) * (bossConeFacing?.FacingY ?? 0));
        var bossSnapAfterKill = bossSnapService.ApplyBossDamage(
            "CHR_SELFCHECK_BOSS_SNAP", 1200, 5089).Count;
        var bossSnapDead = bossSnapService.TryGetSnapshot(
            "CHR_SELFCHECK_BOSS_SNAP", 5090, out var bossSnapDeadSnap);
        Check(
            "alpha.boss_snapshot_is_atomic_and_owner_scoped",
            bossSnapOnce && bossSnapAgain && bossSnapDead &&
            System.Text.RegularExpressions.Regex.IsMatch(
                bossSnapA.EncounterId, @"^ENC-[0-9A-F]{24}$") &&
            bossSnapA.EncounterId == bossSnapB.EncounterId &&
            bossSnapA.QuestId == "P00-05" &&
            bossSnapA.BossRecordId == "MAN-BM-SPAWN_BM_05_QUEST" &&
            // The fixture registers the quest-boss record under its own entity id;
            // the canonical ENT_MAN_BM_SPAWN_BM_05_QUEST pairing is pinned by the
            // shipped example and the contract validator.
            bossSnapA.BossEntityId == "ENT_SELFCHECK_BOSS_QUEST" &&
            bossSnapA.RegisteredCharacterIds.Count == 1 &&
            bossSnapA.RegisteredCharacterIds[0] == "CHR_SELFCHECK_BOSS_SNAP" &&
            bossSnapA.ActiveMove!.CastId == bossSnapB.ActiveMove!.CastId &&
            bossSnapA.ActiveMove.State == "TELEGRAPH" &&
            bossSnapA.ActiveMove.TicksRemaining ==
                bossSnapA.ActiveMove.StateEndsAtTick - bossSnapA.ServerTick &&
            bossSnapA.ActiveMove.StateEndsAtTick >= bossSnapA.ServerTick &&
            bossSnapA.ActiveMove.Shape.Kind == "ANNULUS" &&
            bossSnapA.ActiveMove.Shape.AngleDegrees is null &&
            bossSnapA.ActiveMove.Shape.RangeWu is null &&
            bossSnapA.ActiveMove.Shape.FacingX is null &&
            bossSnapA.ActiveMove.Shape.FacingY is null &&
            bossSnapA.ActiveMove.Shape.RadiusWu is null &&
            bossSnapFacingLength == 0 &&
            bossSnapA.ActiveMove.Shape.OuterRadiusWu == 7 &&
            bossSnapA.ActiveMove.Shape.InnerRadiusWu == 3 &&
            bossSnapA.MoveCooldownRemainingTicks.C == 235 &&
            bossSnapA.MoveCooldownRemainingTicks.A == 0 &&
            bossSnapConeOk &&
            bossConeFacing!.Kind == "CONE" &&
            bossConeFacing.AngleDegrees == 120 &&
            bossConeFacing.RangeWu == 8 &&
            bossConeFacing.InnerRadiusWu is null &&
            bossConeFacing.RadiusWu is null &&
            Math.Abs(bossConeFacingLength - 1.0) < 1e-9 &&
            bossSnapCone!.ActiveMove!.TargetLock == "TELEGRAPH_START_FACING" &&
            bossSnapA.Arena.Shape == "CIRCLE" &&
            bossSnapA.Arena.RadiusWu == 11 &&
            bossSnapA.SafePads.Count == 2 &&
            bossSnapA.SafePads.All(pad => !pad.Applies) &&
            bossSnapA.PhaseNpc.NpcId == "NPC_TA_VAN_KHANH" &&
            bossSnapA.PhaseNpc.XWu == 182 &&
            bossSnapA.PhaseNpc.YWu == 4 &&
            !bossSnapA.TrialNpcVisible &&
            bossSnapB.BossRevision == bossSnapA.BossRevision &&
            bossSnapAfterKill == 1 &&
            bossSnapDeadSnap.Status == "DEFEATED" &&
            bossSnapDeadSnap.BossRevision > bossSnapB.BossRevision &&
            bossSnapDeadSnap.ActiveMove is null &&
            bossSnapDeadSnap.TrialNpcVisible == false,
            $"id={bossSnapA.EncounterId} cast={bossSnapA.ActiveMove?.CastId} " +
            $"rev={bossSnapA.BossRevision}->{bossSnapDeadSnap.BossRevision} " +
            $"cone={bossConeFacing?.Kind}/flen={bossConeFacingLength} " +
            $"dead={bossSnapDeadSnap.Status}/{bossSnapDeadSnap.ActiveMove?.MoveId}");


        // The audience half of the same read model: the v2 world snapshot must show
        // the encounter boss as targetable, with the encounter's HP, to the owner
        // whose casts the engine will actually accept — and must keep the blocked
        // policy for every other viewer, because one owner's encounter is not
        // another player's fight. Same predicate on both sides, so a client can
        // never be handed a target the cast path would refuse.
        var audienceClock = new ServerClock();
        var audienceQuestBoss = BossWorldEntity(
            "ENT_SELFCHECK_AOI_BOSS_QUEST", alphaDesign.QuestRules.P00_05_BossRecordId);
        var audienceRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [audienceQuestBoss]), audienceClock);
        var audienceQuest = new BossEncounterQuestStub();
        audienceQuest.Set("CHR_SELFCHECK_AOI_BOSS_OWNER", QuestStates.Active);
        var audienceService = new AlphaBossEncounterService(
            alphaDesign,
            audienceQuest,
            audienceRegistry,
            enabledCombat,
            new GuardDefenseService(
                new GuardWindowStore(),
                enabledCombat,
                new CombatEventStore(new CombatEventStreamOptions())),
            new PlayerLifeLedger());
        var audienceProjection = new WorldAoiProjectionService(
            audienceRegistry,
            new MobLifecycleService(
                audienceRegistry,
                services.GetRequiredService<IWorldGeometryService>(),
                aoiMobOptions,
                audienceClock),
            enabledCombat,
            new GatherClaimStore(audienceClock),
            new MobCombatStateStore(),
            audienceService);
        var audienceOwner = NewArenaOwner("CHR_SELFCHECK_AOI_BOSS_OWNER", 181);
        var audienceStranger = NewArenaOwner("CHR_SELFCHECK_AOI_BOSS_STRANGER", 175);
        TickBoss(audienceService, audienceOwner, 6000, 6000);
        var audienceBossForOwner = audienceProjection
            .Project(audienceOwner)
            .Single(entity => entity.EntityId == "ENT_SELFCHECK_AOI_BOSS_QUEST");
        var audienceBossForStranger = audienceProjection
            .Project(audienceStranger)
            .Single(entity => entity.EntityId == "ENT_SELFCHECK_AOI_BOSS_QUEST");
        var audienceKillResolutions = audienceService.ApplyBossDamage(
            "CHR_SELFCHECK_AOI_BOSS_OWNER", 1200, 6001).Count;
        var audienceDeadBoss = audienceProjection
            .Project(audienceOwner)
            .Single(entity => entity.EntityId == "ENT_SELFCHECK_AOI_BOSS_QUEST");
        Check(
            "alpha.boss_audience_is_targetable_only_for_its_owner",
            audienceBossForOwner is
            {
                Kind: WorldEntityKinds.Boss,
                HealthState: WorldHealthStates.Alive,
                Targetable: true,
                Hp: 1200,
                MaxHp: 1200
            } &&
            audienceBossForStranger is
            {
                HealthState: WorldHealthStates.Blocked,
                Targetable: false,
                Hp: 0,
                MaxHp: 0
            } &&
            audienceKillResolutions == 1 &&
            audienceDeadBoss is
            {
                HealthState: WorldHealthStates.Dead,
                State: MobBehaviorStates.Dead,
                Targetable: false,
                Hp: 0,
                MaxHp: 1200
            },
            $"owner={audienceBossForOwner.HealthState}/{audienceBossForOwner.Targetable}" +
            $"/{audienceBossForOwner.Hp} stranger={audienceBossForStranger.HealthState} " +
            $"dead={audienceDeadBoss.HealthState}/{audienceDeadBoss.State}/" +
            $"{audienceDeadBoss.Targetable}");

        // ─── Mãng Cốt encounter state machine (Q-F part 1) ────

        var bossRules = new BossEncounterRules(PhaseGuardTicks: 3);
        BossEncounter NewBossEncounter(int cooldownTicks = 10) =>
            new(bossRules,
            [
                new BossMoveDefinition("A", cooldownTicks),
                new BossMoveDefinition("B", cooldownTicks),
                new BossMoveDefinition("C", cooldownTicks)
            ]);

        var badBoss = false;
        try
        {
            _ = new BossEncounter(
                bossRules, [new BossMoveDefinition("A", 1), new BossMoveDefinition("B", 1)]);
        }
        catch (ArgumentException)
        {
            badBoss = true;
        }

        Check(
            "boss.requires_three_named_moves",
            badBoss,
            "A/B/C definitions are required");

        var boss = NewBossEncounter();
        var bossIdleMove = boss.TryBeginMove(0);
        Check(
            "boss.not_engaged",
            bossIdleMove.BlockedReason == BossEncounterErrorCodes.NotEngaged,
            bossIdleMove.BlockedReason);

        var bossEngage = boss.Engage(lifeId: 1, tick: 0);
        Check(
            "boss.engage",
            bossEngage.Engaged &&
            boss.Phase == BossEncounterPhase.One &&
            boss.Status == BossEncounterStatus.Active,
            bossEngage.BlockedReason ?? $"phase={boss.Phase}");

        var bossFirst = boss.TryBeginMove(0);
        Check(
            "boss.priority_c",
            bossFirst.Token is { MoveId: "C" },
            bossFirst.BlockedReason ?? bossFirst.Token?.MoveId);

        var bossOverlap = boss.TryBeginMove(0);
        Check(
            "boss.no_overlap",
            bossOverlap.BlockedReason == BossEncounterErrorCodes.MoveInFlight,
            bossOverlap.BlockedReason);

        var bossFirstImpact = boss.ResolveImpact(bossFirst.Token!, 100, 100, 0);
        Check(
            "boss.impact_keeps_phase_one",
            bossFirstImpact.Accepted &&
            !bossFirstImpact.PhaseChanged &&
            boss.Phase == BossEncounterPhase.One,
            bossFirstImpact.BlockedReason ?? $"phase={boss.Phase}");

        var bossSecond = boss.TryBeginMove(1);
        Check(
            "boss.priority_b_after_c",
            bossSecond.Token is { MoveId: "B" },
            bossSecond.BlockedReason ?? bossSecond.Token?.MoveId);
        boss.ResolveImpact(bossSecond.Token!, 100, 100, 1);

        var bossThird = boss.TryBeginMove(2);
        Check(
            "boss.priority_a_after_b",
            bossThird.Token is { MoveId: "A" },
            bossThird.BlockedReason ?? bossThird.Token?.MoveId);
        boss.ResolveImpact(bossThird.Token!, 100, 100, 2);

        var bossCooldown = boss.TryBeginMove(3);
        Check(
            "boss.no_move_ready",
            bossCooldown.BlockedReason == BossEncounterErrorCodes.NoMoveReady,
            bossCooldown.BlockedReason);

        var bossReadyAgain = boss.TryBeginMove(10);
        Check(
            "boss.cooldown_expires",
            bossReadyAgain.Token is { MoveId: "C" },
            bossReadyAgain.BlockedReason ?? bossReadyAgain.Token?.MoveId);
        boss.Reset();

        var phaseBoss = NewBossEncounter(cooldownTicks: 0);
        phaseBoss.Engage(lifeId: 2, tick: 0);
        var phaseMove = phaseBoss.TryBeginMove(0);
        var toPhaseTwo = phaseBoss.ResolveImpact(phaseMove.Token!, 60, 100, 0);
        Check(
            "boss.phase_two_at_60",
            toPhaseTwo.Accepted &&
            toPhaseTwo.PhaseChanged &&
            phaseBoss.Phase == BossEncounterPhase.Two &&
            phaseBoss.Status == BossEncounterStatus.PhaseGuard &&
            toPhaseTwo.PhaseGuardUntilTick == 3,
            toPhaseTwo.BlockedReason ?? $"phase={phaseBoss.Phase}");

        var guardMove = phaseBoss.TryBeginMove(1);
        Check(
            "boss.phase_guard_blocks_move",
            guardMove.BlockedReason == BossEncounterErrorCodes.PhaseGuard,
            guardMove.BlockedReason);

        var guardEndMove = phaseBoss.TryBeginMove(3);
        Check(
            "boss.phase_guard_expires",
            guardEndMove.Started && phaseBoss.Status == BossEncounterStatus.Active,
            guardEndMove.BlockedReason ?? guardEndMove.Token?.MoveId);

        var toPhaseThree = phaseBoss.ResolveImpact(guardEndMove.Token!, 30, 100, 3);
        Check(
            "boss.phase_three_at_30",
            toPhaseThree.Accepted &&
            toPhaseThree.PhaseChanged &&
            phaseBoss.Phase == BossEncounterPhase.Three,
            toPhaseThree.BlockedReason ?? $"phase={phaseBoss.Phase}");

        var stepBoss = NewBossEncounter(cooldownTicks: 0);
        stepBoss.Engage(lifeId: 3, tick: 0);
        var stepMove = stepBoss.TryBeginMove(0);
        var stepImpact = stepBoss.ResolveImpact(stepMove.Token!, 10, 100, 0);
        Check(
            "boss.one_phase_per_impact",
            stepImpact.Accepted && stepBoss.Phase == BossEncounterPhase.Two,
            stepImpact.BlockedReason ?? $"phase={stepBoss.Phase}");

        var stepGuard = stepBoss.TryBeginMove(1);
        Check(
            "boss.one_step_guard",
            stepGuard.BlockedReason == BossEncounterErrorCodes.PhaseGuard,
            stepGuard.BlockedReason);

        var stepSecondMove = stepBoss.TryBeginMove(3);
        var stepSecondImpact = stepBoss.ResolveImpact(stepSecondMove.Token!, 10, 100, 3);
        Check(
            "boss.second_impact_reaches_phase_three",
            stepSecondImpact.PhaseChanged &&
            stepBoss.Phase == BossEncounterPhase.Three,
            stepSecondImpact.BlockedReason ?? $"phase={stepBoss.Phase}");

        var resetBoss = NewBossEncounter(cooldownTicks: 0);
        resetBoss.Engage(lifeId: 4, tick: 0);
        var resetToken = resetBoss.TryBeginMove(0).Token!;
        var episodeBeforeReset = resetBoss.Episode;
        resetBoss.Reset();
        var lateImpact = resetBoss.ResolveImpact(resetToken, 50, 100, 1);
        Check(
            "boss.reset_rejects_late_impact",
            !lateImpact.Accepted &&
            resetBoss.Phase == BossEncounterPhase.Idle &&
            resetBoss.Status == BossEncounterStatus.Idle &&
            resetBoss.DefeatedLifeId is null,
            lateImpact.BlockedReason);

        var reEngage = resetBoss.Engage(lifeId: 4, tick: 2);
        var replayedToken = resetBoss.ResolveImpact(resetToken, 50, 100, 2);
        Check(
            "boss.re_engage_rejects_old_token",
            reEngage.Engaged &&
            resetBoss.Episode == episodeBeforeReset + 2 &&
            replayedToken.BlockedReason == BossEncounterErrorCodes.StaleMove,
            replayedToken.BlockedReason);

        var deathBoss = NewBossEncounter(cooldownTicks: 0);
        deathBoss.Engage(lifeId: 5, tick: 0);
        var deathMove = deathBoss.TryBeginMove(0);
        var deathImpact = deathBoss.ResolveImpact(deathMove.Token!, 0, 100, 0);
        Check(
            "boss.defeat_marks_life",
            deathImpact.Defeated &&
            deathBoss.Status == BossEncounterStatus.Defeated &&
            deathBoss.DefeatedLifeId == 5,
            deathImpact.BlockedReason ?? $"status={deathBoss.Status}");

        var sameLife = deathBoss.Engage(lifeId: 5, tick: 1);
        Check(
            "boss.same_life_reengage_blocked",
            sameLife.BlockedReason == BossEncounterErrorCodes.LifeAlreadyDefeated,
            sameLife.BlockedReason);

        deathBoss.Reset();
        var sameLifeAfterReset = deathBoss.Engage(lifeId: 5, tick: 2);
        Check(
            "boss.reset_does_not_erase_defeat",
            sameLifeAfterReset.BlockedReason == BossEncounterErrorCodes.LifeAlreadyDefeated,
            sameLifeAfterReset.BlockedReason);

        var nextLife = deathBoss.Engage(lifeId: 6, tick: 3);
        Check(
            "boss.new_life_after_reset",
            nextLife.Engaged && deathBoss.Phase == BossEncounterPhase.One,
            nextLife.BlockedReason ?? $"phase={deathBoss.Phase}");

        // ─── equipment (Q-E) ──────────────────────────────────

        Check(
            "equipment.catalog_variant_merged",
            itemCatalog.Count > 556 &&
            itemCatalog.TryGet("EQ-MK-BOOTS-T1-R-COMMON", out var bootsEntry) &&
            bootsEntry is
            {
                SlotToken: EquipmentSlots.Boots,
                ClassId: PlayerClassId,
                RequiredLevel: 1
            },
            $"count={itemCatalog.Count}");

        Check(
            "equipment.slot_map",
            ItemCatalog.SlotTokenFor(ItemCatalog.ArmorCategory, "Nón") == EquipmentSlots.Hat &&
            ItemCatalog.SlotTokenFor(ItemCatalog.ArmorCategory, "Áo") == EquipmentSlots.Chest &&
            ItemCatalog.SlotTokenFor(ItemCatalog.ArmorCategory, "Giày") == EquipmentSlots.Boots &&
            ItemCatalog.SlotTokenFor(ItemCatalog.ArmorCategory, "Quần") is null &&
            ItemCatalog.SlotTokenFor(ItemCatalog.ArmorCategory, "Găng") is null &&
            ItemCatalog.SlotTokenFor(ItemCatalog.WeaponCategory, "Kiếm") == EquipmentSlots.Weapon &&
            ItemCatalog.SlotTokenFor(ItemCatalog.AccessoryCategory, "Dây chuyền") ==
                EquipmentSlots.Accessory &&
            ItemCatalog.SlotTokenFor(ItemCatalog.AccessoryCategory, "Nhẫn trái") ==
                EquipmentSlots.Accessory &&
            ItemCatalog.SlotTokenFor("Tiêu hao", "Potion HP") is null,
            "approved 5-token enum; Quần/Găng intentionally unmapped");

        var equipmentActor = NewPlayer("CHR_SELFCHECK_EQUIPMENT");
        var equipmentSeed = inventory.Apply(equipmentActor, new InventoryMutation
        {
            AddItems =
            [
                new ItemGrant
                {
                    TemplateId = "EQ-MK-BOOTS-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Bag,
                    Durability = 100
                },
                new ItemGrant
                {
                    TemplateId = "EQ-MK-BOOTS-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Bag,
                    Durability = 100
                },
                new ItemGrant
                {
                    TemplateId = "EQ-MK-WEAPON-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Bag,
                    Durability = 100
                },
                new ItemGrant
                {
                    TemplateId = "EQ-MK-HAT-T2-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Bag,
                    Durability = 100
                },
                new ItemGrant
                {
                    TemplateId = "EQ-AD-HAT-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Bag,
                    Durability = 100
                },
                new ItemGrant
                {
                    TemplateId = "EQ-MK-LEGS-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Bag,
                    Durability = 100
                },
                new ItemGrant
                {
                    TemplateId = "POT-HP-01",
                    Stack = 1,
                    Location = InventoryLocations.Bag
                }
            ]
        });
        Check(
            "equipment.seed",
            equipmentSeed.IsSuccess &&
            equipmentSeed.Snapshot!.InventoryRevision == 1 &&
            equipmentSeed.Snapshot.Items.Count == 7,
            equipmentSeed.ErrorCode ?? $"revision={equipmentSeed.Snapshot?.InventoryRevision}");

        var seedItems = equipmentSeed.Snapshot!.Items;
        var bootsInstances = seedItems
            .Where(item => item.TemplateId == "EQ-MK-BOOTS-T1-R-COMMON")
            .Select(item => item.InstanceId)
            .ToArray();
        var weaponInstance = seedItems
            .Single(item => item.TemplateId == "EQ-MK-WEAPON-T1-R-COMMON").InstanceId;
        var hatInstance = seedItems
            .Single(item => item.TemplateId == "EQ-MK-HAT-T2-R-COMMON").InstanceId;
        var adversaryHatInstance = seedItems
            .Single(item => item.TemplateId == "EQ-AD-HAT-T1-R-COMMON").InstanceId;
        var legsInstance = seedItems
            .Single(item => item.TemplateId == "EQ-MK-LEGS-T1-R-COMMON").InstanceId;
        var potionInstance = seedItems
            .Single(item => item.TemplateId == "POT-HP-01").InstanceId;

        string NewKey() => Guid.NewGuid().ToString("N");

        var equipKey = NewKey();
        var equipBoots = equipment.Equip(equipmentActor, bootsInstances[0], 1, equipKey);
        Check(
            "equipment.equip_moves_bag_to_slot",
            equipBoots.Accepted &&
            equipBoots.Snapshot!.InventoryRevision == 2 &&
            equipBoots.Snapshot.Items.Single(item => item.InstanceId == bootsInstances[0]) is
            {
                Location: InventoryLocations.Equipped,
                Slot: EquipmentSlots.Boots,
                Stack: 1
            },
            equipBoots.Failure?.Code ?? $"revision={equipBoots.Snapshot?.InventoryRevision}");

        var equipReplay = equipment.Equip(equipmentActor, bootsInstances[0], 1, equipKey);
        Check(
            "equipment.replay_returns_recorded_snapshot",
            equipReplay.Accepted &&
            equipReplay.Snapshot!.InventoryRevision == 2 &&
            inventory.GetSnapshot(equipmentActor.CharacterId).InventoryRevision == 2,
            equipReplay.Failure?.Code ?? $"revision={equipReplay.Snapshot?.InventoryRevision}");

        var equipKeyConflict = equipment.Equip(equipmentActor, bootsInstances[1], 1, equipKey);
        Check(
            "equipment.same_key_different_payload_conflicts",
            equipKeyConflict.Failure is
            {
                Code: EquipmentErrorCodes.IdempotencyConflict,
                Retryable: false
            },
            equipKeyConflict.Failure?.Code);

        var slotOccupied = equipment.Equip(equipmentActor, bootsInstances[1], 2, NewKey());
        Check(
            "equipment.slot_occupied",
            slotOccupied.Failure?.Code == EquipmentErrorCodes.SlotOccupied &&
            slotOccupied.Snapshot?.InventoryRevision == 2 &&
            inventory.GetSnapshot(equipmentActor.CharacterId).InventoryRevision == 2,
            slotOccupied.Failure?.Code);

        var equipWeapon = equipment.Equip(equipmentActor, weaponInstance, 2, NewKey());
        Check(
            "equipment.equip_weapon",
            equipWeapon.Accepted &&
            equipWeapon.Snapshot!.InventoryRevision == 3 &&
            equipWeapon.Snapshot.Items.Single(item => item.InstanceId == weaponInstance) is
            {
                Location: InventoryLocations.Equipped,
                Slot: EquipmentSlots.Weapon
            },
            equipWeapon.Failure?.Code ?? $"revision={equipWeapon.Snapshot?.InventoryRevision}");

        var reEquip = equipment.Equip(equipmentActor, weaponInstance, 3, NewKey());
        Check(
            "equipment.wrong_location",
            reEquip.Failure?.Code == EquipmentErrorCodes.WrongLocation,
            reEquip.Failure?.Code);

        var equipmentLevelGate = equipment.Equip(equipmentActor, hatInstance, 3, NewKey());
        Check(
            "equipment.level_required",
            equipmentLevelGate.Failure?.Code == EquipmentErrorCodes.LevelRequired,
            equipmentLevelGate.Failure?.Code);

        var classGate = equipment.Equip(equipmentActor, adversaryHatInstance, 3, NewKey());
        Check(
            "equipment.class_restricted",
            classGate.Failure?.Code == EquipmentErrorCodes.ClassRestricted,
            classGate.Failure?.Code);

        var legsGate = equipment.Equip(equipmentActor, legsInstance, 3, NewKey());
        var potionGate = equipment.Equip(equipmentActor, potionInstance, 3, NewKey());
        Check(
            "equipment.not_equippable",
            legsGate.Failure?.Code == EquipmentErrorCodes.NotEquippable &&
            potionGate.Failure?.Code == EquipmentErrorCodes.NotEquippable,
            $"{legsGate.Failure?.Code}/{potionGate.Failure?.Code}");

        var emptySlot = equipment.Unequip(
            equipmentActor, EquipmentSlots.Accessory, 3, NewKey());
        Check(
            "equipment.unequip_empty_slot",
            emptySlot.Failure?.Code == EquipmentErrorCodes.ItemNotFound,
            emptySlot.Failure?.Code);

        var unequipBoots = equipment.Unequip(
            equipmentActor, EquipmentSlots.Boots, 3, NewKey());
        Check(
            "equipment.unequip_moves_back_to_bag",
            unequipBoots.Accepted &&
            unequipBoots.Snapshot!.InventoryRevision == 4 &&
            unequipBoots.Snapshot.Items.Single(item => item.InstanceId == bootsInstances[0]) is
            {
                Location: InventoryLocations.Bag,
                Slot: null,
                Stack: 1
            },
            unequipBoots.Failure?.Code ?? $"revision={unequipBoots.Snapshot?.InventoryRevision}");

        var equipBootsAgain = equipment.Equip(
            equipmentActor, bootsInstances[0], 4, NewKey());
        Check(
            "equipment.re_equip_after_unequip",
            equipBootsAgain.Accepted &&
            equipBootsAgain.Snapshot!.InventoryRevision == 5,
            equipBootsAgain.Failure?.Code ??
            $"revision={equipBootsAgain.Snapshot?.InventoryRevision}");

        var staleEquip = equipment.Equip(equipmentActor, bootsInstances[1], 1, NewKey());
        Check(
            "equipment.revision_conflict",
            staleEquip.Failure is { Code: EquipmentErrorCodes.RevisionConflict, Retryable: true } &&
            staleEquip.Snapshot?.InventoryRevision == 5,
            staleEquip.Failure?.Code ?? $"revision={staleEquip.Snapshot?.InventoryRevision}");

        Check(
            "equipment.rejections_do_not_mutate",
            inventory.GetSnapshot(equipmentActor.CharacterId) is
            {
                InventoryRevision: 5,
                Items: { Count: 7 }
            },
            inventory.GetSnapshot(equipmentActor.CharacterId).InventoryRevision.ToString());

        var parallelKey = NewKey();
        var parallelBarrier = new Barrier(4);
        var equipmentParallelOutcomes = new EquipmentOutcome?[4];
        var parallelThreads = new Thread[4];
        for (var index = 0; index < parallelThreads.Length; index++)
        {
            var slot = index;
            parallelThreads[slot] = new Thread(() =>
            {
                parallelBarrier.SignalAndWait();
                equipmentParallelOutcomes[slot] = equipment.Unequip(
                    equipmentActor, EquipmentSlots.Weapon, 5, parallelKey);
            });
            parallelThreads[slot].Start();
        }

        foreach (var parallelThread in parallelThreads)
        {
            parallelThread.Join();
        }

        Check(
            "equipment.parallel_same_key_applies_once",
            equipmentParallelOutcomes.All(outcome =>
                outcome is { Accepted: true, Snapshot: { InventoryRevision: 6 } }) &&
            inventory.GetSnapshot(equipmentActor.CharacterId) is
            {
                InventoryRevision: 6,
                Items: { Count: 7 }
            } &&
            inventory.GetSnapshot(equipmentActor.CharacterId).Items.Count(item =>
                item.Location == InventoryLocations.Equipped) == 1,
            string.Join(
                "|",
                equipmentParallelOutcomes.Select(outcome =>
                    outcome?.Failure?.Code ??
                    $"{outcome?.Snapshot?.InventoryRevision}")));

        // ─── QOD-24 Q4: equipment metadata is never an effective stat ────

        // Work order 29 asks for this as a property of the product, so it is tested as
        // one. First the wire half: none of the labels the gear aggregator uses may
        // appear as a property on any contract type. Actor numbers that really are live
        // (Hp/MaxHp/Mp/MaxMp) are deliberately absent from the deny list - the claim is
        // that *catalogue metadata* has no wire home, not that stats are unspeakable. If
        // someone later surfaces "attack" or "armor" on a snapshot, this fails here
        // rather than in a client that assumed the number was resolved.
        var gearStatVocabulary = new HashSet<string>(StringComparer.Ordinal)
        {
            "WeaponPower", "WeaponAttack", "Armor", "PrimaryStat", "PrimaryValue",
            "SecondaryStat", "SecondaryValue", "Strength", "Vitality", "FlatMaxHp",
            "FlatMaxMp", "HpMax", "MpMax", "PhysicalAttack", "Attack", "Defense",
            "EffectiveStats"
        };
        var gearStatPropsOnWire = typeof(InventorySnapshot).Assembly
            .GetTypes()
            .Where(type => type.IsPublic &&
                           type.Namespace == "Server.Health.Contracts")
            .SelectMany(type => type.GetProperties(
                System.Reflection.BindingFlags.Public |
                System.Reflection.BindingFlags.Instance))
            .Where(property => gearStatVocabulary.Contains(property.Name))
            .Select(property => property.DeclaringType?.Name + "." + property.Name)
            .OrderBy(name => name, StringComparer.Ordinal)
            .ToArray();
        Check(
            "equipment.gear_stat_labels_have_no_wire_field",
            gearStatPropsOnWire.Length == 0,
            $"found={string.Join("|", gearStatPropsOnWire)}");

        // Then the runtime half, which is the stronger claim: wearing a hat the catalogue
        // prices at +14 max HP must not move the actor's own numbers by one point. The
        // aggregation is still asked for that item, so the check would go red the day
        // gear is applied *without* the matching decision, in either direction.
        itemCatalog.TryGet("EQ-MK-HAT-T1-R-COMMON", out var wornHatEntry);
        var hatWorth = PlayerStatAggregation.Derive(
            [PlayerStatAggregation.Resolve(wornHatEntry!)]);
        var statProbeSeed = inventory.Apply(equipmentActor, new InventoryMutation
        {
            AddItems =
            [
                new ItemGrant
                {
                    TemplateId = "EQ-MK-HAT-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Bag
                }
            ]
        });
        var statProbeHat = statProbeSeed.Snapshot!.Items
            .Single(item => item.TemplateId == "EQ-MK-HAT-T1-R-COMMON");
        var statsBeforeWearing = (
            equipmentActor.Hp, equipmentActor.MaxHp, equipmentActor.Mp, equipmentActor.MaxMp);
        var wearHat = equipment.Equip(
            equipmentActor, statProbeHat.InstanceId,
            statProbeSeed.Snapshot.InventoryRevision, NewKey());
        var statsAfterWearing = (
            equipmentActor.Hp, equipmentActor.MaxHp, equipmentActor.Mp, equipmentActor.MaxMp);
        Check(
            "equipment.wearing_the_hat_moves_no_actor_stat",
            wearHat.Accepted &&
            // The catalogue row for this hat states durability 100, and a grant that
            // names no durability takes the source - measured here because guessing it
            // is how a "7" got written into this check first.
            statProbeHat.Durability == 100 && wornHatEntry!.Durability == 100 &&
            hatWorth.HpMax == 212 &&
            statsAfterWearing == statsBeforeWearing &&
            inventory.GetSnapshot(equipmentActor.CharacterId)
                .Items.Single(item => item.InstanceId == statProbeHat.InstanceId)
                .Location == InventoryLocations.Equipped,
            $"equip={wearHat.Failure?.Code ?? "OK"} hat.hp={hatWorth.HpMax} " +
            $"hat.durability={statProbeHat.Durability} " +
            $"before={statsBeforeWearing} after={statsAfterWearing}");

        // ─── QOD-24 Q5: consumables, loaded from the source and applied only where the
        // source states a rule ────

        var consumables = ConsumableCatalog.Load(itemCatalog);
        var restoreRows = consumables.Where(entry =>
            entry.Kind == ConsumableEffectKind.RestorePercent).ToArray();
        var unsupportedRows = consumables.Where(entry =>
            entry.Kind == ConsumableEffectKind.Unsupported).ToArray();
        Check(
            "consumable.catalog_shape_is_fourteen_rows_seven_rules_and_seven_effects_this_server_cannot_perform",
            consumables.Count == 14 && restoreRows.Length == 7 &&
            unsupportedRows.Length == 7,
            $"rows={consumables.Count} restore={restoreRows.Length} " +
            $"unsupported={string.Join("|", unsupportedRows.Select(entry => entry.EffectStatLabel))}");

        var consumableByItem = consumables.ToDictionary(
            entry => entry.ItemId, StringComparer.Ordinal);
        Check(
            "consumable.catalog_percents_are_exactly_the_source_cells",
            consumableByItem["POT-HP-01"] is { Percent: 25, Restores: ConsumableCatalog.Hp, ReviveRequired: false } &&
            consumableByItem["POT-HP-02"].Percent == 35 &&
            consumableByItem["POT-HP-03"].Percent == 45 &&
            consumableByItem["POT-MP-01"] is { Percent: 20, Restores: ConsumableCatalog.Mp } &&
            consumableByItem["POT-MP-02"].Percent == 30 &&
            consumableByItem["POT-MP-03"].Percent == 40 &&
            consumableByItem["POT-REVIVE-01"] is { Percent: 15, ReviveRequired: true } &&
            consumableByItem["POT-HP-01"].StackLimit == 99 &&
            consumableByItem["POT-HP-02"].RequiredLevel == 16,
            $"hp={string.Join("|", consumables.Where(entry => entry.Restores == ConsumableCatalog.Hp).Select(entry => entry.Percent))}");

        string? ConsumableLoadFailure(string from, string to)
        {
            var root = Path.Combine(
                Path.GetTempPath(), "p1-consumable-" + Guid.NewGuid().ToString("N"));
            try
            {
                var directory = Path.Combine(root, "docs", "production");
                Directory.CreateDirectory(directory);
                var sourceDirectory =
                    ItemCatalogDiscovery.DiscoverDirectory(AppContext.BaseDirectory);
                foreach (var relative in new[]
                {
                    ItemCatalog.RelativePath, ItemCatalog.VariantRelativePath
                })
                {
                    var lines = File.ReadAllLines(Path.Combine(sourceDirectory, relative));
                    File.WriteAllLines(
                        Path.Combine(directory, Path.GetFileName(relative)),
                        lines.Select(line =>
                            line.Replace(from, to, StringComparison.Ordinal)).ToArray());
                }

                try
                {
                    ConsumableCatalog.Load(ItemCatalog.Load(root));
                    return "LOADED";
                }
                catch (InvalidOperationException exception)
                {
                    return exception.Message;
                }
            }
            finally
            {
                Directory.Delete(root, recursive: true);
            }
        }

        var unparsableRestoreCell = ConsumableLoadFailure("25% HP tối đa", "25 HP");
        var mismatchedRestoreStat = ConsumableLoadFailure(
            "\"25% HP tối đa\"", "\"30% MP tối đa\"");
        var unknownSlotLabel = ConsumableLoadFailure("Potion MP", "Nước uống");
        Check(
            "consumable.catalog_refuses_a_cell_it_cannot_parse_and_a_slot_label_it_does_not_know",
            unparsableRestoreCell.Contains("not '<percent>% HP|MP tối đa'", StringComparison.Ordinal) &&
            mismatchedRestoreStat.Contains("pairs stat label", StringComparison.Ordinal) &&
            unknownSlotLabel.Contains("unknown slot label", StringComparison.Ordinal),
            $"cell={Cut(unparsableRestoreCell)} stat={Cut(mismatchedRestoreStat)} slot={Cut(unknownSlotLabel)}");

        var consumableActor = NewPlayer("CHR_SELFCHECK_CONSUMABLE");
        var consumableSeed = inventory.Apply(consumableActor, new InventoryMutation
        {
            AddItems =
            [
                new ItemGrant { TemplateId = "POT-HP-01", Stack = 3, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "POT-MP-01", Stack = 1, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "POT-HP-02", Stack = 1, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "POT-REVIVE-01", Stack = 1, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "FOOD-ATK-01", Stack = 1, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "EQ-MK-CHEST-T1-R-COMMON", Stack = 1, Location = InventoryLocations.Bag }
            ]
        });
        var consumableItems = consumableSeed.Snapshot!.Items;
        string ConsumableInstance(string templateId) => consumableItems
            .Single(item => item.TemplateId == templateId).InstanceId;
        var hpPotion = ConsumableInstance("POT-HP-01");
        var mpPotion = ConsumableInstance("POT-MP-01");
        var gatedPotion = ConsumableInstance("POT-HP-02");
        var revivePotion = ConsumableInstance("POT-REVIVE-01");
        var foodPotion = ConsumableInstance("FOOD-ATK-01");
        var gearInstance = ConsumableInstance("EQ-MK-CHEST-T1-R-COMMON");
        string ConsumeKey(string prefix) => prefix + new string('0', 32 - prefix.Length);
        var consumableService = new ConsumableService(inventory, consumables);
        var consumableRevision = consumableSeed.Snapshot.InventoryRevision;
        consumableActor.Hp = 60;
        consumableActor.Mp = 10;

        var hpDrink = consumableService.Consume(
            consumableActor, hpPotion, consumableRevision, ConsumeKey("ca"));
        Check(
            "consumable.hp_drink_restores_a_quarter_of_max_and_spends_one_stack",
            hpDrink.Accepted && hpDrink.HpRestored == 25 && hpDrink.HpAfter == 85 &&
            hpDrink.MpRestored == 0 && hpDrink.Snapshot!.InventoryRevision == consumableRevision + 1 &&
            hpDrink.Snapshot.Items.Single(item => item.InstanceId == hpPotion).Stack == 2,
            $"restored={hpDrink.HpRestored} hp={hpDrink.HpAfter} fail={hpDrink.Failure?.Code}");

        var mpDrink = consumableService.Consume(
            consumableActor, mpPotion, consumableRevision + 1, ConsumeKey("cb"));
        Check(
            "consumable.mp_drink_moves_only_its_own_pool_and_empties_the_instance",
            mpDrink.Accepted && mpDrink.MpRestored == 10 && mpDrink.MpAfter == 20 &&
            mpDrink.HpRestored == 0 && mpDrink.HpAfter == 85 &&
            !mpDrink.Snapshot!.Items.Any(item => item.InstanceId == mpPotion),
            $"mp={mpDrink.MpRestored} hp={mpDrink.HpAfter} fail={mpDrink.Failure?.Code}");

        var replayDrink = consumableService.Consume(
            consumableActor, hpPotion, consumableRevision, ConsumeKey("ca"));
        Check(
            "consumable.replayed_key_returns_the_recorded_result_without_a_second_spend",
            replayDrink.Accepted && replayDrink.HpRestored == 25 &&
            inventory.GetSnapshot(consumableActor.CharacterId)
                .Items.Single(item => item.InstanceId == hpPotion).Stack == 2 &&
            consumableActor.Hp == 85,
            $"restored={replayDrink.HpRestored} hp={consumableActor.Hp}");

        var conflictDrink = consumableService.Consume(
            consumableActor, hpPotion, consumableRevision + 5, ConsumeKey("ca"));
        Check(
            "consumable.same_key_with_a_different_payload_is_a_conflict",
            conflictDrink.Failure?.Code == ConsumableErrorCodes.IdempotencyConflict,
            conflictDrink.Failure?.Code);

        consumableActor.Hp = 90;
        var clampDrink = consumableService.Consume(
            consumableActor, hpPotion, consumableRevision + 2, ConsumeKey("cc"));
        Check(
            "consumable.heal_clamps_at_max_hp_and_reports_only_the_points_gained",
            clampDrink.Accepted && clampDrink.HpRestored == 10 && clampDrink.HpAfter == 100 &&
            inventory.GetSnapshot(consumableActor.CharacterId).InventoryRevision ==
                consumableRevision + 3,
            $"restored={clampDrink.HpRestored} hp={clampDrink.HpAfter}");

        var fullDrink = consumableService.Consume(
            consumableActor, hpPotion, consumableRevision + 3, ConsumeKey("cd"));
        Check(
            "consumable.a_drink_with_nothing_to_restore_is_refused_and_the_stack_survives",
            fullDrink.Failure?.Code == ConsumableErrorCodes.NoEffect &&
            inventory.GetSnapshot(consumableActor.CharacterId)
                .Items.Single(item => item.InstanceId == hpPotion).Stack == 1 &&
            inventory.GetSnapshot(consumableActor.CharacterId).InventoryRevision ==
                consumableRevision + 3 &&
            consumableActor.Hp == 100,
            $"fail={fullDrink.Failure?.Code}");

        // The rounding the source never states, made visible instead of buried: floor of
        // 25% of a 3-point maximum is zero, and zero is not a reason to spend an item.
        consumableActor.MaxHp = 3;
        consumableActor.Hp = 0;
        var tinyDrink = consumableService.Consume(
            consumableActor, hpPotion, consumableRevision + 3, ConsumeKey("ce"));
        Check(
            "consumable.floor_rounding_at_a_three_point_maximum_spends_nothing",
            tinyDrink.Failure?.Code == ConsumableErrorCodes.NoEffect &&
            consumableActor.Hp == 0 &&
            inventory.GetSnapshot(consumableActor.CharacterId)
                .Items.Single(item => item.InstanceId == hpPotion).Stack == 1,
            $"fail={tinyDrink.Failure?.Code} hp={consumableActor.Hp}");
        consumableActor.MaxHp = 101;
        var floorDrink = consumableService.Consume(
            consumableActor, hpPotion, consumableRevision + 3, ConsumeKey("cf"));
        Check(
            "consumable.floor_is_the_ruleset_value_convention_not_round_half_up",
            floorDrink.Accepted && floorDrink.HpRestored == 25 && floorDrink.HpAfter == 25,
            $"restored={floorDrink.HpRestored} (101 * 25 / 100 = 25,25)");

        var consumableLevelGate = consumableService.Consume(
            consumableActor, gatedPotion, consumableRevision + 4, ConsumeKey("d0"));
        var consumableReviveGate = consumableService.Consume(
            consumableActor, revivePotion, consumableRevision + 4, ConsumeKey("d1"));
        var consumableEffectGate = consumableService.Consume(
            consumableActor, foodPotion, consumableRevision + 4, ConsumeKey("d2"));
        var consumableGearGate = consumableService.Consume(
            consumableActor, gearInstance, consumableRevision + 4, ConsumeKey("d3"));
        Check(
            "consumable.level_revive_effect_and_category_refusals_all_name_their_row",
            consumableLevelGate.Failure?.Code == ConsumableErrorCodes.LevelRequired &&
            consumableReviveGate.Failure?.Code == ConsumableErrorCodes.ReviveNotModelled &&
            consumableEffectGate.Failure?.Code == ConsumableErrorCodes.EffectUnsupported &&
            consumableByItem["FOOD-ATK-01"].EffectStatLabel == "Damage PvE" &&
            consumableByItem["FOOD-ATK-01"].EffectValueCell == "+2% / 20 phút" &&
            consumableGearGate.Failure?.Code == ConsumableErrorCodes.NotConsumable,
            $"level={consumableLevelGate.Failure?.Code} revive={consumableReviveGate.Failure?.Code} " +
            $"effect={consumableEffectGate.Failure?.Code} gear={consumableGearGate.Failure?.Code}");

        var consumableStaleRevision = consumableService.Consume(
            consumableActor, hpPotion, 1, ConsumeKey("d4"));
        var consumableUnknownInstance = consumableService.Consume(
            consumableActor, "ITM_NEVER_MINTED", consumableRevision + 4, ConsumeKey("d5"));
        Check(
            "consumable.stale_revision_and_unknown_instance_move_nothing",
            consumableStaleRevision.Failure is { Code: ConsumableErrorCodes.RevisionConflict, Retryable: true } &&
            consumableUnknownInstance.Failure?.Code == ConsumableErrorCodes.ItemNotFound &&
            inventory.GetSnapshot(consumableActor.CharacterId).InventoryRevision ==
                consumableRevision + 4,
            $"stale={consumableStaleRevision.Failure?.Code} unknown={consumableUnknownInstance.Failure?.Code}");

        var barrierActor = NewPlayer("CHR_SELFCHECK_CONSUMABLE_RACE");
        var barrierSeed = inventory.Apply(barrierActor, new InventoryMutation
        {
            AddItems = [new ItemGrant
            {
                TemplateId = "POT-HP-01", Stack = 5, Location = InventoryLocations.Bag
            }]
        });
        var barrierPotion = barrierSeed.Snapshot!.Items.Single().InstanceId;
        barrierActor.Hp = 0;
        var consumeRaceKey = ConsumeKey("d6");
        var consumeRaceBarrier = new Barrier(4);
        var consumeRaceOutcomes = new ConsumableOutcome?[4];
        var consumeRaceThreads = new Thread[4];
        for (var index = 0; index < consumeRaceThreads.Length; index++)
        {
            var outcomeSlot = index;
            consumeRaceThreads[outcomeSlot] = new Thread(() =>
            {
                consumeRaceBarrier.SignalAndWait();
                consumeRaceOutcomes[outcomeSlot] = consumableService.Consume(
                    barrierActor, barrierPotion, barrierSeed.Snapshot!.InventoryRevision, consumeRaceKey);
            });
        }

        foreach (var thread in consumeRaceThreads)
        {
            thread.Start();
        }

        foreach (var thread in consumeRaceThreads)
        {
            thread.Join();
        }

        Check(
            "consumable.four_threads_on_one_key_spend_exactly_one_stack",
            consumeRaceOutcomes.All(outcome => outcome is { Accepted: true, HpRestored: 25 }) &&
            inventory.GetSnapshot(barrierActor.CharacterId)
                .Items.Single(item => item.InstanceId == barrierPotion).Stack == 4 &&
            barrierActor.Hp == 25 &&
            consumableService.LedgerCount >= 1,
            $"stacks={inventory.GetSnapshot(barrierActor.CharacterId)
                .Items.Single(item => item.InstanceId == barrierPotion).Stack} hp={barrierActor.Hp}");

        // ─── QOD-24 Q4/Q6: two approved production tables the server had never read ────

        var elites = services.GetRequiredService<IReadOnlyList<MobEliteVariant>>();
        var eliteProfiles = elites.Select(elite => elite.VariantProfileId)
            .Distinct(StringComparer.Ordinal)
            .OrderBy(profile => profile, StringComparer.Ordinal)
            .ToArray();
        var multiplierSets = elites
            .Select(elite => (elite.HpMultiplier, elite.DamageMultiplier, elite.MoveSpeedMultiplier))
            .Distinct()
            .ToArray();
        Check(
            "elite.table_is_nine_rows_three_profiles_and_three_multiplier_sets",
            elites.Count == 9 && eliteProfiles.Length == 3 && multiplierSets.Length == 3 &&
            elites.All(elite => elite.LevelDelta == 2) &&
            elites.All(elite => elite.RespawnDeltaSeconds == 0) &&
            elites.All(elite => elite.BehaviorOverride.Length > 0) &&
            elites.All(elite => elite.LootDelta.Contains("%", StringComparison.Ordinal)) &&
            // Two of the three profiles name a telegraph duration in prose (1.5s and
            // 2.0s); elite_v3 names an area hazard with a safe lane and no telegraph
            // at all, so "elite telegraph timing" is not one sourced number.
            elites.Count(elite => elite.BehaviorOverride.Contains(
                "telegraph", StringComparison.Ordinal)) == 6 &&
            elites.Count(elite => elite.BehaviorOverride.Contains(
                "1.5s", StringComparison.Ordinal)) == 3 &&
            elites.Count(elite => elite.BehaviorOverride.Contains(
                "2.0s", StringComparison.Ordinal)) == 3 &&
            elites.Count(elite => elite.BehaviorOverride.Contains(
                "safe lane", StringComparison.Ordinal)) == 3,
            $"rows={elites.Count} profiles={string.Join("|", eliteProfiles)} " +
            $"sets={multiplierSets.Length} lvl2={elites.All(e => e.LevelDelta == 2)} " +
            $"respawn0={elites.All(e => e.RespawnDeltaSeconds == 0)} " +
            $"telegraphRows={elites.Count(e => e.BehaviorOverride.Contains("telegraph", StringComparison.Ordinal))} " +
            $"lootPct={elites.All(e => e.LootDelta.Contains("%", StringComparison.Ordinal))}");

        Check(
            "elite.no_variant_in_the_source_is_pvp_eligible",
            elites.All(elite => !elite.PvpAllowed) &&
            elites.All(elite => elite.LootTableId.StartsWith("LT_", StringComparison.Ordinal)) &&
            elites.Select(elite => elite.BaseEntityId).Distinct().Count() == 9,
            $"pvp_allowed_anywhere={elites.Any(elite => elite.PvpAllowed)}");

        // The conflict work order 29 asks me to name rather than resolve. The damage path
        // scales elites from the runtime bundle (hp 6.0x, attack 1.6x, defense 1.8x), while
        // the approved elite table states 1.65x / 1.8x / 2.0x hp per profile and a +2 level
        // delta instead. Both numbers are printed so a fix is a decision, not a silent
        // edit of whichever constant was nearer to hand: at the reference level the bundle
        // ships 1152 hp on a base of 1152 / 6.0 = 192, and that same base at the table's
        // largest hp multiplier is 192 * 2.0 = 384. This is the bundle's reference row,
        // not the spawn the report in QOD-24_skill_catalog_coverage names: the shore
        // stalker there carries base 216, so 216 gives 1296 against 388.8. Same conflict,
        // different row - which is why the numbers are printed instead of averaged.
        var tableMaxHpMultiplier = elites.Max(elite => elite.HpMultiplier);
        var bundleReferenceEliteHp = 1152.0;
        var tableDerivedEliteHp = bundleReferenceEliteHp / mobStats.Elite.Hp * tableMaxHpMultiplier;
        Check(
            "elite_the_runtime_bundle_and_the_approved_table_disagree_named",
            mobStats.Elite.Hp == 6.0 && tableMaxHpMultiplier == 2.0 &&
            !elites.Any(elite => Math.Abs(elite.HpMultiplier - mobStats.Elite.Hp) < 0.0001) &&
            Math.Abs(tableDerivedEliteHp - 384.0) < 0.0001,
            $"bundle={mobStats.Elite.Hp}x -> {bundleReferenceEliteHp} hp; " +
            $"table max={tableMaxHpMultiplier}x -> {tableDerivedEliteHp} hp");

        var npcDefinitions = services.GetRequiredService<IReadOnlyList<NpcActorDefinition>>();
        var registryIds = npcDefinitions.Select(npc => npc.NpcId).ToHashSet(StringComparer.Ordinal);
        var anchoredIds = npcAnchors.All.Select(anchor => anchor.NpcId)
            .ToHashSet(StringComparer.Ordinal);
        Check(
            "npc.registry_and_the_anchor_catalog_are_the_same_83_ids_both_ways",
            npcDefinitions.Count == 83 && registryIds.Count == 83 &&
            anchoredIds.Count == 83 && registryIds.SetEquals(anchoredIds) &&
            npcDefinitions.All(npc => !npc.CombatTargetable) &&
            npcDefinitions.All(npc => npc.SourceMapId.StartsWith("MAP_", StringComparison.Ordinal)),
            $"registry={registryIds.Count} anchors={anchoredIds.Count} " +
            $"onlyInRegistry={registryIds.Except(anchoredIds).Count()} " +
            $"onlyInAnchors={anchoredIds.Except(registryIds).Count()}");

        // Service availability (Q6) has a source, and it is not a quest or a flag: it is a
        // named service on the NPC. Loading it means the shop/forge/guild/arena packets can
        // cite the token that exists instead of inventing an endpoint nobody approved.
        var serviceTokens = npcDefinitions
            .Where(npc => npc.InteractionServiceId != "NONE")
            .GroupBy(npc => npc.InteractionServiceId, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.Count(), StringComparer.Ordinal);
        Check(
            "npc.service_tokens_are_the_source_vocabulary_and_none_of_them_has_a_route",
            serviceTokens.Count == 14 &&
            serviceTokens["SERVICE_FORGE"] == 2 && serviceTokens["SERVICE_SHOP"] == 2 &&
            serviceTokens["SERVICE_SHOP_POTION"] == 1 && serviceTokens["SERVICE_TRAVEL"] == 4 &&
            serviceTokens["SERVICE_PVP_QUEUE"] == 1 && serviceTokens["SERVICE_GUILD"] == 1 &&
            serviceTokens["SERVICE_CLASS_SELECTION"] == 1 &&
            npcDefinitions.Count(npc => npc.RoleProfile == "QUEST_GIVER") == 15,
            $"services={string.Join("|", serviceTokens.OrderBy(pair => pair.Key).Select(pair => $"{pair.Key}={pair.Value}"))}");

        string? NpcRegistryTargetableFailure()
        {
            var root = Path.Combine(
                Path.GetTempPath(), "p1-npc-target-" + Guid.NewGuid().ToString("N"));
            try
            {
                var production = Path.Combine(root, "docs", "production");
                Directory.CreateDirectory(production);
                var sourceRoot = ProductionTableDiscovery.DiscoverDirectory(
                    AppContext.BaseDirectory, NpcActorRegistry.RelativePath);
                foreach (var relative in new[]
                {
                    NpcActorRegistry.RelativePath, MobEliteVariantCatalog.RelativePath
                })
                {
                    var lines = File.ReadAllLines(Path.Combine(sourceRoot, relative));
                    File.WriteAllLines(
                        Path.Combine(root, relative),
                        lines.Select(line => line.Replace(
                            ",false,1.0,", ",true,1.0,", StringComparison.Ordinal)).ToArray());
                }

                try
                {
                    NpcActorRegistry.Load(root);
                    return "LOADED";
                }
                catch (InvalidOperationException exception)
                {
                    return exception.Message;
                }
            }
            finally
            {
                Directory.Delete(root, recursive: true);
            }
        }

        var targetableNpcRefused = NpcRegistryTargetableFailure();
        Check(
            "npc_the_loader_refuses_a_registry_row_the_audience_policy_cannot_express",
            targetableNpcRefused.Contains("combat_targetable=true", StringComparison.Ordinal),
            $"refused={Cut(targetableNpcRefused)}");

        // ─── QOD-24: the pet/mount table, read for the first time, against the catalogue ───

        var petRows = services.GetRequiredService<IReadOnlyList<CompanionEntry>>();
        var companionRows = petRows.Where(row => row.IsCompanion).ToArray();
        var mountRows = petRows.Where(row => !row.IsCompanion).ToArray();
        var productionDirectory = ProductionTableDiscovery.DiscoverDirectory(
            AppContext.BaseDirectory, CompanionCatalog.RelativePath);
        Check(
            "companion.table_is_five_companions_and_five_cosmetic_mounts",
            petRows.Count == 10 && companionRows.Length == 5 && mountRows.Length == 5 &&
            companionRows.All(row => row.LevelCap == 30 && row.OwnerRangeWu == 8 &&
                row.Element != "COSMETIC" && row.FeedItemId == "PET-FEED-01" &&
                row.FeedCooldownHours == 12) &&
            mountRows.All(row => row.LevelCap == 1 && row.OwnerRangeWu == 0 &&
                row.Element == "COSMETIC" && row.FeedItemId.Length == 0 &&
                row.FeedCooldownHours == 0 && row.ActiveSkillId.Length == 0 &&
                row.PassiveSkillId.Length == 0) &&
            petRows.All(row => row.FeedStat.Contains("cosmetic", StringComparison.OrdinalIgnoreCase)),
            $"rows={petRows.Count} companionRange={companionRows.Max(row => row.OwnerRangeWu)} " +
            $"companionCap={companionRows.Max(row => row.LevelCap)} " +
            $"mountRange={mountRows.Max(row => row.OwnerRangeWu)} " +
            $"mountCap={mountRows.Max(row => row.LevelCap)} " +
            $"feedHours={companionRows.Max(row => row.FeedCooldownHours)} " +
            $"statFeedRows={petRows.Count(row => !row.FeedStat.Contains("cosmetic", StringComparison.OrdinalIgnoreCase))}");

        // The item catalogue carries its own row for every one of these ids, so the two
        // approved sources can be compared without guessing. `nameDisagreements` is the
        // headline: the same item_id names a different creature in each file, and the pet
        // table's four equipment slots exist in neither catalogue.
        var catalogueRows =
            new Dictionary<string, (string DisplayName, string Element, int RequiredLevel, string PrimaryValue)>(
                StringComparer.Ordinal);
        var petSlotTokenRows = 0;
        foreach (var line in File
                     .ReadAllLines(Path.Combine(productionDirectory, ItemCatalog.RelativePath))
                     .Skip(1))
        {
            var cells = MobEliteVariantCatalog.SplitCsvLine(line);
            if (cells.Count < 12)
            {
                continue;
            }

            if (cells[3].Contains("PET_", StringComparison.Ordinal) ||
                cells[3].Contains("MOUNT_", StringComparison.Ordinal))
            {
                petSlotTokenRows++;
            }

            if (cells[0].StartsWith("PET-", StringComparison.Ordinal) ||
                cells[0].StartsWith("MOUNT-", StringComparison.Ordinal))
            {
                catalogueRows[cells[0]] = (
                    cells[1],
                    cells[5],
                    int.TryParse(cells[6], System.Globalization.NumberStyles.Integer,
                        System.Globalization.CultureInfo.InvariantCulture,
                        out var requiredLevel) ? requiredLevel : -1,
                    cells[11]);
            }
        }

        var nameDisagreements = new List<string>();
        var blankCatalogueElements = 0;
        var impossibleLevelRows = 0;
        var companionPlaceholders = 0;
        var mountSpeedAgreements = 0;
        var missingTemplates = 0;
        foreach (var row in petRows)
        {
            if (!catalogueRows.TryGetValue(row.ItemTemplateId, out var catalogue))
            {
                missingTemplates++;
                continue;
            }

            if (!string.Equals(catalogue.DisplayName, row.DisplayNameVi, StringComparison.Ordinal))
            {
                nameDisagreements.Add($"{row.ItemTemplateId} pet='{row.DisplayNameVi}' " +
                    $"catalogue='{catalogue.DisplayName}'");
            }

            if (catalogue.Element.Length == 0)
            {
                blankCatalogueElements++;
            }

            if (catalogue.RequiredLevel > row.LevelCap)
            {
                impossibleLevelRows++;
            }

            if (row.IsCompanion && catalogue.PrimaryValue == "Pet passive")
            {
                companionPlaceholders++;
            }

            if (!row.IsCompanion &&
                catalogue.PrimaryValue.Contains("+10%", StringComparison.Ordinal))
            {
                mountSpeedAgreements++;
            }
        }

        Check(
            "companion.every_template_id_exists_in_the_item_catalogue_and_names_another_creature",
            missingTemplates == 0 && catalogueRows.Count == 11 &&
            nameDisagreements.Count == 10,
            $"missing={missingTemplates} disagreements={nameDisagreements.Count} " +
            $"first={Cut(nameDisagreements.Count > 0 ? nameDisagreements[0] : "none")} " +
            $"last={Cut(nameDisagreements.Count > 0 ? nameDisagreements[^1] : "none")}");

        Check(
            "companion.the_item_catalogue_states_no_element_and_no_item_fills_a_pet_slot",
            blankCatalogueElements == 10 && petSlotTokenRows == 0,
            $"blankElements={blankCatalogueElements} petSlotItems={petSlotTokenRows}");

        // A mount whose source says level_cap 1 while the catalogue requires level 10 to
        // bind/use it cannot be summoned at any level. This is a decision, not a number I
        // can pick, so it is pinned as five rows until someone states which column wins.
        Check(
            "companion.the_five_mount_rows_gate_above_their_own_level_cap",
            impossibleLevelRows == 5 && mountRows.All(row =>
                catalogueRows[row.ItemTemplateId].RequiredLevel > row.LevelCap) &&
            companionRows.All(row => catalogueRows[row.ItemTemplateId].RequiredLevel <= row.LevelCap),
            $"impossible={impossibleLevelRows} mountRequired=" +
            string.Join("|", mountRows.Select(row =>
                $"{row.ItemTemplateId}:{catalogueRows[row.ItemTemplateId].RequiredLevel}/" +
                $"cap{row.LevelCap}")));

        Check(
            "companion.the_sources_agree_only_on_the_mount_speed_rule",
            mountSpeedAgreements == 5 && companionPlaceholders == 5,
            $"mountSpeed={mountSpeedAgreements} companionPlaceholders={companionPlaceholders}");

        var companionSkillIds = companionRows
            .SelectMany(row => new[] { row.ActiveSkillId, row.PassiveSkillId })
            .ToArray();
        var otherSourceFiles = Directory.EnumerateFiles(productionDirectory)
            .Where(file => file.EndsWith(".csv", StringComparison.OrdinalIgnoreCase) ||
                           file.EndsWith(".md", StringComparison.OrdinalIgnoreCase))
            .Where(file => !file.EndsWith("Pet_Mount_Production_Data_vi.csv", StringComparison.Ordinal))
            .ToArray();
        var skillIdsDefinedElsewhere = companionSkillIds
            .Where(id => otherSourceFiles.Any(file =>
                File.ReadAllText(file).Contains(id, StringComparison.Ordinal)))
            .ToArray();
        Check(
            "companion.the_ten_pet_skill_ids_are_defined_nowhere_but_in_the_pet_table",
            companionSkillIds.Length == 10 &&
            companionSkillIds.Distinct(StringComparer.Ordinal).Count() == 10 &&
            skillIdsDefinedElsewhere.Length == 0,
            $"ids={companionSkillIds.Length} definedElsewhere=" +
            $"{string.Join("|", skillIdsDefinedElsewhere)}");

        string CompanionLoadFailure(string from, string to)
        {
            var root = Path.Combine(
                Path.GetTempPath(), "p1-companion-" + Guid.NewGuid().ToString("N"));
            try
            {
                var directory = Path.Combine(root, "docs", "production");
                Directory.CreateDirectory(directory);
                var source = File.ReadAllLines(
                    Path.Combine(productionDirectory, CompanionCatalog.RelativePath));
                File.WriteAllLines(
                    Path.Combine(directory, Path.GetFileName(CompanionCatalog.RelativePath)),
                    source.Select(line => line.Replace(from, to, StringComparison.Ordinal)).ToArray());

                try
                {
                    CompanionCatalog.Load(root);
                    return "LOADED";
                }
                catch (InvalidOperationException exception)
                {
                    return exception.Message;
                }
            }
            finally
            {
                Directory.Delete(root, recursive: true);
            }
        }

        var statBearingSlots = CompanionLoadFailure(
            "MOUNT_SADDLE cosmetic only", "MOUNT_SADDLE +5% hp");
        var pvpPetRule = CompanionLoadFailure(
            "PvE normal mobs only; no pet damage/heal in PvP",
            "PvE and PvP damage allowed");
        var mountGrowsALeash = CompanionLoadFailure(
            ",0,\"dismount on combat", ",8,\"dismount on combat");
        Check(
            "companion.loader_refuses_a_stat_slot_a_pvp_rule_and_a_mount_that_leashes",
            statBearingSlots.Contains("equipment_slots", StringComparison.Ordinal) &&
            pvpPetRule.Contains("combat_rule", StringComparison.Ordinal) &&
            mountGrowsALeash.Contains("contradicts the MOUNT leash", StringComparison.Ordinal),
            $"slots={Cut(statBearingSlots)}|rule={Cut(pvpPetRule)}|leash={Cut(mountGrowsALeash)}");

        // ─── QOD-21 Q3: the v2 twelve-slot handler ────

        // Same store, same aggregate revision, second vocabulary: these checks pin
        // what v2 is for (two accessories and the two armour slots v1 cannot name)
        // and that v1 keeps seeing its own five tokens for the very same items.
        var eqV2 = new EquipmentV2Service(
            inventory,
            services.GetRequiredService<IInventoryStateStore>(),
            itemCatalog,
            alphaDesign);
        var eqV2Actor = NewPlayer("CHR_SELFCHECK_EQUIP_V2");
        var eqV2Seed = inventory.Apply(eqV2Actor, new InventoryMutation
        {
            AddItems =
            [
                new ItemGrant { TemplateId = "EQ-MK-NECK-T1-R-COMMON", Stack = 1, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "EQ-MK-NECK-T1-R-COMMON", Stack = 1, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "EQ-MK-RING_L-T1-R-COMMON", Stack = 1, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "EQ-MK-RING_R-T1-R-COMMON", Stack = 1, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "EQ-MK-LEGS-T1-R-COMMON", Stack = 1, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "EQ-MK-GLOVES-T1-R-COMMON", Stack = 1, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "EQ-MK-NECK-T2-R-COMMON", Stack = 1, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "EQ-AD-HAT-T1-R-COMMON", Stack = 1, Location = InventoryLocations.Bag },
                new ItemGrant { TemplateId = "POT-HP-01", Stack = 1, Location = InventoryLocations.Bag }
            ]
        });
        var eqV2Items = eqV2Seed.Snapshot!.Items;
        string EqV2Instance(string templateId, int occurrence = 1) => eqV2Items
            .Where(item => item.TemplateId == templateId)
            .Select(item => item.InstanceId)
            .ElementAt(occurrence - 1);

        var eqV2Empty = eqV2.Read(eqV2Actor).Snapshot!;
        var eqV2Neck = eqV2.Equip(
            eqV2Actor, EqV2Instance("EQ-MK-NECK-T1-R-COMMON"), 1, NewKey()).Snapshot!;
        var eqV2RingL = eqV2.Equip(
            eqV2Actor, EqV2Instance("EQ-MK-RING_L-T1-R-COMMON"), 2, NewKey()).Snapshot!;
        var eqV2Legs = eqV2.Equip(
            eqV2Actor, EqV2Instance("EQ-MK-LEGS-T1-R-COMMON"), 3, NewKey()).Snapshot!;
        var eqV2V1View = inventory.GetSnapshot(eqV2Actor.CharacterId);
        var eqV2RingLOut = eqV2.Unequip(eqV2Actor, InventoryV2Slots.RingLeft, 4, NewKey()).Snapshot!;

        Check(
            "equipment_v2.equips_the_twelve_slots_without_moving_v1",
            eqV2Seed.IsSuccess && eqV2Seed.Snapshot!.InventoryRevision == 1 &&
            eqV2Empty.Slots.Count == 12 &&
            eqV2Empty.Slots.All(entry => entry.Item is null) &&
            eqV2Empty.BagSlots == 100 &&
            eqV2Empty.Bag.Count == 9 &&
            string.Equals(eqV2Empty.SlotSpec, alphaDesign.Inventory.WireMigration,
                StringComparison.Ordinal) &&
            eqV2Empty.InventoryRevision == 1 &&
            // Two accessories in two slots is the whole point of v2.
            eqV2RingL.Slots.Single(e => e.SlotId == InventoryV2Slots.Neck).Item is { } wornNeck &&
            wornNeck.SlotId == InventoryV2Slots.Neck &&
            eqV2RingL.Slots.Single(e => e.SlotId == InventoryV2Slots.RingLeft).Item?.TemplateId ==
                "EQ-MK-RING_L-T1-R-COMMON" &&
            eqV2Legs.Slots.Count(e => e.Item is not null) == 3 &&
            eqV2Legs.Bag.Count == 6 &&
            eqV2Legs.InventoryRevision == 4 &&
            // v1 still reads three equipped items, in its own vocabulary or with no
            // slot at all for the two armour pieces it has no token for.
            eqV2V1View.Items.Count(item =>
                item.Location == InventoryLocations.Equipped) == 3 &&
            eqV2V1View.Items.Single(item =>
                item.TemplateId == "EQ-MK-NECK-T1-R-COMMON" &&
                item.Location == InventoryLocations.Equipped).Slot ==
                EquipmentSlots.Accessory &&
            eqV2V1View.Items.Single(item =>
                item.TemplateId == "EQ-MK-RING_L-T1-R-COMMON" &&
                item.Location == InventoryLocations.Equipped).Slot ==
                EquipmentSlots.Accessory &&
            eqV2V1View.Items.Single(item =>
                item.TemplateId == "EQ-MK-LEGS-T1-R-COMMON" &&
                item.Location == InventoryLocations.Equipped).Slot is null &&
            eqV2RingLOut.Slots.Single(e => e.SlotId == InventoryV2Slots.RingLeft).Item is null &&
            eqV2RingLOut.Bag.Single(item =>
                item.TemplateId == "EQ-MK-RING_L-T1-R-COMMON" &&
                item.Location == InventoryLocations.Bag).SlotId is null &&
            inventory.GetSnapshot(eqV2Actor.CharacterId).Items.Count(item =>
                item.Location == InventoryLocations.Equipped) == 2,
            $"slots={eqV2Legs.Slots.Count(e => e.Item is not null)} " +
            $"v1={string.Join('|', eqV2V1View.Items.Where(i => i.Location == InventoryLocations.Equipped).Select(i => i.Slot ?? "(none)"))}");

        var eqV2NeckTaken = eqV2.Equip(
            eqV2Actor, EqV2Instance("EQ-MK-NECK-T1-R-COMMON", 2), 5, NewKey());
        var eqV2Potion = eqV2.Equip(eqV2Actor, EqV2Instance("POT-HP-01"), 5, NewKey());
        var eqV2TooHigh = eqV2.Equip(
            eqV2Actor, EqV2Instance("EQ-MK-NECK-T2-R-COMMON"), 5, NewKey());
        var eqV2WrongClass = eqV2.Equip(
            eqV2Actor, EqV2Instance("EQ-AD-HAT-T1-R-COMMON"), 5, NewKey());
        var eqV2Unknown = eqV2.Equip(eqV2Actor, "ITM_NOPE_NOT_THERE", 5, NewKey());
        var eqV2AlreadyWorn = eqV2.Equip(
            eqV2Actor, EqV2Instance("EQ-MK-LEGS-T1-R-COMMON"), 5, NewKey());
        var eqV2EmptySlot = eqV2.Unequip(eqV2Actor, InventoryV2Slots.Seal, 5, NewKey());
        var eqV2StaleRevision = eqV2.Equip(
            eqV2Actor, EqV2Instance("EQ-MK-GLOVES-T1-R-COMMON"), 2, NewKey());
        var eqV2Key = NewKey();
        var eqV2First = eqV2.Equip(
            eqV2Actor, EqV2Instance("EQ-MK-GLOVES-T1-R-COMMON"), 5, eqV2Key);
        var eqV2Replay = eqV2.Equip(
            eqV2Actor, EqV2Instance("EQ-MK-GLOVES-T1-R-COMMON"), 5, eqV2Key);
        var eqV2Conflict = eqV2.Equip(
            eqV2Actor, EqV2Instance("EQ-MK-RING_R-T1-R-COMMON"), 6, eqV2Key);

        Check(
            "equipment_v2.gates_revisions_and_idempotency_match_v1_rules",
            eqV2NeckTaken.Failure?.Code == EquipmentErrorCodes.SlotOccupied &&
            eqV2NeckTaken.Snapshot is not null &&
            eqV2Potion.Failure?.Code == EquipmentErrorCodes.NotEquippable &&
            eqV2TooHigh.Failure?.Code == EquipmentErrorCodes.LevelRequired &&
            eqV2WrongClass.Failure?.Code == EquipmentErrorCodes.ClassRestricted &&
            eqV2Unknown.Failure?.Code == EquipmentErrorCodes.ItemNotFound &&
            eqV2AlreadyWorn.Failure?.Code == EquipmentErrorCodes.WrongLocation &&
            eqV2EmptySlot.Failure?.Code == EquipmentErrorCodes.WrongLocation &&
            eqV2StaleRevision.Failure?.Code == EquipmentErrorCodes.RevisionConflict &&
            eqV2StaleRevision.Failure.Retryable &&
            eqV2StaleRevision.Snapshot?.InventoryRevision == 5 &&
            eqV2First.Accepted && eqV2First.Snapshot!.InventoryRevision == 6 &&
            eqV2Replay.Accepted && ReferenceEquals(eqV2Replay.Snapshot, eqV2First.Snapshot) &&
            inventory.GetSnapshot(eqV2Actor.CharacterId).Items.Count(item =>
                item.Location == InventoryLocations.Equipped) == 3 &&
            eqV2Conflict.Failure?.Code == EquipmentErrorCodes.IdempotencyConflict,
            $"occupied={eqV2NeckTaken.Failure?.Code} potion={eqV2Potion.Failure?.Code} " +
            $"level={eqV2TooHigh.Failure?.Code} class={eqV2WrongClass.Failure?.Code} " +
            $"stale={eqV2StaleRevision.Failure?.Code} replay={eqV2Replay.Snapshot?.InventoryRevision}");

        // A slot string neither vocabulary can name must surface, not vanish: the
        // decision's incompatibleV1Projection rule, exercised through the store seam
        // because no route can write one.
        var eqV2OrphanActor = NewPlayer("CHR_SELFCHECK_EQUIP_V2_ORPHAN");
        inventory.Apply(eqV2OrphanActor, new InventoryMutation
        {
            AddItems =
            [
                new ItemGrant
                {
                    TemplateId = "POT-HP-01",
                    Stack = 1,
                    Location = InventoryLocations.Equipped,
                    Slot = "TOTEM"
                }
            ]
        });
        var eqV2Orphan = eqV2.Read(eqV2OrphanActor).Snapshot!;

        Check(
            "equipment_v2.unsupported_reports_every_slot_it_cannot_name",
            eqV2Orphan.Slots.Count == 12 &&
            eqV2Orphan.Slots.All(entry =>
                entry.Item is null && entry.SlotId.Length > 0) &&
            eqV2Orphan.Unsupported.Count == 1 &&
            eqV2Orphan.Unsupported[0].Reason == InventoryV2UnsupportedReasons.UnmappedSlot &&
            eqV2Orphan.Unsupported[0].SourceSlot == "TOTEM" &&
            eqV2Orphan.Bag.Count == 0,
            $"unsupported={eqV2Orphan.Unsupported.Count} " +
            $"reason={eqV2Orphan.Unsupported.FirstOrDefault()?.Reason}");

        // ─── turn-in ───────────────────────────────────────────

        var turnInActor = NewPlayer("CHR_SELFCHECK_TURNIN");
        var turnInQuestId = "P00-01";

        // set up objectives complete → READY_TO_TURN_IN
        var turnInAccept = quests.Accept(turnInActor, turnInQuestId);
        Check(
            "turnin.accept_setup",
            turnInAccept.Accepted,
            turnInAccept.Failure?.Code);

        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            var eventId = Guid.NewGuid().ToString("N");
            quests.RecordVerifiedEvent(
                turnInActor, eventId, QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }

        var readyState = quests.GetState(turnInActor.CharacterId, turnInQuestId);
        Check(
            "turnin.ready_state",
            readyState.Accepted &&
            string.Equals(readyState.State!.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal),
            readyState.State?.State);

        // walk to turn-in NPC anchor
        npcAnchors.TryResolve("NPC_TA_VAN_KHANH", "MAP_BEN_MUA", out var turnInAnchor);
        turnInActor.X = turnInAnchor.X;
        turnInActor.Y = turnInAnchor.Y;

        // NPC mismatch
        var turnInWrongNpc = questTurnIn.TurnIn(
            turnInActor, turnInQuestId, "NPC_LYAN", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.npc_mismatch",
            !turnInWrongNpc.Accepted &&
            string.Equals(turnInWrongNpc.Failure!.Code, QuestTurnInErrorCodes.NpcMismatch, StringComparison.Ordinal),
            turnInWrongNpc.Failure?.Code);

        // unknown quest
        var turnInUnknownQuest = questTurnIn.TurnIn(
            turnInActor, "QQ-99", "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.quest_not_found",
            !turnInUnknownQuest.Accepted &&
            string.Equals(turnInUnknownQuest.Failure!.Code, QuestErrorCodes.QuestNotFound, StringComparison.Ordinal),
            turnInUnknownQuest.Failure?.Code);

        // wrong floor: actor on a different floor than the NPC anchor
        turnInActor.FloorId = "MAP_BEN_MUA_F1";
        var wrongFloor = questTurnIn.TurnIn(
            turnInActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.wrong_floor",
            !wrongFloor.Accepted &&
            string.Equals(wrongFloor.Failure!.Code, QuestTurnInErrorCodes.OutOfRange, StringComparison.Ordinal),
            wrongFloor.Failure?.Code);
        turnInActor.FloorId = "OVERWORLD";

        // out of range
        turnInActor.X = 0;
        turnInActor.Y = 0;
        var outOfRange = questTurnIn.TurnIn(
            turnInActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.out_of_range",
            !outOfRange.Accepted &&
            string.Equals(outOfRange.Failure!.Code, QuestTurnInErrorCodes.OutOfRange, StringComparison.Ordinal),
            outOfRange.Failure?.Code);

        // back in range
        turnInActor.X = turnInAnchor.X;
        turnInActor.Y = turnInAnchor.Y;

        // successful turn-in
        var turnInKey = Guid.NewGuid().ToString("N");
        var result = questTurnIn.TurnIn(turnInActor, turnInQuestId, "NPC_TA_VAN_KHANH", turnInKey);
        Check(
            "turnin.success",
            result.Accepted &&
            string.Equals(result.Result!.QuestState.State, QuestStates.Completed, StringComparison.Ordinal) &&
            result.Result!.Rewards.Currency.Any(c =>
                string.Equals(c.CurrencyId, "COIN", StringComparison.Ordinal) && c.Amount == 20) &&
            result.Result!.Rewards.Items.Count == 1 &&
            string.Equals(result.Result!.Rewards.Items[0].TemplateId, "EQ-MK-CHEST-T1-R-COMMON", StringComparison.Ordinal) &&
            !result.Result!.Rewards.Xp.Applied &&
            result.Result!.Unlocks.Count == 1 &&
            string.Equals(result.Result!.Unlocks[0], "P00-02", StringComparison.Ordinal),
            result.Failure?.Code);

        // verify inventory was granted
        var postTurnInInv = inventory.GetSnapshot(turnInActor.CharacterId);
        Check(
            "turnin.inventory_granted",
            postTurnInInv.Currencies.Any(c =>
                string.Equals(c.CurrencyId, "COIN", StringComparison.Ordinal) && c.Amount == 20) &&
            postTurnInInv.Items.Any(i =>
                string.Equals(i.TemplateId, "EQ-MK-CHEST-T1-R-COMMON", StringComparison.Ordinal)),
            $"currencies={postTurnInInv.Currencies.Count} items={postTurnInInv.Items.Count}");

        // replay same key returns identical result
        var replay = questTurnIn.TurnIn(turnInActor, turnInQuestId, "NPC_TA_VAN_KHANH", turnInKey);
        Check(
            "turnin.replay_same_key",
            replay.Accepted &&
            string.Equals(replay.Result!.QuestState.State, QuestStates.Completed, StringComparison.Ordinal),
            replay.Failure?.Code);

        // second turn-in with new key → invalid_transition
        var newKey = Guid.NewGuid().ToString("N");
        var secondTurnIn = questTurnIn.TurnIn(
            turnInActor, turnInQuestId, "NPC_TA_VAN_KHANH", newKey);
        Check(
            "turnin.invalid_transition_after_completed",
            !secondTurnIn.Accepted &&
            string.Equals(secondTurnIn.Failure!.Code, QuestErrorCodes.InvalidTransition, StringComparison.Ordinal),
            secondTurnIn.Failure?.Code);

        // inventory unchanged after rejected second turn-in
        var unchangedInv = inventory.GetSnapshot(turnInActor.CharacterId);
        Check(
            "turnin.inventory_no_double_reward",
            unchangedInv.Currencies.Count == 1 &&
            unchangedInv.Items.Count == 1,
            $"currencies={unchangedInv.Currencies.Count} items={unchangedInv.Items.Count}");

        // idempotency conflict: same key, different payload (different npcId)
        var wrongNpcReplay = questTurnIn.TurnIn(
            turnInActor, turnInQuestId, "NPC_LYAN", turnInKey);
        Check(
            "turnin.same_key_different_npc_conflict",
            !wrongNpcReplay.Accepted &&
            string.Equals(
                wrongNpcReplay.Failure!.Code,
                QuestTurnInErrorCodes.IdempotencyConflict,
                StringComparison.Ordinal),
            wrongNpcReplay.Failure?.Code);

        var turnInIdemActor = NewPlayer("CHR_SELFCHECK_IDEM");
        quests.Accept(turnInIdemActor, "P00-01");
        // progress to READY_TO_TURN_IN
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                turnInIdemActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        turnInIdemActor.X = turnInAnchor.X;
        turnInIdemActor.Y = turnInAnchor.Y;

        var conflictKey2 = Guid.NewGuid().ToString("N");
        var firstCall = questTurnIn.TurnIn(turnInIdemActor, turnInQuestId, "NPC_TA_VAN_KHANH", conflictKey2);
        Check(
            "turnin.idempotency_setup",
            firstCall.Accepted,
            firstCall.Failure?.Code);

        // Data integrity: reward-once via ledger
        var ledgerResult = rewardLedger.Find(turnInIdemActor.CharacterId, turnInQuestId);
        Check(
            "turnin.reward_ledger_recorded",
            ledgerResult is not null &&
            string.Equals(ledgerResult.QuestState.State, QuestStates.Completed, StringComparison.Ordinal),
            ledgerResult?.QuestState.State);

        // ─── failure injection: reward transaction must not partially commit ───

        var failOnceInventory = new FailOnceInventoryDecorator(inventory);
        var failOnceLedger = new RewardLedgerStore();
        var failOnceTurnIn = new InMemoryQuestTurnInService(
            questCatalog,
            quests,
            failOnceInventory,
            npcAnchors,
            services.GetRequiredService<IWorldGeometryService>(),
            failOnceLedger,
            services.GetRequiredService<ExperienceService>(),
            services.GetRequiredService<QuestXpSnapshotStore>(),
            services.GetRequiredService<IOptions<QuestTurnInOptions>>().Value);

        var failActor = NewPlayer("CHR_SELFCHECK_FAILONCE");
        quests.Accept(failActor, turnInQuestId);
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                failActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        failActor.X = turnInAnchor.X;
        failActor.Y = turnInAnchor.Y;

        var failedTurnIn = failOnceTurnIn.TurnIn(
            failActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.failure_injection_rejected",
            !failedTurnIn.Accepted &&
            string.Equals(failedTurnIn.Failure!.Code, InventoryErrorCodes.SlotOccupied, StringComparison.Ordinal) &&
            failedTurnIn.Failure.Retryable,
            failedTurnIn.Failure?.Code);

        var stateAfterFail = quests.GetState(failActor.CharacterId, turnInQuestId);
        Check(
            "turnin.failure_injection_state_kept",
            stateAfterFail.Accepted &&
            string.Equals(stateAfterFail.State!.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal),
            stateAfterFail.State?.State);

        var inventoryAfterFail = inventory.GetSnapshot(failActor.CharacterId);
        Check(
            "turnin.failure_injection_no_partial_reward",
            inventoryAfterFail.Items.Count == 0 && inventoryAfterFail.Currencies.Count == 0,
            $"items={inventoryAfterFail.Items.Count} currencies={inventoryAfterFail.Currencies.Count}");

        Check(
            "turnin.failure_injection_ledger_empty",
            failOnceLedger.Find(failActor.CharacterId, turnInQuestId) is null,
            "ledger entry must not exist after failed grant");

        var retriedTurnIn = failOnceTurnIn.TurnIn(
            failActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.failure_injection_retry_succeeds",
            retriedTurnIn.Accepted &&
            string.Equals(retriedTurnIn.Result!.QuestState.State, QuestStates.Completed, StringComparison.Ordinal),
            retriedTurnIn.Failure?.Code);

        var inventoryAfterRetry = inventory.GetSnapshot(failActor.CharacterId);
        Check(
            "turnin.failure_injection_single_reward",
            inventoryAfterRetry.Currencies.Count == 1 &&
            inventoryAfterRetry.Currencies[0].Amount == 20 &&
            inventoryAfterRetry.Items.Count == 1,
            $"items={inventoryAfterRetry.Items.Count} currencies={inventoryAfterRetry.Currencies.Count}");

        // ─── failure injection: quest flip failure must roll back the grant ───

        var failOnceQuests = new FailOnceQuestDecorator(quests);
        var flipFailLedger = new RewardLedgerStore();
        var flipFailTurnIn = new InMemoryQuestTurnInService(
            questCatalog,
            failOnceQuests,
            inventory,
            npcAnchors,
            services.GetRequiredService<IWorldGeometryService>(),
            flipFailLedger,
            services.GetRequiredService<ExperienceService>(),
            services.GetRequiredService<QuestXpSnapshotStore>(),
            services.GetRequiredService<IOptions<QuestTurnInOptions>>().Value);

        var flipFailActor = NewPlayer("CHR_SELFCHECK_FLIPFAIL");
        quests.Accept(flipFailActor, turnInQuestId);
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                flipFailActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        flipFailActor.X = turnInAnchor.X;
        flipFailActor.Y = turnInAnchor.Y;

        var flipFailed = flipFailTurnIn.TurnIn(
            flipFailActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.flip_failure_rejected",
            !flipFailed.Accepted &&
            string.Equals(flipFailed.Failure!.Code, QuestErrorCodes.InvalidTransition, StringComparison.Ordinal),
            flipFailed.Failure?.Code);

        var flipStateAfter = quests.GetState(flipFailActor.CharacterId, turnInQuestId);
        Check(
            "turnin.flip_failure_state_kept",
            flipStateAfter.Accepted &&
            string.Equals(flipStateAfter.State!.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal),
            flipStateAfter.State?.State);

        var flipInventoryAfter = inventory.GetSnapshot(flipFailActor.CharacterId);
        Check(
            "turnin.flip_failure_grant_rolled_back",
            flipInventoryAfter.Items.Count == 0 && flipInventoryAfter.Currencies.Count == 0,
            $"items={flipInventoryAfter.Items.Count} currencies={flipInventoryAfter.Currencies.Count}");

        Check(
            "turnin.flip_failure_ledger_empty",
            flipFailLedger.Find(flipFailActor.CharacterId, turnInQuestId) is null,
            "ledger entry must not exist after failed flip");

        var flipRetried = flipFailTurnIn.TurnIn(
            flipFailActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.flip_failure_retry_succeeds",
            flipRetried.Accepted &&
            string.Equals(flipRetried.Result!.QuestState.State, QuestStates.Completed, StringComparison.Ordinal),
            flipRetried.Failure?.Code);

        var flipInventoryRetry = inventory.GetSnapshot(flipFailActor.CharacterId);
        Check(
            "turnin.flip_failure_single_reward",
            flipInventoryRetry.Currencies.Count == 1 &&
            flipInventoryRetry.Currencies[0].Amount == 20 &&
            flipInventoryRetry.Items.Count == 1,
            $"items={flipInventoryRetry.Items.Count} currencies={flipInventoryRetry.Currencies.Count}");

        // ─── failure injection: ledger failure must roll back grant and flip ───

        var failOnceLedgerStore = new FailOnceLedgerStore();
        var ledgerFailTurnIn = new InMemoryQuestTurnInService(
            questCatalog,
            quests,
            inventory,
            npcAnchors,
            services.GetRequiredService<IWorldGeometryService>(),
            failOnceLedgerStore,
            services.GetRequiredService<ExperienceService>(),
            services.GetRequiredService<QuestXpSnapshotStore>(),
            services.GetRequiredService<IOptions<QuestTurnInOptions>>().Value);

        var ledgerFailActor = NewPlayer("CHR_SELFCHECK_LEDGERFAIL");
        quests.Accept(ledgerFailActor, turnInQuestId);
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                ledgerFailActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        ledgerFailActor.X = turnInAnchor.X;
        ledgerFailActor.Y = turnInAnchor.Y;

        var ledgerFailed = ledgerFailTurnIn.TurnIn(
            ledgerFailActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.ledger_failure_rejected",
            !ledgerFailed.Accepted &&
            string.Equals(
                ledgerFailed.Failure!.Code,
                QuestTurnInErrorCodes.IdempotencyConflict,
                StringComparison.Ordinal) &&
            ledgerFailed.Failure.Retryable,
            ledgerFailed.Failure?.Code);

        var ledgerStateAfter = quests.GetState(ledgerFailActor.CharacterId, turnInQuestId);
        Check(
            "turnin.ledger_failure_state_kept",
            ledgerStateAfter.Accepted &&
            string.Equals(ledgerStateAfter.State!.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal),
            ledgerStateAfter.State?.State);

        var ledgerInventoryAfter = inventory.GetSnapshot(ledgerFailActor.CharacterId);
        Check(
            "turnin.ledger_failure_grant_rolled_back",
            ledgerInventoryAfter.Items.Count == 0 && ledgerInventoryAfter.Currencies.Count == 0,
            $"items={ledgerInventoryAfter.Items.Count} currencies={ledgerInventoryAfter.Currencies.Count}");

        Check(
            "turnin.ledger_failure_ledger_empty",
            failOnceLedgerStore.Find(ledgerFailActor.CharacterId, turnInQuestId) is null,
            "ledger entry must not exist after failed record");

        var ledgerRetried = ledgerFailTurnIn.TurnIn(
            ledgerFailActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.ledger_failure_retry_succeeds",
            ledgerRetried.Accepted &&
            string.Equals(ledgerRetried.Result!.QuestState.State, QuestStates.Completed, StringComparison.Ordinal),
            ledgerRetried.Failure?.Code);

        var ledgerInventoryRetry = inventory.GetSnapshot(ledgerFailActor.CharacterId);
        Check(
            "turnin.ledger_failure_single_reward",
            ledgerInventoryRetry.Currencies.Count == 1 &&
            ledgerInventoryRetry.Currencies[0].Amount == 20 &&
            ledgerInventoryRetry.Items.Count == 1,
            $"items={ledgerInventoryRetry.Items.Count} currencies={ledgerInventoryRetry.Currencies.Count}");

        // ─── QOD-21 Q4: P00-05's chapter consequence lives inside the transaction ────

        // The design states the consequence as prose, so the two tokens it names are
        // pinned before anything uses them: a design whose sentence drops the flag or
        // swaps the portal map has to fail startup rather than grant something the
        // source no longer names.
        Check(
            "alpha.quest_p5_unlock_clause_is_pinned",
            alphaDesign.QuestRules.P00_05_UnlockText.Contains(
                "CHAPTER_C1_UNLOCKED", StringComparison.Ordinal) &&
            alphaDesign.QuestRules.P00_05_UnlockText.Contains(
                "MAP_THANH_LAC", StringComparison.Ordinal) &&
            AlphaRejects(alphaDesign with
            {
                QuestRules = alphaDesign.QuestRules with
                {
                    P00_05_UnlockText = "P00-05 turn-in commits CHAPTER_C1 and portal"
                }
            }) &&
            AlphaRejects(alphaDesign with
            {
                QuestRules = alphaDesign.QuestRules with
                {
                    P00_05_UnlockText = "P00-05 turn-in commits CHAPTER_C1_UNLOCKED " +
                        "and MAP_GIANG_CHAU portal access"
                }
            }),
            $"text={alphaDesign.QuestRules.P00_05_UnlockText}");

        // A throwaway two-quest graph, because the consequence keys on the quest id
        // the design names: P00-05 must grant, its neighbour must not, and both have
        // to reach READY_TO_TURN_IN through the real quest service.
        QuestDefinition ChapterFixture(string questId) => new(
            questId,
            QuestTypes.Main,
            "NPC_TA_VAN_KHANH",
            1,
            10,
            [],
            [
                new QuestObjectiveDefinition(
                    "OBJ_CH_" + questId, QuestObjectiveTypes.Boss,
                    ["MAN-BM-SPAWN_BM_05_QUEST"], 1, "MAP_BEN_MUA")
            ],
            QuestStepIds.FromObjectiveId("OBJ_CH_" + questId),
            "NPC_TA_VAN_KHANH",
            new QuestRewards([new QuestRewardCurrency("COIN", 20)], [], "LEVEL_BAND_BASE"),
            []);

        var chapterCatalog = new QuestCatalog(new Dictionary<string, QuestDefinition>
        {
            ["P00-05"] = ChapterFixture("P00-05"),
            ["P00-04"] = ChapterFixture("P00-04")
        });
        var chapterQuests = new InMemoryQuestService(
            chapterCatalog, new InMemoryQuestStateStore(), alphaMergedRecords, interactClock);

        InMemoryQuestTurnInService ChapterTurnInService(
            RewardLedgerStore ledger, IChapterUnlockSink sink) => new(
                chapterCatalog,
                chapterQuests,
                inventory,
                npcAnchors,
                services.GetRequiredService<IWorldGeometryService>(),
                ledger,
                services.GetRequiredService<ExperienceService>(),
                services.GetRequiredService<QuestXpSnapshotStore>(),
                services.GetRequiredService<IOptions<QuestTurnInOptions>>().Value,
                sink);

        void WalkToTurnInAnchor(PlayerSession actor, string questId, string eventId)
        {
            chapterQuests.Accept(actor, questId);
            chapterQuests.RecordVerifiedEvent(
                actor, eventId, QuestProgressEventTypes.Kill,
                "MAN-BM-SPAWN_BM_05_QUEST", "MAP_BEN_MUA");
            actor.X = turnInAnchor.X;
            actor.Y = turnInAnchor.Y;
        }

        var chapterStore = new ChapterUnlockStore(new AlphaProfileOptions { Enabled = true });
        var chapterKey = NewKey();
        var chapterActor = NewPlayer("CHR_SELFCHECK_CHAPTER_P5");
        WalkToTurnInAnchor(chapterActor, "P00-05", new string('1', 32));
        var chapterTurnIn = ChapterTurnInService(new RewardLedgerStore(), chapterStore);
        var chapterCommitted = chapterTurnIn.TurnIn(
            chapterActor, "P00-05", "NPC_TA_VAN_KHANH", chapterKey);
        var chapterReplay = chapterTurnIn.TurnIn(
            chapterActor, "P00-05", "NPC_TA_VAN_KHANH", chapterKey);
        var neighbourActor = NewPlayer("CHR_SELFCHECK_CHAPTER_P4");
        WalkToTurnInAnchor(neighbourActor, "P00-04", new string('2', 32));
        var neighbourCommitted = chapterTurnIn.TurnIn(
            neighbourActor, "P00-04", "NPC_TA_VAN_KHANH", NewKey());
        Check(
            "alpha.chapter_unlock.p5_turn_in_grants_flag_and_portal",
            chapterCommitted.Accepted && chapterReplay.Accepted && neighbourCommitted.Accepted &&
            chapterStore.Count == 1 &&
            chapterStore.HasFlag(chapterActor.CharacterId, AlphaChapterUnlockRules.Flag) &&
            chapterStore.AllowsPortal(
                chapterActor.CharacterId, AlphaChapterUnlockRules.PortalMapId) &&
            !chapterStore.AllowsPortal(chapterActor.CharacterId, "MAP_BEN_MUA") &&
            !chapterStore.HasFlag(neighbourActor.CharacterId, AlphaChapterUnlockRules.Flag),
            $"count={chapterStore.Count} p5={chapterCommitted.Failure?.Code} " +
            $"p4={neighbourCommitted.Failure?.Code}");

        // With the profile off the sink is wired but inert: the turn-in still
        // commits, and no chapter consequence is recorded for anybody.
        var chapterOffStore = new ChapterUnlockStore(new AlphaProfileOptions { Enabled = false });
        var chapterOffActor = NewPlayer("CHR_SELFCHECK_CHAPTER_OFF");
        WalkToTurnInAnchor(chapterOffActor, "P00-05", new string('3', 32));
        var chapterOffTurnIn = ChapterTurnInService(new RewardLedgerStore(), chapterOffStore)
            .TurnIn(chapterOffActor, "P00-05", "NPC_TA_VAN_KHANH", NewKey());
        Check(
            "alpha.chapter_unlock.gate_off_records_nothing",
            chapterOffTurnIn.Accepted &&
            chapterOffStore.Count == 0 &&
            !chapterOffStore.HasFlag(chapterOffActor.CharacterId, AlphaChapterUnlockRules.Flag) &&
            !chapterOffStore.AllowsPortal(
                chapterOffActor.CharacterId, AlphaChapterUnlockRules.PortalMapId),
            $"count={chapterOffStore.Count} code={chapterOffTurnIn.Failure?.Code}");

        // A ledger failure rolls the whole transaction back, and the consequence is
        // part of it: the grant has to disappear with the flip and reappear on the
        // retry, never survive a turn-in the client was told failed.
        var chapterRevokeStore = new ChapterUnlockStore(new AlphaProfileOptions { Enabled = true });
        var chapterRevokeLedger = new FailOnceLedgerStore();
        var chapterRevokeTurnIn = ChapterTurnInService(chapterRevokeLedger, chapterRevokeStore);
        var chapterRevokeActor = NewPlayer("CHR_SELFCHECK_CHAPTER_REVOKE");
        WalkToTurnInAnchor(chapterRevokeActor, "P00-05", new string('4', 32));
        var chapterRolledBack = chapterRevokeTurnIn.TurnIn(
            chapterRevokeActor, "P00-05", "NPC_TA_VAN_KHANH", NewKey());
        var chapterRolledState = chapterQuests.GetState(
            chapterRevokeActor.CharacterId, "P00-05").State;
        var countAfterRollback = chapterRevokeStore.Count;
        var grantedAfterRollback = chapterRevokeStore.HasFlag(
            chapterRevokeActor.CharacterId, AlphaChapterUnlockRules.Flag);
        var chapterRetried = chapterRevokeTurnIn.TurnIn(
            chapterRevokeActor, "P00-05", "NPC_TA_VAN_KHANH", NewKey());
        Check(
            "alpha.chapter_unlock.ledger_failure_rolls_the_grant_back",
            !chapterRolledBack.Accepted &&
            countAfterRollback == 0 &&
            !grantedAfterRollback &&
            string.Equals(
                chapterRolledState?.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal) &&
            chapterRetried.Accepted &&
            chapterRevokeStore.HasFlag(
                chapterRevokeActor.CharacterId, AlphaChapterUnlockRules.Flag),
            $"rejected={chapterRolledBack.Failure?.Code} count={countAfterRollback} " +
            $"state={chapterRolledState?.State} retry={chapterRetried.Failure?.Code}");

        // DEC-ALPHA-INTERACT-IDS-20261105 narrows the widening I shipped in
        // 61b96a2: the approval is an exact list of the six published overlay ids,
        // not the ALPHA_ prefix. The interact route therefore addresses ENT_
        // entities plus those six and nothing looser — the training hazard (a
        // position-read rect, not an interaction) and any other ALPHA_ id are
        // refused as invalid_payload before the registry is consulted, so no state
        // can be touched through an id the decision never published. The cast
        // vocabulary stays ENT_-only: /p1/v2/combat checks its target with
        // IsEntityId, which no longer accepts the prefix at all.
        Check(
            "contracts.interact_target_accepts_ent_and_the_six_alpha_ids",
            P1Validation.IsEntityId("ENT_MAN_BM_SPAWN_BM_01") &&
            P1Validation.IsInteractTargetId("ENT_MAN_BM_OBJ_BM_PACKAGE_01") &&
            P1Validation.AlphaInteractEntityIds.All(P1Validation.IsInteractTargetId) &&
            P1Validation.AlphaInteractEntityIds.Count == 6 &&
            !P1Validation.IsEntityId("ALPHA_OBJ_BM_RIPPLE_01") &&
            !P1Validation.IsInteractTargetId("ALPHA_OBJ_BM_RIPPLE_99") &&
            !P1Validation.IsInteractTargetId("ALPHA_WAVE_BM_TRAINING") &&
            !P1Validation.IsInteractTargetId("alpha_obj_bm_fragment") &&
            !P1Validation.IsInteractTargetId("ALPHA-OBJ-BM-FRAGMENT") &&
            !P1Validation.IsInteractTargetId("FOO_MAN_BM_SPAWN_BM_01") &&
            !P1Validation.IsInteractTargetId("ENT-MAN-BM-SPAWN") &&
            !P1Validation.IsInteractTargetId("MAN_BM_SPAWN") &&
            !P1Validation.IsInteractTargetId(null),
            "ENT_ plus the six exact alpha ids accepted; the prefix and everything " +
            "else still refused");

        // The same rule at the route's own front door: an unpublished alpha id is
        // named in fieldErrors and nothing else about the envelope is reported, so
        // the answer cannot be mistaken for a state conflict.
        List<string> InteractTargetErrors(string targetId) =>
            P1Validation.ValidateInteractEnvelope(new InteractEnvelope
            {
                SchemaVersion = 1,
                RequestId = new string('c', 32),
                IdempotencyKey = new string('d', 32),
                SentAtUtc = "2026-11-05T00:00:00Z",
                CharacterId = "CHR_SELFCHECK_INTERACT_ID",
                Payload = new InteractIntent { TargetId = targetId }
            });

        var unpublishedAlphaErrors = InteractTargetErrors("ALPHA_OBJ_BM_RIPPLE_99");
        Check(
            "contracts.interact_envelope_refuses_an_unpublished_alpha_id",
            unpublishedAlphaErrors.Count == 1 &&
            unpublishedAlphaErrors[0] == "payload.targetId" &&
            InteractTargetErrors("ALPHA_OBJ_BM_RIPPLE_01").Count == 0 &&
            InteractTargetErrors("ENT_MAN_BM_OBJ_BM_PACKAGE_01").Count == 0 &&
            InteractTargetErrors("ALPHA_WAVE_BM_TRAINING").Count == 1,
            $"unpublished={string.Join(",", unpublishedAlphaErrors)}");

        // ─── overflow: balance near long.MaxValue rejects without partial commit ───

        var overflowActor = NewPlayer("CHR_SELFCHECK_OVERFLOW");
        quests.Accept(overflowActor, turnInQuestId);
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                overflowActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        overflowActor.X = turnInAnchor.X;
        overflowActor.Y = turnInAnchor.Y;

        // Seed the near-max balance directly in the state store: mutation
        // validation caps currency deltas at 10^12, so the overflow boundary
        // can only be reached by writing the stored balance itself.
        var overflowStateStore = services.GetRequiredService<IInventoryStateStore>();
        var overflowBalanceState = overflowStateStore.GetOrAdd(overflowActor.CharacterId);
        lock (overflowBalanceState.SyncRoot)
        {
            overflowBalanceState.Currencies["COIN"] = long.MaxValue - 10;
        }

        var seedOverflow = inventory.GetSnapshot(overflowActor.CharacterId);
        Check(
            "turnin.overflow_seed",
            seedOverflow.Currencies.Count == 1 &&
            seedOverflow.Currencies[0].Amount == long.MaxValue - 10,
            seedOverflow.Currencies.Count.ToString());

        var overflowTurnIn = questTurnIn.TurnIn(
            overflowActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.overflow_rejected_no_partial",
            !overflowTurnIn.Accepted &&
            string.Equals(overflowTurnIn.Failure!.Code, P1ErrorCodes.InvalidPayload, StringComparison.Ordinal) &&
            overflowTurnIn.Failure.FieldErrors.Contains("currencyDeltas", StringComparer.Ordinal),
            overflowTurnIn.Failure?.Code);

        var overflowState = quests.GetState(overflowActor.CharacterId, turnInQuestId);
        Check(
            "turnin.overflow_state_kept",
            overflowState.Accepted &&
            string.Equals(overflowState.State!.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal),
            overflowState.State?.State);

        var overflowInventory = inventory.GetSnapshot(overflowActor.CharacterId);
        Check(
            "turnin.overflow_inventory_unchanged",
            overflowInventory.Currencies.Count == 1 &&
            overflowInventory.Currencies[0].Amount == long.MaxValue - 10 &&
            overflowInventory.Items.Count == 0,
            $"items={overflowInventory.Items.Count} currencies={overflowInventory.Currencies.Count}");

        // ─── concurrency: parallel turn-ins must grant exactly once ───

        var parallelActor = NewPlayer("CHR_SELFCHECK_PARALLEL");
        quests.Accept(parallelActor, turnInQuestId);
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                parallelActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        parallelActor.X = turnInAnchor.X;
        parallelActor.Y = turnInAnchor.Y;

        var parallelOutcomes = new TurnInOutcome[2];
        RunBarrierParallel(2, index =>
        {
            parallelOutcomes[index] = questTurnIn.TurnIn(
                parallelActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        });

        var parallelAccepted = parallelOutcomes.Count(outcome => outcome.Accepted);
        var parallelInvalid = parallelOutcomes.Count(outcome =>
            !outcome.Accepted &&
            string.Equals(outcome.Failure?.Code, QuestErrorCodes.InvalidTransition, StringComparison.Ordinal));
        Check(
            "turnin.parallel_exactly_one_win",
            parallelAccepted == 1 && parallelInvalid == 1,
            $"accepted={parallelAccepted} invalid={parallelInvalid} " +
            $"codes={string.Join(",", parallelOutcomes.Select(o => o.Failure?.Code ?? "ok"))}");

        var parallelInventory = inventory.GetSnapshot(parallelActor.CharacterId);
        Check(
            "turnin.parallel_single_reward",
            parallelInventory.Currencies.Count == 1 &&
            parallelInventory.Currencies[0].Amount == 20 &&
            parallelInventory.Items.Count == 1,
            $"items={parallelInventory.Items.Count} currencies={parallelInventory.Currencies.Count}");

        // same key in parallel: contention must never double-grant; both threads
        // either replay the stored result or one gets invalid_transition.
        var replayActor = NewPlayer("CHR_SELFCHECK_PARALLEL_REPLAY");
        quests.Accept(replayActor, turnInQuestId);
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                replayActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        replayActor.X = turnInAnchor.X;
        replayActor.Y = turnInAnchor.Y;

        var sameKey = Guid.NewGuid().ToString("N");
        var sameKeyOutcomes = new TurnInOutcome[2];
        RunBarrierParallel(2, index =>
        {
            sameKeyOutcomes[index] = questTurnIn.TurnIn(
                replayActor, turnInQuestId, "NPC_TA_VAN_KHANH", sameKey);
        });

        var sameKeyAccepted = sameKeyOutcomes.Count(outcome => outcome.Accepted);
        var sameKeyRevisions = sameKeyOutcomes
            .Where(outcome => outcome.Accepted)
            .Select(outcome => outcome.Result!.QuestState.Revision)
            .Distinct()
            .Count();
        Check(
            "turnin.parallel_same_key_contention",
            sameKeyAccepted == 2 && sameKeyRevisions == 1,
            $"accepted={sameKeyAccepted} distinctRevisions={sameKeyRevisions} " +
            $"codes={string.Join(",", sameKeyOutcomes.Select(o => o.Failure?.Code ?? "ok"))}");

        var sameKeyInventory = inventory.GetSnapshot(replayActor.CharacterId);
        Check(
            "turnin.parallel_same_key_single_reward",
            sameKeyInventory.Currencies.Count == 1 &&
            sameKeyInventory.Currencies[0].Amount == 20 &&
            sameKeyInventory.Items.Count == 1,
            $"items={sameKeyInventory.Items.Count} currencies={sameKeyInventory.Currencies.Count}");

        var teleportActor = NewPlayer("CHR_SELFCHECK_TELEPORT");
        var badMapShape = teleport.Teleport(
            teleportActor,
            new TeleportCommand("BEN_MUA", options.SpawnX, options.SpawnY, TeleportReasons.Quest));
        Check(
            "teleport.invalid_map_payload",
            badMapShape.ErrorCode == P1ErrorCodes.InvalidPayload,
            badMapShape.ErrorCode);

        var unknownMap = teleport.Teleport(
            teleportActor,
            new TeleportCommand("MAP_SELFCHECK_UNKNOWN", options.SpawnX, options.SpawnY, TeleportReasons.Quest));
        Check(
            "teleport.unknown_map",
            unknownMap.ErrorCode == TeleportErrorCodes.InvalidMap,
            unknownMap.ErrorCode);

        maps.TryResolve(options.DefaultMapId, out var bounds);
        var outside = teleport.Teleport(
            teleportActor,
            new TeleportCommand(options.DefaultMapId, bounds.XMax + 10, options.SpawnY, TeleportReasons.Quest));
        Check(
            "teleport.out_of_bounds",
            outside.ErrorCode == TeleportErrorCodes.OutOfBounds,
            outside.ErrorCode);

        var badReason = teleport.Teleport(
            teleportActor,
            new TeleportCommand(options.DefaultMapId, options.SpawnX, options.SpawnY, "NOWHERE"));
        Check(
            "teleport.invalid_reason",
            badReason.ErrorCode == TeleportErrorCodes.InvalidReason,
            badReason.ErrorCode);

        var prematureRespawn = teleport.Teleport(
            teleportActor,
            new TeleportCommand(options.DefaultMapId, options.SpawnX, options.SpawnY, TeleportReasons.DeathReturn));
        Check(
            "teleport.death_return_requires_death",
            prematureRespawn.ErrorCode == TeleportErrorCodes.InvalidCondition,
            prematureRespawn.ErrorCode);

        var moved = teleport.Teleport(
            teleportActor,
            new TeleportCommand(options.DefaultMapId, 10, 5, TeleportReasons.Quest));
        Check(
            "teleport.success",
            moved.IsSuccess &&
            teleportActor.X == 10 &&
            teleportActor.Y == 5 &&
            moved.Snapshot!.Revision == 2,
            moved.ErrorCode ?? $"x={teleportActor.X} revision={moved.Snapshot?.Revision}");

        var defeated = NewPlayer("CHR_SELFCHECK_DEFEATED", hp: 0);
        var respawn = teleport.Teleport(
            defeated,
            new TeleportCommand(options.DefaultMapId, options.SpawnX, options.SpawnY, TeleportReasons.DeathReturn));
        Check(
            "teleport.death_return",
            respawn.IsSuccess && respawn.Snapshot!.Self.Hp == 0,
            respawn.ErrorCode);

        var failures = results.Count(result => !result.Passed);
        foreach (var (name, passed, detail) in results)
        {
            if (passed)
            {
                logger.LogInformation("PASS {Check}", name);
            }
            else
            {
                logger.LogError("FAIL {Check}: {Detail}", name, detail);
            }
        }

        logger.LogInformation(
            "Service self-check: {Passed} passed, {Failed} failed, {Total} total.",
            results.Count - failures,
            failures,
            results.Count);

        return failures == 0 ? 0 : 1;
    }

    private sealed class FixedYieldRoller : IYieldRoller
    {
        private readonly int _value;

        public FixedYieldRoller(int value)
        {
            _value = value;
        }

        public int Roll(int minInclusive, int maxInclusive) => _value;
    }

    private sealed class FailOnceInventoryDecorator : IInventoryService
    {
        private readonly IInventoryService _inner;
        private bool _failed;

        public FailOnceInventoryDecorator(IInventoryService inner)
        {
            _inner = inner;
        }

        public InventorySnapshot GetSnapshot(string characterId) =>
            _inner.GetSnapshot(characterId);

        public InventoryOutcome Apply(PlayerSession actor, InventoryMutation? mutation)
        {
            if (!_failed)
            {
                _failed = true;
                return InventoryOutcome.Rejected(
                    InventoryErrorCodes.SlotOccupied, retryable: true, "rewards");
            }

            return _inner.Apply(actor, mutation);
        }
    }

    private sealed class FailOnceQuestDecorator : IQuestService
    {
        private readonly IQuestService _inner;
        private bool _failed;

        public FailOnceQuestDecorator(IQuestService inner)
        {
            _inner = inner;
        }

        public QuestOutcome GetState(string characterId, string questId) =>
            _inner.GetState(characterId, questId);

        public IReadOnlyList<QuestState> GetStates(string characterId) =>
            _inner.GetStates(characterId);

        public QuestOutcome Accept(PlayerSession actor, string questId) =>
            _inner.Accept(actor, questId);

        public IReadOnlyList<QuestState> RecordVerifiedEvent(
            PlayerSession actor,
            string eventId,
            string eventType,
            string recordId,
            string mapId) =>
            _inner.RecordVerifiedEvent(actor, eventId, eventType, recordId, mapId);

        public QuestOutcome TurnIn(PlayerSession actor, string questId)
        {
            if (!_failed)
            {
                _failed = true;
                return QuestOutcome.Rejected(
                    QuestErrorCodes.InvalidTransition, retryable: false, "state");
            }

            return _inner.TurnIn(actor, questId);
        }

        public QuestOutcome RevertTurnIn(PlayerSession actor, string questId) =>
            _inner.RevertTurnIn(actor, questId);

        public QuestOutcome Fail(PlayerSession actor, string questId) =>
            _inner.Fail(actor, questId);
    }

    private sealed class RecordingQuestService : IQuestService
    {
        public List<RecordedEvent> Events { get; } = [];

        public QuestOutcome GetState(string characterId, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");

        public IReadOnlyList<QuestState> GetStates(string characterId) => [];

        public QuestOutcome Accept(PlayerSession actor, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");

        public IReadOnlyList<QuestState> RecordVerifiedEvent(
            PlayerSession actor,
            string eventId,
            string eventType,
            string recordId,
            string mapId)
        {
            Events.Add(new RecordedEvent(recordId, eventType, mapId));
            return [];
        }

        public QuestOutcome TurnIn(PlayerSession actor, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");

        public QuestOutcome RevertTurnIn(PlayerSession actor, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");

        public QuestOutcome Fail(PlayerSession actor, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");

        public sealed record RecordedEvent(string RecordId, string EventType, string MapId);
    }

    private sealed class EscortQuestStub : IQuestService
    {
        private readonly Dictionary<string, string> _states = new(StringComparer.Ordinal);

        public void Set(string characterId, string state) => _states[characterId] = state;

        public QuestOutcome GetState(string characterId, string questId) =>
            _states.TryGetValue(characterId, out var state)
                ? QuestOutcome.Success(new QuestState
                {
                    QuestId = questId,
                    State = state,
                    StepId = "STEP_ACTIVE",
                    ObjectiveCounters = new Dictionary<string, int>(),
                    Revision = 1
                })
                : QuestOutcome.Rejected(QuestErrorCodes.QuestNotFound, retryable: false, "stub");

        public IReadOnlyList<QuestState> GetStates(string characterId) => [];

        public QuestOutcome Accept(PlayerSession actor, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");

        public IReadOnlyList<QuestState> RecordVerifiedEvent(
            PlayerSession actor,
            string eventId,
            string eventType,
            string recordId,
            string mapId) => [];

        public QuestOutcome TurnIn(PlayerSession actor, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");

        public QuestOutcome RevertTurnIn(PlayerSession actor, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");

        public QuestOutcome Fail(PlayerSession actor, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");
    }

    // The boss encounter only reads quest state, and its trial-visibility rule
    // also reads the fragment objective's counter, so the stub carries both. The
    // cast integration asserts kill credit through it, so it also records events.
    // Records what the tick engine reports as a resolved kill, so the
    // notification itself can be pinned (one per death, the right life, the same
    // event id the combat stream carries).
    private sealed class RecordingKillSink : ICombatKillSink
    {
        public List<CombatMobKill> Kills { get; } = [];

        public void OnMobKilled(CombatMobKill kill) => Kills.Add(kill);
    }

    private sealed class BossEncounterQuestStub : IQuestService
    {
        private readonly Dictionary<string, string> _states = new(StringComparer.Ordinal);
        private readonly Dictionary<string, int> _fragments = new(StringComparer.Ordinal);
        public List<(string EventType, string RecordId)> VerifiedEvents { get; } = [];

        public void Set(string characterId, string state, int fragment = 0)
        {
            _states[characterId] = state;
            _fragments[characterId] = fragment;
        }

        public QuestOutcome GetState(string characterId, string questId) =>
            _states.TryGetValue(characterId, out var state)
                ? QuestOutcome.Success(new QuestState
                {
                    QuestId = questId,
                    State = state,
                    StepId = "STEP_ACTIVE",
                    ObjectiveCounters = new Dictionary<string, int>
                    {
                        ["OBJ_P00_05_FRAGMENT"] = _fragments.TryGetValue(characterId, out var f) ? f : 0
                    },
                    Revision = 1
                })
                : QuestOutcome.Rejected(QuestErrorCodes.QuestNotFound, retryable: false, "stub");

        public IReadOnlyList<QuestState> GetStates(string characterId) => [];

        public QuestOutcome Accept(PlayerSession actor, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");

        public IReadOnlyList<QuestState> RecordVerifiedEvent(
            PlayerSession actor,
            string eventId,
            string eventType,
            string recordId,
            string mapId)
        {
            VerifiedEvents.Add((eventType, recordId));
            return [];
        }

        public QuestOutcome TurnIn(PlayerSession actor, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");

        public QuestOutcome RevertTurnIn(PlayerSession actor, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");

        public QuestOutcome Fail(PlayerSession actor, string questId) =>
            QuestOutcome.Rejected(QuestErrorCodes.InvalidTransition, retryable: false, "stub");
    }

    private sealed class FailOnceLedgerStore : RewardLedgerStore
    {
        private bool _failed;

        public override bool TryRecord(string characterId, string questId, TurnInResult result)
        {
            if (!_failed)
            {
                _failed = true;
                return false;
            }

            return base.TryRecord(characterId, questId, result);
        }
    }

    private sealed class ChanceThenSelectionRolls : ILootRollSource
    {
        private readonly double _chance;
        private readonly double _selection;

        public ChanceThenSelectionRolls(double chance, double selection)
        {
            _chance = chance;
            _selection = selection;
        }

        public double Uniform01(string seed) =>
            seed.Contains("|chance", StringComparison.Ordinal) ? _chance : _selection;
    }

    private sealed class FixedLootRolls : ILootRollSource
    {
        private readonly double _value;

        public FixedLootRolls(double value)
        {
            _value = value;
        }

        public double Uniform01(string seed) => _value;
    }

    private sealed class FixedCombatRolls : ICombatRollSource
    {
        private readonly bool _hit;
        private readonly bool _crit;

        public FixedCombatRolls(bool hit, bool crit)
        {
            _hit = hit;
            _crit = crit;
        }

        public bool Roll(
            string castId, string targetId, int hitIndex, CombatRollKind kind, double probability) =>
            kind == CombatRollKind.Crit ? _crit : _hit;
    }

    private sealed class FixedQuestXpRule : IQuestXpRule
    {
        private readonly long _amount;

        public FixedQuestXpRule(long amount) => _amount = amount;

        public long? Resolve(QuestXpRequest request) => _amount;
    }

    private static void RunBarrierParallel(int count, Action<int> body)
    {
        using var barrier = new Barrier(count);
        var threads = new Thread[count];
        for (var index = 0; index < count; index++)
        {
            var captured = index;
            threads[index] = new Thread(() =>
            {
                barrier.SignalAndWait();
                body(captured);
            });
            threads[index].Start();
        }

        foreach (var thread in threads)
        {
            thread.Join();
        }
    }
}
