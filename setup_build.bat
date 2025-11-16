@echo off
REM Script d'installation des dépendances de build pour Windows

echo ========================================
echo Installation des dependances de build
echo ========================================
echo.

echo Installation de PyInstaller...
pip install -r requirements-build.txt

echo.
echo ========================================
echo Installation terminee !
echo ========================================
echo.
echo Vous pouvez maintenant lancer le build :
echo   python build.py
echo.
pause
