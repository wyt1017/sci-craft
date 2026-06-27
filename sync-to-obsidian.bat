@echo off
REM sci-craft 同步到 Obsidian Vault 脚本
REM 请双击此文件执行同步

set SOURCE=D:\TRAE SOLO CN\写skill
set OBSIDIAN=C:\Users\33834\agnes_project\Obsidian Vault

echo ========================================
echo 开始同步 sci-craft 到 Obsidian Vault
echo ========================================

REM 创建目录
if not exist "%OBSIDIAN%\sci-craft" mkdir "%OBSIDIAN%\sci-craft"

REM 复制文件
copy /Y "%SOURCE%\sci-craft-main.md" "%OBSIDIAN%\sci-craft.md" >nul
copy /Y "%SOURCE%\sci-craft-design.md" "%OBSIDIAN%\sci-craft\design.md" >nul
copy /Y "%SOURCE%\sci-craft-plan.md" "%OBSIDIAN%\sci-craft\plan.md" >nul
copy /Y "%SOURCE%\sci-craft-skills.md" "%OBSIDIAN%\sci-craft\skills.md" >nul
copy /Y "%SOURCE%\sci-craft-comparison.md" "%OBSIDIAN%\sci-craft\comparison.md" >nul

echo.
echo ========================================
echo 同步完成！
echo ========================================
echo.
echo 已同步文件：
echo   - %OBSIDIAN%\sci-craft.md
echo   - %OBSIDIAN%\sci-craft\design.md
echo   - %OBSIDIAN%\sci-craft\plan.md
echo   - %OBSIDIAN%\sci-craft\skills.md
echo   - %OBSIDIAN%\sci-craft\comparison.md
echo.
pause
