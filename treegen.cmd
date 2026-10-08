@echo off
rem 免安装启动脚本：不依赖 pip / setuptools，直接用模块入口运行。
rem 用法：treegen.cmd <参数...>
setlocal
set "DIR=%~dp0"
set "PYTHONPATH=%DIR%;%PYTHONPATH%"
python -m treegen.cli %*
