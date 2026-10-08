"""treegen 核心逻辑的单元测试（标准库 unittest，无第三方依赖）。"""

import tempfile
import unittest
from pathlib import Path

from treegen.core import DEFAULT_IGNORES, render, scan


def make_tree(root: Path) -> Path:
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text("a", encoding="utf-8")
    (root / "docs").mkdir()
    (root / "docs" / "guide.md").write_text("g", encoding="utf-8")
    (root / "README.md").write_text("r", encoding="utf-8")
    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "x.pyc").write_text("x", encoding="utf-8")
    return root


class ScanTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_tree(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_dirs_come_before_files(self):
        entries = scan(self.root)
        kinds = [is_dir for _, _, is_dir in entries]
        first_file = kinds.index(False)
        self.assertTrue(all(kinds[:first_file]))

    def test_skips_ignored_names(self):
        names = [name for _, name, _ in scan(self.root)]
        self.assertNotIn("__pycache__", names)
        self.assertIn("README.md", names)

    def test_respects_max_depth(self):
        entries = scan(self.root, max_depth=1)
        self.assertTrue(all(depth == 0 for depth, _, _ in entries))

    def test_depth_increases_with_nesting(self):
        entries = scan(self.root, max_depth=2)
        depths = {(name, depth) for depth, name, _ in entries}
        self.assertIn(("src", 0), depths)
        self.assertIn(("a.py", 1), depths)


class RenderTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_tree(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_root_line_uses_given_name(self):
        text = render(scan(self.root), "myproject")
        self.assertEqual(text.splitlines()[0], "myproject/")

    def test_indent_is_four_spaces(self):
        lines = render(scan(self.root, max_depth=2), self.root.name).splitlines()
        self.assertIn("    src/", lines)
        self.assertIn("        a.py", lines)

    def test_output_ends_with_newline(self):
        self.assertTrue(render(scan(self.root), "x").endswith("\n"))


class ConstantsTest(unittest.TestCase):
    def test_default_ignores_is_frozen(self):
        self.assertIsInstance(DEFAULT_IGNORES, frozenset)

    def test_default_ignores_covers_common_junk(self):
        for name in (".git", "__pycache__", "node_modules", ".venv"):
            self.assertIn(name, DEFAULT_IGNORES)


if __name__ == "__main__":
    unittest.main()
