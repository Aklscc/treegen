#!/usr/bin/env bash
# 免安装启动脚本：不依赖 pip / setuptools，直接用模块入口运行。
# 用法：./treegen.sh <参数...>
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Git Bash 下 POSIX 路径 Windows Python 认不出，且分隔符要用 ';'
if command -v cygpath >/dev/null 2>&1; then
  DIR="$(cygpath -w "$DIR")"
  SEP=';'
else
  SEP=':'
fi

export PYTHONPATH="$DIR${PYTHONPATH:+$SEP$PYTHONPATH}"
exec python -m treegen.cli "$@"
