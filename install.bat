@echo off
echo ========================================
echo    CETRI AI Assistant Installer
echo ========================================
echo.
echo Step 1: Creating CETRI_AI folder...
echo.

REM Create CETRI_AI folder in current directory
if not exist "CETRI_AI" mkdir "CETRI_AI"

echo Step 2: Copying files to CETRI_AI folder...
echo.

REM Copy files to CETRI_AI folder
copy "CETRI_AI_Assistant.exe" "CETRI_AI\"
copy "install_step2.bat" "CETRI_AI\install.bat"
copy "README.md" "CETRI_AI\"
copy "requirements.txt" "CETRI_AI\"

echo.
echo ========================================
echo    Files copied successfully!
echo ========================================
echo.
echo CETRI_AI folder created with:
echo - CETRI_AI_Assistant.exe
echo - install.bat (ready to run)
echo - README.md
echo - requirements.txt
echo.
echo Now navigate to the CETRI_AI folder and run install.bat
echo to complete the installation.
echo.
pause
