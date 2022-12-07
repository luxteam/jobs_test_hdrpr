set PATH=c:\python39\;c:\python39\scripts\;%PATH%
set ENGINE=%1
set PYTHON="C:\Python37\python.exe"
set TOOL=%6

if not defined RETRIES set RETRIES=2
if not defined UPDATE_REFS set UPDATE_REFS="No"
if not defined TOOL set TOOL="..\USD\build\bin\usdview"

python -m pip install -r ..\jobs_launcher\install\requirements.txt
%PYTHON% -m pip install -r requirements.txt
python ..\jobs\Scripts\sanityCheck.py --tool_path %TOOL% --res_path "C:\TestResources\hdrpr_autotests_assets" --engine %ENGINE% --python %PYTHON%