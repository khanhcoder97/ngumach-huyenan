using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using static Ngumach.VisualReboot.ModularCharacterModel;

namespace Ngumach.VisualReboot;

/// <summary>Prototype renderer, deliberately not installed on the playable hero.
/// One CanvasItem keeps all avatar layers together under world Y-sort.</summary>
public partial class ModularCharacterRenderer : Node2D
{
    private readonly Session _session=new();
    private Dictionary<string,Texture2D> _textures=new(StringComparer.Ordinal);
    private IReadOnlyList<DrawCommand> _draw=Array.Empty<DrawCommand>();
    private int _lastFrame=-1;
    public Session Animation=>_session;
    public bool PlaybackPaused {get;set;}
    internal Func<string,Texture2D?>? ReviewTextureResolver {get;set;}
    internal bool SeekReviewFrame(int frame){if(!_session.SeekFrame(frame))return false;Refresh();return true;}
    public override void _Ready(){YSortEnabled=false;TextureFilter=TextureFilterEnum.Nearest;}
    public bool TryApply(Look look,out string reason)=>Apply(look,false,out reason);
    internal bool TryApplyForReview(Look look,out string reason)=>Apply(look,true,out reason);
    private bool Apply(Look look,bool reviewMode,out string reason)
    {Dictionary<string,Texture2D>? staged=null;if(!_session.TryApply(look,reviewMode,p=>PrepareTextures(p,out staged),out reason))return false;_textures=staged!;Refresh();return true;}
    public bool TryPlay(string key,bool preservePhase=false)
    {Dictionary<string,Texture2D>? staged=null;if(!_session.TryPlay(key,p=>PrepareTextures(p,out staged),preservePhase))return false;if(staged!=null)_textures=staged;Refresh();return true;}
    private bool PrepareTextures(ClipPlan plan,out Dictionary<string,Texture2D>? prepared)
    {
        prepared=null;
        var commands=plan.Frames.SelectMany(f=>f).ToArray();var paths=commands.Select(c=>c.Texture).Distinct(StringComparer.Ordinal).ToArray();
        if(paths.Length>16)return false; // A clip exceeding the staging budget needs repacking first.
        var next=new Dictionary<string,Texture2D>(StringComparer.Ordinal);long bytes=0;
        foreach(string path in paths)
        {
            bool native=path.StartsWith("master://",StringComparison.Ordinal);
            if(!native&&!FileAccess.FileExists(path))return false;
            var texture=_textures.TryGetValue(path,out var existing)?existing:native?ReviewTextureResolver?.Invoke(path):GD.Load<Texture2D>(path);
            if(texture==null)return false;next.Add(path,texture);bytes+=(long)texture.GetWidth()*texture.GetHeight()*4;
            if(bytes>32L*1024*1024)return false;
        }
        foreach(var c in commands)if(c.Region.X+c.Region.Width>next[c.Texture].GetWidth()||c.Region.Y+c.Region.Height>next[c.Texture].GetHeight())return false;
        prepared=next;return true;
    }
    private void Refresh(){_draw=_session.Commands;_lastFrame=_session.FrameIndex;QueueRedraw();}
    public override void _Process(double delta){if(!PlaybackPaused)_session.Advance(delta);if(_lastFrame!=_session.FrameIndex)Refresh();}
    public override void _Draw()
    {
        foreach(var c in _draw)
        {
            if(!_textures.TryGetValue(c.Texture,out var texture))continue;var t=c.Transform??Identity;
            DrawSetTransform(new Vector2(c.Position.X,c.Position.Y),Mathf.DegToRad((float)t.Degrees),new Vector2((float)t.Scale*(t.FlipH?-1:1),(float)t.Scale*(t.FlipV?-1:1)));
            DrawTextureRectRegion(texture,new Rect2(-(float)t.PivotX,-(float)t.PivotY,(float)c.Region.Width/c.SourcePixelsPerUnit,(float)c.Region.Height/c.SourcePixelsPerUnit),new Rect2(c.Region.X,c.Region.Y,c.Region.Width,c.Region.Height));
        }
        DrawSetTransform(Vector2.Zero,0,Vector2.One);
    }
    // Godot resources may be shared by other avatars. Never Dispose a shared texture here.
    public override void _ExitTree(){_textures.Clear();_draw=Array.Empty<DrawCommand>();}
}
