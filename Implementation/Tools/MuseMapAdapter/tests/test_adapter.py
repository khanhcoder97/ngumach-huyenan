import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[4]
TOOL=ROOT/'Implementation/Tools/MuseMapAdapter'
sys.path.insert(0,str(TOOL))
from adapter import ASSETS,MANIFEST,build,safe_file,PNGValidationProblem
from Implementation.Tools.ContentPipeline.compiler import canonical_bytes


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout=json.loads((TOOL/'fixtures/synthetic_layout.json').read_text())
        cls.bundle=build(cls.layout,ROOT)

    def modified(self,fn):
        value=copy.deepcopy(self.layout);fn(value);return value

    def test_baseline_units_and_candidate_only(self):
        self.assertEqual(0.8,self.bundle['worldCellSizeWu'])
        self.assertFalse(self.bundle['runtimeActivationAllowed'])
        self.assertTrue(self.bundle['synthetic'])
        self.assertEqual('TOPDOWN_REVIEW_REQUIRED',self.bundle['navigationReview'])

    def test_original_manifest_all_rows_and_xy_remain_intact(self):
        before=(ROOT/MANIFEST).read_bytes()
        result=build(self.layout,ROOT)
        self.assertEqual(349,result['canonicalPlacementCount'])
        self.assertEqual(24,result['mapPlacementCount'])
        for p in result['placements']:
            self.assertEqual(p['originalXYWu'],p['candidateXYWu'])
            self.assertEqual(float(p['originalRecord']['x_wu']),p['originalXYWu']['x'])
            self.assertEqual('TOPDOWN_REVIEW_REQUIRED',p['migrationState'])
        self.assertEqual(before,(ROOT/MANIFEST).read_bytes())

    def test_real_muse_actor_geometry_and_bottom_left_conversion(self):
        actor=self.bundle['actors'][0]
        self.assertEqual('CHR_MINH_KIEM_WALK',actor['assetId'])
        self.assertEqual(6,actor['geometry']['grid']['cols']);self.assertEqual(8,actor['geometry']['grid']['rows'])
        self.assertEqual(48,len(actor['frames']))
        self.assertEqual({'x':0,'y':448,'width':48,'height':64},actor['frames'][0]['pixelRectUnity'])
        self.assertEqual({'x':240,'y':448,'width':48,'height':64},actor['frames'][-1]['pixelRectTopLeft'])
        self.assertEqual('UNVERIFIED',actor['engineImport'])

    def test_prop_uses_grid_cell_center_and_atlas_rect(self):
        prop=self.bundle['props'][0]
        self.assertAlmostEqual(1.2,prop['positionWu']['x']);self.assertAlmostEqual(1.2,prop['positionWu']['y'])
        self.assertEqual(16,prop['pixelRectTopLeft']['y'])

    def test_negative_row_axis_is_explicit(self):
        value=build(self.modified(lambda x:x.update(rowAxis='-Y')),ROOT)
        self.assertAlmostEqual(-1.2,value['props'][0]['positionWu']['y'])

    def test_migration_preserves_original_and_requires_review(self):
        value=self.modified(lambda x:x['placementOverrides'].append({'originalRecordId':'MAN-BM-NPC_LYAN','xWu':1,'yWu':1,'reason':'synthetic migration test'}))
        result=build(value,ROOT);p=next(v for v in result['placements'] if v['originalRecordId']=='MAN-BM-NPC_LYAN')
        self.assertEqual(42,p['originalXYWu']['x']);self.assertEqual(1,p['candidateXYWu']['x'])
        self.assertEqual('TOPDOWN_REVIEW_REQUIRED',p['migrationState'])

    def test_output_is_deterministic(self):
        self.assertEqual(canonical_bytes(self.bundle),canonical_bytes(build(self.layout,ROOT)))

    def test_outside_small_fixture_and_draft_art_are_findings(self):
        self.assertTrue(any(f['code']=='OUTSIDE_CANDIDATE_LAYOUT' for f in self.bundle['findings']))
        self.assertTrue(any(f['code']=='ART_NOT_APPROVED' for f in self.bundle['findings']))

    def test_runtime_review_injection_rejected(self):
        with self.assertRaises(ValueError):build(self.modified(lambda x:x.update(navigationReview='REVIEWED')),ROOT)

    def test_pixel_units_cannot_be_changed(self):
        for field,value in [('tilePixels',32),('pixelsPerUnit',20.5),('pixelsPerUnit',True)]:
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):build(self.modified(lambda x:x.update({field:value})),ROOT)

    def test_nonfinite_origin_rejected(self):
        with self.assertRaises(ValueError):build(self.modified(lambda x:x['originWu'].update(x=float('nan'))),ROOT)

    def test_missing_unknown_or_duplicate_references_fail(self):
        changes=[lambda x:x['actorAssets'].append('NO_SUCH_ACTOR'),
                 lambda x:x['actorAssets'].append(x['actorAssets'][0]),
                 lambda x:x['layers'][0].update(tilesetId='MISSING'),
                 lambda x:x['tilesets'].append(copy.deepcopy(x['tilesets'][0])),
                 lambda x:x['props'][0].update(tilesetId='MISSING')]
        for change in changes:
            with self.subTest(change=change),self.assertRaises(ValueError):build(self.modified(change),ROOT)

    def test_invalid_grid_tile_ids_and_budget_fail(self):
        changes=[lambda x:x['layers'][0]['tiles'].append(1),lambda x:x['layers'][0]['tiles'].__setitem__(0,3),
                 lambda x:x['layers'][0]['tiles'].__setitem__(0,True),
                 lambda x:x['layers'][0].update(width=4096,height=4096),
                 lambda x:x['props'][0].update(column=4)]
        for change in changes:
            with self.subTest(change=change),self.assertRaises(ValueError):build(self.modified(change),ROOT)

    def test_unknown_wrong_map_and_unexplained_migration_fail(self):
        for record,reason in [('NO_SUCH_RECORD','test'),('MAN-TL-NPC_NOT_HERE','test'),('MAN-BM-NPC_LYAN','')]:
            value=self.modified(lambda x:x['placementOverrides'].append({'originalRecordId':record,'xWu':1,'yWu':0,'reason':reason}))
            with self.assertRaises(ValueError):build(value,ROOT)

    def test_portable_paths_reject_traversal_drive_and_unc(self):
        for path in ['../outside.png','C:/outside.png','//server/share/a.png','a\\b.png','/absolute.png']:
            with self.subTest(path=path),self.assertRaises(ValueError):safe_file(ROOT,path)

    def clone_inputs(self,root):
        for p in [MANIFEST,ASSETS,'Implementation/Content/map_bounds.json',
                  'Client/Assets/Art/Characters/MinhKiem/minh_kiem_walk.png',
                  'Implementation/Tools/MuseMapAdapter/fixtures/synthetic_tiles.png']:
            dest=root/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/p).read_bytes())

    def test_alternate_root_never_falls_back_to_cwd(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.clone_inputs(root)
            self.assertEqual(canonical_bytes(self.bundle),canonical_bytes(build(self.layout,root)))
            (root/'Client/Assets/Art/Characters/MinhKiem/minh_kiem_walk.png').unlink()
            with self.assertRaises(ValueError):build(self.layout,root)

    def test_corrupt_png_and_lfs_pointer_are_not_images(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.clone_inputs(root);p=root/'Implementation/Tools/MuseMapAdapter/fixtures/synthetic_tiles.png'
            for content in [b'version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 20\n',b'\x89PNG\r\n\x1a\ntruncated']:
                p.write_bytes(content)
                with self.assertRaises((ValueError,PNGValidationProblem)):build(self.layout,root)

    def test_cli_roundtrip_tamper_and_no_source_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'layout.json';source.write_text(json.dumps(self.layout),encoding='utf-8')
            output=Path(d)/'candidate.json';original=source.read_bytes()
            def call(command,dest):return subprocess.run([sys.executable,str(TOOL/'cli.py'),command,'--root',str(ROOT),'--layout',str(source),'--output',str(dest)],cwd=d,capture_output=True,text=True)
            r=call('build',output);self.assertEqual(0,r.returncode,r.stdout+r.stderr)
            self.assertEqual(0,call('check',output).returncode)
            output.write_bytes(output.read_bytes()+b' ')
            self.assertEqual(1,call('check',output).returncode)
            self.assertEqual(1,call('build',source).returncode);self.assertEqual(original,source.read_bytes())


if __name__=='__main__':unittest.main()
