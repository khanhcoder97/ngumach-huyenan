#!/usr/bin/env python3
"""Build/check a review-only Muse map sidecar. No Unity or game server required."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from adapter import ASSETS, CODE_ROOT, MANIFEST, build, PNGValidationProblem
from Implementation.Tools.ContentPipeline.compiler import canonical_bytes
from Implementation.Tools.ContentPipeline.cli import atomic_write
from Implementation.Tools.ContentPipeline.validation import load_json_file
from Implementation.Tools.ContentPipeline.compiler_core import PipelineEnvironmentError


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['build','check'])
    p.add_argument('--root',type=Path,default=CODE_ROOT)
    p.add_argument('--layout',type=Path,required=True)
    p.add_argument('--asset-manifest',default=ASSETS)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    try:
        root=a.root.resolve();layout=load_json_file(a.layout,'layout')
        output=(a.output or root/'Implementation/Content/BuildCandidates/BEN_MUA/muse_map_candidate.json').resolve()
        if output==a.layout.resolve():
            raise ValueError('output must not overwrite the source layout')
        if output.is_relative_to(root) and not output.is_relative_to((root/'Implementation/Content/BuildCandidates').resolve()):
            raise ValueError('repository output must stay in BuildCandidates')
        candidate=build(layout,root,a.asset_manifest)
        data=canonical_bytes(candidate)
        if a.command=='check':
            if output.read_bytes()!=data:raise ValueError('map candidate is stale or tampered')
        else:atomic_write(output,data)
        print(f"{a.command}: {candidate['mapId']} / {candidate['mapPlacementCount']} placements / "
              f"{len(candidate['actors'])} actors / {len(candidate['findings'])} findings / runtime OFF")
        return 0
    except (ValueError,OSError,KeyError,TypeError,PNGValidationProblem,PipelineEnvironmentError) as e:
        print('MAP CANDIDATE ERROR: '+str(e));return 1


if __name__=='__main__':raise SystemExit(main())
