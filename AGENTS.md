# treegen · 给智能体的导航

> 这是**地图**，不是手册。每条只回答「去哪找」，不重复内容。

## 这是什么

扫描目录，生成 Markdown 目录树的小工具。零运行时依赖，测试用标准库 `unittest`。

## 从哪开始

| 你想做什么 | 去哪 |
|---|---|
| 了解用法 | `README.md` |
| 看目录结构 | `TREE.md`（由工具自己生成，不是手写的） |
| 看输出示例 | `examples/sample.txt` |
| **想知道某条规矩为什么存在** | **`docs/incidents.md`** |
| 改代码 | `treegen/core.py`（扫描与渲染）· `treegen/cli.py`（参数） |

## 运行

```bash
./treegen.sh .                                    # Git Bash / Linux / macOS
treegen.cmd .                                     # Windows cmd / PowerShell
python -m unittest discover -s tests              # 测试
./treegen.sh . -d 2 -o TREE.md                    # 重新生成目录树
./treegen.sh . -d 1 -o examples/sample.txt        # 重新生成输出示例
```

## ⚠️ 多源真相清单

**这个项目里同一个事实写在多个地方。改一处，要想着另外几处。**
**报错文本里的「文档锚点」用编号引用本清单。**

| # | 事实 | 写在哪儿 |
|---|---|---|
| 1 | **版本号** | `treegen/__init__.py` · `pyproject.toml` · `CHANGELOG.md` 最新条目 |
| 2 | **支持哪些参数** | `treegen/cli.py` 的 argparse 定义 · `--help` 文本 · `README.md` 的用法表 |
| 3 | **默认忽略哪些名字** | `treegen/core.py` 的 `DEFAULT_IGNORES` · `.gitignore` · `README.md` 的「默认忽略」段 |
| 4 | **目录结构** | 真实文件系统 · `TREE.md` ← **已有检查** |
| 5 | **输出长什么样** | 真实输出 · `examples/sample.txt`（README 已改为形状示意，不再存副本） |

## 自查

```bash
bash scripts/check-tree.sh          # 第 4 条：过期会自动重新生成，然后放行
bash scripts/check-tree.sh --check  # 只检查不修改，过期则 exit 1（给 CI 用）
```

**还没被检查保护的：第 1、2、3、5 条**——它们目前靠人记着。
