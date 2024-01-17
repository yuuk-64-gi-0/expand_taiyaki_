@echo off
if not exist .\venv\Scripts\activate (
echo "started to create virtual environment"
python3 -m venv venv
call .\venv\Scripts\activate
echo "started to install required libraries"
pip install -r .\script\requirements.txt --no-cache-dir
call deactivate
echo "finished installing libraries"
) else (
rem 
)

echo "activating virtual environment"
call call .\venv\Scripts\activate.bat
cd script
call launcher.bat
call deactivate
cd ..