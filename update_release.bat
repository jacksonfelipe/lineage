@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title Gerenciador de branches — develop ^| main

set "SCRIPT_DIR=%~dp0"
set "VERSION_FILE=core\version.py"
set "VERSION_FILE_FULL=%SCRIPT_DIR%core\version.py"
cd /d "%SCRIPT_DIR%"

:: Se recebeu argumento numérico, pula o menu (para automação)
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
if "%~1"=="5" goto :SYNC_DEVELOP_FROM_MAIN
goto :MENU

:MENU
echo.
echo ========== Workflow (workflow.md) — develop ^| main ==========
echo.
echo   [1] Atualizar develop    — checkout develop + pull
echo   [2] Atualizar main       — checkout main + pull (sincronizar local)
echo   [3] Lançar release       — nova versão: develop -^> main, tag, push
echo   [4] Status               — branch atual, última tag, pendências
echo   [5] Sincronizar develop  — merge main -^> develop (após release)
echo   [0] Sair
echo.
set /p OPCAO="Escolha (0-5): "
if "%OPCAO%"=="0" exit /b 0
if "%OPCAO%"=="1" goto :UPDATE_DEVELOP
if "%OPCAO%"=="2" goto :UPDATE_MAIN
if "%OPCAO%"=="3" goto :RELEASE
if "%OPCAO%"=="4" goto :STATUS
if "%OPCAO%"=="5" goto :SYNC_DEVELOP_FROM_MAIN
echo Opção inválida.
goto :MENU

:: ---------- [1] Atualizar develop ----------
:UPDATE_DEVELOP
echo.
echo [1] Atualizar branch develop...
git fetch origin
git checkout develop
if errorlevel 1 ( echo Erro: checkout develop falhou. & pause & goto :MENU )
git pull origin develop
if errorlevel 1 ( echo Erro: pull develop falhou. & pause & goto :MENU )
echo OK. Branch atual: develop.
pause
goto :MENU

:: ---------- [2] Atualizar main ----------
:UPDATE_MAIN
echo.
echo [2] Atualizar branch main (apenas local)...
git fetch origin
git checkout main
if errorlevel 1 ( echo Erro: checkout main falhou. & pause & goto :MENU )
git pull origin main
if errorlevel 1 ( echo Erro: pull main falhou. & pause & goto :MENU )
echo OK. Branch atual: main.
pause
goto :MENU

:: ---------- [4] Status ----------
:STATUS
echo.
echo [4] Status do repositório...
echo.
for /f "tokens=*" %%a in ('git branch --show-current 2^>nul') do set "CURRENT_BRANCH=%%a"
echo Branch atual: %CURRENT_BRANCH%
echo.
git status -sb
echo.
for /f "tokens=*" %%a in ('git describe --tags --abbrev^=0 2^>nul') do set "LAST_TAG=%%a"
if defined LAST_TAG (echo Última tag: !LAST_TAG!) else (echo Última tag: nenhuma)
echo.
pause
goto :MENU

:: ---------- [5] Sincronizar develop com main (merge main -> develop) ----------
:SYNC_DEVELOP_FROM_MAIN
echo.
echo [5] Sincronizar develop com main (merge main em develop)...
git fetch origin
git checkout develop
if errorlevel 1 ( echo Erro: checkout develop falhou. & pause & goto :MENU )
git pull origin develop
if errorlevel 1 ( echo Erro: pull develop falhou. & pause & goto :MENU )
git merge main -m "Sync: merge main into develop"
if errorlevel 1 (
    echo Conflitos no merge. Resolva e finalize manualmente.
    pause
    goto :MENU
)
git push origin develop
if errorlevel 1 ( echo Aviso: push develop falhou. & pause & goto :MENU )
echo OK. develop sincronizada com main.
pause
goto :MENU

:: ---------- [3] Lançar release ----------
:RELEASE
set "NEWVER=%~2"
if "%~2"=="" set /p NEWVER="Nova versão (ex: 1.17.51): "
set "NEWVER=!NEWVER: =!"
if "!NEWVER!"=="" (
    echo Versão não informada. Use: update_release.bat 3 1.17.51
    pause
    goto :MENU
)
if "!NEWVER:~0,1!"=="v" set "NEWVER=!NEWVER:~1!"

:: Validar: nova versão maior que version.py E maior que a última tag no Git
echo Verificando versao: arquivo + Git...
powershell -NoProfile -Command "$p='%VERSION_FILE_FULL%'; $new='!NEWVER!'; if (-not (Test-Path -LiteralPath $p)) { exit 1 }; $cur=$null; Get-Content -LiteralPath $p -Encoding UTF8 | ForEach-Object { if ($_ -match \"__version__\s*=\s*'([^']+)'\") { $cur=$matches[1] } }; if (-not $cur) { exit 1 }; try { $vCur=[System.Version]$cur; $vNew=[System.Version]$new } catch { exit 2 }; if ($vNew -le $vCur) { exit 3 }; $maxTag=$null; git tag -l 2>$null | ForEach-Object { $t=$_ -replace '^v',''; try { $v=[System.Version]$t; if ($maxTag -eq $null -or $v -gt $maxTag) { $maxTag=$v } } catch {} }; if ($maxTag -ne $null -and $vNew -le $maxTag) { exit 4 }; exit 0"
set "VER_ERR=!errorlevel!"
if !VER_ERR! geq 1 (
    echo.
    if !VER_ERR! equ 3 (
        echo Recusado: !NEWVER! nao e maior que a versao em version.py.
        echo Informe uma versao maior para lancar a release.
    ) else (
        if !VER_ERR! equ 4 (
            echo Recusado: no Git ja existe uma tag maior ou igual a !NEWVER!
            echo Use "git tag -l" para ver as tags. Informe uma versao maior.
        ) else (
            if !VER_ERR! equ 2 (
                echo Formato de versao invalido. Use apenas numeros: 1.17.51 ou 2.0.0
            ) else (
                echo Nao foi possivel ler a versao atual em %VERSION_FILE%
            )
        )
    )
    echo Release cancelada.
    pause
    goto :MENU
)
echo       OK. Versao !NEWVER! valida ^(arquivo + Git^).
echo.

echo ========== Release v!NEWVER! (workflow.md) ==========
echo.

:: 1) Atualizar core/version.py (escreve em .new e move, para não travar se o arquivo estiver aberto no editor)
echo [1/9] Atualizando %VERSION_FILE% para !NEWVER!...
set "VERSION_FILE_NEW=core\version.py.new"
powershell -NoProfile -Command "$p='%VERSION_FILE%'; $pnew='%VERSION_FILE_NEW%'; $v='!NEWVER!'; Get-Content -Path $p -Encoding UTF8 | ForEach-Object { if ($_ -match \"__version__ = '\") { \"__version__ = '$v'\" } else { $_ } } | Set-Content -Path $pnew -Encoding UTF8"
if errorlevel 1 ( echo Erro ao gerar novo conteúdo. & pause & goto :MENU )
move /Y "%VERSION_FILE_NEW%" "%VERSION_FILE%" >nul 2>&1
if errorlevel 1 (
    echo.
    echo O arquivo version.py está em uso. Feche-o no editor e tente novamente,
    echo ou copie manualmente o conteúdo de %VERSION_FILE_NEW% para %VERSION_FILE%
    if exist "%VERSION_FILE_NEW%" ( echo Arquivo gerado: %VERSION_FILE_NEW% )
    pause
    goto :MENU
)
echo       OK.

:: 2) Garantir develop e pull
echo [2/9] checkout develop e pull...
git fetch origin
git checkout develop
if errorlevel 1 ( echo Erro: checkout develop. & pause & goto :MENU )
git pull origin develop
if errorlevel 1 ( echo Erro: pull develop. & pause & goto :MENU )
echo       OK.

:: 3) Commit do bump na develop
echo [3/9] Commit da versão na develop...
git add "%VERSION_FILE%"
git commit -m "Bump version to !NEWVER!"
if errorlevel 1 (
    echo Nada para commitar (versão já igual?) ou commit falhou.
) else (
    echo       OK.
    echo [3b] Push develop...
    git push origin develop
    if errorlevel 1 ( echo Aviso: push develop falhou. )
)
echo       OK.

:: 4) Ir para main e pull
echo [4/9] checkout main e pull...
git checkout main
if errorlevel 1 ( echo Erro: checkout main. & pause & goto :MENU )
git pull origin main
if errorlevel 1 ( echo Erro: pull main. & pause & goto :MENU )
echo       OK.

:: 5) Merge develop em main
echo [5/9] merge develop em main...
git merge develop -m "Release v!NEWVER!: merge develop"
if errorlevel 1 (
    echo Conflitos. Resolva e depois: git add ., git commit, git push.
    pause
    goto :MENU
)
echo       OK.

:: 6) Tag
echo [6/9] tag v!NEWVER!...
git tag -a "v!NEWVER!" -m "Release v!NEWVER!"
if errorlevel 1 (
    echo Tag v!NEWVER! já existe? Remova ou use outra versão.
    pause
    goto :MENU
)
echo       OK.

:: 7) Push main e tags
echo [7/9] push origin main --tags...
git push origin main --tags
if errorlevel 1 (
    echo Erro no push. Verifique remoto.
    pause
    goto :MENU
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
echo ========== Release v!NEWVER! concluída ==========
echo   main: atualizada e com tag v!NEWVER!
echo   develop: atual e sincronizada com main
echo ==========
pause
goto :MENU
