Markdown

# TMS Simulation & Cerebellar Mapping Pipeline 🧠🧲

An automated, end-to-end computational pipeline for simulating Transcranial Magnetic Stimulation (TMS) electric fields and projecting them onto high-resolution 2D cerebellar flatmaps. 

This repository acts as a bridge between **SimNIBS** (Finite Element Method physics solver) and **SUITPy** (Cerebellar atlas and mapping toolbox). It is designed to allow researchers to visualize deep-brain magnetic induction thresholds with high computational efficiency and reproducibility.

---

## 📁 Repository Architecture

This pipeline is structured to strictly separate source code, configuration, heavy input data, and generated outputs.

```text
simulation_tms_cerebellum/
├── input/
│   ├── Drakaki_BrainStim_2022/      <-- Coil files (User provided)
│   └── m2m_MNI152/                  <-- Head mesh & FreeSurfer surfaces (User provided)
├── src/
│   ├── simnibs_script.py            <-- Physics solver module
│   └── suitpy_script.py             <-- Visualisation module
├── output/                          <-- Auto-generated results
│   ├── simnibs/                     <-- FEM calculations and NIfTI volumes
│   └── suitpy/                      <-- Final 2D PNG flatmaps
├── .gitignore                       <-- Ignores outputs and large meshes
├── config.sh                        <-- User-specific absolute software paths
├── requirements.txt                 <-- Python dependencies for SUITPy
├── run_pipeline.sh                  <-- The main executable orchestrator
└── README.md                        <-- This document

⚙️ Software Installation & Python Environments

This pipeline orchestrates two different software packages that require their own isolated Python environments. Do not attempt to install SUITPy inside the SimNIBS environment.
1. SimNIBS 4.6+

SimNIBS is a massive C++ and Python suite that comes with its own "frozen" Python environment.

    Installation: Download and install SimNIBS from the official SimNIBS website.

    Environment: You do not need to install anything via pip for SimNIBS. The pipeline will call the Python executable bundled inside your SimNIBS installation folder (e.g., simnibs_env/bin/python3).

2. SUITPy

SUITPy requires a standard Python 3.10+ environment. You must create a virtual environment specifically for this step.

    Installation: Open your terminal in the root of this repository and run:
    Bash

    # Create a virtual environment named 'venv'
    python3 -m venv venv

    # Activate the environment
    source venv/bin/activate

    # Install the specific versions of matplotlib, nibabel, and SUITPy
    pip install -r requirements.txt

🚀 Data Staging

⚠️ CRITICAL NOTE ON DATA SIZING: SimNIBS head meshes (.msh) and MRI volumes (.nii.gz) frequently exceed GitHub's 100MB file limit. Therefore, the input/ folder is explicitly ignored by version control. You must populate the input templates locally before running the pipeline.

Create an input/ folder at the root of this project and populate it with the following two items:
1. The Head Mesh (m2m_MNI152)

We use the standard MNI152 template brain.

    Where to find it: Download the m2m_MNI152.zip file from the "Example Datasets" section on the SimNIBS website.

    Action: Extract the folder and place it directly into your input/ directory. (Note: Linux is case-sensitive; ensure the folder is named exactly m2m_MNI152).

2. The Coil Model (Drakaki_BrainStim_2022)

We use the MagStim Double Cone Coil (DCC). You do not need to download this from the internet; it is bundled internally with your SimNIBS software.

    Where to find it: Navigate into your local SimNIBS installation path. The coil folder is usually located deep in the site-packages:
    .../simnibs_env/lib/python3.X/site-packages/simnibs/resources/coil_models/Drakaki_BrainStim_2022/

    Action: Copy the entire Drakaki_BrainStim_2022 folder and paste it into your input/ directory.

🛠️ Configuration

Before running, you must tell the pipeline where your software lives.

Open the config.sh file and replace the example absolute paths with the exact locations of your SimNIBS Python executable and your newly created SUITPy Python executable.
Bash

# Example config.sh
simnibs_python_executable="/path/to/your/SimNIBS-4.6/simnibs_env/bin/python3"
suitpy_python_executable="/path/to/your/simulation_tms_cerebellum/venv/bin/python"

💻 Usage

Once your inputs are staged and your config.sh is set, execute the master orchestrator script from your terminal:
Bash

bash run_pipeline.sh

Pipeline Workflow:

    Pre-flight Check: Automatically detects and safely clears out any previous output/ files for the specified subject to prevent physics engine conflicts.

    Physics Solver: Triggers src/simnibs_script.py to calculate the spatial electric field magnitude.

    Standardisation: Isolates the correct .nii.gz volume from the SimNIBS output array.

    Visualisation: Triggers src/suitpy_script.py, scales the baseline field by the stimulator power (e.g., 70 A/µs), and flattens the 3D data onto the SUIT cerebellar atlas.

    Review: Automatically opens the final high-resolution flatmap.

🖥️ Operating System Compatibility

This pipeline is orchestrated using Bash (.sh) scripts and is natively optimized for Linux environments (e.g., Ubuntu, Debian).

    macOS: macOS is a UNIX-based system, meaning bash run_pipeline.sh will work out of the box. However, pay close attention to your config.sh paths, as macOS applications are typically stored in the /Applications/ directory (e.g., /Applications/SimNIBS-4.6/...).

    Windows: Standard Windows Command Prompt cannot natively run .sh Bash scripts. To run this pipeline on Windows, it is highly recommended to install the Windows Subsystem for Linux (WSL 2). Install Ubuntu via WSL, install SimNIBS/Python inside that Linux subsystem, and run the pipeline exactly as documented above.
