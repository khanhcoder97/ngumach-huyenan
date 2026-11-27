using System;
using NguMach.Client.P1;

internal static class InputGateChecks
{
    public static void Run()
    {
        int assertions = 0;
        void Check(bool ok, string label)
        { assertions++; if (!ok) throw new Exception("Input gate: " + label); }
        var gate = new P1GameplayInputGate();
        Check(!gate.AllowsGameplay, "initial held input cannot leak into a new HUD");
        gate.SetSurface(true, false, false, false);
        gate.ObserveControls(true, true, true);
        Check(gate.AllowsGameplay, "neutral frame arms control");
        gate.ObserveControls(false, false, false);
        Check(gate.AllowsGameplay, "ordinary held movement does not repeatedly disarm");
        gate.SetSurface(true, false, true, false);
        Check(!gate.AllowsGameplay, "journal/bag/audio modal blocks movement and skill input");
        gate.ObserveControls(true, true, true);
        gate.SetSurface(true, false, false, false);
        gate.ObserveControls(false, true, true);
        Check(!gate.AllowsGameplay, "movement held through modal close must be released");
        gate.ObserveControls(true, false, true);
        Check(!gate.AllowsGameplay, "cast hotkey held through modal close must be released");
        gate.ObserveControls(true, true, false);
        Check(!gate.AllowsGameplay, "held touch must also be released");
        gate.ObserveControls(true, true, true);
        Check(gate.AllowsGameplay, "all released after close");
        gate.SetSurface(false, false, false, false);
        Check(!gate.AllowsGameplay, "unfocused application blocks controls");
        gate.SetSurface(true, false, false, false);
        Check(!gate.AllowsGameplay, "regaining focus alone does not replay held controls");
        gate.ObserveControls(true, true, true);
        Check(gate.AllowsGameplay, "focus regained with neutral controls");
        gate.SetSurface(true, true, false, false);
        Check(!gate.AllowsGameplay, "application pause blocks controls");
        gate.SetSurface(true, false, false, true);
        gate.ObserveControls(true, true, true);
        Check(!gate.AllowsGameplay, "editing a slider/text field blocks gameplay shortcuts");
        gate.SetSurface(true, false, false, false);
        gate.ObserveControls(true, true, true);
        Check(gate.AllowsGameplay, "leaving editor can rearm on neutral input");
        gate.Reset();
        Check(!gate.AllowsGameplay, "explicit reset discards presentation input");
        Console.WriteLine("PASS P1 gameplay input policy assertions: " + assertions);
    }
}
