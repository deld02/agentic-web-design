from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EntrypointTests(unittest.TestCase):
    def test_skill_fails_closed_without_managed_harness_context(self):
        text = (ROOT/'skills/agentic-web-design/SKILL.md').read_text(encoding='utf-8')
        for token in ('Execution lock', 'MANAGED', 'UNMANAGED', 'HARNESS_RUN_DIR', 'must not build HTML'):
            self.assertIn(token, text)

    def test_chatgpt_entrypoint_forbids_manual_pipeline_fallback(self):
        text = (ROOT/'CHATGPT-PROJECT-INSTRUCTIONS.md').read_text(encoding='utf-8')
        for token in ('HARNESS_STAGE', 'UNMANAGED', 'must stop before', 'unacceptable fallback', 'IMAGE_GEN', 'chat-next'):
            self.assertIn(token, text)
