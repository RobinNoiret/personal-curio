@echo off
echo ========================================
echo   PROSIT MANAGER - DEMARRAGE PROPRE
echo ========================================
echo.
echo 1. Fermeture de tous les processus Python...
taskkill /F /IM python.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    [OK] Processus Python arretes
) else (
    echo    [INFO] Aucun processus Python en cours
)
timeout /t 2 /nobreak >nul

echo.
echo 2. Nettoyage du cache Python...
if exist src\__pycache__ (
    rd /s /q src\__pycache__
    echo    [OK] Cache supprime
) else (
    echo    [INFO] Pas de cache a supprimer
)

echo.
echo 3. Lancement de Prosit Manager...
echo.
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] L'application a rencontre une erreur
    pause
)
