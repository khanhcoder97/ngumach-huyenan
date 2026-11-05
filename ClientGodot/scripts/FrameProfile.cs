using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
namespace Ngumach.VisualReboot;
/// <summary>Native renderer measurement; never changes simulation or camera.</summary>
public partial class FrameProfile : Node
{
    public string OutputPath="";
    public bool Walk;
    public Action? Completed;
    private int _keyDirection=-1;
    private Vector2? _lastPosition;
    private double _distance;
    private double _elapsed,_previous;
    private readonly System.Diagnostics.Stopwatch _wall=System.Diagnostics.Stopwatch.StartNew();
    private readonly List<double> _frames=new(),_cpu=new(),_draws=new();
    public override void _Process(double delta)
    {
        if(Walk){int direction=(int)(_wall.Elapsed.TotalSeconds/2)%2;if(direction!=_keyDirection){Input.ParseInputEvent(new InputEventKey{Keycode=Key.D,PhysicalKeycode=Key.D,Pressed=direction==0});Input.ParseInputEvent(new InputEventKey{Keycode=Key.A,PhysicalKeycode=Key.A,Pressed=direction==1});_keyDirection=direction;}var hero=GetParent().GetNode<CharacterBody2D>("DepthSorted/Hero");if(_lastPosition!=null)_distance+=hero.Position.DistanceTo(_lastPosition.Value);_lastPosition=hero.Position;}
        _elapsed=_wall.Elapsed.TotalSeconds;double frameSeconds=_elapsed-_previous;_previous=_elapsed;if(_elapsed<3)return;
        _frames.Add(frameSeconds*1000);_cpu.Add(Performance.GetMonitor(Performance.Monitor.TimeProcess)*1000);
        _draws.Add(Performance.GetMonitor(Performance.Monitor.RenderTotalDrawCallsInFrame));
        if(_elapsed<15)return;
        var sorted=_frames.OrderBy(x=>x).ToArray();
        var result=new{renderer=RenderingServer.GetVideoAdapterName(),profileWalk=Walk,travelledPixels=_distance,clock="Stopwatch wall time",targetFps=60,engineLimit=Engine.MaxFps,vsync=DisplayServer.WindowGetVsyncMode().ToString(),frames=_frames.Count,seconds=_frames.Sum()/1000,
            averageFps=1000/_frames.Average(),medianMs=sorted[sorted.Length/2],p95Ms=sorted[(int)(sorted.Length*.95)],cpuMs=_cpu.Average(),drawCalls=_draws.Average(),
            textureMiB=Performance.GetMonitor(Performance.Monitor.RenderTextureMemUsed)/1048576,
            nodes=Performance.GetMonitor(Performance.Monitor.ObjectNodeCount)};
        System.IO.File.WriteAllText(OutputPath,JsonSerializer.Serialize(result,new JsonSerializerOptions{WriteIndented=true}));
        GetViewport().GetTexture().GetImage().SavePng(OutputPath+".png");
        GD.Print("FRAME_PROFILE "+JsonSerializer.Serialize(result));SetProcess(false);if(Completed!=null)Completed();else GetTree().Quit();
    }
}
