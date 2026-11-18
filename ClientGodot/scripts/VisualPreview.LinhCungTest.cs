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
        async Task Until(Func<bool> condition, string message, int frameLimit = 150)
        {
            for (int frame = 0; frame < frameLimit && !condition(); frame++)
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
            KeyPress(Key.Key4);
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
            int beforeTrap = assertions;
            var trap = practice.Trap;
            void PlaceAt(Vector2 world) => Click(GetViewport().GetCanvasTransform() * world);
            var start = _hero.GlobalPosition;
            Click(PreviewHud.SkillCenters()[1]);
            await Until(() => trap.IsAiming, "The second HUD button selects a trap position.");
            Click(PreviewHud.SkillCenters()[3]);
            Check(trap.IsAiming && trap.Placed == 0, "Clicking another HUD slot never plants under the HUD.");
            KeyPress(Key.Escape);
            await Until(() => !trap.IsAiming, "Escape cancels ground selection.");
            Check(trap.Placed == 0, "No seed is released after cancelling.");

            KeyPress(Key.Key2);
            await Until(() => trap.IsAiming, "Key 2 can select a trap location.");
            PlaceAt(start + new Vector2(196,0));
            await Until(() => _hud.CombatHint.Contains("Điểm đặt"), "Out-of-range placement is rejected.");
            Check(trap.IsAiming && !practice.IsCasting, "Invalid placement keeps the cursor without starting cast.");
            var inside = _environment.SolidFootprints.Find(rect => rect.GetCenter().DistanceTo(start) < 100);
            Check(inside.Size != Vector2.Zero, "There is a terrain obstacle near the practice spawn.");
            PlaceAt(inside.GetCenter());
            for (int i = 0; i < 3; i++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            Check(trap.IsAiming && trap.Placed == 0, "Terrain footprint cannot receive a seed.");

            var shore = start + new Vector2(-88,100);
            var water = start + new Vector2(-88,190);
            Check(_environment.IsWalkable(shore) && Geometry2D.IsPointInPolygon(water, _environment.WaterPolygon) &&
                  !_environment.Piers.Exists(pier => pier.HasPoint(water)), "Water rejection uses a real river cell beside dry ground.");
            _hero.GlobalPosition = shore;
            _hero.ResetPhysicsInterpolation();
            for (int i = 0; i < 3; i++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            PlaceAt(water);
            for (int i = 0; i < 3; i++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            Check(trap.IsAiming && trap.Placed == 0, "Water inside placement range rejects the ground click.");
            _hero.GlobalPosition = start;
            _hero.ResetPhysicsInterpolation();
            for (int i = 0; i < 3; i++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);

            await Until(() => trap.Target.Velocity.X > 20 && trap.Target.GlobalPosition.X < start.X - 100,
                        "Patrol approaches the area where it will step outside the trap before arming.", 380);
            var patrolPath = start + new Vector2(-106,8);
            PlaceAt(patrolPath);
            await Until(() => trap.CurrentStage == LinhCungTrapPractice.Stage.Windup, "Valid ground click begins the authored placement pose.");
            Check(animator.ActionDirection == 6 && trap.Placed == 0, "The cast faces its ground target and waits for the hand cue.");
            await Until(() => trap.CurrentStage == LinhCungTrapPractice.Stage.Seed, "The release cue starts the seed effect.");
            Check(trap.GroundPoint.DistanceTo(patrolPath) < .2f && trap.Placed == 1, "Seed begins at the confirmed ground point.");
            await Until(() => trap.CurrentStage == LinhCungTrapPractice.Stage.Growing, "The seed's contact starts growth.");
            if (_capture != null)
            {
                for (int frame = 0; frame < 18; frame++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                await Capture("trap_growth");
            }
            await Until(() => trap.CurrentStage == LinhCungTrapPractice.Stage.Armed, "The trap becomes armed after growing.");
            Check(trap.Triggered == 0 && trap.Expired == 0, "Growth and arming have no trigger side effect.");
            Check(trap.Target.GlobalPosition.DistanceTo(trap.GroundPoint) > 40,
                  "The patrol is outside the two-metre boundary at arming.");
            await Capture("trap_armed");
            KeyPress(Key.Key2);
            Check(!trap.IsAiming, "An active trap prevents a duplicate placement.");
            await Until(() => trap.Triggered == 1, "The patrol enters the armed trap.", 270);
            Check(trap.CurrentStage == LinhCungTrapPractice.Stage.Retracting && trap.SlowSeconds > 2.4,
                  "The trap retracts once and applies the patrol slow.");
            for (int i = 0; i < 2; i++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            Check(Mathf.IsEqualApprox(trap.Target.Velocity.Length(), 32 * .6f), "Patrol steps slow by forty percent after contact.");
            if (_capture != null)
            {
                for (int frame = 0; frame < 8; frame++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                await Capture("trap_trigger");
            }
            await Until(() => trap.CurrentStage == LinhCungTrapPractice.Stage.Idle, "Triggered trap completes retraction.");
            Check(trap.Triggered == 1 && trap.Expired == 0, "A resolved trap cannot expire or hit again.");

            KeyPress(Key.Key2);
            await Until(() => trap.IsAiming, "A new placement is available after recovery.");
            var emptyGround = start + new Vector2(76,22);
            PlaceAt(emptyGround);
            await Until(() => trap.CurrentStage == LinhCungTrapPractice.Stage.Armed, "An empty-ground trap also arms.", 165);
            for (int frame = 0; frame < 236; frame++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            Check(trap.CurrentStage == LinhCungTrapPractice.Stage.Armed, "The empty trap remains active for its four-second window.");
            await Until(() => trap.Expired == 1, "The empty trap expires without a new hit.");
            Check(trap.Triggered == 1 && trap.Placed == 2 && trap.SlowSeconds == 0, "Expiry never applies crowd control.");
            if (_capture != null)
            {
                for (int frame = 0; frame < 8; frame++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                await Capture("trap_expire");
            }
            await Until(() => trap.CurrentStage == LinhCungTrapPractice.Stage.Idle, "Expired trap retracts.");
            for (int facing = 0; facing < 8; facing++)
            {
                FaceDirection(Vector2.Up.Rotated(facing * Mathf.Pi / 4));
                Check(animator.TryCast("trap") && animator.ActionDirection == facing, $"Trap selects authored facing {facing}.");
                var frames = new HashSet<int>();
                for (int tick = 0; tick < 100 && practice.IsCasting; tick++)
                {
                    frames.Add(animator.DisplayedFrame);
                    await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                }
                Check(frames.Count == 16 && !practice.IsCasting, $"Trap facing {facing} plays all sixteen poses and recovers.");
            }
            Check(trap.Placed == 2, "An animation alone cannot add a trap.");
            GD.Print($"LINH_CUNG_TRAP PASS assertions={assertions - beforeTrap} facings=8 authoringFrames=128");

            int beforeVolley = assertions;
            var volley = practice.Volley;
            Check(practice.SelectAt(practice.TargetPoint), "The volley can lock the east dummy before drawing.");
            Click(PreviewHud.SkillCenters()[2]);
            await Until(() => volley.Active, "The third HUD button starts Liên Châu.");
            Check(animator.CurrentAction == "volley" && volley.Released == 0 && volley.InFlight == 0,
                  "Windup keeps all arrows in the quiver.");
            await Until(() => volley.NocksVisible == 5, "Five ready dots appear before releasing.");
            await Capture("volley_ready");
            var releaseFrames = new List<int>();
            bool flightCaptured = false;
            for (int frame = 0; volley.Active && frame < 90; frame++)
            {
                if (volley.Released > releaseFrames.Count)
                {
                    Check(volley.Released == releaseFrames.Count + 1, "Each release comes from a separate action cue.");
                    releaseFrames.Add(frame);
                    Check(volley.NocksVisible == 5 - volley.Released, "A firing cue removes one ready dot.");
                }
                if (!flightCaptured && releaseFrames.Count == 2 && volley.InFlight == 2)
                {
                    flightCaptured = true;
                    await Capture("volley_flight");
                    KeyPress(Key.Key3);
                }
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            }
            Check(!volley.Active && volley.Released == 5 && releaseFrames.Count == 5, "The volley resolves exactly five times.");
            Check(flightCaptured, "Two distinct arrows can fly at once.");
            for (int i = 1; i < releaseFrames.Count; i++)
                Check(releaseFrames[i] - releaseFrames[i - 1] is 6 or 7, "Shot spacing is 110 ms at fixed 60 FPS.");
            Check(volley.Hits == 3 && volley.Capped == 2 && volley.Blocked == 0 && volley.Expired == 0,
                  "Five arrows contact the dummy, with only three counted hits.");
            await Capture("volley_result");
            await Until(() => !practice.IsCasting, "The volley body recovers fully.");

            var barrier = new StaticBody2D { Position = _hero.Position + new Vector2(58, -16), CollisionLayer = 1 };
            AddChild(barrier);
            barrier.AddChild(new CollisionShape2D { Shape = new RectangleShape2D { Size = new Vector2(8, 70) } });
            for (int i = 0; i < 3; i++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            KeyPress(Key.Key3);
            await Until(() => volley.Active, "Key 3 starts the volley.");
            await Until(() => !volley.Active, "The blocked burst resolves to recovery.");
            Check(volley.Released == 5 && volley.Blocked == 5 && volley.Hits == 0 && volley.Capped == 0,
                  "Terrain stops all five arrows before the selected dummy.");
            barrier.QueueFree();
            await Until(() => !practice.IsCasting, "The blocked volley body recovers.");

            practice.ClearTarget();
            for (int facing = 0; facing < 8; facing++)
            {
                FaceDirection(Vector2.Up.Rotated(facing * Mathf.Pi / 4));
                KeyPress(Key.Key3);
                await Until(() => animator.CurrentAction == "volley", $"Volley starts in facing {facing}.");
                Check(animator.ActionDirection == facing, $"Volley selects its dedicated art for facing {facing}.");
                var frames = new HashSet<int>();
                for (int tick = 0; tick < 80 && practice.IsCasting; tick++)
                {
                    frames.Add(animator.DisplayedFrame);
                    await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                }
                Check(frames.Count == 16, $"Volley facing {facing} renders all sixteen poses.");
                await Until(() => !volley.Active, $"Volley facing {facing} resolves all projectiles.");
                Check(volley.Released == 5 && volley.Hits + volley.Capped + volley.Blocked + volley.Expired == 5,
                      $"Volley facing {facing} accounts for every distinct arrow.");
            }
            GD.Print($"LINH_CUNG_VOLLEY PASS assertions={assertions - beforeVolley} facings=8 authoringFrames=128");
            GetTree().Quit();
        }
        catch (Exception error)
        {
            GD.PushError("LINH_CUNG_PRACTICE FAIL " + error);
            GetTree().Quit(1);
        }
    }
}
