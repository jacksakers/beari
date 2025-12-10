"""
Setup script for Beari3
Automates installation of dependencies and spaCy model
"""

import subprocess
import sys


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"  {description}")
    print('='*50)
    
    try:
        subprocess.check_call(command, shell=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during: {description}")
        print(f"  {e}")
        return False


def main():
    print("\n" + "="*50)
    print("   BEARI3 SETUP")
    print("="*50)
    
    # Install requirements
    success = run_command(
        "pip install -r requirements.txt",
        "Installing Python packages"
    )
    
    if not success:
        print("\n⚠️  Failed to install requirements")
        return
    
    # Download spaCy model
    success = run_command(
        f"{sys.executable} -m spacy download en_core_web_sm",
        "Downloading spaCy English model"
    )
    
    if not success:
        print("\n⚠️  Failed to download spaCy model")
        print("You can try manually: python -m spacy download en_core_web_sm")
        return
    
    print("\n" + "="*50)
    print("   SETUP COMPLETE!")
    print("="*50)
    print("\n✓ All dependencies installed")
    print("✓ spaCy model downloaded")
    print("\nYou can now run: python train.py")


if __name__ == "__main__":
    main()
