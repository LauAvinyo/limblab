import subprocess
import sys 

folder = sys.argv[1]

# Run script 1
print("Running script 1...")
subprocess.run(["python", "20.select_isovalue.py", folder], check=True)

# Run script 2
print("Running script 2...")
subprocess.run(["python", "21.extract_surface.py", folder], check=True)

# Run script 3
print("Running script 3...")
subprocess.run(["python", "30.staging.py", folder, "../limb-stagig/src/limbstager"], check=True)

print("All scripts executed successfully.")
