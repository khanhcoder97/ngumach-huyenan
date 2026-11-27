using System;
using System.Collections.Generic;
using NguMach.Client.P1;

namespace Ngumach.VisualReboot;

/// <summary>Presentation deduplication and scope checks, never combat authority.</summary>
public sealed class CombatEventGate
{
    private (string Session,string Instance,string Floor,string Phase,string Actor)? _scope;
    private long _highest;
    private readonly SortedDictionary<long,string> _cursors=new();
    private readonly HashSet<string> _ids=new(StringComparer.Ordinal);
    public int RetainedCount=>_cursors.Count;
    public bool Bind(NativeOnlineFrame frame)
    {
        var w=frame.WorldV2;
        var next=w==null?((string,string,string,string,string)?)null:(frame.SessionId,w.mapInstanceId,w.floorId,w.phase,w.self.characterId);
        if(_scope==next)return false;
        _scope=next;_highest=0;_cursors.Clear();_ids.Clear();return true;
    }
    public bool Accept(P1EventV2 e)
    {
        if(_scope is not {} scope||e.mapInstanceId!=scope.Instance||e.floorId!=scope.Floor||
            e.cursor<=0||string.IsNullOrEmpty(e.eventId)||e.cursor<=_highest-1024||
            _cursors.ContainsKey(e.cursor)||_ids.Contains(e.eventId))return false;
        _highest=Math.Max(_highest,e.cursor);_cursors.Add(e.cursor,e.eventId);_ids.Add(e.eventId);
        while(_cursors.Count>0)
        {
            using var first=_cursors.GetEnumerator();first.MoveNext();var item=first.Current;
            if(item.Key>_highest-1024)break;
            _ids.Remove(item.Value);_cursors.Remove(item.Key);
        }
        return true;
    }
    public static bool MatchesLife(P1EventV2 e,P1EntityV2? target)=>target!=null&&
        e.targetId==target.entityId&&e.targetLifeId==target.lifeId&&
        e.mapInstanceId==target.mapInstanceId&&e.floorId==target.floorId;
}

public sealed record CombatTargetInfo(string EntityId,long LifeId,string Name,string Kind,
    int Hp,int MaxHp,double Distance,string State);
