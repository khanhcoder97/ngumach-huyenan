using Godot;
using System;
using System.Collections.Generic;
using System.Text.Json;
namespace Ngumach.VisualReboot;

/// <summary>Sixteen authored poses per direction/action. Never expands a four-frame loop by duplication.</summary>
public partial class HeroAnimator : Sprite2D
{
    private sealed record PoseFrame(Texture2D Texture,Rect2 Rect,Vector2 Pivot,bool Flip);
    private sealed record Clip(double Duration,float Height,PoseFrame[] Frames,double Release,Vector2 ReleaseOffset);
    private readonly Dictionary<string,Clip[]> _clips=new();
    private readonly Dictionary<string,Texture2D> _textures=new();
    private int _direction=4,_actionDirection=4;
    private PoseFrame? _shown;
    private bool _moving;
    private string _action="";
    private double _clock,_actionClock;
    private (string Action,int Direction,int PoseFrame)? _review;
    public int DisplayedFrame{get;private set;}
    internal int ActionDirection=>_actionDirection;
    public int AnimationFrameCount=>16;
    public const float BodyHeight=36f;
    public string AssetRoot{get;init;}="res://assets/motion16/";
    public event Action<string,Vector2>? ActionReleased;
    public bool IsAttacking=>_action.Length>0;
    public string CurrentAction=>_review?.Action??(_action.Length>0?_action:_moving?"walk":"idle");
    public override void _Ready()
    {
        RegionEnabled=true;Centered=false;TextureFilter=TextureFilterEnum.Nearest;
        using var json=JsonDocument.Parse(FileAccess.GetFileAsString(AssetRoot+"manifest.json"));
        foreach(var action in json.RootElement.GetProperty("clips").EnumerateObject())
        {
            var directions=new List<Clip>();
            foreach(var clip in action.Value.EnumerateArray())
            {
                var frames=new List<PoseFrame>();
                foreach(var f in clip.GetProperty("frames").EnumerateArray())
                {
                    string file=f.GetProperty("file").GetString()!;
                    if(!_textures.TryGetValue(file,out var texture))
                    {
                        string path=file.StartsWith("res://",StringComparison.Ordinal)?file:AssetRoot+file;
                        texture=GD.Load<Texture2D>(path)??throw new InvalidOperationException("Motion texture unavailable: "+path);
                        _textures[file]=texture;
                    }
                    var r=f.GetProperty("rect");var p=f.GetProperty("pivot");
                    frames.Add(new PoseFrame(texture,new Rect2(r[0].GetSingle(),r[1].GetSingle(),r[2].GetSingle(),r[3].GetSingle()),new Vector2(p[0].GetSingle(),p[1].GetSingle()),f.GetProperty("flip").GetBoolean()));
                }
                if(frames.Count!=16)throw new InvalidOperationException("Motion clip must contain16 authored poses");
                double duration=clip.GetProperty("duration").GetDouble();
                double release=clip.TryGetProperty("release",out var at)?at.GetDouble():-1;
                var offset=clip.TryGetProperty("releaseOffset",out var m)?new Vector2(m[0].GetSingle(),m[1].GetSingle()):Vector2.Zero;
                if(release>=duration)throw new InvalidOperationException("Release time must be inside the motion clip.");
                directions.Add(new Clip(duration,clip.GetProperty("sourceHeight").GetSingle(),frames.ToArray(),release,offset));
            }
            if(directions.Count!=8)throw new InvalidOperationException("Motion clip must cover8directions");
            _clips[action.Name]=directions.ToArray();
        }
        RenderFrame();
    }
    public void SetFacing(int direction)=>_direction=((direction%8)+8)%8;
    public void SetMoving(bool moving){if(moving!=_moving)_clock=0;_moving=moving;}
    private void StartAction(string action)
    {
        if(_action==action&&_actionClock<.32)return;
        _action=action;_actionClock=0;_actionDirection=_direction;RenderFrame();
    }
    public void Attack()=>StartAction("attack");
    public void Cast()=>StartAction("cast");
    public bool TryCast(string action="cast")
    {
        if(IsAttacking||!_clips.ContainsKey(action))return false;
        StartAction(action);
        return true;
    }
    public void ReviewPose(string action,int direction,int frame){_review=(action,direction,frame);RenderFrame();}
    public void ClearReview(){_review=null;_action="";_clock=0;RenderFrame();}
    public override void _Process(double delta)
    {
        if(_review!=null)return;
        _clock+=delta;
        if(_action.Length>0)
        {
            var clip=_clips[_action][_actionDirection];
            var previous=_actionClock;
            _actionClock+=delta;
            if(previous<clip.Release&&_actionClock>=clip.Release)
                ActionReleased?.Invoke(_action,clip.ReleaseOffset*BodyHeight);
            if(_actionClock>=clip.Duration){_action="";if(clip.Release>=0)_clock=0;}
        }
        RenderFrame();
    }
    private void RenderFrame()
    {
        if(_clips.Count==0)return;
        string action=CurrentAction;int direction=_review?.Direction??(_action.Length>0?_actionDirection:_direction);
        var clip=_clips[action][direction];
        int phase=_review?.PoseFrame??(_action.Length>0?Math.Min(15,(int)(_actionClock/clip.Duration*16)):(int)(_clock/clip.Duration*16)%16);
        var frame=clip.Frames[phase];DisplayedFrame=phase;
        if(ReferenceEquals(_shown,frame))return;_shown=frame;
        Texture=frame.Texture;RegionRect=frame.Rect;FlipH=frame.Flip;
        var pivot=frame.Pivot;if(frame.Flip)pivot.X=frame.Rect.Size.X-pivot.X;
        Offset=-pivot;Scale=Vector2.One*(BodyHeight/clip.Height);
    }
}
