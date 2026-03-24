@echo off
chcp 65001 >nul

if exist "build" rmdir /s /q "build"
if exist "dist\LimbusAutoluxer" rmdir /s /q "dist\LimbusAutoluxer"

pyinstaller ^
    --onedir ^
    --name "LimbusAutoluxer" ^
    --windowed ^
    --icon=NONE ^
    --hidden-import=pynput.mouse ^
    --hidden-import=pynput.keyboard ^
    --hidden-import=pydirectinput ^
    --hidden-import=mss ^
    --hidden-import=cv2 ^
    --hidden-import=numpy ^
    --hidden-import=pygetwindow ^
    --collect-all=tkinter ^
    app.py

if %errorlevel% neq 0 (
    echo Ошибка сборки
    pause
    exit /b 1
)

if exist "battle-images" (
    xcopy "battle-images" "dist\LimbusAutoluxer\battle-images" /E /I /Y
) else (
    echo Папка battle-images не найдена!
)

pause