import copy
import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
TOOL = ROOT / 'Implementation/Tools/ContentPipeline'
sys.path.insert(0, str(TOOL))
from compiler import canonical_bytes, compile_bundle, digest_for, finalize_candidate
from compiler_core import PipelineError, PipelineEnvironmentError, SOURCE_SPECS, load_context
from validation import field_diff, load_json_file, validate_bundle


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx, cls.bundle = compile_bundle(ROOT)

    def seal(self, bundle):
        bundle['candidates'] = [finalize_candidate(c) for c in bundle['candidates']]
        bundle['bundleDigest'] = digest_for({k:v for k,v in bundle.items() if k != 'bundleDigest'})
        return bundle

    def test_baseline_valid_candidate_and_explicit_runtime_gate(self):
        self.assertEqual([], validate_bundle(self.bundle, self.ctx))
        self.assertFalse(self.bundle['activation']['runtimeActivationAllowed'])
        self.assertFalse(self.bundle['activation']['eligible'])
        self.assertTrue(self.bundle['activation']['requiresReview'])

    def test_all_five_quests_have_separate_objective_maps(self):
        for kind in ['QUEST','OBJECTIVE_MAP']:
            self.assertEqual({f'P00-0{i}' for i in range(1,6)},
                             {c['targetId'] for c in self.bundle['candidates'] if c['kind']==kind})

    def test_footwear_exists_and_is_not_reported_as_missing_catalog(self):
        item=next(c for c in self.bundle['candidates'] if c['candidateId']=='ITEM-REF-P00-03-SHOES')
        self.assertEqual(5,len(item['definition']['candidateItemIds']))
        self.assertTrue(all(self.ctx.item_master_by_id[i]['slot']=='Giày' for i in item['definition']['candidateItemIds']))
        self.assertNotIn('No footwear',item['unresolved'][0]['reason'])

    def test_class_weapon_macro_resolves_all_classes_without_selecting_player_class(self):
        item=next(c for c in self.bundle['candidates'] if c['candidateId']=='ITEM-REF-P00-05-CLASS-WEAPON')
        self.assertEqual('CLASS_CONDITIONAL',item['definition']['resolution'])
        self.assertEqual(5,len(item['definition']['classCandidates']))
        self.assertNotIn('resolvedItemId',item['definition'])
        self.assertEqual([],item['unresolved'])

    def test_conditional_weapon_cannot_cross_class_or_drop_a_class(self):
        b=copy.deepcopy(self.bundle)
        item=next(c for c in b['candidates'] if c['candidateId']=='ITEM-REF-P00-05-CLASS-WEAPON')
        item['definition']['classCandidates'][0]['classId']='CLASS_UNKNOWN'
        self.assertTrue(validate_bundle(self.seal(b),self.ctx))

    def test_missing_data_stays_blocked_with_provenance(self):
        self.assertGreater(self.bundle['summary']['unresolvedCount'],0)
        for c in self.bundle['candidates']:
            self.assertTrue(c['fieldProvenance'])
            if c['status']=='BLOCKED_UNRESOLVED':self.assertTrue(any(e['blocking'] for e in c['unresolved']))

    def test_deterministic_bytes(self):
        self.assertEqual(canonical_bytes(self.bundle),canonical_bytes(compile_bundle(ROOT)[1]))

    def test_ids_explicitly_abbreviated_in_atlas_are_resolved(self):
        self.assertIn('OBJ_BM_WATER_RIPPLE_02',self.ctx.design_ids)
        self.assertIn('OBJ_BM_WATER_RIPPLE_03',self.ctx.design_ids)
        self.assertNotIn('OBJ_BM_WATER_RIPPLE_04',self.ctx.design_ids)

    def test_tampered_digest_rejected(self):
        b=copy.deepcopy(self.bundle);b['bundleDigest']='sha256:'+'0'*64
        self.assertTrue(validate_bundle(b,self.ctx))

    def test_duplicate_candidate_rejected_even_resigned(self):
        b=copy.deepcopy(self.bundle);b['candidates'].append(copy.deepcopy(b['candidates'][0]))
        self.assertTrue(validate_bundle(self.seal(b),self.ctx))

    def test_dangling_target_rejected_even_resigned(self):
        b=copy.deepcopy(self.bundle);b['candidates'][0]['definition']['objectives'][0]['targetIds']=['OBJ_DOES_NOT_EXIST']
        self.assertTrue(any('dangling' in e for e in validate_bundle(self.seal(b),self.ctx)))

    def test_prerequisite_cycle_rejected(self):
        b=copy.deepcopy(self.bundle)
        b['candidates'][0]['definition']['prerequisiteQuestIds']=['P00-02']
        self.assertTrue(any('cycle' in e.lower() for e in validate_bundle(self.seal(b),self.ctx)))

    def test_schema_cannot_be_replaced_with_another_kind(self):
        b=copy.deepcopy(self.bundle);b['candidates'][0]['targetSchema']='Implementation/Content/Schemas/ItemDefinition.schema.json'
        self.assertTrue(any('candidate kind' in e for e in validate_bundle(self.seal(b),self.ctx)))

    def test_runtime_gate_cannot_be_enabled_even_resigned(self):
        b=copy.deepcopy(self.bundle);b['activation']['runtimeActivationAllowed']=True
        self.assertTrue(validate_bundle(self.seal(b),self.ctx))

    def test_missing_provenance_rejected(self):
        b=copy.deepcopy(self.bundle);b['candidates'][0]['fieldProvenance']=[]
        self.assertTrue(validate_bundle(self.seal(b),self.ctx))

    def test_wrong_units_rejected(self):
        b=copy.deepcopy(self.bundle)
        b['candidates'][0]['fieldProvenance'][0]['units']='INVALID_UNIT'
        self.assertTrue(validate_bundle(self.seal(b),self.ctx))

    def test_source_path_escape_rejected(self):
        b=copy.deepcopy(self.bundle);b['sources'][0]['path']='../outside.json'
        self.assertTrue(validate_bundle(self.seal(b),self.ctx))

    def test_malformed_shape_returns_errors_instead_of_crash(self):
        b=copy.deepcopy(self.bundle);b['sources'][0]['sourceId']=[]
        self.assertTrue(validate_bundle(b,self.ctx))

    def test_field_diff_identifies_changed_field(self):
        changes=field_diff({'value':1},{'value':2})
        self.assertEqual('/value',changes[0]['path'])

    def copied_sources(self, root):
        for spec in SOURCE_SPECS.values():
            target=root/spec.path;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/spec.path).read_bytes())

    def test_source_edit_requires_transcription_review(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.copied_sources(root)
            p=root/SOURCE_SPECS['QUEST_SPEC'].path;p.write_bytes(p.read_bytes()+b'\nchanged source\n')
            with self.assertRaisesRegex(PipelineError,'transcription review'):load_context(root)

    def test_lf_crlf_and_utf8_bom_produce_same_digests(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.copied_sources(root)
            for spec in SOURCE_SPECS.values():
                p=root/spec.path;s=p.read_text(encoding='utf-8-sig')
                p.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))
            self.assertEqual(self.ctx.sources,load_context(root).sources)

    def test_fixed_item_variant_parity_for_every_fixed_item(self):
        fixed={i:r for i,r in self.ctx.item_master_by_id.items() if not i.startswith('EQ-')}
        self.assertEqual(136,len(fixed));self.assertTrue(all(self.ctx.item_rarity_by_id.get(i)==r for i,r in fixed.items()))
        self.assertIn('TOOL-ROD-01',fixed)

    def test_fixed_item_drift_is_not_silently_merged(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.copied_sources(root)
            p=root/SOURCE_SPECS['ITEM_RARITY'].path
            with p.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
            row=next(r for r in rows if r['item_id']=='TOOL-ROD-01');key=next(k for k in row if k!='item_id');row[key]='tampered'
            with p.open('w',encoding='utf-8',newline='') as f:
                w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
            with self.assertRaisesRegex(PipelineError,'fixed item catalog drift'):load_context(root)

    def test_missing_source_fails(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(PipelineEnvironmentError):load_context(Path(d))

    def test_duplicate_json_members_and_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json'
            for text in ['{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}']:
                p.write_text(text,encoding='utf-8')
                with self.assertRaises(PipelineEnvironmentError):load_json_file(p,'fixture')

    def test_cli_build_check_require_ready_and_invalid_leave_source_untouched(self):
        source=(ROOT/SOURCE_SPECS['QUEST_EXAMPLE_P00_01'].path);before=source.read_bytes()
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'candidate.json'
            def call(*args):
                return subprocess.run([sys.executable,str(TOOL/'cli.py'),*args],cwd=d,capture_output=True,text=True,encoding='utf-8')
            r=call('build','--root',str(ROOT),'--output',str(output));self.assertEqual(0,r.returncode,r.stdout+r.stderr)
            self.assertEqual(0,call('check','--root',str(ROOT),'--bundle',str(output)).returncode)
            self.assertEqual(3,call('validate','--root',str(ROOT),'--bundle',str(output),'--require-ready').returncode)
            untouched=Path(d)/'must_not_exist.json'
            self.assertEqual(3,call('build','--root',str(ROOT),'--output',str(untouched),'--require-ready').returncode)
            self.assertFalse(untouched.exists())
            self.assertEqual(1,call('build','--root',str(ROOT),'--output',str(source)).returncode)
        self.assertEqual(before,source.read_bytes())


if __name__=='__main__':unittest.main()
