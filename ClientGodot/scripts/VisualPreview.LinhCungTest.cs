using Godot;
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;

namespace Ngumach.VisualReboot;

public partial class VisualPreview
{
    private async void RunLinhCungPracticeTests()
    {
        int assertions = 0;
        void Check(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
            assertions++;
        }
        async Task Until(Func<bool> condition, string message)
        {
            for (int frame = 0; frame < 150 && !condition(); frame++)
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Check(condition(), message);
        }
        void KeyPress(Key key) => Input.ParseInputEvent(new InputEventKey { Keycode = key, Pressed = true });
        void Click(Vector2 point) => Input.ParseInputEvent(new InputEventMouseButton
        {
            ButtonIndex = MouseButton.Left, Pressed = true, Position = point, GlobalPosition = point
        });
        async Task Capture(string? phase = null)
        {
            if (_capture == null) return;
            string path = phase == null ? _capture : Path.Combine(Path.GetDirectoryName(_capture) ?? "",
                Path.GetFileNameWithoutExtension(_capture) + "_" + phase + ".png");
            await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
            Check(GetViewport().GetTexture().GetImage().SavePng(path) == Error.Ok, "Native gameplay capture saved.");
        }
        var practice = _practice!;
        var animator = (HeroAnimator)_body;
        try
        {
            await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Check(_online == null && !_camera.Compact && animator.AssetRoot == LinhCungPractice.AssetRoot, "Practice starts locally with the wide gameplay camera.");
            Check(practice.Selected, "The east practice dummy is selected at entry.");
            if (_capture != null)
            {
                _hud.StaticArtReview = true;
                for (int i = 0; i < 12; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            }
            await Capture("ready");
            KeyPress(Key.Key2);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Check(!practice.IsCasting && practice.Releases == 0, "Unavailable skill does not start the animation.");
            Click(PreviewHud.SkillCenters()[0]);
            await Until(() => practice.IsCasting, "The first HUD button starts Khóa Mạch.");
            Check(animator.ActionDirection == 2 && !practice.ArrowVisible && !practice.MarkVisible, "The release and mark wait for the draw.");
            KeyPress(Key.Key1);
            await Until(() => animator.DisplayedFrame == 7, "Authored draw pose is reached before release.");
            await Capture("draw");
            await Until(() => practice.Releases == 1, "The draw releases one arrow.");
            Check(practice.Hits == 0 && practice.ArrowVisible && !practice.MarkVisible, "Projectile is visible before contact.");
            await Until(() => practice.Hits == 1, "The arrow collides with the selected dummy.");
            Check(!practice.ArrowVisible && practice.MarkVisible, "Confirmed contact starts the mark and removes the arrow.");
            if (_capture != null)
            {
                for (int i = 0; i < 9; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                await Capture();
            }
            await Until(() => !practice.IsCasting && !practice.MarkVisible, "Cast and contact effect return to idle.");
            Check(practice.Releases == 1, "Repeated input during draw cannot release a second arrow.");
            await Capture("idle");

            var wall = new StaticBody2D { Position = _hero.Position + new Vector2(58, -16), CollisionLayer = 1 };
            AddChild(wall);
            wall.AddChild(new CollisionShape2D { Shape = new RectangleShape2D { Size = new Vector2(8, 70) } });
            for (int i = 0; i < 3; i++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            KeyPress(Key.Key1);
            await Until(() => practice.Misses == 1, "A terrain collider intercepts the arrow.");
            Check(practice.Hits == 1 && !practice.MarkVisible, "Blocked shot cannot apply the dummy mark.");
            wall.QueueFree();
            await Until(() => !practice.IsCasting, "Blocked shot finishes its recovery.");

            practice.ClearTarget();
            for (int facing = 0; facing < 8; facing++)
            {
                FaceDirection(Vector2.Up.Rotated(facing * Mathf.Pi / 4));
                int before = practice.Releases;
                KeyPress(Key.Key1);
                await Until(() => practice.IsCasting, $"Key 1 starts direction {facing}.");
                Check(animator.ActionDirection == facing, $"Facing {facing} selects its dedicated clip.");
                var frames = new HashSet<int>();
                for (int tick = 0; tick < 90 && practice.IsCasting && frames.Count < 16; tick++)
                {
                    frames.Add(animator.DisplayedFrame);
                    await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                }
                Check(frames.Count == 16, $"Facing {facing} draws all 16 source frames.");
                await Until(() => !practice.IsCasting && !practice.ArrowVisible, $"Facing {facing} completes its shot.");
                Check(practice.Releases == before + 1, $"Facing {facing} fires only once.");
            }
            GD.Print($"LINH_CUNG_PRACTICE PASS assertions={assertions} facings=8 authoringFrames=128");
            GetTree().Quit();
        }
        catch (Exception error)
        {
            GD.PushError("LINH_CUNG_PRACTICE FAIL " + error);
            GetTree().Quit(1);
        }
    }
}
