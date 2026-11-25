@echo off
rem Picks an Afterglow colour scheme from a script: imports NAME.reg from this folder (the theme manager's ColorName and the six
rem title colours), then logs off when /logoff is given, since the registry route takes effect at the next logon. Display
rem Properties, Appearance, Color scheme switches schemes at once instead.
rem Usage: apply-scheme.cmd NAME [/logoff], NAME the file stem: dusk, ember, aurora, graphite, dusk-light, ember-light,
rem aurora-light, graphite-light (on the deploy.sh test CD the light ones are DUSKLT, EMBERLT, AURORALT, GRAPHLT)
rem (c) Copyright 2026 Liminal HQ, Scott Morris
rem SPDX-License-Identifier: Apache-2.0 OR MIT
if "%1"=="" goto usage
if not exist "%~dp0%1.reg" goto usage
regedit /s "%~dp0%1.reg"
echo apply-scheme: %1 regedit %ERRORLEVEL% >> COM1
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\ThemeManager" /v ColorName >> COM1
if /i "%2"=="/logoff" logoff
goto end
:usage
echo usage: apply-scheme.cmd NAME [/logoff], NAME one of the .reg files next to this script
:end
