set PATH=c:\python39\;c:\python39\scripts\;%PATH%
set ENGINE=%1
set TOOL=%2
set PYTHON=%3

if not defined RETRIES set RETRIES=2
if not defined UPDATE_REFS set UPDATE_REFS="No"
if not defined TOOL set TOOL="..\USD\build\bin\usdview"
if not defined PYTHON set PYTHON="C:\Python37\python.exe"

python -m pip install -r ..\jobs_launcher\install\requirements.txt
%PYTHON% -m pip install -r requirements.txt
python ..\jobs\Scripts\sanityCheck.py --tool_path %TOOL% --res_path "C:\TestResources\hdrpr_autotests_assets" --engine %ENGINE% --python %PYTHON%