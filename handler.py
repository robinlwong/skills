import subprocess
import os
import sys

def read_x_post(url):
    """
    Handler function called by OpenClaw.
    """
    print(f"🕵️‍♂️ Jarvis is analyzing X post: {url}")
    
    # Define paths relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, "stealth.py")
    
    # CRITICAL: Point to the Python inside the virtual environment
    venv_python = os.path.join(current_dir, "venv", "bin", "python")
    
    # Fallback to system python if venv is missing (though it will likely fail)
    python_executable = venv_python if os.path.exists(venv_python) else "python3"

    if not os.path.exists(script_path):
        return "Error: stealth.py not found in the x-stealth skill folder."

    try:
        # Run the script using the VENV python
        result = subprocess.run(
            [python_executable, script_path, url], 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        if result.returncode != 0:
            # Check if it's a missing library error
            if "No module named" in result.stderr:
                 return f"Configuration Error: Dependencies not found. Did you create the venv?\nDebug: {result.stderr}"
            return f"Script Error: {result.stderr}"
            
        return result.stdout.strip()
        
    except Exception as e:
        return f"Failed to execute stealth scraper: {str(e)}"
