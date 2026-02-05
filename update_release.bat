@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title Release - Atualizar repositório e versão

:: ========== Configuração ==========
set "VERSION_FILE=core\version.py"
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: ========== Obter nova versão ==========
set "NEWVER=%~1"
if "%NEWVER%"=="" (
    set /p NEWVER="Digite a nova versão (ex: 1.17.51): "
)
if "!NEWVER!"=="" (
    echo Erro: versão não informada.
    exit /b 1
)

:: Remove 'v' se o usuário digitou v1.17.51
if "!NEWVER:~0,1!"=="v" set "NEWVER=!NEWVER:~1!"

echo.
echo ========== Workflow de Release (workflow.md) ==========
echo Versão: !NEWVER!
echo ==========

:: 1) Atualizar core/version.py
echo [1/8] Atualizando %VERSION_FILE% para !NEWVER!...
powershell -NoProfile -Command "(Get-Content -Path '%VERSION_FILE%' -Raw) -replace \"__version__ = '[^']*'\", \"__version__ = '!NEWVER!'\" | Set-Content -Path '%VERSION_FILE%'"
if errorlevel 1 (
    echo Erro ao atualizar arquivo de versão.
    exit /b 1
)
echo       OK.

:: 2) Garantir que estamos em develop e dar pull
echo [2/8] git checkout develop e pull...
git checkout develop
if errorlevel 1 exit /b 1
git pull
if errorlevel 1 exit /b 1
echo       OK.

:: 3) Commit do bump de versão na develop e push
echo [3/8] Commit e push da nova versão na develop...
git add "%VERSION_FILE%"
git commit -m "Bump version to !NEWVER!"
if errorlevel 1 (
    echo Aviso: Nada para commitar ou commit falhou. Continuando...
) else (
    git push origin develop
    if errorlevel 1 echo Aviso: push develop falhou.
)
echo       OK.

:: 4) Ir para main e pull
echo [4/8] git checkout main e pull...
git checkout main
if errorlevel 1 exit /b 1
git pull
if errorlevel 1 exit /b 1
echo       OK.

:: 5) Merge develop em main
echo [5/8] git merge develop...
git merge develop -m "Merge develop: Release !NEWVER!"
if errorlevel 1 (
    echo Erro no merge. Resolva conflitos e rode novamente.
    exit /b 1
)
echo       OK.

:: 6) Tag da release
echo [6/8] git tag v!NEWVER!...
git tag -a "v!NEWVER!" -m "Release v!NEWVER!"
if errorlevel 1 (
    echo Erro ao criar tag. Tag v!NEWVER! já existe?
    exit /b 1
)
echo       OK.

:: 7) Push main e tags
echo [7/8] git push origin main --tags...
git push origin main --tags
if errorlevel 1 (
    echo Erro no push. Verifique remoto e permissões.
    exit /b 1
)
echo       OK.

:: 8) Voltar para develop
echo [8/8] Voltando para branch develop...
git checkout develop
if errorlevel 1 exit /b 1
echo       OK.

echo.
echo ========== Concluído ==========
echo Release v!NEWVER! criada e enviada (main + tags).
echo Branch atual: develop.
echo ==========
endlocal
exit /b 0
