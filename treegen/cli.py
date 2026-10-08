"""treegen 命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import render, scan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="treegen",
        description="扫描目录，生成 Markdown 目录树",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="要扫描的目录（默认当前目录）",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="写入文件，而不是打印到标准输出",
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        type=int,
        default=None,
        help="最大递归深度（默认不限）",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"treegen {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.path)
    if not root.is_dir():
        print(f"treegen: 错误：{root} 不是目录")
        return 1

    entries = scan(root, max_depth=args.max_depth)
    text = render(entries, root.resolve().name)

    # 统一用 LF 输出，避免同一份产物在 Windows / Linux 上字节不同
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8", newline="\n")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(newline="\n")
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
