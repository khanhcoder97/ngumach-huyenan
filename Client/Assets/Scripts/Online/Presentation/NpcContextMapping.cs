// NpcContextMapping: maps world entities, records, and templates for dialogue interactions.
// Sources: world_entities_bm.json, QuestDefinition/P00-01.json.
// Pure C#, no Unity dependency.
// Owner: Antigravity Remote — Issue #85.

using System;
using System.Collections.Generic;

namespace NguMach.Client.Presentation
{
    public sealed class NpcContextInfo
    {
        public string EntityId { get; }
        public string RecordId { get; }
        public string TemplateId { get; }
        public string DisplayName { get; }

        public NpcContextInfo(string entityId, string recordId, string templateId, string displayName)
        {
            EntityId = entityId;
            RecordId = recordId;
            TemplateId = templateId;
            DisplayName = displayName;
        }
    }

    public static class NpcContextMapping
    {
        private static readonly Dictionary<string, NpcContextInfo> ByAnyId =
            new Dictionary<string, NpcContextInfo>(StringComparer.OrdinalIgnoreCase);

        static NpcContextMapping()
        {
            Register(new NpcContextInfo("ENT_MAN_BM_NPC_LYAN", "MAN-BM-NPC_LYAN", "NPC_LYAN", "Lý An"));
            Register(new NpcContextInfo("ENT_MAN_BM_NPC_TA_VAN_KHANH", "MAN-BM-NPC_TA_VAN_KHANH", "NPC_TA_VAN_KHANH", "Tạ Vân Khanh"));
            Register(new NpcContextInfo("ENT_MAN_BM_NPC_MEDIC_BEN", "MAN-BM-NPC_MEDIC_BEN", "NPC_MEDIC_BEN", "Thầy Thuốc Bến"));
            Register(new NpcContextInfo("ENT_MAN_BM_NPC_BOAT_KEEPER", "MAN-BM-NPC_BOAT_KEEPER", "NPC_BOAT_KEEPER", "Người Giữ Thuyền"));
            Register(new NpcContextInfo("ENT_MAN_BM_NPC_CLASS_TRIAL", "MAN-BM-NPC_CLASS_TRIAL", "NPC_CLASS_TRIAL", "Người Thử Thách Môn Phái"));
            Register(new NpcContextInfo("ENT_MAN_BM_NPC_FISHER_01", "MAN-BM-NPC_FISHER_01", "NPC_FISHER_01", "Ngư Dân Bến Mưa"));
            Register(new NpcContextInfo("ENT_MAN_BM_NPC_BM_RESCUE_01", "MAN-BM-NPC_BM_RESCUE_01", "NPC_BM_RESCUE_01", "Dân Làng Bến Mưa 1"));
            Register(new NpcContextInfo("ENT_MAN_BM_NPC_BM_RESCUE_02", "MAN-BM-NPC_BM_RESCUE_02", "NPC_BM_RESCUE_02", "Dân Làng Bến Mưa 2"));
        }

        private static void Register(NpcContextInfo info)
        {
            if (!string.IsNullOrEmpty(info.EntityId)) ByAnyId[info.EntityId] = info;
            if (!string.IsNullOrEmpty(info.RecordId)) ByAnyId[info.RecordId] = info;
            if (!string.IsNullOrEmpty(info.TemplateId)) ByAnyId[info.TemplateId] = info;
        }

        public static NpcContextInfo Resolve(string id)
        {
            if (string.IsNullOrEmpty(id)) return null;
            if (ByAnyId.TryGetValue(id, out var info)) return info;

            // Fallback for unregistered IDs: templateId is null to avoid forging canonical identity
            return new NpcContextInfo(id, null, null, id + " (UNRESOLVED — catalog not yet connected)");
        }
    }

    public static class QuestNpcCatalog
    {
        private static readonly Dictionary<string, (string startNpc, string turnInNpc)> Quests =
            new Dictionary<string, (string, string)>(StringComparer.OrdinalIgnoreCase)
            {
                ["P00-01"] = ("NPC_LYAN", "NPC_TA_VAN_KHANH")
            };

        public static bool IsQuestStartNpc(string questId, string npcTemplateId)
        {
            if (string.IsNullOrEmpty(questId) || string.IsNullOrEmpty(npcTemplateId)) return false;
            if (Quests.TryGetValue(questId, out var entry))
            {
                return entry.startNpc.Equals(npcTemplateId, StringComparison.OrdinalIgnoreCase);
            }
            return false;
        }

        public static bool IsQuestTurnInNpc(string questId, string npcTemplateId)
        {
            if (string.IsNullOrEmpty(questId) || string.IsNullOrEmpty(npcTemplateId)) return false;
            if (Quests.TryGetValue(questId, out var entry))
            {
                return entry.turnInNpc.Equals(npcTemplateId, StringComparison.OrdinalIgnoreCase);
            }
            return false;
        }
    }
}
