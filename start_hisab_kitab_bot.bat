@echo off
title Hisab-Kitab Telegram Bot (@Hisab_Kitab_1Bot)
cd /d "%~dp0"
echo ========================================================
echo   Starting Hisab-Kitab Telegram Bot (@Hisab_Kitab_1Bot)
echo   Deals Fetcher Ecosystem - 100%% Free & Lifetime
echo ========================================================
echo.
py -3.10 -m hisab_kitab_bot.bot
if %errorlevel% neq 0 (
    echo.
    echo Bot stopped with code %errorlevel%.
    pause
)
