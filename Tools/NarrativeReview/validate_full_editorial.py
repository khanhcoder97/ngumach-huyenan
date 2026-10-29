"""Validate the full dialogue edit against its immutable Git source and export a readthrough.

Only copy/status can change in this editorial batch. No engine/voice approval.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import re
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV = 'docs/production/Quest_Dialogue_Production_Data_vi.csv'
BASE = ROOT / 'Tools/NarrativeReview/baseline_20261029.json'
REPORT = ROOT / 'Implementation/Reports/Dialogue_Editorial_Full_20261029.json'
READTHROUGH = ROOT / 'docs/production/Dialogue_Readthrough_vi.md'
EDITABLE = {'text_vi', 'localization_status'}


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text_sha(path):
    return sha(path.read_bytes().replace(b'\r\n', b'\n'))


def parse_csv(text):
    reader = csv.DictReader(io.StringIO(text.lstrip('\ufeff')))
    return reader.fieldnames, list(reader)


def logic(rows, fields):
    return [{k: r[k] for k in fields if k not in EDITABLE} for r in rows]


def validate():
    baseline = json.loads(BASE.read_text(encoding='utf-8-sig'))
    fields, rows = parse_csv((ROOT / CSV).read_text(encoding='utf-8-sig'))
    source_commit = baseline['sourceCommit']
    if not re.fullmatch('[0-9a-f]{40}', source_commit):
        raise ValueError('Invalid baseline Git revision')
    try:
        original_text = subprocess.check_output(
            ['git', 'show', source_commit + ':' + CSV], cwd=ROOT, stderr=subprocess.PIPE).decode('utf-8-sig')
    except subprocess.CalledProcessError as exc:
        raise ValueError('Fetch Git history containing editorial baseline ' + source_commit) from exc
    old_fields, original = parse_csv(original_text)
    if fields != old_fields or fields != baseline['fields']:
        raise ValueError('CSV headers changed')
    if len(rows) != 230 or len(original) != 230:
        raise ValueError('Expected exactly 230 original rows')
    digest = sha(canonical(logic(original, fields)))
    if digest != baseline['logicSha256'] or sha(canonical(logic(rows, fields))) != digest:
        raise ValueError('Non-editorial field or row order changed')
    old_records = [dict(key=[r['quest_id'], r['node_id'], r['choice_id']], status=r['localization_status'],
                        textSha256=sha(r['text_vi'].encode('utf-8'))) for r in original]
    if baseline['rows'] != old_records:
        raise ValueError('Baseline manifest does not match immutable Git source')
    keys = [tuple(r[k] for k in ('quest_id', 'node_id', 'choice_id')) for r in rows]
    if len(set(keys)) != len(keys):
        raise ValueError('Duplicate dialogue/choice identity')
    errors, changed = [], []
    for old, row in zip(original, rows):
        key = row['node_id'] + (':' + row['choice_id'] if row['choice_id'] else '')
        text = row['text_vi']
        if not text.strip() or text != unicodedata.normalize('NFC', text):
            errors.append(key + ': empty/non-NFC text')
        if re.search(r'(?:NPC_|MAP_|MOB_|OBJ_|DLG_|QUEST_)|\b(?:instance|server|respawn|DPS|checkpoint)\b|\b[xy]\s*=', text, re.I):
            errors.append(key + ': technical identifier in spoken copy')
        if any(s in text for s in ('Ta cần ngươi giúp việc này:', 'Quan sát dấu hiệu, làm từng mục tiêu theo nhật ký',
                                    'mục tiêu đã hoàn tất sẽ được lưu', 'chuyển phần thưởng vào túi')):
            errors.append(key + ': unedited template or premature reward claim')
        if old['localization_status'] != 'VI_BASELINE':
            if row != old:
                errors.append(key + ': earlier 33 edited rows must stay unchanged')
        else:
            expected = 'VI_EDITED_SIDE' if row['quest_id'].startswith('SQ-') else 'VI_EDITED_CAMPAIGN'
            if text == old['text_vi'] or row['localization_status'] != expected:
                errors.append(key + ': remaining baseline copy not edited')
            changed.append(key)
    if len(changed) != 197:
        errors.append('Expected exactly 197 new edits')
    by_text, choices = collections.defaultdict(list), collections.defaultdict(list)
    for row in rows:
        by_text[row['text_vi']].append(row)
        if row['node_type'] == 'CHOICE':
            choices[(row['graph_id'], row['node_id'], row['choice_group_id'])].append(row)
    for group in by_text.values():
        if len(group) > 1 and (any(r['node_type'] != 'CHOICE' for r in group) or
                len({(r['graph_id'], r['node_id'], r['choice_group_id']) for r in group}) != 1):
            errors.append('Repeated full dialogue text outside a shared choice prompt')
    for key, group in choices.items():
        if len({r['text_vi'] for r in group}) != 1:
            errors.append(str(key) + ': one choice node must keep one common question')
    quests = {r['quest_id'] for r in rows}
    if len(quests) != 76 or sum(q.startswith('SQ-') for q in quests) != 40:
        errors.append('Quest coverage changed')
    if errors:
        raise ValueError('\n'.join(errors))
    report = dict(state='ALL_230_LINES_EDITED_CANDIDATE_NOT_VOICE_OR_ENGINE_APPROVAL',
        sourceCommit=source_commit, baselineFileSha256Utf8Lf=text_sha(BASE), csvSha256Utf8Lf=text_sha(ROOT / CSV),
        totalRows=len(rows), newEdits=len(changed), preservedEarlierEdits=33, baselineRowsRemaining=0,
        quests=len(quests), mainQuests=36, sideQuests=40, distinctSpeakers=len({r['speaker_id'] for r in rows}),
        distinctPromptTexts=len(by_text), sharedChoicePromptGroups=len(choices),
        statusCounts=dict(collections.Counter(r['localization_status'] for r in rows)),
        logicSha256=digest, logicFieldsAndOrderUnchanged=True, choiceLabelsAndFlagsUnchanged=True,
        minimumCharacters=min(len(r['text_vi']) for r in rows), maximumCharacters=max(len(r['text_vi']) for r in rows),
        voiceReferencesPresent=sum(bool(r['voice_asset_id']) for r in rows),
        changedRowKeys=changed, issues=[],
        exclusions=['Voice performance and recording', 'Unity font/subtitle/readability QA',
                    'Runtime objective, reveal, phase and reward guard implementation', 'Final owner sign-off'])
    return rows, report


def render(rows):
    names = {}
    with (ROOT / 'docs/production/NPC_Actor_Production_Registry_vi.csv').open(encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            names[row['npc_id']] = row['display_name_vi']
    names['NPC_MASTER_BY_PLAYER_CLASS'] = 'Thầy môn phái tương ứng'
    labels = {'OFFER': 'Nhận nhiệm vụ', 'CLUE': 'Gợi ý khi đang làm', 'TURN_IN': 'Báo cáo khi sẵn sàng', 'CHOICE': 'Lời hỏi lựa chọn'}
    chapters = {'P00': 'Mở đầu · Bến Mưa', 'C1': 'Chương I · Năm lời thề', 'C2': 'Chương II · Rừng nhớ tên người',
        'C3': 'Chương III · Lò không tắt', 'C4': 'Chương IV · Những người dưới mệnh lệnh',
        'C5': 'Chương V · Quyền được trở về', 'C6': 'Chương VI · Huyền Ấn mới',
        'SQ-BM': 'Nhiệm vụ phụ · Bến Mưa', 'SQ-TL': 'Nhiệm vụ phụ · Thanh Lạc', 'SQ-LT': 'Nhiệm vụ phụ · Lâm Triều',
        'SQ-SH': 'Nhiệm vụ phụ · Sa Hỏa', 'SQ-TS': 'Nhiệm vụ phụ · Trấn Sơn', 'SQ-BU': 'Nhiệm vụ phụ · Bạch Uyên',
        'SQ-VN': 'Nhiệm vụ phụ · Vực Nghịch Mạch', 'SQ-DM': 'Nhiệm vụ phụ · Đại Ngũ Mạch'}
    lines = ['# Ngũ Mạch: Huyền Ấn — bản đọc toàn bộ lời thoại nhiệm vụ', '',
        '230 lời / 76 nhiệm vụ. Bản biên tập ứng viên; chưa lồng tiếng hoặc nghiệm thu subtitle/runtime.',
        'Sinh từ Quest_Dialogue_Production_Data_vi.csv; sửa CSV rồi chạy Tools/NarrativeReview/validate_full_editorial.py --write.', '',
        'Nhãn điều kiện bên dưới là metadata phát triển, không phải lời NPC. Không phát thưởng từ việc mở/đọc/hết video.', '']
    last_group = last_quest = last_choice = None
    for row in rows:
        quest = row['quest_id']; group = quest.rsplit('-', 1)[0]
        if group != last_group:
            lines.extend(['## ' + chapters[group], '']); last_group = group
        if quest != last_quest:
            lines.extend(['### ' + quest + ' — ' + row['quest_title_vi'], '']); last_quest = quest
        choice_key = (row['graph_id'], row['node_id'], row['choice_group_id']) if row['node_type'] == 'CHOICE' else None
        actor = names.get(row['speaker_id'], row['speaker_id'])
        if choice_key is None or choice_key != last_choice:
            lines.extend(['**' + labels[row['node_type']] + ' · ' + actor + '**', '',
                          '`' + row['condition_key'] + '` · `' + row['node_id'] + '`', '', '> ' + row['text_vi'], ''])
        if row['choice_id']:
            lines.extend(['Lựa chọn: **' + row['choice_text_vi'] + '** · `' + row['choice_id'] + '` → `' + row['set_flag'] + '`', ''])
        last_choice = choice_key
    return '\n'.join(lines).rstrip() + '\n'


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--write', action='store_true'); args = parser.parse_args()
    try:
        rows, report = validate()
        outputs = {REPORT: json.dumps(report, ensure_ascii=False, indent=2) + '\n', READTHROUGH: render(rows)}
        for path, expected in outputs.items():
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True); path.write_text(expected, encoding='utf-8', newline='\n')
            elif not path.is_file() or path.read_text(encoding='utf-8-sig') != expected:
                raise ValueError('Stale export/report: ' + str(path.relative_to(ROOT)) + '; run --write')
    except (ValueError, OSError, KeyError) as exc:
        print('FAIL: ' + str(exc)); return 1
    print('PASS: 197 new + 33 preserved = 230 edited lines; 76 quests; logic/choices/order unchanged against Git baseline. Voice/engine unverified.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
