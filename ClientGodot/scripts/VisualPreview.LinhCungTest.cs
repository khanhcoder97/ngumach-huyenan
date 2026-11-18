using Godot;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
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
            KeyPress(Key.Key6);
            await Until(() => practice.Rain.IsAiming, "The ultimate opens ground aiming without a cast.");
            Check(!practice.IsCasting && practice.Releases == 0 && !practice.Rain.Active, "Aiming has no hit or release.");
            KeyPress(Key.Escape);
            await Until(() => !practice.Rain.IsAiming, "Escape closes the ultimate cursor.");
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
            Click(PreviewHud.SkillCenters()[5]);
            await Until(() => practice.Rain.IsAiming, "The sixth HUD button switches ground selection.");
            Check(!trap.IsAiming && trap.Placed == 0 && practice.Rain.IsAiming && !practice.Rain.Active,
                  "Switching ground skills changes the cursor without casting underneath the HUD.");
            KeyPress(Key.Escape);
            await Until(() => !practice.Rain.IsAiming, "Escape cancels the replacement cursor.");
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

            int beforeFan = assertions;
            var fan = practice.Fan;
            Check(LinhCungFanPractice.HitScale(Vector2.Right, Vector2.Right.Rotated(Mathf.DegToRad(49)) * 40) == 1 &&
                  LinhCungFanPractice.HitScale(Vector2.Right, Vector2.Right.Rotated(Mathf.DegToRad(51)) * 40) == 0,
                  "The fan includes a point inside 50 degrees and rejects an outside point.");
            Check(LinhCungFanPractice.HitScale(Vector2.Right, Vector2.Left * 30) == 0 &&
                  LinhCungFanPractice.HitScale(Vector2.Right, Vector2.Right * (LinhCungFanPractice.Range + 1)) == 0,
                  "The fan rejects rear and out-of-range targets.");
            Check(Mathf.IsEqualApprox(LinhCungFanPractice.HitScale(Vector2.Right, Vector2.Right * 15), .7f) &&
                  LinhCungFanPractice.HitScale(Vector2.Right, Vector2.Right * LinhCungFanPractice.NearDistance) == 1,
                  "The reduced factor applies strictly below the 0.8 metre boundary.");
            var dummyFoot = practice.TargetPoint - LinhCungPractice.TargetOffset;
            var normalPosition = dummyFoot - Vector2.Right * 59;
            var closePosition = dummyFoot - Vector2.Right * 14;
            async Task StandAt(Vector2 position)
            {
                Check(_environment.IsWalkable(position), "The fan setup uses walkable ground.");
                _hero.GlobalPosition = position;
                _hero.ResetPhysicsInterpolation();
                for (int frame = 0; frame < 3; frame++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            }

            await StandAt(normalPosition);
            Check(practice.SelectAt(practice.TargetPoint), "The fan can aim toward the east dummy.");
            Click(PreviewHud.SkillCenters()[3]);
            await Until(() => fan.Active, "The fourth HUD button starts Tán Hoa.");
            Check(animator.CurrentAction == "fan" && !fan.FanVisible && !fan.Resolved, "The cone waits for the bow release.");
            await Until(() => fan.FanVisible, "The measured bow cue opens the fan.");
            Check(!fan.Resolved, "The opening effect appears before hit resolution.");
            await Until(() => fan.Resolved, "Targets are resolved at the fully opened frame.");
            Check(fan.NormalHits == 1 && fan.CloseHits == 0 && fan.Blocked == 0, "The east dummy counts one normal hit.");
            await Capture("fan_open");
            await Until(() => fan.LeavesVisible, "The falling fragments follow the main petal fan.");
            await Capture("fan_leaves");
            await Until(() => !fan.Active && !practice.IsCasting, "The fan and fragments finish recovery.");

            await StandAt(closePosition);
            practice.LowFx = true;
            KeyPress(Key.Key4);
            await Until(() => fan.Active, "Key 4 casts Tán Hoa at close range.");
            await Until(() => fan.Resolved, "The close cast resolves.");
            Check(fan.NormalHits == 0 && fan.CloseHits == 1 && fan.FanVisible, "The close hit reduces effect to seventy percent and keeps the visual cone.");
            await Capture("fan_close");
            for (int frame = 0; frame < 18; frame++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Check(fan.Active && !fan.LeavesVisible, "Low VFX hides falling fragments during the normal fall window.");
            await Until(() => !fan.Active && !practice.IsCasting, "The close cast finishes.");
            practice.LowFx = false;

            await StandAt(normalPosition);
            var fanWall = new StaticBody2D { Position = normalPosition + Vector2.Right * 33, CollisionLayer = 1 };
            AddChild(fanWall);
            fanWall.AddChild(new CollisionShape2D { Shape = new RectangleShape2D { Size = new Vector2(8, 80) } });
            for (int frame = 0; frame < 3; frame++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            KeyPress(Key.Key4);
            await Until(() => fan.Active, "The wall test starts the art sequence.");
            await Until(() => fan.Resolved, "The blocked fan resolves.");
            Check(fan.NormalHits + fan.CloseHits == 0 && fan.Blocked == 1, "An obstacle prevents the dummy hit.");
            fanWall.QueueFree();
            await Until(() => !fan.Active && !practice.IsCasting, "The wall test completes recovery.");

            practice.ClearTarget();
            await StandAt(start);
            for (int facing = 0; facing < 8; facing++)
            {
                FaceDirection(Vector2.Up.Rotated(facing * Mathf.Pi / 4));
                KeyPress(Key.Key4);
                await Until(() => animator.CurrentAction == "fan", $"Fan starts in facing {facing}.");
                Check(animator.ActionDirection == facing, $"Fan selects its authored clip for facing {facing}.");
                var frames = new HashSet<int>();
                for (int tick = 0; tick < 90 && practice.IsCasting; tick++)
                {
                    frames.Add(animator.DisplayedFrame);
                    await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                }
                Check(frames.Count == 16, $"Fan facing {facing} renders all sixteen poses.");
                await Until(() => fan.Resolved && !fan.Active, $"Fan facing {facing} resolves exactly once and recovers.");
            }
            GD.Print($"LINH_CUNG_FAN PASS assertions={assertions - beforeFan} facings=8 authoringFrames=128");

            int beforeRetreat = assertions;
            var retreat = practice.Retreat;
            await StandAt(start);
            Check(practice.SelectAt(practice.TargetPoint), "The east dummy can be selected for the countershot.");
            Click(PreviewHud.SkillCenters()[4]);
            await Until(() => retreat.Active, "The fifth HUD button starts Phi Diệp.");
            Check(animator.CurrentAction == "retreat" && retreat.Releases == 0 &&
                  retreat.DistanceMoved == 0 && retreat.MarksShown == 0, "Windup holds ground and keeps the arrow hidden.");
            await Until(() => retreat.MarksShown == 1, "The first mark appears at the beginning of retreat.");
            ulong startTick = Engine.GetPhysicsFrames();
            await Until(() => retreat.Releases == 1, "A single countershot leaves the bow during retreat.");
            ulong elapsedTicks = Engine.GetPhysicsFrames() - startTick;
            Check(elapsedTicks is 7 or 8, $"The native movement-to-shot interval represents 120 ms at 60 Hz ({elapsedTicks} ticks).");
            Check(retreat.MarksShown == 2 && retreat.ArrowVisible && retreat.Hits == 0 &&
                  retreat.DistanceMoved is > 1 and < LinhCungRetreatPractice.RetreatDistance,
                  "The second mark and the shot begin before retreat finishes.");
            Check(retreat.ShotDirection.IsEqualApprox(Vector2.Right), "The countershot follows the starting aim.");
            await Capture("retreat_release");
            KeyPress(Key.Key5);
            await Until(() => retreat.Hits == 1, "The countershot contacts the selected dummy.");
            await Capture("retreat_hit");
            await Until(() => !retreat.Active && !practice.IsCasting, "The clear retreat fully recovers.");
            Check(Mathf.Abs(retreat.DistanceMoved - LinhCungRetreatPractice.RetreatDistance) < .25f &&
                  _hero.GlobalPosition.DistanceTo(start - Vector2.Right * LinhCungRetreatPractice.RetreatDistance) < .25f,
                  "The clear route applies exactly five metres of backward physics travel.");
            Check(retreat.Releases == 1 && retreat.MarksShown == 2 && retreat.Hits == 1, "Repeated input adds no shot or footprint.");

            await StandAt(start);
            var retreatWall = new StaticBody2D { Position = start - Vector2.Right * 32, CollisionLayer = 1 };
            AddChild(retreatWall);
            retreatWall.AddChild(new CollisionShape2D { Shape = new RectangleShape2D { Size = new Vector2(10, 80) } });
            for (int frame = 0; frame < 3; frame++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            KeyPress(Key.Key5);
            await Until(() => retreat.Active && retreat.BlockedRetreat, "The wall clips backward movement.");
            var stopped = _hero.GlobalPosition;
            Check(retreat.DistanceMoved is > 0 and < 32, "Retreat stops at the first obstruction with reduced travel.");
            await Until(() => retreat.Releases == 1 && retreat.ArrowVisible, "A blocked retreat still fires.");
            Check(stopped.DistanceTo(_hero.GlobalPosition) < .1f && retreat.ShotDirection.IsEqualApprox(Vector2.Right),
                  "The blocked actor holds ground and keeps the same shot angle.");
            await Capture("retreat_blocked");
            await Until(() => !retreat.Active, "The blocked retreat and the separate shot finish.");
            Check(retreat.Hits == 1 && retreat.Releases == 1, "The rear obstruction does not cancel the forward countershot.");
            retreatWall.QueueFree();
            for (int frame = 0; frame < 3; frame++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);

            await StandAt(start);
            var shotWall = new StaticBody2D { Position = start + Vector2.Right * 51, CollisionLayer = 1 };
            AddChild(shotWall);
            shotWall.AddChild(new CollisionShape2D { Shape = new RectangleShape2D { Size = new Vector2(10, 80) } });
            for (int frame = 0; frame < 3; frame++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            KeyPress(Key.Key5);
            await Until(() => retreat.Active, "The front-obstruction cast starts.");
            await Until(() => retreat.Releases == 1 && !retreat.ArrowVisible, "The separate projectile stops at the forward wall.");
            Check(retreat.Hits == 0 && _hud.CombatHint.Contains("tên bị chặn"), "The forward wall prevents any hit.");
            await Until(() => !retreat.Active, "The forward-obstruction cast finishes the retreat.");
            Check(Mathf.Abs(retreat.DistanceMoved - LinhCungRetreatPractice.RetreatDistance) < .25f && !retreat.BlockedRetreat,
                  "A forward obstruction does not shorten the rear movement.");
            shotWall.QueueFree();
            for (int frame = 0; frame < 3; frame++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);

            practice.ClearTarget();
            await StandAt(shore);
            FaceDirection(Vector2.Up);
            KeyPress(Key.Key5);
            await Until(() => retreat.Active, "The shore retreat starts.");
            await Until(() => !retreat.Active, "The shore retreat ends.");
            Check(retreat.BlockedRetreat && _environment.IsWalkable(_hero.GlobalPosition) && retreat.Releases == 1,
                  "The built-in river collision stops retreat on shore and keeps the shot.");
            await Capture("retreat_shore");

            for (int facing = 0; facing < 8; facing++)
            {
                await StandAt(start);
                var aim = Vector2.Up.Rotated(facing * Mathf.Pi / 4);
                FaceDirection(aim);
                KeyPress(Key.Key5);
                await Until(() => animator.CurrentAction == "retreat", $"Retreat starts in facing {facing}.");
                Check(animator.ActionDirection == facing, $"Retreat selects its authored clip for facing {facing}.");
                var poses = new HashSet<int>();
                for (int tick = 0; tick < 90 && practice.IsCasting; tick++)
                {
                    poses.Add(animator.DisplayedFrame);
                    await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                }
                Check(poses.Count == 16, $"Retreat facing {facing} renders all sixteen poses.");
                await Until(() => !retreat.Active, $"Retreat facing {facing} clears its effects.");
                Check(retreat.Releases == 1 && retreat.MarksShown == 2 && retreat.ShotDirection.IsEqualApprox(aim),
                      $"Retreat facing {facing} has one shot and two marks.");
            }
            GD.Print($"LINH_CUNG_RETREAT PASS assertions={assertions - beforeRetreat} facings=8 authoringFrames=128");

            int beforeRain = assertions;
            var rain = practice.Rain;
            await StandAt(start);
            Click(PreviewHud.SkillCenters()[5]);
            await Until(() => rain.IsAiming, "The sixth HUD button opens the ultimate cursor.");
            PlaceAt(start + new Vector2(244, 0));
            await Until(() => _hud.CombatHint.Contains("ngoài tầm"), "The ultimate rejects a center beyond twelve metres.");
            Check(rain.IsAiming && !rain.Active, "Invalid range keeps the cursor open.");
            await StandAt(shore);
            PlaceAt(water);
            for (int frame = 0; frame < 3; frame++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            Check(rain.IsAiming && !rain.Active, "A real water point inside the cast range is rejected.");
            await StandAt(start);
            PlaceAt(closePosition);
            await Until(() => rain.Active && rain.WarningVisible, "Valid dry ground starts a fixed warning circle.");
            ulong chargeStarted = Engine.GetPhysicsFrames();
            Check(animator.CurrentAction == "rain" && rain.Center.DistanceTo(closePosition) < .2f &&
                  rain.VisibleArrows == 0 && rain.WavesApplied == 0,
                  "The bow raises while the warning remains centered and has no early contacts.");
            await Capture("rain_charge");
            await Until(() => !rain.WarningVisible && rain.VisibleArrows > 0, "The first arrows follow the complete warning.");
            ulong warningTicks = Engine.GetPhysicsFrames() - chargeStarted;
            Check(warningTicks is 72 or 73, $"The visible warning spans 1.2 seconds at 60 Hz ({warningTicks} ticks).");
            Check(rain.WavesApplied == 0 && rain.VisibleArrows == 6, "Six full-VFX shafts descend before their first contact.");
            await Capture("rain_drop");
            ulong previousWave = 0;
            for (int wave = 1; wave <= 4; wave++)
            {
                int index = wave;
                await Until(() => rain.WavesApplied == index, $"Rain wave {wave} contacts as its own event.");
                ulong tick = Engine.GetPhysicsFrames();
                if (previousWave > 0) Check(tick - previousWave == 12, "Rain contacts are 200 milliseconds apart.");
                Check(rain.Hits == wave && rain.FactorPerWave == 75, "One in-zone dummy receives seventy-five percent in each wave.");
                previousWave = tick;
            }
            await Capture("rain_wave4");
            await Until(() => !rain.Active, "The ultimate clears its remaining visual layers.");
            Check(rain.WavesApplied == 4 && rain.Hits == 4 && rain.VisibleArrows == 0, "There is no extra hit or visible projectile after cleanup.");

            // Inject the server-style resource for the boosted training case.
            // The practice does not replace the normal-attack earn rules.
            rain.WoodMarks = 3;
            practice.LowFx = true;
            KeyPress(Key.Key6);
            await Until(() => rain.IsAiming, "The ultimate can aim again after recovery.");
            KeyPress(Key.Escape);
            await Until(() => !rain.IsAiming, "Escape cancels the empowered aim.");
            Check(rain.WoodMarks == 3, "Canceling ground selection preserves the resource.");
            KeyPress(Key.Key6);
            await Until(() => rain.IsAiming, "The empowered cast reacquires the cursor.");
            PlaceAt(closePosition);
            await Until(() => rain.Active && rain.WarningVisible, "Three marks empower an accepted cast.");
            ulong boostedStart = Engine.GetPhysicsFrames();
            Check(rain.Empowered && rain.WoodMarks == 0 && rain.Center.DistanceTo(closePosition) < .2f &&
                  rain.BoostVisible && rain.FactorPerWave == 90, "Boost consumes three marks and adds visible center glints.");
            await Capture("rain_boost");
            await Until(() => !rain.WarningVisible && rain.VisibleArrows > 0, "Low VFX keeps the first falling wave.");
            Check(Engine.GetPhysicsFrames() - boostedStart == warningTicks && rain.VisibleArrows == 3 && !rain.BoostVisible,
                  "Boost and Low VFX preserve the warning window and keep three core arrows.");
            await Until(() => !rain.Active, "All boosted waves finish.");
            Check(rain.WavesApplied == 4 && rain.Hits == 4 && rain.FactorPerWave * rain.WavesApplied == 360,
                  "Low VFX does not remove hits and the boost is twenty percent overall.");
            practice.LowFx = false;

            var candidates = new List<Node2D>();
            for (int i = 0; i < 11; i++)
            {
                var target = new Node2D { Position = closePosition + new Vector2(i * 11, 0) };
                AddChild(target);
                candidates.Add(target);
            }
            var distant = new Node2D { Position = closePosition + new Vector2(LinhCungRainPractice.Radius + 1, 0) };
            AddChild(distant);
            Check(LinhCungRainPractice.TargetsInZone(new[] { distant }, closePosition).Count() == 0,
                  "A target outside the six-metre radius does not take a hit.");
            var selected = LinhCungRainPractice.TargetsInZone(candidates.AsEnumerable().Reverse(), closePosition).ToArray();
            Check(selected.Length == 8 && selected.SequenceEqual(candidates.Take(8)), "The nearest eight ordinary targets are selected.");
            foreach (var target in candidates) target.QueueFree();
            distant.QueueFree();

            for (int facing = 0; facing < 8; facing++)
            {
                FaceDirection(Vector2.Up.Rotated(facing * Mathf.Pi / 4));
                Check(animator.TryCast("rain") && animator.ActionDirection == facing, $"Rain uses its dedicated facing {facing}.");
                var poses = new HashSet<int>();
                for (int tick = 0; tick < 100 && practice.IsCasting; tick++)
                {
                    poses.Add(animator.DisplayedFrame);
                    await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                }
                Check(poses.Count == 16 && !practice.IsCasting, $"Rain facing {facing} renders all sixteen poses.");
            }
            Check(!rain.Active && rain.WavesApplied == 4, "Playing body art cannot start a new damage area.");
            GD.Print($"LINH_CUNG_RAIN PASS assertions={assertions - beforeRain} facings=8 authoringFrames=128");
            GetTree().Quit();
        }
        catch (Exception error)
        {
            GD.PushError("LINH_CUNG_PRACTICE FAIL " + error);
            GetTree().Quit(1);
        }
    }
}
