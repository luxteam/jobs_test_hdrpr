#!/bin/bash
DELETE_BASELINES=${1:-False}

python3.9 -m pip install -r ../jobs_launcher/install/requirements.txt
python3.9 ../jobs_launcher/common/scripts/generate_baselines.py --results_root ../Work/Results/HdRPR --baseline_root ../Work/GeneratedBaselines --remove_old $DELETE_BASELINES
