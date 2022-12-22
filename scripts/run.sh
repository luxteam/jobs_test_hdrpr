#!/bin/bash
FILE_FILTER=$1
TESTS_FILTER="$2"
ENGINE=$3
RETRIES=${4:-2}
UPDATE_REFS=${5:-No}
TOOL=${6:-/home/admin/JN/WS/HdRPR_Build/USD/build/bin/usdview}
PYTHON=${7:-python3.9}

python3.9 -m pip install --user -r ../jobs_launcher/install/requirements.txt
python3.9 -m pip uninstall -y opencv-python
python3.9 -m pip install opencv-python-headless==4.5.5.62
$PYTHON -m pip install -r requirements.txt
python3.9 ../jobs_launcher/executeTests.py --test_filter $TESTS_FILTER --file_filter $FILE_FILTER --tests_root ../jobs --work_root ../Work/Results --work_dir HdRPR --cmd_variables Python $PYTHON Tool $TOOL ResPath "$CIS_TOOLS/../TestResources/hdrpr_autotests_assets" Engine $ENGINE Retries $RETRIES UpdateRefs $UPDATE_REFS

