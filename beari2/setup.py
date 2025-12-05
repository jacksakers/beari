"""
Installation and setup script for Beari2
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages."""
    print("="*70)
    print("📦 Installing Dependencies")
    print("="*70)
    print()
    
    try:
        print("Installing Flask and Flask-CORS...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\n✓ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing dependencies: {e}")
        return False

def initialize_db():
    """Initialize the database."""
    print("\n" + "="*70)
    print("🗄️  Initializing Database")
    print("="*70)
    print()
    
    try:
        from db.init_db import initialize_database
        initialize_database("beari2.db")
        print()
        return True
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        return False

def run_tests():
    """Run system tests."""
    print("\n" + "="*70)
    print("🧪 Running System Tests")
    print("="*70)
    print()
    
    try:
        result = subprocess.run([sys.executable, "test_system.py"], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return False

def main():
    """Main setup routine."""
    print("\n" + "="*70)
    print("🐻 Beari2 Installation & Setup")
    print("="*70)
    print()
    print("This script will:")
    print("  1. Install Python dependencies (Flask, Flask-CORS)")
    print("  2. Initialize the database")
    print("  3. Run system tests")
    print()
    
    choice = input("Continue with setup? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("\nSetup cancelled.")
        return
    
    # Step 1: Install dependencies
    print()
    if not install_dependencies():
        print("\n⚠️  Setup incomplete. Please install dependencies manually.")
        print("   Run: pip install -r requirements.txt")
        return
    
    # Step 2: Initialize database
    if not initialize_db():
        print("\n⚠️  Setup incomplete. Please initialize database manually.")
        print("   Run: python db/init_db.py")
        return
    
    # Step 3: Run tests
    if not run_tests():
        print("\n⚠️  Tests failed. Please check the errors above.")
        return
    
    # Success!
    print("\n" + "="*70)
    print("✅ Setup Complete!")
    print("="*70)
    print()
    print("🚀 You're ready to use Beari2!")
    print()
    print("Quick Start:")
    print("  • Chat interface:      python beari2.py")
    print("  • Real-time viewer:    python viewer/app.py")
    print("  • Interactive demo:    python demo.py")
    print("  • Guided start:        python start.py")
    print()
    print("Documentation:")
    print("  • README.md           - User guide")
    print("  • PROJECT_OVERVIEW.md - Technical details")
    print()
    print("Tip: Run the viewer first, then chat, to see objects grow in real-time!")
    print()

if __name__ == "__main__":
    main()
