#!/bin/sh
set -eu

# =============================================================================
# TMS Simulation and Cerebellar Mapping Orchestrator
# 
# Description:
#   Runs a simulation of cerebellar magnetic induction using the MNI152 
#   template and the MagStim Double Cone Coil.
# =============================================================================

# Load configuration variables.
. ./config.sh

# Verify configuration paths to prevent missing-file errors later in execution.
if [ ! -f "$simnibs_python_executable" ]; then
    echo "[ERROR] SimNIBS executable not found. Verify config.sh paths."
    exit 1
fi

# --- STATIC EXPERIMENTAL PARAMETERS ---
# These variables lock the simulation to the standard coordinates required 
# for the cerebellar inhibition (CBI) demonstration.
subject_id="standard_cbi_mni"

position_x=30
position_y=-115.71
position_z=-40.03

direction_x=30
direction_y=-115.71
direction_z=0     

scaling_factor=70  

project_directory="."
head_mesh="./input/m2m_MNI152/MNI152.msh"
coil_file="./input/Drakaki_BrainStim_2022/MagStim_DCC.ccd"

# --- EXECUTION LOGIC ---

echo "[INFO] Initiating locked pipeline for subject: $subject_id"

# Clear existing output directories. SimNIBS requires a clean target 
# directory and will halt execution if it detects previous files here.
target_output_dir="$project_directory/output/simnibs/$subject_id"
if [ -d "$target_output_dir" ]; then
    echo "[INFO] Existing output found for $subject_id. Purging directory."
    rm -rf "$target_output_dir"
fi

echo "[INFO] Executing SimNIBS physics solver..."
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

echo "[INFO] Executing SUITPy visualization module..."
"$suitpy_python_executable" src/suitpy_script.py \
    --project_directory "$project_directory" \
    --subject_id "$subject_id" \
    --scaling_factor "$scaling_factor"

echo "[INFO] Pipeline complete."
xdg-open "$project_directory/output/suitpy/${subject_id}_cerebellar_flatmap.png" &
