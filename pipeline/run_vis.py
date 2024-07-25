import subprocess
import sys 

folder = sys.argv[1]

# Run script 1

print("Running script 0...")
subprocess.run(["python", "41.rotate.py", folder], check=True)

print("Running script 1...")
subprocess.run(["python", "60.smooth.py", folder], check=True)

# Run script 2
print("Running script 2...")
subprocess.run(["python", "61.isosurface_pickers.py", folder], check=True)

# Run script 3
print("Running script 3...")
subprocess.run(["python", "62.visualize_isosurfaces.py", folder], check=True)

print("All scripts executed successfully.")
