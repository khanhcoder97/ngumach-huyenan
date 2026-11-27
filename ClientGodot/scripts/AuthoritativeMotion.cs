using Godot;
using System;
using System.Collections.Generic;
namespace Ngumach.VisualReboot;
/// <summary>Interpolates only received positions. No extrapolation or local gameplay authority.</summary>
public sealed class AuthoritativeMotion
{
    private readonly List<(double Time,Vector2 Point)> _samples=new();
    public const double DelaySeconds=.10;
    public static double Now=>System.Diagnostics.Stopwatch.GetTimestamp()/(double)System.Diagnostics.Stopwatch.Frequency;
    public void Clear()=>_samples.Clear();
    public void Push(Vector2 point,double now,bool reset=false)
    {
        if(reset||_samples.Count==0||point.DistanceTo(_samples[^1].Point)>240){_samples.Clear();_samples.Add((now,point));return;}
        if(now<_samples[^1].Time)return;
        if(point.DistanceSquaredTo(_samples[^1].Point)<.0001f)
        {if(now-_samples[^1].Time>.25){_samples.Add((now,point));while(_samples.Count>24)_samples.RemoveAt(0);}return;}
        // Hold the last confirmed position after an idle/network gap, then ease into the new confirmed sample.
        if(now-_samples[^1].Time>DelaySeconds+.05)_samples.Add((now-DelaySeconds,_samples[^1].Point));
        _samples.Add((now,point));while(_samples.Count>24)_samples.RemoveAt(0);
    }
    public Vector2 Sample(double now,Vector2 fallback)
    {
        if(_samples.Count==0)return fallback;
        double at=now-DelaySeconds;
        while(_samples.Count>2&&_samples[1].Time<=at)_samples.RemoveAt(0);
        if(_samples.Count==1||at>=_samples[^1].Time)return _samples[^1].Point;
        var a=_samples[0];var b=_samples[1];
        return a.Point.Lerp(b.Point,(float)Math.Clamp((at-a.Time)/Math.Max(.001,b.Time-a.Time),0,1));
    }
}
