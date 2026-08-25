import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def run(repo):
    return subprocess.run([sys.executable,'tools/validate_design_capabilities.py'],cwd=repo,text=True,capture_output=True,encoding='cp1252',errors='replace')

class DesignCapabilityTests(unittest.TestCase):
    def clone(self):
        td=tempfile.TemporaryDirectory(); dst=Path(td.name)/'repo'
        shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('.git','__pycache__'))
        return td,dst

    def mutate(self,repo,fn):
        path=repo/'config/design-capabilities.json'; data=json.loads(path.read_text(encoding='utf-8')); fn(data)
        path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

    def test_clean_capabilities_pass(self):
        result=run(ROOT); self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_only_one_direction_primary(self):
        td,repo=self.clone()
        try:
            def change(d):
                extra=dict(d['capabilities'][0]); extra['id']='second-primary'; d['capabilities'].append(extra)
            self.mutate(repo,change); result=run(repo)
            self.assertNotEqual(result.returncode,0); self.assertIn('direction-primary',result.stdout)
        finally: td.cleanup()

    def test_taste_challenge_is_core_automatic(self):
        td,repo=self.clone()
        try:
            def change(d): next(x for x in d['capabilities'] if x['id']=='taste-direction-challenger')['activation']='conditional'
            self.mutate(repo,change); result=run(repo)
            self.assertNotEqual(result.returncode,0); self.assertIn('core capability needs automatic activation',result.stdout)
        finally: td.cleanup()

    def test_lookup_has_no_decision_authority(self):
        td,repo=self.clone()
        try:
            def change(d): next(x for x in d['capabilities'] if x['slot']=='knowledge-lookup')['decision_authority']=True
            self.mutate(repo,change); result=run(repo)
            self.assertNotEqual(result.returncode,0); self.assertIn('cannot have decision authority',result.stdout)
        finally: td.cleanup()

    def test_immersive_requires_explicit_direction(self):
        td,repo=self.clone()
        try:
            def change(d): next(x for x in d['capabilities'] if x['slot']=='immersive-booster')['activation']='conditional'
            self.mutate(repo,change); result=run(repo)
            self.assertNotEqual(result.returncode,0); self.assertIn('explicit-direction-only',result.stdout)
        finally: td.cleanup()

    def test_skill_frontmatter_name_matches_folder(self):
        td,repo=self.clone()
        try:
            path=repo/'skills/web-design-capabilities/SKILL.md'
            path.write_text(path.read_text(encoding='utf-8').replace('name: web-design-capabilities','name: wrong-name',1),encoding='utf-8')
            result=run(repo)
            self.assertNotEqual(result.returncode,0); self.assertIn('name must match folder',result.stdout)
        finally: td.cleanup()

    def test_gsap_runtime_is_conditional_and_non_authoritative(self):
        data=json.loads((ROOT/'config/design-capabilities.json').read_text(encoding='utf-8'))
        item=next(x for x in data['capabilities'] if x['id']=='gsap-official-runtime')
        self.assertEqual(item['activation'],'selected-runtime-only')
        self.assertFalse(item['decision_authority'])
        self.assertIn('implementation',item['allowed_stages'])

    def test_impeccable_adapter_requires_review_finding(self):
        data=json.loads((ROOT/'config/design-capabilities.json').read_text(encoding='utf-8'))
        item=next(x for x in data['capabilities'] if x['id']=='impeccable-craft-correction')
        self.assertEqual(item['activation'],'review-finding-only')
        self.assertFalse(item['decision_authority'])

    def test_structural_challenger_is_the_only_new_automatic_core(self):
        data=json.loads((ROOT/'config/design-capabilities.json').read_text(encoding='utf-8'))
        item=next(x for x in data['capabilities'] if x['id']=='hallmark-structure-challenger')
        self.assertEqual((item['tier'],item['activation']),('core','automatic'))
        self.assertEqual(item['allowed_agents'],['02'])

if __name__=='__main__': unittest.main()
