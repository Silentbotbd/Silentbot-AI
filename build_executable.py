import PyInstaller.__main__
import os
import shutil

print("--- BUILDING SILENTBOT EXECUTABLE ---")

# Define build arguments
args = [
    'main.py',                       # Entry point
    '--name=SilentBot',              # Executable name
    '--onefile',                     # Single .exe file
    '--console',                     # Console application (so CLI works)
    '--add-data=src/silentbot/ui/index.html;src/silentbot/ui', # Include UI
    '--icon=src/silentbot/ui/static/favicon.ico',
    '--clean',
]

# Run PyInstaller
try:
    PyInstaller.__main__.run(args)
    print("\n✅ BUILD SUCCESSFUL")
    print(f"Executable is located at: {os.path.abspath('dist/SilentBot.exe')}")
    print("You can zip the 'dist' folder and distribute it to users.")
except Exception as e:
    print(f"\n❌ BUILD FAILED: {str(e)}")
