@echo off

set VENV_DIR=..\venv

python -m venv %VENV_DIR%

call %VENV_DIR%\Scripts\activate

python -m pip install --upgrade pip

IF EXIST ..\requirements.txt (
    pip install -r ..\requirements.txt
)

echo.
echo Created venv in %VENV_DIR% and installed dependencies!
echo Further venv activation: %VENV_DIR%\Scripts\activate
pause