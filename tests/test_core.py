"""treegen 核心逻辑的单元测试（标准库 unittest，无第三方依赖）。"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
        entries, _ = scan(self.root)
        kinds = [is_dir for _, _, is_dir in entries]
        first_file = kinds.index(False)
        self.assertTrue(all(kinds[:first_file]))

    def test_skips_ignored_names(self):
        entries, _ = scan(self.root)
        names = [name for _, name, _ in entries]
        self.assertNotIn("__pycache__", names)
        self.assertIn("README.md", names)

    def test_respects_max_depth(self):
        entries, _ = scan(self.root, max_depth=1)
        self.assertTrue(all(depth == 0 for depth, _, _ in entries))

    def test_depth_increases_with_nesting(self):
        entries, _ = scan(self.root, max_depth=2)
        depths = {(name, depth) for depth, name, _ in entries}
        self.assertIn(("src", 0), depths)
        self.assertIn(("a.py", 1), depths)

    def test_clean_tree_reports_nothing_skipped(self):
        _, skipped = scan(self.root)
        self.assertEqual(skipped, [])


class ScanFailureTest(unittest.TestCase):
    """无法读取的目录必须被**记下来**，不能静默跳过（事故 05）。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_tree(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def _scan_with_locked_docs(self):
        real_iterdir = Path.iterdir

        def fake_iterdir(self_path):
            if self_path.name == "docs":
                raise PermissionError("locked by another process")
            return real_iterdir(self_path)

        with mock.patch.object(Path, "iterdir", fake_iterdir):
            return scan(self.root)

    def test_unreadable_dir_is_recorded(self):
        _, skipped = self._scan_with_locked_docs()
        self.assertEqual(skipped, [("docs", "PermissionError")])

    def test_unreadable_dir_keeps_its_own_entry(self):
        """目录本身还在（在父层就记下了），丢的是它下面的内容。"""
        entries, _ = self._scan_with_locked_docs()
        self.assertIn(("docs", 0), {(name, depth) for depth, name, _ in entries})
        self.assertNotIn("guide.md", [name for _, name, _ in entries])

    def test_scan_does_not_raise_on_unreadable_dir(self):
        """跳过而不是整体失败——健壮性。"""
        entries, skipped = self._scan_with_locked_docs()
        self.assertTrue(entries)
        self.assertEqual(len(skipped), 1)


class RenderTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_tree(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_root_line_uses_given_name(self):
        entries, _ = scan(self.root)
        text = render(entries, "myproject")
        self.assertEqual(text.splitlines()[0], "myproject/")

    def test_indent_is_four_spaces(self):
        entries, _ = scan(self.root, max_depth=2)
        lines = render(entries, self.root.name).splitlines()
        self.assertIn("    src/", lines)
        self.assertIn("        a.py", lines)

    def test_output_ends_with_newline(self):
        entries, _ = scan(self.root)
        self.assertTrue(render(entries, "x").endswith("\n"))


class ConstantsTest(unittest.TestCase):
    def test_default_ignores_is_frozen(self):
        self.assertIsInstance(DEFAULT_IGNORES, frozenset)

    def test_default_ignores_covers_common_junk(self):
        for name in (".git", "__pycache__", "node_modules", ".venv"):
            self.assertIn(name, DEFAULT_IGNORES)


if __name__ == "__main__":
    unittest.main()
