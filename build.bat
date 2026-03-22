@echo off
chcp 65001 >nul
if exist "build" rmdir /s /q "build"
if exist "dist\LimbusAutoluxer" rmdir /s /q "dist\LimbusAutoluxer"

pyinstaller ^
    --onedir ^
    --name "LimbusAutoluxer" ^
    --windowed ^
    --icon=NONE ^
    app.py

if exist "battle-images" (
    xcopy "battle-images" "dist\LimbusAutoluxer\battle-images" /E /I /Y

)

pause