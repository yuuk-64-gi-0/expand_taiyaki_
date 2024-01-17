@echo off
if not exist .\script\venv\Scripts\activate (
echo "started to create virtual environment"
python3 -m venv script\venv
call .\script\venv\Scripts\activate
echo "started to install required libraries"
pip install -r .\script\requirements.txt --no-cache-dir
call deactivate
echo "finished installing libraries"
) else (
rem 
)

echo "activating virtual environment"
call call .\script\venv\Scripts\activate.bat
cd script
call launcher.bat
call deactivate
cd ..