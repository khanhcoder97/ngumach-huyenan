"""Validate the versioned design input and arithmetic, not server mechanics."""
import json
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "Implementation/Content/DesignBaselines/p1_guard_precision_v1.json"


def validate(bundle):
    errors = []

    def require(ok, label):
        if not ok:
            errors.append(label)

    require(bundle["schemaVersion"] == 1, "schemaVersion")
    require(bundle["decisionId"] == "DEC-022", "decisionId")
    require(bundle["activation"] == "DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION", "activation must not enable runtime")
    require((ROOT / bundle["sourceRef"]).is_file(), "sourceRef must exist")
    guard, whiff, counter, oracle = (bundle[k] for k in ("guard", "whiff", "counter", "oracle"))
    skill = json.loads((ROOT / "Implementation/Content/Examples/SkillDefinition/SK-MK-01.json").read_text(encoding="utf-8-sig"))
    art = json.loads((ROOT / "Implementation/Content/DesignBaselines/skill_vfx_art_v1.json").read_text(encoding="utf-8-sig"))
    # Canonical values; no exports or runtime data are modified by this check.
    require(bundle["tickHz"] == 20, "tickHz")
    require(Decimal(str(skill["telegraphSeconds"])) * bundle["tickHz"] == guard["durationTicks"], "guard duration differs from source")
    require(guard["rangeWu"] == skill["targeting"]["rangeWu"] == counter["rangeWu"], "range differs from source")
    require(guard["angleDegrees"] == skill["targeting"]["angleDegrees"] == counter["angleDegrees"], "angle differs from source")
    require(counter["maxTargets"] == skill["targeting"]["maxTargets"] == 1, "counter target cap")
    require(counter["delayTicks"] == 1, "counter must not recursively resolve in same tick")
    require(guard["maxConfirmations"] == 1, "confirmation cap")
    require(guard["damageReduction"] == 0.7, "front guard DR baseline")
    require(guard["swordIntentGain"] == 2 and guard["swordIntentCap"] == 5, "resource limits")
    require(guard["interval"] == "START_INCLUSIVE_END_EXCLUSIVE", "interval boundary")
    require(guard["origin"] == "DEFENDER_CURRENT_FOOT" and guard["facing"] == "CAST_START_SNAPSHOT", "self-attached geometry")
    require(whiff["durationTicks"] == 20 and whiff["damageReduction"] == 0.2, "whiff baseline")
    require(set(whiff["excludedOn"]) == {"DEATH", "MAP_CHANGE", "SESSION_END", "HARD_CONTROL", "DODGE_CANCEL"}, "whiff cleanup")
    require(set(counter["flags"]) == {"NO_COUNTER_TRIGGER", "NO_EXTRA_RESOURCE_ON_DAMAGE", "NO_NEW_MP_COST", "NO_NEW_COOLDOWN"}, "counter safety flags")
    require(counter["attackSnapshot"] == "GUARD_ACCEPTED", "counter attack snapshot")
    require(not counter["bossHardControl"] and not counter["refundOnMissOrTargetDeath"], "counter control/refund")
    require(bundle["ordering"]["confirmationUniqueKey"] == ["guardCastId"], "one confirmation per guard")
    require(bundle["ordering"]["impacts"] == ["scheduledTick", "castStartTick", "castIdOrdinal", "hitIndex", "targetIdOrdinal"], "deterministic impact order")
    require(bundle["presentation"]["confirmationSemantic"] == "COUNTER_CONFIRMED", "presentation semantic")
    require(bundle["presentation"]["whiffCue"] is None, "whiff must not play parry")

    cue = bundle["presentation"]["confirmationCue"]
    audio = json.loads((ROOT / "Implementation/Content/DesignBaselines/audio_cues_v1.json").read_text(encoding="utf-8-sig"))
    entries = audio["cues"]
    matches = [c for c in entries if c["cueKey"] == cue]
    require(len(matches) == 1 and matches[0]["triggerSemantic"] == "COUNTER_CONFIRMED", "cue must already exist with confirmed semantic")
    # Art schema may evolve; search the concrete skill record without changing it.
    require("SK-MK-01" in json.dumps(art), "skill art source exists")

    start = oracle["castStartTick"]
    end = start + guard["durationTicks"]
    require(end == oracle["guardEndExclusiveTick"], "guard end oracle")
    require(end + whiff["durationTicks"] == oracle["whiffEndExclusiveTick"], "whiff end oracle")
    for dr in (guard["damageReduction"], whiff["damageReduction"]):
        require(0 <= dr <= 0.8, "damage reduction outside DR cap")

    def damage(raw, reduction, crit=1):
        value = Decimal(str(raw)) * 100 / (100 + Decimal(str(oracle["armor"])))
        value *= Decimal(str(crit)) * (1 - Decimal(str(reduction)))
        return max(1, int(value.to_integral_value(rounding=ROUND_FLOOR)))

    raw = oracle["rawDamage"]
    for reduction, key in ((0, "outsideFinalDamage"), (guard["damageReduction"], "guardFinalDamage"),
                           (whiff["damageReduction"], "whiffFinalDamage"), (0.8, "cappedFinalDamage")):
        require(damage(raw, reduction) == oracle[key], key)
    require(oracle["guardAndOtherReductionAtCap"] == min(0.8, guard["damageReduction"] + whiff["damageReduction"]), "DR bucket cap oracle")
    require(oracle["counterPveCoefficient"] == skill["coefficients"]["pve"], "counter coefficient source")
    raw_counter = Decimal(str(oracle["counterAttack"])) * Decimal(str(oracle["counterPveCoefficient"]))
    require(damage(raw_counter, 0) == oracle["counterNonCritFinalDamage"], "counter non-crit oracle")
    require(damage(raw_counter, 0, 1.5) == oracle["counterCritFinalDamage"], "counter crit oracle")
    return errors


if __name__ == "__main__":
    try:
        findings = validate(json.loads(PATH.read_text(encoding="utf-8-sig")))
    except (KeyError, TypeError, ValueError, OSError) as exc:
        findings = ["invalid design bundle: " + str(exc)]
    for finding in findings:
        print("ERROR: " + finding)
    print("FAIL: design input invalid" if findings else "PASS: DEC-022 design/source/timeline/arithmetic; server and Unity remain unverified")
    raise SystemExit(1 if findings else 0)
