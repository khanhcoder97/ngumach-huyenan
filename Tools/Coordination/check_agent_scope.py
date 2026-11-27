"""Audit Muse media-only scope using policy from the trusted base checkout."""
import argparse, json, subprocess, sys
from pathlib import Path, PurePosixPath

def violations(paths, branch, policy):
    rules = policy['muse']
    if not branch.startswith('muse/'):
        return []
    if branch in rules['frozenBranches'] or not branch.startswith(rules['newBranchPrefix']):
        return ['Muse graphics/runtime branches are frozen; use muse/media-* for media only.']
    bad = []
    for raw in paths:
        path = PurePosixPath(raw)
        normalized = path.as_posix()
        suffix = path.suffix.lower()
        if path.is_absolute() or '..' in path.parts or suffix in rules['forbiddenRuntimeExtensions']:
            bad.append(normalized); continue
        is_tool = normalized.startswith(rules['allowedToolRoot'])
        is_media = any(normalized.startswith(root) for root in rules['allowedMediaRoots'])
        allowed_ext = rules['toolExtensions'] if is_tool else rules['mediaExtensions']
        if not (is_tool or is_media) or suffix not in allowed_ext:
            bad.append(normalized)
    return bad

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', required=True)
    parser.add_argument('--head', required=True)
    parser.add_argument('--branch', required=True)
    parser.add_argument('--policy', default='Implementation/Coordination/agent_scope_v2.json')
    args = parser.parse_args()
    policy = json.loads(Path(args.policy).read_text(encoding='utf-8'))
    common = subprocess.check_output(['git','merge-base',args.base,args.head],text=True).strip()
    raw = subprocess.check_output(['git','diff','--no-renames','--name-only','-z',common,args.head])
    paths = [s for s in raw.decode('utf-8').split('\0') if s]
    bad = violations(paths,args.branch,policy)
    for path in bad:
        print('OUT_OF_SCOPE: '+path)
    print(f'Scope audit: {len(paths)} changed paths, {len(bad)} violations')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main())
