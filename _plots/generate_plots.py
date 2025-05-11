import os
import json
import importlib
import glob
from pathlib import Path

def generate_all_plots():
    """Generate all plots from Python scripts in the _plots directory."""
    # Create plots directory if it doesn't exist
    os.makedirs("assets/plots", exist_ok=True)
    
    # Get all Python files in the _plots directory except this script
    plot_scripts = [f for f in glob.glob("_plots/*.py") 
                  if not f.endswith("generate_plots.py")]
    
    # Dictionary to store metadata about all generated plots
    plots_metadata = {}
    
    # Process each plot script
    for script_path in plot_scripts:
        script_name = os.path.basename(script_path)[:-3]  # Remove .py extension
        print(f"Processing {script_name}...")
        
        try:
            # Import the script as a module
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # If the module has a generate_plots function, call it
            if hasattr(module, 'generate_plots'):
                # Generate plots should return a dictionary of plot metadata
                script_plots = module.generate_plots()
                plots_metadata.update(script_plots)
            else:
                print(f"Warning: {script_name} does not have a generate_plots function")
        except Exception as e:
            print(f"Error processing {script_name}: {e}")
    
    # Save metadata about all plots for the build script to use
    with open("_plots/plots_metadata.json", "w") as f:
        json.dump(plots_metadata, f, indent=2)
    
    print(f"Generated {len(plots_metadata)} plots")
    return plots_metadata

if __name__ == "__main__":
    generate_all_plots()