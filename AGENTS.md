# treegen · 给智能体的导航

> 这是**地图**，不是手册。每条只回答「去哪找」，不重复内容。

## 这是什么

扫描目录，生成 Markdown 目录树的小工具。零运行时依赖，测试用标准库 `unittest`。

## 从哪开始

| 你想做什么 | 去哪 |
|---|---|
| 了解用法 | `README.md` |
| 看目录结构 | `TREE.md`（由工具自己生成，不是手写的） |
| 看输出示例 | `TREE.md`（本仓库自己的目录树） |
| **想知道某条规矩为什么存在** | **`docs/incidents.md`** |
| 改代码 | `treegen/core.py`（扫描与渲染）· `treegen/cli.py`（参数） |

## 运行

```bash
./treegen.sh .                                    # Git Bash / Linux / macOS
treegen.cmd .                                     # Windows cmd / PowerShell
python -m unittest discover -s tests              # 测试
./treegen.sh . -d 2 -o TREE.md                    # 重新生成目录树
bash scripts/check-tree.sh                        # 校验 TREE.md 是否最新
```

## 输出约定

| 通道 | 用途 | 会被 `>` 重定向吗 |
|---|---|---|
| **stdout** | **数据**（产物） | **会** —— `treegen . > TREE.md` |
| **stderr** | **诊断**（警告、错误） | 不会 |

**退出码**：`0` = 完整成功；**非 0 = 有目录被跳过，产物残缺**。

> 日志绝不能走 stdout——它会污染产物。见 `docs/incidents.md` 事故 05。

## ⚠️ 多源真相清单

**这个项目里同一个事实写在多个地方。改一处，要想着另外几处。**
**报错文本里的「文档锚点」用编号引用本清单。**

| # | 事实 | 写在哪儿 |
|---|---|---|
| 1 | **版本号** | `treegen/__init__.py` · `pyproject.toml` · `CHANGELOG.md` 最新条目 |
| 2 | **支持哪些参数** | `treegen/cli.py` 的 argparse 定义 · `--help` 文本 · `README.md` 的用法表 |
| 3 | **默认忽略哪些名字** | `treegen/core.py` 的 `DEFAULT_IGNORES` · `.gitignore` · `README.md` 的「默认忽略」段 |
| 4 | **目录结构** | 真实文件系统 · `TREE.md` ← **已有检查** |
| 5 | **输出长什么样** | 真实输出 · `TREE.md`（README 只有形状示意，不存副本） |

> ⚠️ **第 4 条的范围**：`TREE.md` 是 `treegen . -d 2` 的产物，**只覆盖前两层**。
> 深度超过 2 的文件（例如 `treegen/utils/helpers.py`）**不在它里面**——这是 `-d 2` 的定义，不是漂移。
> **`check-tree.sh` 检查的是「TREE.md 与 `-d 2` 的输出一致」，不是「TREE.md 覆盖了全部文件」。** 两者不要混。
>
> **这是一个设计取舍，刻意不机械化**：「深度够不够」没有可判定的标准，取决于你期望它覆盖什么。
> 硬做只会得到一个永远绿的假检查（见知识点笔记 K3.4）。
> **所以：把 `TREE.md` 当"前两层概览"用，不要当"完整清单"用。**

## 自查

```bash
bash scripts/check-tree.sh          # 第 4 条：过期会自动重新生成，然后放行
bash scripts/check-tree.sh --check  # 只检查不修改，过期则 exit 1
```

**本地守卫**：`.githooks/pre-commit` 会在提交前跑 `--check` 模式。

> **启用是本地配置，不随仓库走**——新克隆的人要自己跑一次：
> ```bash
> git config core.hooksPath .githooks
> ```
> **不跑就没有 hook。** 这就是「本地 Hook 可绕过」的具体形态——不是恶意绕过，是根本不知道要启用。
> **真正兜底的是 CI**（尚未搭建）。

**为什么 hook 用 `--check` 而不是修复模式**：pre-commit 时改文件 = 改你正在提交的内容；而「修了但不 add」比不修更糟（提交里留着旧版本，工作区是新版本）。**只检查，把决策留给人。**

**还没被检查保护的：第 1、2、3、5 条**——它们目前靠人记着。
