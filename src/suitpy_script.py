import os
import argparse
import tempfile
import matplotlib.pyplot as plt
import nibabel as nb
import SUITPy.flatmap as flatmap

def generate_cerebellar_flatmap(arguments):
    """
    Loads the 3D physics data, multiplies it by the stimulator power, 
    and squashes it into a 2D flatmap for scientific visualisation.
    """
    # -------------------------------------------------------------------------
    # VISUALISATION SETTINGS
    # -------------------------------------------------------------------------
    PLOT_THRESHOLD = 5       
    COLOUR_MAXIMUM = 80           
    COLOUR_MAP = "magma"
    FIGURE_SIZE = (10, 8)
    PROJECTION_METHOD = "nanmean"
    # -------------------------------------------------------------------------

    # Update: Now reads from the 'output' parent directory
    electric_field_file = os.path.join(
        os.path.abspath(arguments.project_directory), 
        "output",
        "simnibs", 
        arguments.subject_id, 
        "subject_volumes", 
        "simulation_output.nii.gz"
    )

    print(f"LOADING STANDARDISED DATA FROM: {electric_field_file}")
    
    image_data = nb.load(electric_field_file)
    scaled_data_array = image_data.get_fdata() * arguments.scaling_factor

    with tempfile.NamedTemporaryFile(suffix='.nii.gz', delete=True) as temp_file:
        scaled_file_name = temp_file.name
        scaled_image_object = nb.Nifti1Image(scaled_data_array, image_data.affine, image_data.header)
        nb.save(scaled_image_object, scaled_file_name)

        print("MAPPING VOLUME TO FLATMAP...")
        surface_data = flatmap.vol_to_surf(
            scaled_file_name,
            space="MNI",      
            stats=PROJECTION_METHOD,
            ignore_zeros=True,
        )

    print("GENERATING VISUALISATION...")
    figure = plt.figure(figsize=FIGURE_SIZE)
    
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
    
    main_brain_axis = plt.gcf().axes[0]
    main_brain_axis.axis('off')

    colourbar_axis = plt.gcf().axes[-1]
    colourbar_axis.set_ylabel("Electric Field (V/m)", rotation=270, labelpad=20, fontsize=12)

    # Update: Now saves inside the 'output' parent directory
    suitpy_output_directory = os.path.join(os.path.abspath(arguments.project_directory), "output", "suitpy")
    os.makedirs(suitpy_output_directory, exist_ok=True)
    
    output_image_path = os.path.join(suitpy_output_directory, f"{arguments.subject_id}_cerebellar_flatmap.png")
    
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight', transparent=True)
    print(f"--- SUCCESS: FLATMAP SAVED TO {output_image_path} ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_directory', required=True)
    parser.add_argument('--subject_id', required=True)
    parser.add_argument('--scaling_factor', type=float, required=True)
    arguments = parser.parse_args()
    
    generate_cerebellar_flatmap(arguments)
