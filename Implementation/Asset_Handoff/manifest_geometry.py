"""OPC-06 manifest v2 frame geometry rules.

The shared JSON Schema validator in ``Implementation/Tools/json_schema.py`` only
implements a small subset of JSON Schema, so conditional rules live here instead
of in ``allOf``/``if`` blocks that would be silently ignored.

This module is filesystem-free and standard-library only. The caller passes a
report object whose ``error(asset_id, file, field, message)`` method collects
findings in the same shape as ``validate_asset_delivery.Report``.
"""

DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")

# Layouts this draft actually validates end to end. Anything else must fail
# loudly instead of being cropped from a guessed frame count.
SUPPORTED_LAYOUTS = ("direction_rows", "strip")

# Only these kinds carry frame geometry in v2. Static icons, UI textures,
# tilesets, tilemaps and non-image animation clips keep their legacy shape.
GEOMETRY_KINDS = ("sprite_sheet", "vfx_sheet")

FRAME_COUNT_ALIASES = ("frames", "frameCount")


def positive_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def non_negative_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def frame_size_of(asset):
    """Return ``(width, height)`` when frameSize is structurally usable."""
    frame = asset.get("frameSize")
    if not isinstance(frame, dict):
        return None
    width, height = frame.get("width"), frame.get("height")
    if positive_int(width) and positive_int(height):
        return width, height
    return None


def declared_frame_count(animation, layout):
    """Return ``(field_name, value)`` for the layout's canonical frame field."""
    if layout == "direction_rows":
        if "framesPerDirection" in animation:
            return "framesPerDirection", animation.get("framesPerDirection")
        return None, None
    for key in FRAME_COUNT_ALIASES:
        if key in animation:
            return key, animation.get(key)
    return None, None


def check_directions_v2(label, path, directions, report):
    """Direction-rows sheets must list the locked eight directions in order."""
    if not isinstance(directions, list):
        report.error(
            label,
            path,
            "directions",
            "direction_rows requires the eight canonical directions "
            f"{list(DIRECTIONS)} in order",
        )
        return
    unknown = [value for value in directions if value not in DIRECTIONS]
    if unknown:
        report.error(
            label,
            path,
            "directions",
            f"unknown direction(s) {unknown}; allowed are {list(DIRECTIONS)}",
        )
        return
    duplicates = sorted({value for value in directions if directions.count(value) > 1})
    if duplicates:
        report.error(label, path, "directions", f"duplicate direction(s) {duplicates}")
        return
    if len(directions) != len(DIRECTIONS):
        missing = [value for value in DIRECTIONS if value not in directions]
        report.error(
            label,
            path,
            "directions",
            f"expected {len(DIRECTIONS)} directions, found {len(directions)} (missing {missing})",
        )
        return
    if tuple(directions) != DIRECTIONS:
        report.error(
            label,
            path,
            "directions",
            f"direction order must be {list(DIRECTIONS)}, found {list(directions)}",
        )


def check_animation_names(label, path, animations, report):
    names = [
        animation.get("name")
        for animation in animations
        if isinstance(animation, dict) and isinstance(animation.get("name"), str)
    ]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        report.error(label, path, "animations", f"duplicate animation name(s) {duplicates}")


def check_overlap(label, path, ranges, layout, report):
    ordered = sorted(ranges)
    for left, right in zip(ordered, ordered[1:]):
        if right[0] < left[1]:
            report.error(
                label,
                path,
                "animations",
                f"clips '{left[2]}' and '{right[2]}' overlap on {layout} "
                f"range {right[0]}..{min(left[1], right[1]) - 1}",
            )


def _check_direction_rows(label, path, asset, frame, directions, animations, report):
    width, height = asset.get("pixelWidth"), asset.get("pixelHeight")
    if not positive_int(width) or not positive_int(height):
        return
    frame_width, frame_height = frame
    rows = len(directions) if isinstance(directions, list) else 0
    if rows == 0:
        return
    if width % frame_width:
        report.error(
            label,
            path,
            "frameSize",
            f"pixelWidth {width} is not divisible by frameSize.width {frame_width}",
        )
        return
    columns = width // frame_width
    expected_height = frame_height * rows
    if height != expected_height:
        report.error(
            label,
            path,
            "frameSize",
            f"pixelHeight {height} must equal frameSize.height {frame_height} x "
            f"{rows} direction rows = {expected_height}",
        )
    ranges = []
    for index, animation in enumerate(animations):
        if not isinstance(animation, dict):
            continue
        name = animation.get("name") or f"animations[{index}]"
        if "framesPerDirection" not in animation:
            alias = next((key for key in FRAME_COUNT_ALIASES if key in animation), None)
            if alias:
                report.error(
                    label,
                    path,
                    f"animations[{index}].{alias}",
                    "direction_rows requires framesPerDirection; legacy aliases are "
                    "only valid for strip layout",
                )
            else:
                report.error(
                    label,
                    path,
                    f"animations[{index}].framesPerDirection",
                    "direction_rows requires framesPerDirection",
                )
            continue
        frames = animation.get("framesPerDirection")
        if not positive_int(frames):
            report.error(
                label,
                path,
                f"animations[{index}].framesPerDirection",
                f"must be an integer >= 1, found {frames!r}",
            )
            continue
        start = animation.get("columnStart", 0)
        if not non_negative_int(start):
            report.error(
                label,
                path,
                f"animations[{index}].columnStart",
                f"must be an integer >= 0, found {start!r}",
            )
            continue
        end = start + frames
        if end > columns:
            report.error(
                label,
                path,
                f"animations[{index}].columnStart",
                f"clip '{name}' covers columns {start}..{end - 1} but the sheet has "
                f"{columns} frame columns (pixelWidth {width} / frameWidth {frame_width})",
            )
        if "frameStart" in animation:
            report.error(
                label,
                path,
                f"animations[{index}].frameStart",
                "frameStart is only valid for strip layout",
            )
        ranges.append((start, end, name))
    check_overlap(label, path, ranges, "direction_rows", report)


def _check_strip(label, path, asset, frame, animations, report):
    width, height = asset.get("pixelWidth"), asset.get("pixelHeight")
    if not positive_int(width) or not positive_int(height):
        return
    frame_width, frame_height = frame
    if height != frame_height:
        report.error(
            label,
            path,
            "frameSize",
            f"strip layout requires exactly one row: pixelHeight {height} must equal "
            f"frameSize.height {frame_height}",
        )
    if width % frame_width:
        report.error(
            label,
            path,
            "frameSize",
            f"pixelWidth {width} is not divisible by frameSize.width {frame_width}",
        )
        return
    total = width // frame_width
    ranges = []
    for index, animation in enumerate(animations):
        if not isinstance(animation, dict):
            continue
        name = animation.get("name") or f"animations[{index}]"
        key, frames = declared_frame_count(animation, "strip")
        if key is None:
            if "framesPerDirection" in animation:
                report.error(
                    label,
                    path,
                    f"animations[{index}].framesPerDirection",
                    "strip layout uses frames or frameCount, not framesPerDirection",
                )
            else:
                report.error(
                    label,
                    path,
                    f"animations[{index}]",
                    "strip layout requires frames or frameCount",
                )
            continue
        if not positive_int(frames):
            report.error(
                label,
                path,
                f"animations[{index}].{key}",
                f"frame count must be an integer >= 1, found {frames!r}",
            )
            continue
        start = animation.get("frameStart", 0)
        if not non_negative_int(start):
            report.error(
                label,
                path,
                f"animations[{index}].frameStart",
                f"must be an integer >= 0, found {start!r}",
            )
            continue
        end = start + frames
        if end > total:
            report.error(
                label,
                path,
                f"animations[{index}].frameStart",
                f"clip '{name}' covers frames {start}..{end - 1} but the strip has "
                f"{total} frames (pixelWidth {width} / frameWidth {frame_width})",
            )
        if "columnStart" in animation:
            report.error(
                label,
                path,
                f"animations[{index}].columnStart",
                "columnStart is only valid for direction_rows layout",
            )
        ranges.append((start, end, name))
    check_overlap(label, path, ranges, "strip", report)


def validate_v2_asset(label, asset, report):
    """Validate the v2 layout/version rules for one asset entry."""
    kind = asset.get("kind")
    path = asset.get("path")
    is_directional = asset.get("isDirectional")
    layout = asset.get("layout")
    frame = frame_size_of(asset)
    animations = asset.get("animations")
    directions = asset.get("directions")

    if kind not in GEOMETRY_KINDS:
        if "frameSize" in asset:
            report.error(
                label,
                path,
                "frameSize",
                "only sprite_sheet and vfx_sheet carry frame geometry in v2",
            )
        if "layout" in asset:
            report.error(
                label,
                path,
                "layout",
                "only sprite_sheet and vfx_sheet carry a layout in v2",
            )
        if "isDirectional" in asset and not isinstance(is_directional, bool):
            report.error(label, path, "isDirectional", "must be a boolean")
        if is_directional is True:
            report.error(
                label,
                path,
                "isDirectional",
                "only sprite_sheet supports isDirectional=true",
            )
        if isinstance(directions, list) and directions:
            report.error(
                label,
                path,
                "directions",
                "static and non-sheet kinds must not declare directions in v2",
            )
        return

    if not isinstance(is_directional, bool):
        report.error(
            label,
            path,
            "isDirectional",
            "v2 sprite_sheet/vfx_sheet must declare isDirectional explicitly "
            "(true for the eight-direction actor layout, false for a single-direction sheet)",
        )
    if frame is None:
        report.error(
            label,
            path,
            "frameSize",
            "v2 sprite_sheet/vfx_sheet requires frameSize {width,height} with integers >= 1",
        )
    if layout not in SUPPORTED_LAYOUTS:
        report.error(
            label,
            path,
            "layout",
            f"unsupported layout {layout!r}; supported layouts: {', '.join(SUPPORTED_LAYOUTS)}",
        )
    if not isinstance(animations, list) or not animations:
        report.error(
            label,
            path,
            "animations",
            "v2 sprite_sheet/vfx_sheet requires at least one animation",
        )
        animations = []
    else:
        check_animation_names(label, path, animations, report)

    if kind == "vfx_sheet" and is_directional is True:
        report.error(
            label,
            path,
            "isDirectional",
            "vfx_sheet is single-direction in this contract; directional VFX is unsupported",
        )
    if is_directional is True and layout == "strip":
        report.error(
            label,
            path,
            "layout",
            "isDirectional=true requires direction_rows layout",
        )
    if is_directional is False and layout == "direction_rows":
        report.error(
            label,
            path,
            "layout",
            "direction_rows requires isDirectional=true",
        )

    if is_directional is True:
        check_directions_v2(label, path, directions, report)
    elif is_directional is False:
        if isinstance(directions, list) and directions:
            report.error(
                label,
                path,
                "directions",
                "isDirectional=false must not declare non-empty directions",
            )
        elif directions is not None and not isinstance(directions, list):
            report.error(label, path, "directions", "must be an array of direction codes")

    if frame is None or layout not in SUPPORTED_LAYOUTS:
        return
    if layout == "direction_rows":
        _check_direction_rows(label, path, asset, frame, directions, animations, report)
    elif layout == "strip":
        _check_strip(label, path, asset, frame, animations, report)
