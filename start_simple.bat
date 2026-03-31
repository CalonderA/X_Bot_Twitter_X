@echo off
chcp 65001 >nul
cls
echo.
echo ==========================================
echo     TWITTER BOT - Quick Launch
echo ==========================================
echo.

:: Find Python
set PYTHON_CMD=
for %%C in (python python3 py) do (
    %%C --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=%%C
        goto :found_python
    )
)

:found_python
if "%PYTHON_CMD%"=="" (
    echo [X] Python not found in PATH!
    echo.
    echo Trying common locations...
    
    for %%P in (
        "%LOCALAPPDATA%\Programs\Python\Python3*\python.exe"
        "C:\Python3*\python.exe"
        "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python3*\python.exe"
    ) do (
        if exist "%%P" (
            set PYTHON_CMD=%%P
            echo [OK] Found: %%P
            goto :python_ok
        )
    )
    
    echo.
    echo [X] Python not found!
    echo Please install Python 3.10+ from https://python.org
    echo Or add Python to your PATH
    echo.
    pause
    exit /b 1
)

:python_ok
echo [OK] Python found: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

:: Use system Python directly (no venv)
set PYTHON=%PYTHON_CMD%

:: Check dependencies
echo [*] Checking dependencies...
%PYTHON% -c "import aiohttp" >nul 2>&1
if errorlevel 1 (
    echo [+] Installing dependencies...
    %PYTHON% -m pip install -r requirements.txt --user
    if errorlevel 1 (
        echo [!] Some dependencies failed, installing basic...
        %PYTHON% -m pip install loguru python-dotenv aiohttp aiosqlite --user
    )
    echo [OK] Dependencies installed
echo.
) else (
    echo [OK] Dependencies found
echo.
)

:: Menu
:menu
cls
echo.
echo ==========================================
echo     TWITTER BOT - Select Mode
echo ==========================================
echo.
echo  [1] Run DEMO version (final_bot.py)
echo        - Works without setup
echo        - Shows all features
echo        - Simulation mode
echo.
echo  [2] Run full GUI (gui.py)
echo        - Full interface
echo        - Real Twitter work
echo        - Requires account setup
echo.
echo  [3] Exit
echo.
echo ==========================================
set /p choice="Select mode (1-3): "

if "%choice%"=="1" goto demo
if "%choice%"=="2" goto gui
if "%choice%"=="3" goto exit

echo [X] Invalid choice. Try again.
timeout /t 2 >nul
goto menu

:demo
echo.
echo [>>] Starting DEMO version...
echo Press Ctrl+C to stop
echo.
%PYTHON% final_bot.py
goto end

:gui
echo.
echo [>>] Checking GUI requirements...

:: Check tkinter
%PYTHON% -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [!] tkinter not found! Installing...
    %PYTHON% -m pip install tk --user
    if errorlevel 1 (
        echo [X] Failed to install tkinter.
        echo [*] Please install full Python from python.org with tcl/tk option.
        echo.
        pause
        goto menu
    )
    echo [OK] tkinter installed!
    echo.
)

echo [>>] Starting GUI...
echo Add account and press Start
echo.
%PYTHON% gui.py
goto end

:exit
echo.
echo Bye!
exit /b 0

:end
echo.
echo [=] Done
echo.
pause
