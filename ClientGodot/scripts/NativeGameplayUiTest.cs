#nullable enable
using Godot;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace Ngumach.VisualReboot;

/// <summary>Native UI acceptance for an ordinary real network session.
/// Drives actual visible/enabled Godot buttons through their Pressed signal.
/// This is UI-signal injection, not a physical mouse/pointer or hardware-input test.
/// No HTTP shortcut, local grant, teleport, private store access, or fake quest state.</summary>
public partial class NativeGameplayUiTest : Node
{
    private const string QuestId="P00-01";
    private const string CounterId="OBJ_P00_01_PACKAGES";
    private const string CoatId="EQ-MK-CHEST-T1-R-COMMON";
    private const int TotalTimeoutSeconds=75;
    private readonly CancellationTokenSource _lifetime=new();
    private CancellationToken _token;
    private readonly Stopwatch _clock=new();
    private NativeOnlineSession _session=null!;
    private NativeDialoguePanel _panel=null!;
    private Action _interact=null!,_openInventory=null!;
    private Action<int> _passed=null!;
    private Action<string> _failed=null!;
    private bool _configured,_started,_exiting;
    private int _assertions;
    private string _stage="configure";
    private string[] _offer=Array.Empty<string>(),_turnIn=Array.Empty<string>(),_committed=Array.Empty<string>();
    private (string Label,string Text)[] _replies=Array.Empty<(string,string)>();
    private readonly Dictionary<string,string> _itemNames=new(StringComparer.Ordinal);

    /// <summary>The host must suppress its normal keyboard SetMove updates while
    /// this test owns movement. Its launcher must supply a clean loopback server
    /// with scenario=false and the normal P00-01 public routes enabled.</summary>
    public void Configure(NativeOnlineSession session,NativeDialoguePanel panel,Action interact,
        Action openInventory,Action<int> passed,Action<string> failed)
    {
        if(_started)throw new InvalidOperationException("The native UI test is already running.");
        _session=session??throw new ArgumentNullException(nameof(session));
        _panel=panel??throw new ArgumentNullException(nameof(panel));
        _interact=interact??throw new ArgumentNullException(nameof(interact));
        _openInventory=openInventory??throw new ArgumentNullException(nameof(openInventory));
        _passed=passed??throw new ArgumentNullException(nameof(passed));
        _failed=failed??throw new ArgumentNullException(nameof(failed));
        _configured=true;TryStart();
    }

    public override void _Ready()=>TryStart();
    private void TryStart()
    {
        if(!_configured||_started||!IsNodeReady())return;
        _started=true;_token=_lifetime.Token;_clock.Start();
        _=RunAsync();
    }

    private async Task RunAsync()
    {
        try
        {
            GD.Print("NATIVE_UI_INPUT_MODE GODOT_BUTTON_SIGNAL_NOT_PHYSICAL_POINTER");
            LoadExpectedSource();
            Stage("wait_for_real_session");
            await WaitFor(()=>_session.Frame.ConnectionState==P1ConnectionState.Ready&&
                _session.Frame.World!=null&&_session.Frame.Inventory!=null&&CurrentQuest()!=null,20);
            Check(_session.Frame.World!.mapId=="MAP_BEN_MUA","server map is Bến Mưa");
            Check(_session.Frame.World.self.classId=="CLASS_MINH_KIEM","supported class is Minh Kiếm");
            Check(CurrentQuest()!.state=="AVAILABLE","fresh quest is AVAILABLE");
            Check(Coins()==0&&Coats()==0,"fresh character has no pre-granted reward");
            Check(Math.Abs(Self().X-18)<.05&&Math.Abs(Self().Y)<.05,"fresh authoritative spawn is (18,0)");
            Stage("journal_before_accept");
            await PressJournalKey();
            Check(VisibleText().Contains("Nhật ký · Bến Mưa",StringComparison.Ordinal),"J opens actual journal");
            Check(VisibleText().Contains("Có thể nhận",StringComparison.Ordinal),"journal shows server AVAILABLE state");
            Check(CurrentQuest()!.state=="AVAILABLE"&&Coins()==0&&Coats()==0,"journal reading grants nothing");
            await Press("×");

            Stage("inventory_before_reward");
            _session.SetMove(Vector2.Zero);
            _openInventory();
            await WaitFor(()=>_panel.IsOpen&&VisibleText().Contains("Túi đồ",StringComparison.Ordinal),5);
            Check(Coins()==0&&Coats()==0,"opening inventory does not grant a reward");
            Check(VisibleText().Contains("Túi đồ đang trống.",StringComparison.Ordinal),"empty inventory is rendered");
            await Press("×");
            Check(!_panel.IsOpen,"close button dismisses modal");

            // Stand safely on the NPC side of the parcel/NPC nearest-target boundary.
            // At x39.5 the .6 arrival tolerance could stop below the midpoint x39.
            await WalkTo(40);
            Stage("read_offer_without_accepting");
            _interact();
            await WaitFor(()=>_panel.IsOpen,5);
            await Frames(2);
            await ReadPagesWithoutMutation(_offer,"Nhận nhiệm vụ","AVAILABLE");
            foreach(var reply in _replies)
            {
                await Press(reply.Label);
                Check(VisibleBodyEquals(reply.Text),"optional reply uses the authored text");
                Check(CurrentQuest()!.state=="AVAILABLE","optional reply does not accept");
                await Press("Trở lại");
                Check(VisibleBodyEquals(_offer[^1]),"reply returns to the same final offer page");
            }
            Check(CurrentQuest()!.state=="AVAILABLE","all four offer pages still leave quest unaccepted");
            await Press("Nhận nhiệm vụ");
            await WaitFor(()=>CurrentQuest()?.state=="ACTIVE",10);
            Check(CurrentQuest()!.state=="ACTIVE","explicit final-page action is accepted by server");
            await Press("×");
            Check(!_panel.IsOpen,"dialog closes after accept");

            int expected=0;
            foreach(double x in new[]{36d,44d,52d})
            {
                await WalkTo(x);
                Stage("collect_parcel_"+(++expected));
                int before=Counter();
                Check(before==expected-1,"parcel counter starts at expected authoritative value");
                _interact();
                int targetCount=expected;
                await WaitFor(()=>Counter()==targetCount,10);
                Check(Counter()==targetCount,"root interaction credits one parcel through server");
                Check(!_panel.IsOpen,"parcel interaction does not open an NPC dialog");
            }
            Check(Counter()==3,"all three parcels are credited");

            await WalkTo(61.5);
            Stage("read_turnin_without_grant");
            _interact();
            await WaitFor(()=>_panel.IsOpen,5);
            await Frames(2);
            Check(CurrentQuest()?.state=="READY_TO_TURN_IN","server marks quest ready to turn in");
            await ReadPagesWithoutMutation(_turnIn,"Xác nhận giao nhận","READY_TO_TURN_IN");
            Check(Coins()==0&&Coats()==0,"reading the complete turn-in scene does not grant");
            await Press("Xác nhận giao nhận");
            await WaitFor(()=>CurrentQuest()?.state=="COMPLETED"&&Coins()==20&&Coats()==1,10);
            Check(CurrentQuest()!.state=="COMPLETED","explicit hand-in commits server quest");
            Check(Coins()==20,"fresh inventory contains exactly 20 COIN");
            Check(Coats()==1,"fresh inventory contains exactly one canonical coat");

            Stage("read_committed_pages");
            await WaitFor(()=>VisibleBodyEquals(_committed[0]),5);
            Check(VisibleBodyEquals(_committed[0]),"first committed page appears after server completion");
            for(int i=1;i<_committed.Length;i++)
            {
                await Press("Tiếp");
                Check(VisibleBodyEquals(_committed[i]),"committed page "+(i+1)+" uses source");
            }
            Check(VisibleButton("Xác nhận giao nhận")==null,"committed pages offer no duplicate grant action");
            Check(Coins()==20&&Coats()==1,"committed page navigation leaves reward unchanged");
            await Press("Rời đi");
            Check(!_panel.IsOpen,"leave button dismisses committed dialog");
            await CaptureWorldIfRequested();
            Stage("journal_after_completion");
            await PressJournalKey();
            Check(VisibleText().Contains("Đã hoàn thành",StringComparison.Ordinal),"journal shows real completion");
            Check(VisibleText().Contains("Kiện hàng: 3 / 3",StringComparison.Ordinal),"journal shows server counters with sourced totals");
            Check(VisibleText().Contains(_committed[0][..Math.Min(80,_committed[0].Length)],StringComparison.Ordinal),"completed journal uses committed story, not unfinished objective hint");
            Check(Coins()==20&&Coats()==1,"reading completed journal does not repeat reward");
            await CaptureWorldIfRequested("native_ui_p00_01_journal.png");
            await Press("×");

            Stage("inventory_after_reward");
            _openInventory();
            await WaitFor(()=>_panel.IsOpen&&VisibleText().Contains(ItemName(CoatId),StringComparison.Ordinal),5);
            string text=Normalize(VisibleText());
            Check(text.Contains("Túi đồ",StringComparison.Ordinal),"inventory title is visible");
            Check(text.Contains(Normalize("Đồng 20"),StringComparison.Ordinal),"actual currency amount is rendered with localized label");
            Check(text.Contains(ItemName(CoatId),StringComparison.Ordinal)&&text.Contains("×1",StringComparison.Ordinal),
                "localized actual coat row and stack are rendered");
            Check(_session.Frame.Inventory!.items.Count(i=>i.templateId==CoatId)==1,"actual server inventory has one coat instance");
            Check(Coins()==20&&Coats()==1,"opening inventory does not duplicate grant");
            _session.SetMove(Vector2.Zero);
            if(OS.GetCmdlineUserArgs().Contains("--motion-online-test",StringComparer.Ordinal))
            {
                Stage("native_pointer_guard_and_feedback");await Press("×");
                var hud=Descendants(GetTree().Root).OfType<PreviewHud>().Single();
                async Task Click(int slot)
                {
                    var position=PreviewHud.SkillCenters()[slot];
                    GetViewport().PushInput(new InputEventMouseButton{ButtonIndex=MouseButton.Left,Position=position,Pressed=true},true);await Frames(1);
                    GetViewport().PushInput(new InputEventMouseButton{ButtonIndex=MouseButton.Left,Position=position,Pressed=false},true);await Frames(1);
                }
                await Click(0);
                await WaitFor(()=>_session.Frame.CooldownEnds.ContainsKey("SK-MK-01")&&_session.Frame.World!.self.mp==38,10);
                Check(_session.Frame.World!.self.mp==38,"real guard pointer action consumes12MP once");
                Check(hud.Cooldown(0)>0,"HUD binds actual server cooldown");
                Check(!hud.CombatHint.Contains("Không",StringComparison.Ordinal),"self skill with no target is accepted");
                await CaptureWorldIfRequested("native_combat_guard.png");
                string cooldown=_session.Frame.CooldownEnds["SK-MK-01"];
                await Click(0);await Frames(4);
                Check(_session.Frame.World!.self.mp==38&&_session.Frame.CooldownEnds["SK-MK-01"]==cooldown,"cooldown pointer press grants no second cast");
                Check(hud.CombatHint.Contains("Đang hồi",StringComparison.Ordinal),"cooldown rejection is visible immediately");
                await Click(5);
                Check(hud.CombatHint.Contains("chưa được mở",StringComparison.Ordinal),"unsupported skill has explicit feedback: "+hud.CombatHint);
                Check(Coins()==20&&Coats()==1,"combat feedback leaves authoritative quest rewards unchanged");
                _openInventory();await Frames(2);
                GD.Print("NATIVE_MOTION_COMBAT PASS pointer_event_injection=true");
            }
            GD.Print("NATIVE_UI_P00_01_PASS assertions="+_assertions);
            _passed(_assertions);
        }
        catch(OperationCanceledException) when(_exiting||_token.IsCancellationRequested){}
        catch(Exception ex)
        {
            _session?.SetMove(Vector2.Zero);
            string error=_stage+": "+ex.Message+" | "+Diagnostic();
            GD.PushError("NATIVE_UI_P00_01_FAIL "+error);
            try{_failed(error);}catch(Exception callback){GD.PushError("Native UI failure callback: "+callback);}
        }
    }

    private void LoadExpectedSource()
    {
        using var doc=JsonDocument.Parse(FileAccess.GetFileAsString(
            "res://assets/combat_v1/dialogue_vi.json").TrimStart('\uFEFF'));
        var entries=doc.RootElement.GetProperty("entries").EnumerateArray().ToArray();
        var offer=entries.Single(e=>e.GetProperty("nodeId").GetString()=="DLG_P00_01_OFFER");
        var turnin=entries.Single(e=>e.GetProperty("nodeId").GetString()=="DLG_P00_01_TURN_IN");
        _offer=offer.GetProperty("pages").EnumerateArray().Select(x=>x.GetString()!).ToArray();
        _turnIn=turnin.GetProperty("pages").EnumerateArray().Select(x=>x.GetString()!).ToArray();
        _committed=turnin.GetProperty("committedPages").EnumerateArray().Select(x=>x.GetString()!).ToArray();
        _replies=offer.GetProperty("replies").EnumerateArray().Select(x=>(
            x.GetProperty("label").GetString()!,x.GetProperty("text").GetString()!)).ToArray();
        Check(_offer.Length==4,"source offer contains four complete pages");
        Check(_turnIn.Length==4&&_committed.Length==2,"source turn-in contains four pre-commit and two committed pages");
        Check(_replies.Length==2,"source offer contains two optional replies");
        if(FileAccess.FileExists("res://assets/combat_v1/item_names.json"))
        {
            using var names=JsonDocument.Parse(FileAccess.GetFileAsString(
                "res://assets/combat_v1/item_names.json").TrimStart('\uFEFF'));
            foreach(var item in names.RootElement.EnumerateObject())
                if(item.Value.ValueKind==JsonValueKind.String)_itemNames[item.Name]=item.Value.GetString()!;
        }
    }

    private async Task PressJournalKey()
    {
        Input.ParseInputEvent(new InputEventKey{Keycode=Key.J,PhysicalKeycode=Key.J,Pressed=true});
        await Frames(2);
        Input.ParseInputEvent(new InputEventKey{Keycode=Key.J,PhysicalKeycode=Key.J,Pressed=false});
        await WaitFor(()=>_panel.IsOpen,5);
    }

    private async Task CaptureWorldIfRequested(string filename="native_ui_p00_01_world.png")
    {
        var args=OS.GetCmdlineUserArgs();
        int index=Array.IndexOf(args,"--capture");
        if(index<0||index+1>=args.Length)return;
        var directory=System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(args[index+1]))!;
        string path=System.IO.Path.Combine(directory,filename);
        await Frames(3);
        await ToSignal(RenderingServer.Singleton,RenderingServer.SignalName.FramePostDraw);
        var result=GetViewport().GetTexture().GetImage().SavePng(path);
        if(result!=Error.Ok)throw new InvalidOperationException("Native world capture: "+result);
        GD.Print("NATIVE_UI_WORLD_CAPTURE "+path);
    }

    private async Task ReadPagesWithoutMutation(string[] pages,string finalAction,string expectedState)
    {
        for(int i=0;i<pages.Length;i++)
        {
            Check(VisibleBodyEquals(pages[i]),"visible authored page "+(i+1)+" / "+pages.Length);
            Check(CurrentQuest()?.state==expectedState,"page reading preserves authoritative quest state");
            Check(Coins()==0&&Coats()==0,"page reading has no reward side effect");
            if(i<pages.Length-1)
            {
                Check(VisibleButton(finalAction)==null,"final mutation action is not offered before last page");
                await Press("Tiếp");
            }
        }
        await WaitFor(()=>VisibleButton(finalAction) is Button b&&!b.Disabled,5);
        Check(VisibleButton(finalAction)!=null,"explicit final-page action is available");
    }

    private async Task WalkTo(double x)
    {
        if(_panel.IsOpen)throw new InvalidOperationException("A previous modal is still open before movement.");
        Stage("walk_to_"+x.ToString("0.#",System.Globalization.CultureInfo.InvariantCulture));
        try
        {
            await WaitFor(()=>
            {
                var p=Self();
                double dx=x-p.X,dy=-p.Y;
                if(dx*dx+dy*dy<=.36){_session.SetMove(Vector2.Zero);return true;}
                var direction=new Vector2((float)Math.Clamp(dx/1.2,-1,1),(float)Math.Clamp(dy/1.2,-1,1));
                if(direction.LengthSquared()>1)direction=direction.Normalized();
                _session.SetMove(direction);
                return false;
            },20);
        }
        finally{_session.SetMove(Vector2.Zero);}
        await Frames(3);
        var self=Self();
        Check(Math.Abs(self.X-x)<=.9&&Math.Abs(self.Y)<=.6,"arrived near canonical ("+x+",0) without teleport");
        await WaitFor(()=>_session.Frame.ConnectionState==P1ConnectionState.Ready,5);
    }

    private async Task Press(string text)
    {
        await WaitFor(()=>VisibleButton(text) is Button b&&!b.Disabled,5);
        var button=VisibleButton(text)!;
        var rect=button.GetGlobalRect();
        Check(rect.Size.X>0&&rect.Size.Y>0&&GetViewport().GetVisibleRect().Encloses(rect),
            "button is laid out inside viewport: "+text);
        Check(!button.Disabled,"button is enabled: "+text);
        // Invoke the real engine signal and its connected production UI handler.
        // No direct call to panel navigation/private methods and no mutation fixture.
        button.EmitSignal(Button.SignalName.Pressed);
        await Frames(2);
    }

    private static IEnumerable<Node> Descendants(Node root)
    {
        foreach(var child in root.GetChildren())
        {
            yield return child;
            foreach(var nested in Descendants(child))yield return nested;
        }
    }
    private Button? VisibleButton(string text)=>Descendants(_panel).OfType<Button>()
        .FirstOrDefault(b=>b.IsVisibleInTree()&&b.Text==text);
    private bool VisibleBodyEquals(string text)=>Descendants(_panel).OfType<RichTextLabel>()
        .Any(label=>label.IsVisibleInTree()&&label.Text==text);
    private string VisibleText()=>string.Join("\n",Descendants(_panel).OfType<Control>()
        .Where(c=>c.IsVisibleInTree()).Select(c=>c switch{Label l=>l.Text,RichTextLabel r=>r.Text,_=>""}));
    private static string Normalize(string text)=>Regex.Replace(text,@"\s+"," ").Trim();
    private string ItemName(string id)
    {
        if(_itemNames.TryGetValue(id,out var name))return name;
        int variant=id.IndexOf("-R-",StringComparison.Ordinal);
        if(variant>0&&_itemNames.TryGetValue(id[..variant],out name))return name;
        return id;
    }
    private P1Quest? CurrentQuest()=>_session.Frame.Quests.FirstOrDefault(q=>q.questId==QuestId);
    private int Counter()
    {
        var quest=CurrentQuest();
        return quest!=null&&quest.objectiveCounters.TryGetValue(CounterId,out var value)?value:0;
    }
    private long Coins()=>_session.Frame.Inventory?.currencies.Where(c=>c.currencyId=="COIN").Sum(c=>c.amount)??0;
    private int Coats()=>_session.Frame.Inventory?.items.Where(i=>i.templateId==CoatId).Sum(i=>i.stack)??0;
    private Vector2 Self()
    {
        var self=_session.Frame.World?.self??_session.Frame.WorldV2?.self;
        return self==null?new Vector2(float.NaN,float.NaN):new Vector2((float)self.x,(float)self.y);
    }

    private async Task WaitFor(Func<bool> condition,int stageSeconds)
    {
        long deadline=Math.Min(_clock.ElapsedMilliseconds+stageSeconds*1000L,TotalTimeoutSeconds*1000L);
        while(!condition())
        {
            _token.ThrowIfCancellationRequested();
            if(_clock.ElapsedMilliseconds>deadline)throw new TimeoutException("Timed out waiting for "+_stage);
            await ToSignal(GetTree(),SceneTree.SignalName.PhysicsFrame);
        }
    }
    private async Task Frames(int count)
    {
        for(int i=0;i<count;i++)
        {
            _token.ThrowIfCancellationRequested();
            if(_clock.ElapsedMilliseconds>TotalTimeoutSeconds*1000L)throw new TimeoutException("Native UI total deadline exceeded.");
            await ToSignal(GetTree(),SceneTree.SignalName.PhysicsFrame);
        }
    }
    private void Check(bool condition,string message)
    {
        _assertions++;
        if(!condition)throw new InvalidOperationException("Assertion: "+message);
    }
    private void Stage(string stage){_stage=stage;GD.Print("NATIVE_UI_STAGE "+stage);}
    private string Diagnostic()
    {
        var self=Self();
        return "connection="+_session.Frame.ConnectionState+" quest="+(CurrentQuest()?.state??"missing")+
            " parcels="+Counter()+" self=("+self.X+","+self.Y+") panel="+_panel.IsOpen+
            " message="+_session.Frame.Message;
    }
    public override void _ExitTree(){_exiting=true;_lifetime.Cancel();_session?.SetMove(Vector2.Zero);}
}
