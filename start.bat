@echo off
title Hisab-Kitab Telegram Bot
echo ===================================================
echo Starting Hisab-Kitab Telegram Bot (@Hisab_Kitab_1Bot)...
echo ===================================================
cd /d "%~dp0"
py -3.10 -m hisab_kitab_bot.bot
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Bot stopped with an error. Trying with python...
    python -m hisab_kitab_bot.bot
)
pause
