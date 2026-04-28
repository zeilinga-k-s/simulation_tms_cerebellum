import os
import argparse
import matplotlib.pyplot as plt
import SUITPy.flatmap as flatmap

# =============================================================================
# VISUALISATION CONFIGURATION
# =============================================================================
# Set a 5 V/m threshold to isolate relevant cortical induction from background noise.
PLOT_THRESHOLD = 5       

# Cap the color scale at 80 V/m so deeper cerebellar gradients remain visible 
# against much higher superficial maxima.
COLOUR_MAXIMUM = 80           
COLOUR_MAP = "magma"
FIGURE_SIZE = (10, 8)

# Use nanmean projection to average voxel values across cortical depth. 
# This avoids localization artifacts common with maximum-value projections.
PROJECTION_METHOD = "nanmean"
# =============================================================================

def generate_cerebellar_flatmap(arguments):
    """
    Extracts the FEM volumetric data, projects it to a 2D surface, and 
    scales the magnitude to reflect experimental stimulator intensities.
    """
    electric_field_file = os.path.join(
        os.path.abspath(arguments.project_directory), 
        "output",
        "simnibs", 
        arguments.subject_id, 
        "subject_volumes", 
        "simulation_output.nii.gz"
    )
    
    # Map the unscaled 3D volume directly to the 2D surface. This avoids loading 
    # and transforming the full 3D array in memory.
    raw_surface_data = flatmap.vol_to_surf(
        electric_field_file,
        space="MNI",      
        stats=PROJECTION_METHOD,
        ignore_zeros=True,
    )

    # Scale the projected 1D array instead of the 3D volume. Because nanmean 
    # is a linear operation, this produces the exact same mathematical result 
    # with far less computation.
    surface_data = raw_surface_data * arguments.scaling_factor

    plt.figure(figsize=FIGURE_SIZE)
    
    flatmap.plot(
        data=surface_data,
        cmap=COLOUR_MAP,
        cscale=[0, COLOUR_MAXIMUM],   
        threshold=PLOT_THRESHOLD,      
        render="matplotlib",
        colorbar=True,       
        new_figure=False,
    )

    plt.title(f"Cerebellar |E| (V/m) - Scaled to {arguments.scaling_factor} A/µs", pad=20)
    
    # Remove boundary lines and axes from the plot
    main_brain_axis = plt.gcf().axes[0]
    main_brain_axis.axis('off')

    colourbar_axis = plt.gcf().axes[-1]
    colourbar_axis.set_ylabel("Electric Field (V/m)", rotation=270, labelpad=20, fontsize=12)

    suitpy_output_directory = os.path.join(os.path.abspath(arguments.project_directory), "output", "suitpy")
    os.makedirs(suitpy_output_directory, exist_ok=True)
    output_image_path = os.path.join(suitpy_output_directory, f"{arguments.subject_id}_cerebellar_flatmap.png")
    
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight', transparent=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_directory', required=True)
    parser.add_argument('--subject_id', required=True)
    parser.add_argument('--scaling_factor', type=float, required=True)
    arguments = parser.parse_args()
    
    generate_cerebellar_flatmap(arguments)
