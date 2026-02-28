import os
import subprocess
import sys
import customtkinter

def build_app():
    # Get the location of customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    
    # Path to the main script
    main_script = "main.py"
    
    # Check if assets directory exists
    if not os.path.exists("assets"):
        os.makedirs("assets")
        print("Created missing assets directory.")
    
    # Build the PyInstaller command
    # --noconsole: Don't show terminal window
    # --onefile: Combine everything into a single .exe
    # --add-data: Include assets and customtkinter data files
    # Syntax for --add-data on Windows is "source;destination"
    
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--name=Multi-Buzzer",
        f"--add-data=assets;assets",
        f"--add-data={ctk_path};customtkinter",
        main_script
    ]
    
    print("Running PyInstaller build command...")
    print(" ".join(cmd))
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild successful! Your standalone app is in the 'dist' folder.")
    except Exception as e:
        print(f"\nBuild failed: {e}")

if __name__ == "__main__":
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    build_app()
