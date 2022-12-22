#!/bin/bash
ENGINE=$1
TOOL=${2:-/home/admin/JN/WS/HdRPR_Build/USD/build/bin/usdview}
PYTHON=${3:-python3.9}

python3.9 -m pip install --user -r ../jobs_launcher/install/requirements.txt
python3.9 -m pip uninstall -y opencv-python
python3.9 -m pip install opencv-python-headless==4.5.5.62
$PYTHON -m pip install -r requirements.txt
python3.9 ../jobs/Scripts/sanityCheck.py --tool_path $TOOL --res_path "$CIS_TOOLS/../TestResources/hdrpr_autotests_assets" --engine $ENGINE --python $PYTHON

