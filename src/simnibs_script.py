import os
import sys
import glob
import shutil
import argparse
from simnibs import sim_struct, run_simnibs

def run_physics_simulation(arguments):
    """
    Initializes and executes the SimNIBS Finite Element Method (FEM) solver.
    """
    session = sim_struct.SESSION()
    session.subid = arguments.subject_id
    session.pathrun = os.path.abspath(arguments.project_directory)
    session.fnamehead = os.path.abspath(arguments.head_mesh)

    output_directory = os.path.join(session.pathrun, 'output', 'simnibs', session.subid)
    os.makedirs(output_directory, exist_ok=True)
    session.pathfem = output_directory

    tms_coil_list = session.add_tmslist()
    tms_coil_list.fnamecoil = os.path.abspath(arguments.coil_file)

    pos_obj = sim_struct.POSITION() 
    pos_obj.centre = [arguments.position_x, arguments.position_y, arguments.position_z]  
    pos_obj.pos_ydir = [arguments.direction_x, arguments.direction_y, arguments.direction_z]      
    tms_coil_list.pos.append(pos_obj)

    session.open_in_gmsh = True   
    session.map_to_vol = True     
    
    # Disable surface mapping to save computation time. The downstream SUITPy 
    # mapping relies entirely on the volumetric NIfTI output.
    session.map_to_surf = False   
    session.fields = 'e'          

    run_simnibs(session)
    return session.pathfem

def standardise_output_names(output_directory):
    """
    Renames the output NIfTI file to a standard name. This ensures the 
    visualization script functions independently of SimNIBS's variable 
    naming conventions.
    """
    volume_directory = os.path.join(output_directory, "subject_volumes")
    search_pattern = os.path.join(volume_directory, "*magnE.nii.gz")
    found_files = glob.glob(search_pattern)
    
    if found_files:
        original_file = found_files[0]
        standard_file = os.path.join(volume_directory, "simulation_output.nii.gz")
        shutil.move(original_file, standard_file)
    else:
        # Halt execution and return an error code to the shell if the NIfTI 
        # file is missing. This prevents the downstream script from crashing.
        print("[ERROR] SimNIBS failed to generate a valid magnE NIfTI volume.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_directory', required=True)
    parser.add_argument('--head_mesh', required=True)
    parser.add_argument('--coil_file', required=True)
    parser.add_argument('--subject_id', required=True)
    parser.add_argument('--position_x', type=float, required=True)
    parser.add_argument('--position_y', type=float, required=True)
    parser.add_argument('--position_z', type=float, required=True)
    parser.add_argument('--direction_x', type=float, required=True)
    parser.add_argument('--direction_y', type=float, required=True)
    parser.add_argument('--direction_z', type=float, required=True)
    arguments = parser.parse_args()
    
    folder_path = run_physics_simulation(arguments)
    standardise_output_names(folder_path)
