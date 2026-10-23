"""Exercise installation in temporary directories, never in real Agent homes."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from install_develop import destination, install
from package_develop import COPIES, ROOT


class InstallTests(unittest.TestCase):
    def test_package_matches_sources(self):
        for source, copy in COPIES.items():
            self.assertEqual(source.read_bytes(), copy.read_bytes())

    def test_project_install_is_complete_and_repeat_preserves_customization(self):
        for agent, directory in (("codex", ".agents"), ("claude", ".claude")):
            with self.subTest(agent=agent), tempfile.TemporaryDirectory() as tmp:
                project = Path(tmp)
                (project / "AGENTS.md").write_text("Existing rules", encoding="utf-8")
                install(agent, project)
                target = project / directory / "skills/develop"
                for source in (ROOT / "skills/develop").rglob("*"):
                    if source.is_file():
                        self.assertEqual(source.read_bytes(), (target / source.relative_to(ROOT / "skills/develop")).read_bytes())
                custom = target / "SKILL.md"
                custom.write_text("Custom skill", encoding="utf-8")
                with self.assertRaises(ValueError):
                    install(agent, project)
                self.assertEqual("Custom skill", custom.read_text(encoding="utf-8"))
                self.assertEqual("Existing rules", (project / "AGENTS.md").read_text(encoding="utf-8"))
                self.assertFalse((project / "CLAUDE.md").exists())

    def test_user_install_uses_current_home(self):
        for agent, directory in (("codex", ".agents"), ("claude", ".claude")):
            with self.subTest(agent=agent), tempfile.TemporaryDirectory() as tmp:
                with patch("install_develop.Path.home", return_value=Path(tmp)), patch.dict(os.environ, {}, clear=True):
                    install(agent, None)
                    self.assertTrue((Path(tmp) / directory / "skills/develop/SKILL.md").is_file())

    def test_claude_config_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": tmp}):
                install("claude", None)
                self.assertTrue((Path(tmp) / "skills/develop/SKILL.md").is_file())
                self.assertEqual(Path(tmp) / ".claude/skills/develop", destination("claude", Path(tmp)))

    def test_existing_command_blocks_claude_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            command = project / ".claude/commands/develop.md"
            command.parent.mkdir(parents=True)
            command.write_text("Custom command", encoding="utf-8")
            with self.assertRaises(ValueError):
                install("claude", project)
            self.assertEqual("Custom command", command.read_text(encoding="utf-8"))
            self.assertFalse((project / ".claude/skills/develop").exists())

    def test_manual_and_unknown_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            install("manual", project)
            self.assertTrue((project / ".using-ai/workflows/develop/references/develop.md").is_file())
            with self.assertRaises(ValueError):
                install("unknown", project)
            self.assertFalse((project / ".agents").exists())

    def test_missing_project_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "missing"
            with self.assertRaises(ValueError):
                install("codex", project)
            self.assertFalse(project.exists())


if __name__ == "__main__":
    unittest.main()
