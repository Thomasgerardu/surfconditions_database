@echo off
cd C:\Github\surfconditions_database
call .\venv\Scripts\activate.bat
python C:\Github\surfconditions_database\scrape_al_and_hb.py %*
pause