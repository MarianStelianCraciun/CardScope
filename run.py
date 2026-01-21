import subprocess
import sys
import threading
import os
import time

def run_backend():
    print("Starting Backend...")
    # Using python -m uvicorn to ensure it's run from the correct environment
    # Note: Backend remains on HTTP for simplicity; frontend will fetch it via HTTP or HTTPS depending on browser policy.
    # Modern browsers often allow HTTPS sites to fetch from local IP HTTP, but it can be tricky.
    # Added --ssl-keyfile and --ssl-certfile to support HTTPS directly in the backend
    # but we need to generate or provide them. 
    # For now, let's stick to HTTP but ensure it works with the HTTPS frontend.
    subprocess.run(["poetry", "run", "uvicorn", "backend.app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"], shell=True)

def run_frontend():
    print("Starting Frontend (HTTPS enabled for camera access)...")
    print("NOTE: You will see a 'Your connection is not private' warning in your browser.")
    print("This is EXPECTED because we are using a self-signed certificate.")
    print("To proceed: Click 'Advanced' -> 'Proceed to localhost (unsafe)'")
    os.chdir("frontend")
    # Set HTTPS=true to allow camera access on mobile browsers
    os.environ["HTTPS"] = "true"
    # For Windows, npm start often works better with shell=True
    subprocess.run(["npm", "start"], shell=True)

if __name__ == "__main__":
    # Ensure dependencies are installed for backend
    print("Checking backend dependencies...")
    try:
        subprocess.run(["poetry", "install"], shell=True, check=True)
    except Exception as e:
        print(f"Warning: Poetry install failed, attempting to continue... {e}")

    # Load sample data if database doesn't exist
    if not os.path.exists("sql_app.db"):
        print("Initializing database and loading sample data...")
        subprocess.run(["poetry", "run", "python", "-m", "backend.app.load_sample_data"], shell=True)

    # Note: Frontend npm install is usually done once, but we'll mention it in README.
    
    backend_thread = threading.Thread(target=run_backend)
    frontend_thread = threading.Thread(target=run_frontend)

    backend_thread.start()
    
    # Small delay to let backend start first
    time.sleep(2)
    
    frontend_thread.start()

    backend_thread.join()
    frontend_thread.join()
