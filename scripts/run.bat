set PATH=c:\python39\;c:\python39\scripts\;%PATH%
set FILE_FILTER=%1
set TESTS_FILTER="%2"
set ENGINE=%3
set RETRIES=%4
set UPDATE_REFS=%5
set PYTHON="C:\Python37\python.exe"

if not defined RETRIES set RETRIES=2
if not defined UPDATE_REFS set UPDATE_REFS="No"

python -m pip install -r ..\jobs_launcher\install\requirements.txt
%PYTHON% -m pip install -r requirements.txt
python ..\jobs_launcher\executeTests.py --test_filter %TESTS_FILTER% --file_filter %FILE_FILTER% --tests_root ..\jobs --work_root ..\Work\Results --work_dir HdRPR --cmd_variables Python %PYTHON% Tool "..\USD\build\bin\usdview" ResPath "C:\TestResources\hdrpr_autotests_assets" Engine %ENGINE% Retries %RETRIES% UpdateRefs %UPDATE_REFS%