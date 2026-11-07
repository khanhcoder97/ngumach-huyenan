#!/usr/bin/env python3
"""Pin selected combat/social source data; never apply it at runtime."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = "Implementation/Content/Examples/ClassDefinition"
SKILL_EXAMPLES = "Implementation/Content/Examples/SkillDefinition"
SOURCES = {
    "bible": "docs/production/Content_Bible_Ngu_Mach_Huyen_An_vi.md",
    "rules": "docs/production/Production_Rules_Complete_v1_vi.md",
    "guild": "docs/production/Guild_Social_Spec_vi.md",
    "currency": "docs/production/Currency_Production_Data_vi.csv",
    "classes": "docs/production/Character_Equipment_Inventory_Spec_vi.md",
    "example": f"{EXAMPLES}/CLASS_MINH_KIEM.json",
    "skills": "docs/production/Combat_Skills_VFX_Animation_Spec_vi.md",
}
SKILL_PINS = {
    "Minh Kiếm": ("MK", [
        ("Phản Quang", 10, 12), ("Tầm Long", 8, 16), ("Kiếm Trận", 10, 22),
        ("Thiết Y", 16, 24), ("Bạch Hồng (cơ động)", 9, 10),
        ("Vạn Tượng Quy Nhất (tuyệt kỹ)", 60, 40),
    ]),
    "Ảnh Đao": ("AD", [
        ("Huyết Nguyệt", 8, 14), ("Tàn Hỏa", 12, 18), ("Xích Ảnh", 10, 20),
        ("Tước Mạch", 14, 22), ("Ảnh Bộ (cơ động)", 8, 10),
        ("Tử Diệm (tuyệt kỹ)", 60, 35),
    ]),
    "Huyền Bút": ("HB", [
        ("Mực Triều", 6, 12), ("Hàn Châm", 12, 18), ("Thủy Kính", 16, 22),
        ("Mưa Tinh", 18, 28), ("Lưu Thủy Bộ (cơ động)", 10, 10),
        ("Long Mạch Hồi Nguyên (tuyệt kỹ)", 70, 45),
    ]),
    "Thạch Chùy": ("TC", [
        ("Trấn Sơn", 8, 14), ("Chấn Địa", 14, 20), ("Thiết Bích", 18, 24),
        ("Khiêu Chiến", 20, 16), ("Phá Nham (cơ động)", 10, 12),
        ("Sơn Thần Giáng Thế (tuyệt kỹ)", 70, 40),
    ]),
    "Linh Cung": ("LC", [
        ("Khóa Mạch", 10, 16), ("Dây Gai", 14, 18), ("Liên Châu", 8, 18),
        ("Tán Hoa", 12, 20), ("Phi Diệp (cơ động)", 9, 12),
        ("Bách Tiễn Quy Tông (tuyệt kỹ)", 65, 40),
    ]),
}
SHIPPED_SKILL_IDS = {"SK-MK-01", "SK-MK-02", "SK-MK-03", "SK-HB-02", "SK-HB-04", "SK-TC-01", "SK-TC-05"}
CLASS_IDS = {
    "Minh Kiếm": "CLASS_MINH_KIEM",
    "Ảnh Đao": "CLASS_ANH_DAO",
    "Huyền Bút": "CLASS_HUYEN_BUT",
    "Thạch Chùy": "CLASS_THACH_CHUY",
    "Linh Cung": "CLASS_LINH_CUNG",
}
RESOURCE_PINS = {
    "Minh Kiếm": (
        "Kiếm Ý",
        "Đánh thường hoàn tất chuỗi 3 nhát cho +1 Kiếm Ý; đỡ hoàn hảo cho +2. Ultimate tiêu Kiếm Ý.",
        {
            "Phản Quang": "Giảm 70% sát thương 0.4s; đỡ trúng phản kích 180% và +2 Kiếm Ý; hụt chỉ giảm 20%",
            "Tầm Long": "Lao 5.5m, gây 150% lên mục tiêu đầu; không xuyên vật cản; +1 Kiếm Ý",
            "Vạn Tượng Quy Nhất (tuyệt kỹ)": "Đường kiếm 7m: 260% + 60% mỗi Kiếm Ý, tối đa 5",
        },
    ),
    "Ảnh Đao": (
        "Nhiệt",
        "Đòn trúng cho +1 Nhiệt tối đa mỗi 1.5s; né thành công +1.",
        {
            "Tàn Hỏa": "Dấu 5s; đòn sau nổ 120% vùng nhỏ; đủ 5 Nhiệt thì 180%",
            "Tử Diệm (tuyệt kỹ)": "230% vùng nhỏ +45% mỗi Nhiệt, tiêu sạch Nhiệt",
        },
    ),
    "Huyền Bút": (
        "Thủy Ấn",
        "Mỗi chuỗi 3 đòn thường tạo 1 Thủy Ấn; kỹ năng hồi phục tiêu 2 ấn để tăng hồi.",
        {
            "Mưa Tinh": "Bán kính 3m hồi 8% HP +2%/s trong 3s; tiêu 2 ấn tăng tổng hồi 30%",
        },
    ),
    "Thạch Chùy": (
        "Thế",
        "Đánh thường trúng hoặc chặn sát thương cho +1 Thế, tối đa một lần mỗi 2s.",
        {
            "Thiết Bích": "Giảm 25% sát thương nhận 4s; tiêu 2 Thế tăng lên 35%",
            "Sơn Thần Giáng Thế (tuyệt kỹ)": "Vùng chắn 4m trong 5s, gây 180%; tiêu Thế thêm tối đa 2s",
        },
    ),
    "Linh Cung": (
        "Mộc Tiêu",
        "Đánh thường bắn 3 tên; trúng cùng mục tiêu tích 1 Mộc Tiêu mỗi 2s, đổi mục tiêu đặt lại chuỗi.",
        {
            "Bách Tiễn Quy Tông (tuyệt kỹ)": "Báo vùng 1.2s, mưa tên 6m tổng 300%; tiêu 3 Mộc Tiêu tăng 20%",
        },
    ),
}
STATUS_PINS = {
    "bible": {
        "Chậm": ["giảm tốc; boss chỉ 10%, PvP tối đa 25%"],
        "Khiên": ["hấp thụ trước HP; không cộng dồn, lấy khiên lớn nhất"],
    },
    "rules": {
        "slow": [
            "mạnh nhất, lấy expiry của application mạnh nhất; cap50%",
            "boss miễn chậm, PvP cap30%", "slow",
        ],
        "shield": [
            "cùng skill giữ lớn nhất; source khác được tồn tại, tổng cap30% maxHP",
            "PvP cap20%", "không dispel mặc định",
        ],
    },
}
RESOURCE_RULE = "Resource lớp cap5; chết/đổi map về0, đổi target chỉ reset Mộc Tiêu như Combat Spec."
CREATE_RULE = "nhân vật cấp 10+, chưa thuộc bang, trả 20.000 Đồng và 10 Huy hiệu Thanh Lạc."
DONATION_RULE = "Mỗi thành viên đóng góp tối đa 5.000 Đồng/ngày và 30 đơn vị vật liệu bang/ngày tính XP, chặn alt-farm."
TREASURY_RULE = "hai sổ cái tách: Đồng thường và Điểm Công Trình."
CURRENCY_HEADER = "currency_id,display_name_vi,currency_type,tradeable,storage_scope,balance_cap,daily_cap,weekly_reset,sources,sinks,notes".split(",")
CONTRIBUTION_NOTES = "50 per eligible guild quest; donation exchange 1000 COIN:1; bound to earning character"


class Drift(Exception):
    def __init__(self, name: str, detail: str):
        self.name = name
        super().__init__(f"{name}: {detail}")


def require(condition: bool, name: str, detail: str) -> None:
    if not condition:
        raise Drift(name, detail)


def pin(actual: object, expected: object, name: str) -> None:
    require(actual == expected, name, f"expected {expected!r}; actual {actual!r}")


def unique(items: list, name: str):
    require(len(items) == 1, name, f"expected unique selection; found {len(items)}")
    return items[0]


def text(sources: dict[str, str], alias: str) -> str:
    path = SOURCES.get(alias, alias)
    require(path in sources, f"source.{alias}", f"missing {path}")
    return sources[path]


def ref(alias: str, line: int) -> str:
    return f"{SOURCES.get(alias, alias)}:{line}"


def section(sources: dict[str, str], alias: str, heading: str, name: str) -> list[tuple[int, str]]:
    lines = list(enumerate(text(sources, alias).splitlines(), 1))
    index = unique([i for i, (_, line) in enumerate(lines) if line == heading], name)
    level = len(heading.split(" ", 1)[0])
    end = next((i for i in range(index + 1, len(lines))
                if re.match(rf"^#{{1,{level}}} ", lines[i][1])), len(lines))
    return lines[index + 1:end]


def cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def table(lines: list[tuple[int, str]], headers: list[str], name: str) -> list[dict]:
    index = unique([i for i, (_, line) in enumerate(lines)
                    if line.startswith("|") and cells(line) == headers], f"{name}.header")
    require(index + 1 < len(lines), f"{name}.separator", "missing separator")
    separator = cells(lines[index + 1][1])
    require(len(separator) == len(headers) and all(re.fullmatch(r":?-{3,}:?", c) for c in separator),
            f"{name}.separator", "invalid separator")
    rows = []
    for number, line in lines[index + 2:]:
        if not line.startswith("|"):
            break
        values = cells(line)
        require(len(values) == len(headers), f"{name}.columns", f"invalid row at line {number}")
        rows.append({"cells": values, "line": number})
    return rows


def selected(rows: list[dict], key: str, name: str) -> dict:
    return unique([row for row in rows if row["cells"][0] == key], name)


def match(pattern: str, raw: str, name: str) -> re.Match:
    return unique(list(re.finditer(pattern, raw)), name)


def number(pattern: str, raw: str, expected: int, name: str) -> int:
    value = int(match(pattern, raw, name).group(1).replace(".", ""))
    pin(value, expected, name)
    return value


def fragment(lines: list[tuple[int, str]], pattern: str, alias: str, name: str) -> dict:
    found = [(line, m.group(0)) for line, raw in lines for m in re.finditer(pattern, raw)]
    line, raw = unique(found, name)
    return {"raw": raw, "sourceRefs": [ref(alias, line)]}


def load_sources() -> dict[str, str]:
    paths = set(SOURCES.values())
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / EXAMPLES).glob("*.json"))
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / SKILL_EXAMPLES).glob("*.json"))
    sources = {}
    for path in sorted(paths):
        try:
            sources[path] = (ROOT / path).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            raise Drift(f"source.{path}", str(exc)) from exc
    return sources


def extract_skills(sources: dict[str, str], bible_skills: dict[str, dict]) -> dict[str, dict]:
    library = section(sources, "skills", "## Thư viện 30 kỹ năng", "skills.library")
    class_headings = [raw for _, raw in library if raw.startswith("### ")]
    pin(sorted(h.split(" — ", 1)[0][4:] for h in class_headings), sorted(SKILL_PINS), "skills.spec.classes")
    records = {}
    for class_name, (prefix, baseline) in SKILL_PINS.items():
        heading = unique([raw for raw in class_headings if raw.startswith(f"### {class_name} — ")],
                         f"skills.spec.{class_name}.section")
        lines = section(sources, "skills", heading, f"skills.spec.{class_name}.section")
        headers = [(index, header_match.group(1), header_match.group(2)) for index, (_, raw) in enumerate(lines)
                   if (header_match := re.fullmatch(r"\*\*(SK-[A-Z0-9]+-[A-Z0-9]+) — (.+)\*\*\s*", raw))]
        expected = {f"SK-{prefix}-{index:02}": name for index, (name, _, _) in enumerate(baseline, 1)}
        pin(sorted(sid for _, sid, _ in headers), sorted(expected), f"skills.spec.{CLASS_IDS[class_name]}.ids")
        for position, (index, sid, name) in enumerate(headers):
            pin(name, expected[sid], f"skills.spec.{sid}.name")
            end = headers[position + 1][0] if position + 1 < len(headers) else len(lines)
            body = [(line, raw) for line, raw in lines[index + 1:end] if raw.strip()]
            require(bool(body), f"skills.spec.{sid}.body", "missing mechanics text")
            raw = "\n".join(value for _, value in body)
            cost = match(r"CD (\d+)s[,;] (\d+) MP", raw, f"skills.spec.{sid}.cost")
            parsed = (int(cost.group(1)), int(cost.group(2)))
            bible = bible_skills[sid]
            pin(parsed, (bible["cooldownSeconds"], bible["mpCost"]), f"skills.spec.{sid}.cost")
            records[sid] = {**bible, "rawSpecMechanics": raw, "rawSpecHeading": lines[index][1],
                            "sourceRefs": [ref("skills", lines[index][0]), ref("skills", body[0][0]), *bible["sourceRefs"]],
                            "exampleSourceRef": None}
    examples = set()
    for path in sorted(p for p in sources if p.startswith(f"{SKILL_EXAMPLES}/")):
        def pairs(values):
            keys = [key for key, _ in values]
            require(len(set(keys)) == len(keys), "skills.example.keys", f"duplicate key in {path}")
            return dict(values)
        try:
            data = json.loads(sources[path], object_pairs_hook=pairs)
        except ValueError as exc:
            raise Drift("skills.example.json", f"{path}: {exc}") from exc
        require(isinstance(data, dict), "skills.example.json", f"not an object: {path}")
        sid = data.get("skillId")
        require(isinstance(sid, str) and sid in records, "skills.example.id", f"unknown skillId {sid!r}")
        require(sid not in examples, "skills.example.id", f"duplicate skillId {sid}")
        pin(Path(path).stem, sid, f"skills.example.{sid}.filename")
        record = records[sid]
        pin(data.get("classId"), record["classId"], f"skills.example.{sid}.classId")
        pin(data.get("cooldownSeconds"), record["cooldownSeconds"], f"skills.example.{sid}.cooldownSeconds")
        pin(data.get("resourceCost"), {"resource": "MP", "amount": record["mpCost"]}, f"skills.example.{sid}.resourceCost")
        line = unique([i for i, raw in enumerate(sources[path].splitlines(), 1)
                       if re.search(r'"skillId"\s*:', raw)], f"skills.example.{sid}.line")
        record["exampleSourceRef"] = ref(path, line)
        examples.add(sid)
    require(SHIPPED_SKILL_IDS <= examples, "skills.example.required", f"missing shipped skills: {sorted(SHIPPED_SKILL_IDS - examples)}")
    return records


def extract(sources: dict[str, str]) -> dict:
    class_rows = table(section(sources, "classes", "### 1. Vòng đời nhân vật", "classes.section"),
                       ["ID", "Tên", "Ngũ hành", "Vai trò thiết kế", "Vũ khí", "Độ khó"], "classes.table")
    examples = {}
    text(sources, "example")  # The existing example is required, not an optional fallback.
    for path in sorted(p for p in sources if p.startswith(f"{EXAMPLES}/")):
        def pairs(values):
            keys = [key for key, _ in values]
            require(len(set(keys)) == len(keys), "classes.example.keys", f"duplicate key in {path}")
            return dict(values)
        try:
            data = json.loads(sources[path], object_pairs_hook=pairs)
        except ValueError as exc:
            raise Drift("classes.example.json", f"{path}: {exc}") from exc
        require(isinstance(data, dict), "classes.example.json", f"not an object: {path}")
        class_id = data.get("classId")
        require(class_id in CLASS_IDS.values(), "classes.example.id", f"unknown classId {class_id!r}")
        require(class_id not in examples, "classes.example.id", f"duplicate classId {class_id}")
        pin(data.get("displayNameKey"), f"CLASS.{class_id}.NAME", "classes.example.displayNameKey")
        line = unique([i for i, raw in enumerate(sources[path].splitlines(), 1)
                       if re.search(r'"classId"\s*:', raw)], "classes.example.id.line")
        examples[class_id] = ref(path, line)
    pin(json.loads(text(sources, "example")).get("classId"), "CLASS_MINH_KIEM", "classes.example.minh_kiem")

    resources = []
    bible_skills = {}
    for class_name, (resource_name, gain_pin, skill_pins) in RESOURCE_PINS.items():
        class_id = CLASS_IDS[class_name]
        identity = selected(class_rows, class_id, f"classes.{class_id}.row")
        pin(identity["cells"][1], class_name, f"classes.{class_id}.name")
        heading_line, heading = unique([(i, raw) for i, raw in enumerate(text(sources, "bible").splitlines(), 1)
                                       if raw.startswith(f"### {class_name} — ")], f"resource.{class_id}.header")
        bounds = match(r" — (.+) (\d+)–(\d+)$", heading, f"resource.{class_id}.range")
        pin(bounds.group(1), resource_name, f"resource.{class_id}.name")
        low, high = int(bounds.group(2)), int(bounds.group(3))
        pin(low, 0, f"resource.{class_id}.min")
        pin(high, 5, f"resource.{class_id}.max")
        lines = section(sources, "bible", heading, f"resource.{class_id}.header")
        skill_rows = table(lines, ["Kỹ năng", "CD / MP", "Hiệu lực cấp 1"], f"resource.{class_id}.skills")
        prefix, baseline = SKILL_PINS[class_name]
        pin(sorted(row["cells"][0] for row in skill_rows), sorted(name for name, _, _ in baseline),
            f"skills.bible.{class_id}.names")
        for index, (skill_name, cooldown, mp_cost) in enumerate(baseline, 1):
            sid = f"SK-{prefix}-{index:02}"
            row = selected(skill_rows, skill_name, f"skills.bible.{sid}.row")
            cost = match(r"^(\d+)s / (\d+)$", row["cells"][1], f"skills.bible.{sid}.cost")
            parsed_cd, parsed_mp = int(cost.group(1)), int(cost.group(2))
            pin((parsed_cd, parsed_mp), (cooldown, mp_cost), f"skills.bible.{sid}.cost")
            bible_skills[sid] = {"skillId": sid, "classId": class_id, "name": skill_name,
                                 "cooldownSeconds": parsed_cd, "mpCost": parsed_mp,
                                 "rawBibleCost": row["cells"][1], "rawBibleMechanics": row["cells"][2],
                                 "sourceRefs": [ref("bible", row["line"]), ref("classes", identity["line"])]}
        first_table = next(i for i, (_, raw) in enumerate(lines) if raw.startswith("|"))
        gain_line, gain = unique([(i, raw) for i, raw in lines[:first_table] if raw.strip()], f"resource.{class_id}.gain")
        pin(gain, gain_pin, f"resource.{class_id}.gain")
        relevant = [row for row in skill_rows if resource_name in row["cells"][2]
                    or (resource_name == "Thủy Ấn" and re.search(r"tiêu \d+ ấn", row["cells"][2]))]
        require(len({r["cells"][0] for r in relevant}) == len(relevant),
                f"resource.{class_id}.skill_rows", "duplicate resource skill")
        pin({r["cells"][0]: r["cells"][2] for r in relevant}, skill_pins, f"resource.{class_id}.skill_text")
        skills = [{"skill": r["cells"][0], "raw": r["cells"][2], "sourceRefs": [ref("bible", r["line"])]}
                  for r in relevant]
        spend = [s for s in skills if re.search(r"(?:^|[;,] )tiêu ", s["raw"])
                 or (resource_name == "Kiếm Ý" and "(tuyệt kỹ)" in s["skill"])]
        id_refs = [examples[class_id]] if class_id in examples else [ref("classes", identity["line"])]
        resources.append({"classId": class_id, "name": resource_name, "min": low, "max": high,
                          "rawGainText": gain, "rawSkillResourceText": skills, "rawSkillSpendText": spend,
                          "classIdSource": "ClassDefinition" if class_id in examples else "canonical class table; example absent",
                          "sourceRefs": [ref("bible", heading_line), ref("bible", gain_line), *id_refs]})

    rule = fragment(section(sources, "rules", "## 3. Status registry", "rules.section"),
                    r"Resource lớp [^\n]+", "rules", "resource.rules.row")
    raw = rule["raw"]
    rule["cap"] = number(r"Resource lớp cap(\d+)", raw, 5, "resource.rules.cap")
    rule["deathMapReset"] = number(r"chết/đổi map về(\d+)", raw, 0, "resource.rules.death_map_reset")
    rule["targetResetResource"] = match(r"đổi target chỉ reset (.+) như Combat Spec\.", raw, "resource.rules.target_reset").group(1)
    pin(rule["targetResetResource"], "Mộc Tiêu", "resource.rules.target_reset")
    pin(raw, RESOURCE_RULE, "resource.rules.raw")

    status = {}
    for alias, heading, headers in (
        ("bible", "## 6. Trạng thái hiệu ứng", ["Hiệu ứng", "Quy tắc"]),
        ("rules", "## 3. Status registry", ["Status", "Stack/refresh", "Boss/PvP", "Cleanse"]),
    ):
        rows = table(section(sources, alias, heading, f"status.{alias}.section"), headers, f"status.{alias}.table")
        status[alias] = {}
        for key in STATUS_PINS[alias]:
            row = selected(rows, key, f"status.{alias}.{key}.row")
            status[alias][key] = {"rawCells": row["cells"][1:], "sourceRefs": [ref(alias, row["line"])]}
    bible_slow = status["bible"]["Chậm"]
    bible_slow["parsed"] = {
        "bossSlowPercent": number(r"boss chỉ (\d+)%", bible_slow["rawCells"][0], 10, "slow.bible.boss_percent"),
        "pvpCapPercent": number(r"PvP tối đa (\d+)%", bible_slow["rawCells"][0], 25, "slow.bible.pvp_cap"),
        "globalCapPercent": None,
    }
    rules_slow = status["rules"]["slow"]
    immune = "boss miễn chậm" in rules_slow["rawCells"][1]
    pin(immune, True, "slow.rules.boss_immunity")
    rules_slow["parsed"] = {
        "bossImmune": immune,
        "pvpCapPercent": number(r"PvP cap(\d+)%", rules_slow["rawCells"][1], 30, "slow.rules.pvp_cap"),
        "globalCapPercent": number(r"cap(\d+)%", rules_slow["rawCells"][0], 50, "slow.rules.global_cap"),
    }
    bible_shield = status["bible"]["Khiên"]
    bible_shield["parsed"] = {"globalNonstackStrongest": "không cộng dồn, lấy khiên lớn nhất" in bible_shield["rawCells"][0],
                              "totalHpCapPercent": None, "pvpHpCapPercent": None}
    rules_shield = status["rules"]["shield"]
    rules_shield["parsed"] = {
        "sameSkillStrongest": "cùng skill giữ lớn nhất" in rules_shield["rawCells"][0],
        "differentSourcesCoexist": "source khác được tồn tại" in rules_shield["rawCells"][0],
        "totalHpCapPercent": number(r"tổng cap(\d+)% maxHP", rules_shield["rawCells"][0], 30, "shield.rules.hp_cap"),
        "pvpHpCapPercent": number(r"PvP cap(\d+)%", rules_shield["rawCells"][1], 20, "shield.rules.pvp_cap"),
    }
    for alias, policies in STATUS_PINS.items():
        for key, expected in policies.items():
            pin(status[alias][key]["rawCells"], expected, f"status.{alias}.{key}.cells")

    creation = fragment(section(sources, "guild", "### 2. Tạo bang và vòng đời", "guild.creation.section"),
                        r"(?<=\*\*Điều kiện tạo:\*\* )[^\n]+?Thanh Lạc\.", "guild", "guild.creation.row")
    creation["minLevel"] = number(r"cấp (\d+)\+", creation["raw"], 10, "guild.creation.level")
    creation["coin"] = number(r"trả ([\d.]+) Đồng", creation["raw"], 20000, "guild.creation.coin")
    creation["badges"] = number(r"và (\d+) Huy hiệu Thanh Lạc", creation["raw"], 10, "guild.creation.badges")
    creation["badgeId"] = None
    pin(creation["raw"], CREATE_RULE, "guild.creation.raw")
    donation = fragment(section(sources, "guild", "### 4. Cấp bang, XP và mở khóa", "guild.donation.section"),
                        r"Mỗi thành viên đóng góp[^\n]+", "guild", "guild.donation.row")
    donation["limits"] = [
        {"amount": number(r"tối đa ([\d.]+) Đồng/ngày", donation["raw"], 5000, "guild.donation.coin_cap"),
         "unit": "COIN", "scope": "member/day", "eligibility": "guild XP"},
        {"amount": number(r"và (\d+) đơn vị vật liệu bang/ngày", donation["raw"], 30, "guild.donation.material_cap"),
         "unit": "guild-material units", "scope": "member/day", "eligibility": "guild XP"},
    ]
    pin(donation["raw"], DONATION_RULE, "guild.donation.raw")
    treasury = fragment(section(sources, "guild", "### 5. Kho bang, quỹ và công trình", "guild.treasury.section"),
                        r"(?<=\*\*Quỹ bang:\*\* )[^\n]+?Công Trình\.", "guild", "guild.treasury.row")
    ledgers = match(r"hai sổ cái tách: (.+)\.", treasury["raw"], "guild.treasury.ledgers").group(1).split(" và ")
    pin(ledgers, ["Đồng thường", "Điểm Công Trình"], "guild.treasury.ledgers")
    treasury["ledgers"] = [{"name": name, "currencyIdMapping": None} for name in ledgers]
    pin(treasury["raw"], TREASURY_RULE, "guild.treasury.raw")

    csv_rows = list(csv.reader(io.StringIO(text(sources, "currency"))))
    unique([r for r in csv_rows if r == CURRENCY_HEADER], "currency.header")
    pin(csv_rows[0] if csv_rows else [], CURRENCY_HEADER, "currency.header")
    target = unique([(i, r) for i, r in enumerate(csv_rows, 1) if r and r[0] == "CURRENCY_GUILD_CONTRIBUTION"],
                    "contribution.row")
    line, values = target
    pin(len(values), len(CURRENCY_HEADER), "contribution.columns")
    row = dict(zip(CURRENCY_HEADER, values))
    coin = unique([r for r in csv_rows if r and r[0] == "COIN"], "currency.coin.row")
    pin(len(coin), len(CURRENCY_HEADER), "currency.coin.columns")
    pin(coin[1], "Đồng", "currency.coin.name")
    contribution = {"currencyId": row["currency_id"], "unit": "contribution points",
                    "scope": row["storage_scope"], "sourceRefs": [ref("currency", line)],
                    "rawCells": {key: row[key] for key in ("currency_type", "tradeable", "storage_scope", "daily_cap", "notes")}}
    contribution["dailyCap"] = number(r"^(\d+)$", row["daily_cap"], 5000, "contribution.daily_cap")
    pin(row["storage_scope"], "character", "contribution.owner")
    pin(row["currency_type"], "SOCIAL", "contribution.type")
    pin(row["tradeable"], "false", "contribution.tradeable")
    contribution["exchange"] = {
        "coin": number(r"donation exchange (\d+) COIN:", row["notes"], 1000, "contribution.exchange.coin"),
        "points": number(r"COIN:(\d+)", row["notes"], 1, "contribution.exchange.points"),
    }
    pin(row["notes"], CONTRIBUTION_NOTES, "contribution.notes")
    return {"resources": resources, "resourceRule": rule, "status": status,
            "creation": creation, "donation": donation, "treasury": treasury,
            "contribution": contribution, "examples": examples,
            "skills": extract_skills(sources, bible_skills)}


def compact(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def refs(record: dict) -> str:
    aliases = {path: alias for alias, path in SOURCES.items()}
    return ",".join(f"{aliases.get(path, path)}:{line}"
                    for path, line in (r.rsplit(":", 1) for r in record["sourceRefs"]))


def report(data: dict) -> None:
    for alias, path in SOURCES.items():
        print(f"source {alias}={path}")
    resources, status = data["resources"], data["status"]
    missing = [r["classId"] for r in resources if r["classId"] not in data["examples"]]
    print(f"collections: resources={len(resources)} resource-skill-cells={sum(len(r['rawSkillResourceText']) for r in resources)} "
          f"selected-status-rows={sum(len(rows) for rows in status.values())} "
          f"treasury-ledgers={len(data['treasury']['ledgers'])} class-examples={len(data['examples'])}")
    print(f"UNRESOLVED class-definition-examples: {len(missing)} absent -> {','.join(missing)}; IDs explicitly sourced from classes table")
    for resource in resources:
        print(f"resource {resource['classId']} {resource['name']}={resource['min']}–{resource['max']} sourceRefs={refs(resource)}")
        print(f"  rawGainText={compact(resource['rawGainText'])}")
        spend_names = {s["skill"] for s in resource["rawSkillSpendText"]}
        for skill in resource["rawSkillResourceText"]:
            kind = "rawSkillSpendText" if skill["skill"] in spend_names else "rawSkillResourceText"
            print(f"  {kind} {skill['skill']}={compact(skill['raw'])} sourceRefs={refs(skill)}")
    rule = data["resourceRule"]
    print(f"resource-reset: cap={rule['cap']} death/map={rule['deathMapReset']} target-only={rule['targetResetResource']} "
          f"raw={compact(rule['raw'])} sourceRefs={refs(rule)}")
    for alias, rows in status.items():
        for key, record in rows.items():
            print(f"status {alias}.{key}: rawCells={compact(record['rawCells'])} parsed={compact(record['parsed'])} sourceRefs={refs(record)}")
    for key in ("creation", "donation", "treasury", "contribution"):
        record = data[key]
        print(f"guild {key}: {compact({k: v for k, v in record.items() if k != 'sourceRefs'})} sourceRefs={refs(record)}")
    bslow, rslow = status["bible"]["Chậm"]["parsed"], status["rules"]["slow"]["parsed"]
    bshield, rshield = status["bible"]["Khiên"]["parsed"], status["rules"]["shield"]["parsed"]
    divergences = {
        "slow.boss": f"Bible {bslow['bossSlowPercent']}% vs Rules immunity={rslow['bossImmune']}",
        "slow.pvp": f"Bible {bslow['pvpCapPercent']}% vs Rules {rslow['pvpCapPercent']}%",
        "slow.global-cap": f"Bible unspecified vs Rules {rslow['globalCapPercent']}%",
        "shield.stacking": f"Bible global nonstack strongest={bshield['globalNonstackStrongest']} vs Rules same-skill strongest={rshield['sameSkillStrongest']}, different sources coexist={rshield['differentSourcesCoexist']}",
        "shield.hp-cap": f"Bible unspecified vs Rules {rshield['totalHpCapPercent']}% maxHP",
        "shield.pvp-cap": f"Bible unspecified vs Rules {rshield['pvpHpCapPercent']}%",
        "guild.cap-units": f"XP donation {data['donation']['limits'][0]['amount']} COIN/member/day != currency {data['contribution']['dailyCap']} contribution points/character/day; not equated",
    }
    print(f"named-divergences={len(divergences)} (no precedence applied)")
    for name, value in divergences.items():
        print(f"DIVERGENCE {name}: {value}")
    skills = data["skills"]
    missing_skills = sorted(sid for sid, skill in skills.items() if skill["exampleSourceRef"] is None)
    example_count = sum(skill["exampleSourceRef"] is not None for skill in skills.values())
    print(f"skill-source-coverage: canonical={len(skills)} classes={len({s['classId'] for s in skills.values()})} "
          f"examples={example_count} absent={len(missing_skills)}; checked ID/name/class/CD/MP only, not runtime mechanics")
    for sid, skill in skills.items():
        print(f"skill {sid} class={skill['classId']} CD={skill['cooldownSeconds']} MP={skill['mpCost']} "
              f"sourceRefs={refs(skill)} example={skill['exampleSourceRef'] or 'ABSENT'}")
        print(f"  rawBibleMechanics={compact(skill['rawBibleMechanics'])}")
        print(f"  rawSpecMechanics={compact(skill['rawSpecMechanics'])}")
    print(f"UNRESOLVED skill-definition-examples: {','.join(missing_skills)}")
    print("UNRESOLVED badge-ID and treasury/currency mappings: no inferred mapping")
    print("UNSUPPORTED runtime application: source reconciliation does not implement skill mechanics or status/guild services, "
          "change MP costs, authorize startingSkillIds or widen wire; raw mechanics are retained, not normalized or fully pinned")
    print("OK: current pinned disagreements preserved; no source drift")


def self_test(sources: dict[str, str]) -> int:
    baseline = extract(sources)
    cases = [
        ("resource-max-5-to-4", "bible", "Kiếm Ý 0–5", "Kiếm Ý 0–4", "resource.CLASS_MINH_KIEM.max"),
        ("rules-resource-cap-5-to-4", "rules", "Resource lớp cap5", "Resource lớp cap4", "resource.rules.cap"),
        ("slow-pvp-25-to-24", "bible", "PvP tối đa 25%", "PvP tối đa 24%", "slow.bible.pvp_cap"),
        ("rules-boss-immunity-change", "rules", "boss miễn chậm", "boss chịu chậm", "slow.rules.boss_immunity"),
        ("rules-slow-pvp-cap-30-to-31", "rules", "boss miễn chậm, PvP cap30%", "boss miễn chậm, PvP cap31%", "slow.rules.pvp_cap"),
        ("rules-slow-global-cap-50-to-51", "rules", "cap50% | boss", "cap51% | boss", "slow.rules.global_cap"),
        ("shield-30-to-31", "rules", "tổng cap30% maxHP", "tổng cap31% maxHP", "shield.rules.hp_cap"),
        ("donation-5000-to-5001", "guild", "5.000 Đồng/ngày", "5.001 Đồng/ngày", "guild.donation.coin_cap"),
        ("contribution-daily-cap-5000-to-5001", "currency", ",100000,5000,", ",100000,5001,", "contribution.daily_cap"),
        ("exchange-1000-to-1001", "currency", "exchange 1000 COIN:1", "exchange 1001 COIN:1", "contribution.exchange.coin"),
    ]
    for alias, policies in STATUS_PINS.items():
        for key, raw in policies.items():
            row = "| " + " | ".join([key, *raw]) + " |\n"
            cases.extend([
                (f"remove-{alias}-{key}", alias, row, "", f"status.{alias}.{key}.row"),
                (f"duplicate-{alias}-{key}", alias, row, row + row, f"status.{alias}.{key}.row"),
            ])
    header = "| Hiệu ứng | Quy tắc |\n"
    cases.extend([
        ("remove-status-header", "bible", header, "", "status.bible.table.header"),
        ("duplicate-status-header", "bible", header, header + header, "status.bible.table.header"),
    ])
    for sid, skill in baseline["skills"].items():
        heading = skill["rawSpecHeading"] + "\n"
        raw = skill["rawSpecMechanics"]
        cooldown, mp = skill["cooldownSeconds"], skill["mpCost"]
        cost = match(r"CD \d+s[,;] \d+ MP", raw, f"self-test.{sid}.cost").group(0)
        bible_row = f"| {skill['name']} | {skill['rawBibleCost']} | {skill['rawBibleMechanics']} |\n"
        cases.extend([
            (f"remove-spec-{sid}", "skills", heading, "", f"skills.spec.{skill['classId']}.ids"),
            (f"duplicate-spec-{sid}", "skills", heading, heading + heading, f"skills.spec.{skill['classId']}.ids"),
            (f"unknown-id-{sid}", "skills", heading, heading.replace(sid, sid[:-2] + "99"), f"skills.spec.{skill['classId']}.ids"),
            (f"rename-spec-{sid}", "skills", heading, heading.replace(skill["name"], "UNSOURCED"), f"skills.spec.{sid}.name"),
            (f"spec-cd-{sid}", "skills", raw, raw.replace(cost, cost.replace(f"{cooldown}s", f"{cooldown + 1}s")), f"skills.spec.{sid}.cost"),
            (f"spec-mp-{sid}", "skills", raw, raw.replace(cost, cost.replace(f"{mp} MP", f"{mp + 1} MP")), f"skills.spec.{sid}.cost"),
            (f"remove-bible-{sid}", "bible", bible_row, "", f"skills.bible.{skill['classId']}.names"),
            (f"duplicate-bible-{sid}", "bible", bible_row, bible_row + bible_row, f"skills.bible.{skill['classId']}.names"),
            (f"bible-cd-{sid}", "bible", bible_row, bible_row.replace(skill["rawBibleCost"], f"{cooldown + 1}s / {mp}"), f"skills.bible.{sid}.cost"),
            (f"bible-mp-{sid}", "bible", bible_row, bible_row.replace(skill["rawBibleCost"], f"{cooldown}s / {mp + 1}"), f"skills.bible.{sid}.cost"),
        ])
        if skill["exampleSourceRef"] is not None:
            path = skill["exampleSourceRef"].rsplit(":", 1)[0]
            current = text(sources, path)
            for key, value in (("classId", "CLASS_UNSOURCED"), ("cooldownSeconds", cooldown + 1),
                               ("resourceCost", {"resource": "MP", "amount": mp + 1}),
                               ("resourceCost", {"resource": "HEAT", "amount": mp})):
                changed_example = json.loads(current)
                changed_example[key] = value
                cases.append((f"example-{sid}-{key}-{value}", path, current, compact(changed_example), f"skills.example.{sid}.{key}"))
            cases.append((f"duplicate-json-key-{sid}", path, '"skillId":', f'"skillId": "{sid}", "skillId":', "skills.example.keys"))
    passed = []
    for label, alias, old, new, diagnostic in cases:
        current = text(sources, alias)
        require(current.count(old) == 1, f"self-test.{label}.fixture", "mutation must select exactly one source span")
        changed = dict(sources)
        changed[SOURCES.get(alias, alias)] = current.replace(old, new, 1)
        try:
            extract(changed)
        except Drift as exc:
            require(exc.name == diagnostic, f"self-test.{label}.diagnostic", f"expected {diagnostic}; got {exc}")
        else:
            raise Drift(f"self-test.{label}", f"mutation passed; expected {diagnostic}")
        passed.append(label)
        print(f"PASS {label} -> {diagnostic}")
    missing_cases = [(SOURCES[alias], f"source.{alias}") for alias in ("bible", "skills")]
    missing_cases.extend((f"{SKILL_EXAMPLES}/{sid}.json", "skills.example.required") for sid in sorted(SHIPPED_SKILL_IDS))
    for path, diagnostic in missing_cases:
        changed = dict(sources)
        del changed[path]
        try:
            extract(changed)
        except Drift as exc:
            pin(exc.name, diagnostic, f"self-test.missing-{path}.diagnostic")
        else:
            raise Drift(f"self-test.missing-{path}", "missing source passed")
        passed.append(f"missing-{path}")
        print(f"PASS missing-{path} -> {diagnostic}")
    extract(sources)
    print(f"SELF-TEST OK: {len(passed)} independent drift cases rejected; restored current sources pass; in-memory only")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="mutate in-memory source copies")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        sources = load_sources()
        if args.self_test:
            return self_test(sources)
        report(extract(sources))
        return 0
    except Drift as exc:
        print(f"DRIFT {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
