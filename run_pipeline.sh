#!/bin/bash
set -euo pipefail
# =============================================================================
# TMS SIMULATION & CEREBELLAR MAPPING PIPELINE
# =============================================================================

# --- 1. LOAD CONFIGURATION ---
. ./config.sh

# --- 2. FILE PATHS (Relative) ---
project_directory="."
head_mesh="./input/m2m_MNI152/MNI152.msh"
coil_file="/home/kszeilinga/software/simnibs/simnibs_env/lib/python3.11/site-packages/simnibs/resources/coil_models/Drakaki_BrainStim_2022/MagStim_DCC.ccd"

# --- 3. SIMULATION SETTINGS ---
subject_id="standard_cbi_mni"
scaling_factor=70  

# --- 4. COIL POSITION & DIRECTION ---
position_x=30
position_y=-115.71
position_z=-40.03

direction_x=30
direction_y=-115.71
direction_z=0     

# =============================================================================
# EXECUTION LOGIC 
# =============================================================================

echo "========================================"
echo " STEP 0: PRE-FLIGHT CHECKS              "
echo "========================================"
# Update: Now points inside the 'output' parent directory
target_output_dir="$project_directory/output/simnibs/$subject_id"
if [ -d "$target_output_dir" ]; then
    echo "Notice: Previous simulation found for $subject_id. Clearing old files..."
    rm -rf "$target_output_dir"
fi
echo "Environment clear. Proceeding."

echo "========================================"
echo " STEP 1: EXECUTING PHYSICS SOLVER       "
echo "========================================"

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

if [ $? -ne 0 ]; then
    echo "ERROR: SimNIBS simulation failed. Exiting pipeline."
    exit 1
fi

echo "========================================"
echo " STEP 2: EXECUTING VISUALISATION        "
echo "========================================"

# We no longer source activate. We just use the direct python executable.
"$suitpy_python_executable" src/suitpy_script.py \
    --project_directory "$project_directory" \
    --subject_id "$subject_id" \
    --scaling_factor "$scaling_factor"

echo "========================================"
echo " PIPELINE COMPLETE. OPENING FLATMAP.    "
echo "========================================"

# Update: Now opens the image from the 'output' parent directory
xdg-open "$project_directory/output/suitpy/${subject_id}_cerebellar_flatmap.png" &
