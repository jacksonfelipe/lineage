@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title Gerenciador - develop ^| main

set "SCRIPT_DIR=%~dp0"
set "VERSION_FILE=core\version.py"
cd /d "%SCRIPT_DIR%"

set "SKIP_MENU=0"
if "%~1"=="1" set "SKIP_MENU=1"
if "%~1"=="2" set "SKIP_MENU=1"
if "%~1"=="3" set "SKIP_MENU=1"
if "%~1"=="4" set "SKIP_MENU=1"
if "%~1"=="5" set "SKIP_MENU=1"

if %SKIP_MENU%==0 goto :MENU
if "%~1"=="1" goto :UPDATE_DEVELOP
if "%~1"=="2" goto :UPDATE_MAIN
if "%~1"=="3" goto :RELEASE
if "%~1"=="4" goto :STATUS
if "%~1"=="5" goto :SYNC_DEVELOP
goto :MENU

:MENU
echo.
echo ========== Workflow - develop ^| main ==========
echo.
echo   [1] Atualizar develop
echo   [2] Atualizar main
echo   [3] Lancar release
echo   [4] Status
echo   [5] Sincronizar develop com main
echo   [0] Sair
echo.
set /p OPCAO="Escolha (0-5): "
if "%OPCAO%"=="0" exit /b 0
if "%OPCAO%"=="1" goto :UPDATE_DEVELOP
if "%OPCAO%"=="2" goto :UPDATE_MAIN
if "%OPCAO%"=="3" goto :RELEASE
if "%OPCAO%"=="4" goto :STATUS
if "%OPCAO%"=="5" goto :SYNC_DEVELOP
echo Opcao invalida.
goto :MENU

:UPDATE_DEVELOP
echo.
git fetch origin
git checkout develop
if errorlevel 1 ( echo Erro checkout develop. & pause & goto :MENU )
git pull origin develop
if errorlevel 1 ( echo Erro pull origin develop. & pause & goto :MENU )
echo OK. Branch: develop.
pause
goto :MENU

:UPDATE_MAIN
echo.
git fetch origin
git checkout main
if errorlevel 1 ( echo Erro checkout main. & pause & goto :MENU )
git pull origin main
if errorlevel 1 ( echo Erro pull origin main. & pause & goto :MENU )
echo OK. Branch: main.
pause
goto :MENU

:STATUS
echo.
for /f "tokens=*" %%a in ('git branch --show-current 2^>nul') do set "CURRENT=%%a"
echo Branch: %CURRENT%
git status -sb
for /f "tokens=*" %%a in ('git describe --tags --abbrev^=0 2^>nul') do set "TAG=%%a"
if defined TAG (echo Ultima tag: !TAG!) else (echo Ultima tag: nenhuma)
echo.
pause
goto :MENU

:SYNC_DEVELOP
echo.
git fetch origin
git checkout develop
if errorlevel 1 ( echo Erro. & pause & goto :MENU )
git pull origin develop
if errorlevel 1 ( echo Erro. & pause & goto :MENU )
git merge main -m "Sync: merge main into develop"
if errorlevel 1 ( echo Conflitos. & pause & goto :MENU )
git push origin develop
if errorlevel 1 ( echo Erro push. & pause & goto :MENU )
echo OK.
pause
goto :MENU

:RELEASE
set "NEWVER=%~2"
if "%~2"=="" set /p NEWVER="Nova versao (ex: 1.17.51): "
set "NEWVER=!NEWVER: =!"
if "!NEWVER!"=="" ( echo Informe a versao. & pause & goto :MENU )
if "!NEWVER:~0,1!"=="v" set "NEWVER=!NEWVER:~1!"

echo.
echo Verificando versao...
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0scripts\check_release_version.py" "!NEWVER!"
) else (
    python "%~dp0scripts\check_release_version.py" "!NEWVER!"
)
set "VER_ERR=!errorlevel!"
if !VER_ERR! geq 1 (
    echo.
    if !VER_ERR! equ 3 ( echo Recusado: !NEWVER! nao e maior que a versao em version.py )
    if !VER_ERR! equ 4 ( echo Recusado: ja existe tag maior ou igual a !NEWVER! no Git )
    if !VER_ERR! equ 2 ( echo Formato de versao invalido. Use 1.17.51 )
    if !VER_ERR! equ 1 ( echo Nao foi possivel ler version.py )
    echo Release cancelada.
    pause
    goto :MENU
)
echo OK. Versao !NEWVER! valida.
echo.

echo ========== Release v!NEWVER! ==========
echo.

echo [1/9] Atualizando version.py...
set "VERSION_NEW=core\version.py.new"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '%SCRIPT_DIR%'; $f='core\version.py'; $n='core\version.py.new'; $v='!NEWVER!'; Get-Content $f -Encoding UTF8 | ForEach-Object { if ($_ -match \"__version__ = '\") { \"__version__ = '$v'\" } else { $_ } } | Set-Content $n -Encoding UTF8"
if errorlevel 1 ( echo Erro. & pause & goto :MENU )
move /Y "%VERSION_NEW%" "%VERSION_FILE%" >nul 2>&1
if errorlevel 1 ( echo version.py em uso. Feche no editor. & pause & goto :MENU )
echo       OK.

echo [2/9] develop...
git fetch origin
git checkout develop
if errorlevel 1 ( echo Erro. & pause & goto :MENU )
git pull origin develop
if errorlevel 1 ( echo Erro. & pause & goto :MENU )
echo       OK.

echo [3/9] Commit e push develop...
git add "%VERSION_FILE%"
git commit -m "Bump version to !NEWVER!"
if not errorlevel 1 git push origin develop
echo       OK.

echo [4/9] main...
git checkout main
if errorlevel 1 ( echo Erro. & pause & goto :MENU )
git pull origin main
if errorlevel 1 ( echo Erro. & pause & goto :MENU )
echo       OK.

echo [5/9] merge develop em main...
git merge develop -m "Release v!NEWVER!: merge develop"
if errorlevel 1 ( echo Conflitos. & pause & goto :MENU )
echo       OK.

echo [6/9] tag v!NEWVER!...
git tag -a "v!NEWVER!" -m "Release v!NEWVER!"
if errorlevel 1 ( echo Tag ja existe. & pause & goto :MENU )
echo       OK.

echo [7/9] push main --tags...
git push origin main --tags
if errorlevel 1 ( echo Erro push. & pause & goto :MENU )
echo       OK.

echo [8/9] checkout develop...
git checkout develop
if errorlevel 1 ( echo Erro. & pause & goto :MENU )
echo       OK.

echo [9/9] merge main em develop...
git merge main -m "Sync after release v!NEWVER!"
if not errorlevel 1 git push origin develop
echo       OK.

echo.
echo ========== Concluido - Release v!NEWVER! ==========
pause
goto :MENU
