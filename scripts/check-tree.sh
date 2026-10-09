#!/usr/bin/env bash
# check-tree.sh —— 保证 TREE.md 与真实目录结构一致
#
# 这条约束从 docs/incidents.md 的事故 04 长出来。三个量的判断：
#   静默       —— 触发它的动作（比对 TREE.md 与真实目录）不在正常使用路径上
#   逃逸概率 高 —— 每次增删文件都会触发
#   逃逸代价 中 —— 读者 / agent 会按过期的目录树找文件
#   等待成本 低 —— 违反后能自动修复，不需要人做判断
# 结论：该门控；且因为「违反后能自动修复」，是纯 Sensor（不占前馈位）。
#
# 两种模式：
#   bash scripts/check-tree.sh          修复模式：过期就重新生成，exit 0
#   bash scripts/check-tree.sh --check  只检查不修改，过期则 exit 1
#
# 为什么分两种模式：「能自动修复」和「该不该阻断」是两个独立的问题。
# 本地跑时修完就该放行；CI 里改不了工作区，只能红。
# 但 pre-commit 用 --check —— 提交时改文件 = 改你正在提交的内容（见 .githooks/pre-commit）。
#
# 实现上不落临时文件（用进程替换），避免平台差异带来的清理问题。

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

TARGET="TREE.md"
MODE="${1:-fix}"

# 把缩进的目录树展开成完整路径（每行一个）。
#
# 为什么要这一步：直接 diff 两棵树，报告里会丢掉缩进——而缩进就是层级信息。
# 于是 `.githooks/` 和 `pre-commit` 变成两个并列条目，看不出父子关系，
# 「缺少什么」也就说不清。展开成路径后，缺什么是明确的。
tree_to_paths() {
  awk '
    {
      match($0, /^ */)
      indent = RLENGTH
      name = substr($0, indent + 1)
      if (name == "") next
      depth = int(indent / 4)
      stack[depth] = name
      path = ""
      for (i = 0; i < depth; i++) path = path stack[i]
      print path name
    }
  '
}

# 把多行列表缩进成报告里的一栏；空列表显示「无」。
as_block() {
  if [ -z "$1" ]; then
    printf '            无'
  else
    printf '%s\n' "$1" | sed 's/^/            /'
  fi
}

CURRENT="$(cat "$TARGET")"

# treegen 在跳过目录时返回非零（产物残缺）。必须在这里明确报错，
# 而不是让 set -e 默默 abort —— 一个没有解释的退出码，读的人无从下手。
if ! ACTUAL="$(./treegen.sh . -d 2)"; then
  cat >&2 <<EOF
✗ 无法生成目录树 —— treegen 报告了错误（见上方 stderr）

在哪    · 生成阶段就失败了，没有可比的产物
为什么  · $TARGET 由 treegen 生成，也由 treegen 校验（循环验证）；
          生成不可信时，比对结果毫无意义
怎么改  · 先解决 treegen 报告的问题，再重跑本检查
文档    · AGENTS.md · 多源真相清单 · 目录结构
EOF
  exit 1
fi

CUR_PATHS="$(printf '%s\n' "$CURRENT" | tree_to_paths | LC_ALL=C sort)"
ACT_PATHS="$(printf '%s\n' "$ACTUAL" | tree_to_paths | LC_ALL=C sort)"

if [ "$CUR_PATHS" = "$ACT_PATHS" ]; then
  echo "✓ $TARGET 与真实目录结构一致"
  exit 0
fi

DIFF="$(diff <(printf '%s\n' "$CUR_PATHS") <(printf '%s\n' "$ACT_PATHS") || true)"
# 注意：每条都要 || true —— 开了 pipefail，grep 找不到匹配会返回 1，会把整个脚本带停
ADDED=$(printf '%s\n' "$DIFF" | grep -c '^>' || true)
REMOVED=$(printf '%s\n' "$DIFF" | grep -c '^<' || true)
MISSING=$(printf '%s\n' "$DIFF" | grep '^>' | sed 's/^> //' || true)
EXTRA=$(printf '%s\n' "$DIFF" | grep '^<' | sed 's/^< //' || true)

if [ "$MODE" = "--check" ]; then
  cat <<EOF
✗ $TARGET 已过期

在哪    · 缺少（真实目录有、$TARGET 里没有）：
$(as_block "$MISSING")
          多余（$TARGET 里有、真实目录没有）：
$(as_block "$EXTRA")
为什么  · $TARGET 是仓库的目录地图，会被 agent 当作导航读；它漂移会让 agent 按错的路径找文件
怎么改  · 运行 bash scripts/check-tree.sh（会自动重新生成）
文档    · AGENTS.md · 多源真相清单 · 目录结构
EOF
  exit 1
fi

printf '%s\n' "$ACTUAL" > "$TARGET"

cat <<EOF
✗ $TARGET 已过期 —— 已自动重新生成

在哪    · 缺少（真实目录有、$TARGET 里没有）：
$(as_block "$MISSING")
          多余（$TARGET 里有、真实目录没有）：
$(as_block "$EXTRA")
为什么  · $TARGET 是仓库的目录地图，会被 agent 当作导航读；它漂移会让 agent 按错的路径找文件
怎么改  · 已自动重新生成（新增 $ADDED 条、删除 $REMOVED 条）
文档    · AGENTS.md · 多源真相清单 · 目录结构
EOF

echo
echo "提示：工作区的 $TARGET 已被修改。如果它已暂存，请重新 git add。"
exit 0
