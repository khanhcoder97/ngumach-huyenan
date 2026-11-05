#nullable enable
using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using NguMach.Client.P1;
namespace Ngumach.VisualReboot;

/// <summary>Presentation labels only. Server states/counters decide progress.</summary>
public static class NativeQuestCatalog
{
    public sealed record Objective(string Id,string Label,int Count);
    public sealed record Card(string Id,string Title,string StartNpc,string TurnInNpc,string Offer,string Clue,string Completed,Objective[] Objectives);
    private static Card[]? _all;
    public static IReadOnlyList<Card> All=>_all??=Load();
    private static Card[] Load()
    {
        using var doc=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/combat_v1/quest_catalog.json"));
        string S(JsonElement e,string key)=>e.GetProperty(key).GetString()!;
        return doc.RootElement.GetProperty("quests").EnumerateArray().Select(e=>new Card(
            S(e,"questId"),S(e,"title"),S(e,"startNpc"),S(e,"turnInNpc"),S(e,"offer"),S(e,"clue"),S(e,"completed"),
            e.GetProperty("objectives").EnumerateArray().Select(o=>new Objective(S(o,"objectiveId"),S(o,"label"),o.GetProperty("count").GetInt32())).ToArray())).ToArray();
    }
    public static Card? Find(string id)=>All.FirstOrDefault(c=>c.Id==id);
    public static P1Quest? Tracked(NativeOnlineFrame? frame)=>frame?.Quests.Where(q=>Find(q.questId)!=null)
        .Where(q=>q.state is "READY_TO_TURN_IN" or "ACTIVE" or "AVAILABLE" or "COMPLETED")
        .OrderByDescending(q=>q.state switch{"READY_TO_TURN_IN"=>4,"ACTIVE"=>3,"AVAILABLE"=>2,_=>1})
        .ThenBy(q=>q.state=="COMPLETED"?"":q.questId,StringComparer.Ordinal)
        .ThenByDescending(q=>q.questId,StringComparer.Ordinal).FirstOrDefault();
    public static string StateLabel(string? state)=>state switch{
        "AVAILABLE"=>"Có thể nhận","ACTIVE"=>"Đang thực hiện","READY_TO_TURN_IN"=>"Có thể trả nhiệm vụ",
        "COMPLETED"=>"Đã hoàn thành","FAILED"=>"Chưa thành công","LOCKED"=>"Chưa mở",_=>"Chưa có dữ liệu"};
    public static string Summary(P1Quest? q)
    {
        if(q==null||Find(q.questId) is not Card card)return "Nhấn J để xem nhật ký.";
        return q.state switch{
            "AVAILABLE"=>"Gặp "+card.StartNpc+" để nhận việc.",
            "READY_TO_TURN_IN"=>"Báo lại "+card.TurnInNpc+".",
            "COMPLETED"=>"Đã hoàn thành và nhận thưởng.",
            "ACTIVE"=>Progress(q,card),_=>StateLabel(q.state)};
    }
    private static string Progress(P1Quest q,Card card)
    {
        var obj=card.Objectives.FirstOrDefault(o=>!q.objectiveCounters.TryGetValue(o.Id,out int value)||value<o.Count);
        if(obj==null)return "Theo dõi diễn biến trong nhật ký.";
        q.objectiveCounters.TryGetValue(obj.Id,out int count);
        return obj.Label+": "+count+" / "+obj.Count;
    }
}
