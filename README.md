# treegen

扫描一个目录，生成 Markdown 格式的目录树。用于给项目 README、笔记、文档自动附上一份结构清单。

## 安装与运行

本项目零依赖，**不需要安装**。两种运行方式：

```bash
# 方式一：启动脚本（推荐，免安装、免联网）
./treegen.sh .            # Git Bash / Linux / macOS
treegen.cmd .             # Windows cmd / PowerShell

# 方式二：模块入口
python -m treegen.cli .
```

只有在**已装 setuptools 且能访问 PyPI** 时，才可以用 `pip install -e .` 装成全局命令。

## 用法

```bash
treegen [path] [-o OUTPUT] [-d MAX_DEPTH] [--version]
```

| 参数 | 说明 | 默认 |
|------|------|------|
| `path` | 要扫描的目录 | `.` |
| `-o, --output` | 写入文件，而不是打印到标准输出 | 打印 |
| `-d, --max-depth` | 最大递归深度 | 不限 |
| `--version` | 显示版本号 | — |

## 示例

```bash
treegen . -d 1
```

输出是一棵 Markdown 目录树：**目录排在文件前面**，每层缩进 4 个空格，根目录名在第一行。

```text
<根目录名>/
    <子目录>/
        <文件>
    <文件>
```

> 上面是**形状示意**，不是真实输出——它不引用任何具体文件，**所以永远不会过期**。
> 完整输出见 [`TREE.md`](TREE.md)（本仓库自己的目录树），或者直接跑一遍。

## 默认忽略

`.git`、`.hg`、`.svn`、`__pycache__`、`.pytest_cache`、`.mypy_cache`、`.ruff_cache`、
`.venv`、`venv`、`node_modules`、`dist`、`build`、`.DS_Store`、`.ccgui`

## 开发

本项目零运行时依赖，测试用标准库 `unittest`：

```bash
python -m unittest discover -s tests -v
```
