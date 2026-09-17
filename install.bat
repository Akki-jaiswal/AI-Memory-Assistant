@echo off
echo ===================================================
echo AI Memory Assistant - One-Click Installer
echo ===================================================
echo.
echo Privacy First: All data is saved LOCALLY on your device.
echo Nothing is ever sent to the cloud.
echo.
echo Please ensure Python is installed on your system.
pause

echo.
if not exist requirements.txt (
    echo ===================================================
    echo [ERROR] COULD NOT FIND requirements.txt!
    echo ===================================================
    echo Are you running this directly from inside the downloaded ZIP file?
    echo You MUST extract the folder first!
    echo.
    echo 1. Close this window.
    echo 2. Right-click the downloaded .zip file and select "Extract All..."
    echo 3. Open the new extracted folder and run install.bat again.
    echo.
    pause
    exit
)

echo [1/2] Installing required AI libraries (This may take a minute)...
pip install -r requirements.txt

echo.
echo [2/2] Starting the Assistant silently in the background...
start pythonw MemoryAssistant.pyw

echo.
echo ===================================================
echo INSTALLATION COMPLETE!
echo ===================================================
echo Look for the Blue Square icon in your Windows Taskbar 
echo (bottom right corner near your clock).
echo Double click it to search your memory!
echo.
pause
