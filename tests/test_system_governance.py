import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def run(repo,*args):
    return subprocess.run([sys.executable,*args],cwd=repo,text=True,capture_output=True,encoding='cp1252',errors='replace')


class SystemGovernanceTests(unittest.TestCase):
    def clone(self,project=False):
        td=tempfile.TemporaryDirectory(); dst=Path(td.name)/'repo'
        shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('.git','__pycache__'))
        if project:
            result=run(dst,'tools/new_project.py','test-project')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        return td,dst

    def mutate(self,repo,rel,fn):
        path=repo/rel; data=json.loads(path.read_text(encoding='utf-8')); fn(data)
        path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

    def test_clean_system_audit_passes(self):
        result=run(ROOT,'tools/audit_system.py')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_overdue_system_audit_fails(self):
        td,repo=self.clone()
        try:
            self.mutate(repo,'config/system-governance.json',lambda d:d.update(last_audit='2020-01-01',next_review='2020-03-01'))
            result=run(repo,'tools/audit_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('system audit overdue',result.stdout)
        finally: td.cleanup()

    def test_stale_capability_fails(self):
        td,repo=self.clone()
        try:
            self.mutate(repo,'config/design-capabilities.json',lambda d:d['capabilities'][0].update(last_checked='2020-01-01'))
            result=run(repo,'tools/audit_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('capability review overdue',result.stdout)
        finally: td.cleanup()

if __name__=='__main__': unittest.main()
