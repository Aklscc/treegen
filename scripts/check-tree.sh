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
#   bash scripts/check-tree.sh --check  只检查不修改，过期则 exit 1（给 CI 用）
#
# 为什么分两种模式：「能自动修复」和「该不该阻断」是两个独立的问题。
# 本地跑时修完就该放行；CI 里改不了工作区，只能红——而 CI 红说明有人没跑本地检查。
#
# 实现上不落临时文件（用进程替换），避免平台差异带来的清理问题。

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

TARGET="TREE.md"
MODE="${1:-fix}"

CURRENT="$(cat "$TARGET")"
ACTUAL="$(./treegen.sh . -d 2)"

if [ "$CURRENT" = "$ACTUAL" ]; then
  echo "✓ $TARGET 与真实目录结构一致"
  exit 0
fi

DIFF="$(diff <(printf '%s\n' "$CURRENT") <(printf '%s\n' "$ACTUAL") || true)"
# 注意：每条都要 || true —— 开了 pipefail，grep 找不到匹配会返回 1，会把整个脚本带停
ADDED=$(printf '%s\n' "$DIFF" | grep -c '^>' || true)
REMOVED=$(printf '%s\n' "$DIFF" | grep -c '^<' || true)
MISSING=$(printf '%s\n' "$DIFF" | grep '^>' | sed -E 's/^> +//' | tr '\n' ' ' || true)
EXTRA=$(printf '%s\n' "$DIFF" | grep '^<' | sed -E 's/^< +//' | tr '\n' ' ' || true)

if [ "$MODE" = "--check" ]; then
  cat <<EOF
✗ $TARGET 已过期

在哪    · 缺少：${MISSING:-无}
          多余：${EXTRA:-无}
为什么  · $TARGET 是仓库的目录地图，会被 agent 当作导航读；它漂移会让 agent 按错的路径找文件
怎么改  · 运行 bash scripts/check-tree.sh（会自动重新生成）
文档    · AGENTS.md · 多源真相清单 · 目录结构
EOF
  exit 1
fi

printf '%s\n' "$ACTUAL" > "$TARGET"

cat <<EOF
✗ $TARGET 已过期 —— 已自动重新生成

在哪    · 缺少：${MISSING:-无}
          多余：${EXTRA:-无}
为什么  · $TARGET 是仓库的目录地图，会被 agent 当作导航读；它漂移会让 agent 按错的路径找文件
怎么改  · 已自动重新生成（新增 $ADDED 条、删除 $REMOVED 条）
文档    · AGENTS.md · 多源真相清单 · 目录结构
EOF

echo
echo "提示：工作区的 $TARGET 已被修改。如果它已暂存，请重新 git add。"
exit 0
