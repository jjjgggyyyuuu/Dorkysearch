import subprocess
import sys
import os

def install_dependencies():
    """Install required packages for the domain research application."""
    print("Installing required packages...")
    
    # List of required packages
    required_packages = [
        'flask',
        'requests'
    ]
    
    # Install packages
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")
    
    # Create required directories
    os.makedirs('agents', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("Installation complete!")

if __name__ == "__main__":
    install_dependencies() 