#!/bin/bash
set -euo pipefail

# =============================================================================
# TMS Simulation & Cerebellar Mapping Orchestrator
# 
# Usage:
#   bash run_pipeline.sh [SUBJECT_ID] [POS_X] [POS_Y] [POS_Z]
# 
# Example:
#   bash run_pipeline.sh "patient_01" 30 -115.71 -40.03
# =============================================================================

# Load environment configuration
. ./config.sh

# Sanity check: Ensure paths are configured
if [ ! -f "$simnibs_python_executable" ]; then
    echo "[ERROR] SimNIBS executable not found. Please verify config.sh."
    exit 1
fi

# --- ARGUMENT PARSING & CUSTOMIZATION ---
# Uses command-line arguments if provided, otherwise falls back to defaults.
subject_id=${1:-"standard_cbi_mni"}
position_x=${2:-30}
position_y=${3:--115.71}
position_z=${4:--40.03}

# Static parameters
scaling_factor=70  
direction_x=30
direction_y=-115.71
direction_z=0     

project_directory="."
head_mesh="./input/m2m_MNI152/MNI152.msh"
coil_file="/home/kszeilinga/software/simnibs/simnibs_env/lib/python3.11/site-packages/simnibs/resources/coil_models/Drakaki_BrainStim_2022/MagStim_DCC.ccd"

# --- EXECUTION LOGIC ---

echo "[INFO] Initiating pipeline for subject: $subject_id"

# 1. Pre-flight cleanup to prevent SimNIBS internal conflicts
target_output_dir="$project_directory/output/simnibs/$subject_id"
if [ -d "$target_output_dir" ]; then
    echo "[INFO] Existing output found for $subject_id. Purging to ensure clean run."
    rm -rf "$target_output_dir"
fi

# 2. FEM Calculation (SimNIBS)
echo "[INFO] Launching SimNIBS physics solver..."
"$simnibs_python_executable" src/simnibs_script.py \
    --project_directory "$project_directory" \
    --head_mesh "$head_mesh" \
    --coil_file "$coil_file" \
    --subject_id "$subject_id" \
    --position_x "$position_x" \
    --position_y "$position_y" \
    --position_z "$position_z" \
    --direction_x "$direction_x" \
    --direction_y "$direction_y" \
    --direction_z "$direction_z"

# 3. Projection & Visualization (SUITPy)
echo "[INFO] Launching SUITPy visualization module..."
"$suitpy_python_executable" src/suitpy_script.py \
    --project_directory "$project_directory" \
    --subject_id "$subject_id" \
    --scaling_factor "$scaling_factor"

echo "[INFO] Pipeline complete. Opening flatmap."
xdg-open "$project_directory/output/suitpy/${subject_id}_cerebellar_flatmap.png" &
