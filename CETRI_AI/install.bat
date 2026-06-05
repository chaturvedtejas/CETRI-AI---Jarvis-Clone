@echo off
echo ========================================
echo    CETRI AI Assistant - Final Installation
echo ========================================
echo.
echo Installing CETRI AI Assistant to your system...
echo.

REM Create installation directory in user profile
if not exist "%USERPROFILE%\CETRI_AI" mkdir "%USERPROFILE%\CETRI_AI"

REM Copy executable and files
copy "CETRI_AI_Assistant.exe" "%USERPROFILE%\CETRI_AI\"
copy "README.md" "%USERPROFILE%\CETRI_AI\"
copy "requirements.txt" "%USERPROFILE%\CETRI_AI\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\CETRI AI Assistant.lnk'); $Shortcut.TargetPath = '%USERPROFILE%\CETRI_AI\CETRI_AI_Assistant.exe'; $Shortcut.WorkingDirectory = '%USERPROFILE%\CETRI_AI'; $Shortcut.IconLocation = '%%SystemRoot%%\system32\SHELL32.dll,13'; $Shortcut.Save()"

REM Create start menu entry
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\CETRI AI" mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\CETRI AI"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\CETRI AI\CETRI AI Assistant.lnk'); $Shortcut.TargetPath = '%USERPROFILE%\CETRI_AI\CETRI_AI_Assistant.exe'; $Shortcut.WorkingDirectory = '%USERPROFILE%\CETRI_AI'; $Shortcut.IconLocation = '%%SystemRoot%%\system32\SHELL32.dll,13'; $Shortcut.Save()"

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo CETRI AI Assistant has been installed to:
echo %USERPROFILE%\CETRI_AI\
echo.
echo Shortcuts created:
echo - Desktop: CETRI AI Assistant
echo - Start Menu: CETRI AI\CETRI AI Assistant
echo.
echo Double-click the desktop shortcut to launch CETRI!
echo First run may take longer as Whisper downloads models.
echo.
pause
