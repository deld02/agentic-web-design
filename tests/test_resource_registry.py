import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def run(repo):
    return subprocess.run([sys.executable,'tools/validate_resource_registry.py'],cwd=repo,text=True,capture_output=True,encoding='cp1252',errors='replace')

class ResourceRegistryValidationTests(unittest.TestCase):
    def clone(self):
        td=tempfile.TemporaryDirectory(); dst=Path(td.name)/'repo'
        shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('.git','__pycache__'))
        return td,dst

    def test_clean_registry_passes(self):
        result=run(ROOT); self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_per_item_source_cannot_be_default_reusable(self):
        td,repo=self.clone()
        try:
            path=repo/'config/resource-sources.json'; data=json.loads(path.read_text(encoding='utf-8'))
            item=next(x for x in data['sources'] if x.get('license_scope')=='per-item'); item['reusable_by_default']=True
            path.write_text(json.dumps(data,indent=2),encoding='utf-8')
            result=run(repo); self.assertNotEqual(result.returncode,0)
        finally: td.cleanup()

    def test_novelty_cannot_outrank_fit(self):
        td,repo=self.clone()
        try:
            path=repo/'config/resource-sources.json'; data=json.loads(path.read_text(encoding='utf-8'))
            order=data['policy']['selection_order']; order.remove('novelty'); order.insert(0,'novelty')
            path.write_text(json.dumps(data,indent=2),encoding='utf-8')
            result=run(repo); self.assertNotEqual(result.returncode,0)
        finally: td.cleanup()

if __name__=='__main__': unittest.main()
