import subprocess
import sys
import os

# Get the current directory of this script
base_path = os.path.dirname(os.path.abspath(__file__))

# Paths to the scripts relative to the base directory
scraper_path = os.path.join(base_path, "PCont", "scraper.py")
intro_path = os.path.join(base_path, "PCont", "intro.py")
config_path = os.path.join(base_path, "PCont", "config.py")  

def run_script(script_path):
    try:
        subprocess.run(["sudo", "python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}", file=sys.stderr)

def main():
    # Run scraper.py
    run_script(scraper_path)
    
    # Run intro.py
    run_script(intro_path)
    
    # Run configurator.py
    run_script(config_path)  

if __name__ == "__main__":
    main()
