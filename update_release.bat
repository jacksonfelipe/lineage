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

:: 1) Atualizar core/version.py (escreve em .new e move, para não travar se o arquivo estiver aberto no editor)
echo [1/9] Atualizando %VERSION_FILE% para !NEWVER!...
set "VERSION_FILE_NEW=core\version.py.new"
powershell -NoProfile -Command "$p='%VERSION_FILE%'; $pnew='%VERSION_FILE_NEW%'; $v='!NEWVER!'; Get-Content -Path $p -Encoding UTF8 | ForEach-Object { if ($_ -match \"__version__ = '\") { \"__version__ = '$v'\" } else { $_ } } | Set-Content -Path $pnew -Encoding UTF8"
if errorlevel 1 ( echo Erro ao gerar novo conteúdo. & pause & goto :MENU )
move /Y "%VERSION_FILE_NEW%" "%VERSION_FILE%" >nul 2>&1
if errorlevel 1 (
    echo Erro ao atualizar arquivo de versão.
    exit /b 1
)
echo       OK.

:: 2) Garantir develop e pull
echo [2/9] checkout develop e pull...
git fetch origin
git checkout develop
if errorlevel 1 exit /b 1
git pull
if errorlevel 1 exit /b 1
echo       OK.

:: 3) Commit do bump na develop
echo [3/9] Commit da versão na develop...
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
echo [4/9] checkout main e pull...
git checkout main
if errorlevel 1 exit /b 1
git pull
if errorlevel 1 exit /b 1
echo       OK.

:: 5) Merge develop em main
echo [5/9] merge develop em main...
git merge develop -m "Release v!NEWVER!: merge develop"
if errorlevel 1 (
    echo Erro no merge. Resolva conflitos e rode novamente.
    exit /b 1
)
echo       OK.

:: 6) Tag
echo [6/9] tag v!NEWVER!...
git tag -a "v!NEWVER!" -m "Release v!NEWVER!"
if errorlevel 1 (
    echo Erro ao criar tag. Tag v!NEWVER! já existe?
    exit /b 1
)
echo       OK.

:: 7) Push main e tags
echo [7/9] push origin main --tags...
git push origin main --tags
if errorlevel 1 (
    echo Erro no push. Verifique remoto e permissões.
    exit /b 1
)
echo       OK.

:: 8) Voltar para develop
echo [8/9] checkout develop...
git checkout develop
if errorlevel 1 ( echo Erro ao voltar para develop. & pause & goto :MENU )
echo       OK.

:: 9) Opcional: merge main em develop para manter histórico
echo [9/9] Sincronizar develop com main (merge main -^> develop)...
git merge main -m "Sync after release v!NEWVER!"
if errorlevel 1 (
    echo Aviso: merge main em develop falhou. Pode fazer depois pelo menu [5].
) else (
    git push origin develop
    if errorlevel 1 ( echo Aviso: push develop falhou. )
)
echo       OK.

echo.
echo ========== Concluído ==========
echo Release v!NEWVER! criada e enviada (main + tags).
echo Branch atual: develop.
echo ==========
endlocal
exit /b 0
