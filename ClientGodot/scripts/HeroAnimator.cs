using Godot;
using System;
using System.Collections.Generic;
using System.Text.Json;
namespace Ngumach.VisualReboot;

/// <summary>Sixteen authored poses per direction/action. Never expands a four-frame loop by duplication.</summary>
public partial class HeroAnimator : Sprite2D
{
    private sealed record PoseFrame(Texture2D Texture,Rect2 Rect,Vector2 Pivot,bool Flip);
    private sealed record Clip(double Duration,float Height,PoseFrame[] Frames);
    private readonly Dictionary<string,Clip[]> _clips=new();
    private readonly Dictionary<string,Texture2D> _textures=new();
    private int _direction=4,_actionDirection=4;
    private PoseFrame? _shown;
    private bool _moving;
    private string _action="";
    private double _clock,_actionClock;
    private (string Action,int Direction,int PoseFrame)? _review;
    public int DisplayedFrame{get;private set;}
    public int AnimationFrameCount=>16;
    public bool IsAttacking=>_action.Length>0;
    public string CurrentAction=>_review?.Action??(_action.Length>0?_action:_moving?"walk":"idle");
    public override void _Ready()
    {
        RegionEnabled=true;Centered=false;TextureFilter=TextureFilterEnum.Nearest;
        using var json=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/motion16/manifest.json"));
        foreach(var action in json.RootElement.GetProperty("clips").EnumerateObject())
        {
            var directions=new List<Clip>();
            foreach(var clip in action.Value.EnumerateArray())
            {
                var frames=new List<PoseFrame>();
                foreach(var f in clip.GetProperty("frames").EnumerateArray())
                {
                    string file=f.GetProperty("file").GetString()!;
                    if(!_textures.TryGetValue(file,out var texture)){texture=GD.Load<Texture2D>("res://assets/motion16/"+file);_textures[file]=texture;}
                    var r=f.GetProperty("rect");var p=f.GetProperty("pivot");
                    frames.Add(new PoseFrame(texture,new Rect2(r[0].GetSingle(),r[1].GetSingle(),r[2].GetSingle(),r[3].GetSingle()),new Vector2(p[0].GetSingle(),p[1].GetSingle()),f.GetProperty("flip").GetBoolean()));
                }
                if(frames.Count!=16)throw new InvalidOperationException("Motion clip must contain16 authored poses");
                directions.Add(new Clip(clip.GetProperty("duration").GetDouble(),clip.GetProperty("sourceHeight").GetSingle(),frames.ToArray()));
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
    public void ReviewPose(string action,int direction,int frame){_review=(action,direction,frame);RenderFrame();}
    public void ClearReview(){_review=null;_action="";_clock=0;RenderFrame();}
    public override void _Process(double delta)
    {
        if(_review!=null)return;
        _clock+=delta;
        if(_action.Length>0){_actionClock+=delta;if(_actionClock>=_clips[_action][_actionDirection].Duration)_action="";}
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
        Offset=-pivot;Scale=Vector2.One*(36f/clip.Height);
    }
}
