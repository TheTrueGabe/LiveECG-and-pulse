import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# List of packages to install
packages = [
    "tkinter",  # tkinter is typically available by default in standard Python installations
    "pyserial", # This package provides the 'serial' functionality
    "matplotlib", # For plotting capabilities
    "scipy",  # Provides various scientific tools including signal processing
    "numpy"  # Essential for numerical operations
]

for package in packages:
    try:
        install(package)
        print(f"{package} installed successfully.")
    except Exception as e:
        print(f"An error occurred while installing {package}: {e}")

print("All requested packages have been processed.")