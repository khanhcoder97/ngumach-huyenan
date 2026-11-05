#nullable enable
using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using NguMach.Client.P1;
namespace Ngumach.VisualReboot;

/// <summary>Source/DTO UI test only. No server, grant, or completion simulation.</summary>
public static class QuestPresentationSelfTest
{
    public static async void Run(Node host)
    {
        int checks=0,commands=0;
        void Check(bool ok,string name){checks++;if(!ok)throw new InvalidOperationException(name);}
        async Task Frames(){for(int i=0;i<2;i++)await host.ToSignal(host.GetTree(),SceneTree.SignalName.PhysicsFrame);}
        var panel=new NativeDialoguePanel();host.AddChild(panel);
        IEnumerable<Node> Nodes(Node n){foreach(var child in n.GetChildren()){yield return child;foreach(var sub in Nodes(child))yield return sub;}}
        Button? Button(string text)=>Nodes(panel).OfType<Button>().FirstOrDefault(b=>b.IsVisibleInTree()&&b.Text==text);
        string Text()=>string.Join("\n",Nodes(panel).OfType<Control>().Where(c=>c.IsVisibleInTree()).Select(c=>c switch{Label l=>l.Text,RichTextLabel r=>r.Text,_=>""}));
        try
        {
            GD.Print("QUEST_PRESENTATION_TEST_MODE SOURCE_DTO_UI_ONLY_NO_HTTP_NO_GRANTS");
            var q1=new P1Quest{questId="P00-01",state="COMPLETED",revision=1,stepId="DONE",objectiveCounters=new(){{"OBJ_P00_01_PACKAGES",3}}};
            var q2=new P1Quest{questId="P00-02",state="AVAILABLE",revision=1,stepId="START",objectiveCounters=new(){{"OBJ_P00_02_CARPLING",0}}};
            var q3=new P1Quest{questId="P00-03",state="LOCKED",revision=1,stepId="START",objectiveCounters=new()};
            var frame=new NativeOnlineFrame{SessionId="PRESENTATION_FIXTURE",ConnectionState=P1ConnectionState.Ready,
                World=new P1World{mapId="MAP_BEN_MUA",self=new P1Self{x=62,y=0},entities=new[]{new P1Entity{entityId="ENT_MAN_BM_NPC_TA_VAN_KHANH",kind="NPC",x=64,y=0}}},Quests=new[]{q1,q2,q3}};
            panel.CommandRequested+=(kind,target,quest)=>{commands++;Check(kind=="ACCEPT"&&target=="NPC_TA_VAN_KHANH"&&quest=="P00-02","actual final action binds next quest and NPC");};
            panel.ShowNpc("NPC_TA_VAN_KHANH",frame);await Frames();
            Check(Text().Contains(NativeQuestCatalog.Find("P00-02")!.Title,StringComparison.Ordinal),"available next quest wins over completed predecessor");
            Check(Button("Nhận nhiệm vụ")==null,"accept hidden on first source page");
            int pages=0;
            while(Button("Tiếp") is Button next){next.EmitSignal(Godot.Button.SignalName.Pressed);await Frames();if(++pages>20)throw new InvalidOperationException("page loop");}
            Check(commands==0&&q2.state=="AVAILABLE","reading pages does not accept");
            var accept=Button("Nhận nhiệm vụ");Check(accept!=null&&!accept.Disabled,"next quest final action is ready");
            accept!.EmitSignal(Godot.Button.SignalName.Pressed);await Frames();
            Check(commands==1&&q2.state=="AVAILABLE","UI emits command without changing authoritative DTO");
            accept.EmitSignal(Godot.Button.SignalName.Pressed);await Frames();
            Check(commands==1,"waiting state suppresses duplicate accept");
            q2.state="ACTIVE";q2.revision++;panel.ApplyFrame(frame);await Frames();
            Check(Button("Nhận nhiệm vụ")==null,"server ACTIVE changes panel to clue");
            Check(NativeQuestCatalog.Tracked(frame)?.questId=="P00-02","tracker follows active next quest");
            panel.ShowJournal(frame);await Frames();
            Check(!Text().Contains(NativeQuestCatalog.Find("P00-03")!.Title,StringComparison.Ordinal),"locked future chapter title is hidden");
            Check(Text().Contains("Đã hoàn thành",StringComparison.Ordinal),"journal preserves completed history");
            Check(commands==1,"journal emits no mutation");
            // Read-only menu navigation must not turn a source fixture into gameplay grants.
            foreach(var section in NativeDialoguePanel.Sections)
            {
                panel.ShowMenu(section.Id,frame);await Frames();panel.AuditWorkspaceBounds();
                Check(panel.CurrentSection==section.Id,"menu opens and keeps selected navigation visible: "+section.Id);
            }
            panel.ShowMenu("Character",frame);await Frames();
            var gear=Button("Trang bị");Check(gear!=null,"character equipment tab exists");
            gear!.EmitSignal(Godot.Button.SignalName.Pressed);await Frames();
            Check(Text().Contains("Nhẫn trái",StringComparison.Ordinal)&&Text().Contains("Ngọc bội",StringComparison.Ordinal),"equipment tab has named presentation slots");
            panel.ShowInventory(frame);await Frames();
            var material=Button("Nguyên liệu");Check(material!=null,"bag category filter exists");
            material!.EmitSignal(Godot.Button.SignalName.Pressed);await Frames();
            var search=Nodes(panel).OfType<LineEdit>().First(e=>e.IsVisibleInTree());
            search.EmitSignal(LineEdit.SignalName.TextSubmitted,"không có trong túi");await Frames();
            Check(Text().Contains("0 vật phẩm",StringComparison.Ordinal),"empty filtered bag stays empty");
            Check(commands==1&&q2.state=="ACTIVE"&&frame.Inventory==null,"menu navigation and search emit no gameplay mutation");
            GD.Print("QUEST_PRESENTATION_SELF_TEST PASS assertions="+checks);host.GetTree().Quit();
        }
        catch(Exception ex){GD.PushError("QUEST_PRESENTATION_SELF_TEST FAIL "+ex);host.GetTree().Quit(1);}
    }
}
