"""目录扫描与 Markdown 渲染。"""

from __future__ import annotations

from pathlib import Path

# 默认忽略的目录名与文件名
DEFAULT_IGNORES: frozenset[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        ".DS_Store",
        ".ccgui",
    }
)

# 每个缩进层级使用的字符串
INDENT = "    "


def scan(
    root: Path,
    ignores: frozenset[str] = DEFAULT_IGNORES,
    max_depth: int | None = None,
) -> tuple[list[tuple[int, str, bool]], list[tuple[str, str]]]:
    """深度优先扫描 root，返回 (entries, skipped)。

    entries —— [(depth, name, is_dir), ...]
        depth 从 0 开始，表示相对 root 的层级；root 自身不在结果中。
        max_depth 为 None 表示不限深度。
    skipped —— [(相对路径, 异常类名), ...]
        无法读取、被跳过的目录。

    无法读取的目录会被跳过，而不是让整个扫描失败——但**一定会被记下来**。
    静默跳过会让产物残缺却看起来正常，而下游无法察觉（见 docs/incidents.md 事故 05）。
    """
    entries: list[tuple[int, str, bool]] = []
    skipped: list[tuple[str, str]] = []

    def walk(directory: Path, depth: int) -> None:
        if max_depth is not None and depth >= max_depth:
            return
        try:
            children = sorted(
                directory.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )
        except (PermissionError, FileNotFoundError) as exc:
            skipped.append((str(directory.relative_to(root)), type(exc).__name__))
            return
        for child in children:
            if child.name in ignores:
                continue
            is_dir = child.is_dir()
            entries.append((depth, child.name, is_dir))
            if is_dir:
                walk(child, depth + 1)

    walk(root, 0)
    return entries, skipped


def render(entries: list[tuple[int, str, bool]], root_name: str) -> str:
    """把 scan 的结果渲染成 Markdown 目录树文本。"""
    lines = [f"{root_name}/"]
    for depth, name, is_dir in entries:
        prefix = INDENT * (depth + 1)
        lines.append(f"{prefix}{name}/" if is_dir else f"{prefix}{name}")
    return "\n".join(lines) + "\n"
