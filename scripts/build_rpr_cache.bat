set PATH=c:\python39\;c:\python39\scripts\;%PATH%
set ENGINE=%1
set PYTHON="C:\Python37\python.exe"

if not defined RETRIES set RETRIES=2
if not defined UPDATE_REFS set UPDATE_REFS="No"

python -m pip install -r ..\jobs_launcher\install\requirements.txt
%PYTHON% -m pip install -r requirements.txt
python ..\jobs\Scripts\sanityCheck.py --tool_path "..\USD\build\bin\usdview" --res_path "C:\TestResources\hdrpr_autotests_assets" --engine %ENGINE% --python %PYTHON%