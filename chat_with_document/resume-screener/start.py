import os
import sys
import subprocess
import time
import webbrowser
from threading import Thread

def start_backend():
    """Start the FastAPI backend server"""
    print("Starting backend server...")
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    
    # Check if virtual environment exists, if not create one
    venv_dir = os.path.join(backend_dir, 'venv')
    python_executable = os.path.join(venv_dir, 'Scripts', 'python') if sys.platform == 'win32' else os.path.join(venv_dir, 'bin', 'python')
    
    if not os.path.exists(venv_dir):
        print("Setting up virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
    
    # Install requirements
    pip_executable = os.path.join(venv_dir, 'Scripts', 'pip') if sys.platform == 'win32' else os.path.join(venv_dir, 'bin', 'pip')
    print("Installing backend dependencies...")
    
    # Set environment variables for the subprocess
    env = os.environ.copy()
    # Add environment variable to allow deprecated sklearn package
    env['SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL'] = 'True'
    
    subprocess.run([pip_executable, 'install', '-r', os.path.join(backend_dir, 'requirements.txt')], 
                  check=True, env=env)
    
    # Start the backend server
    os.chdir(backend_dir)
    if sys.platform == 'win32':
        # On Windows
        uvicorn_path = os.path.join(venv_dir, 'Scripts', 'uvicorn')
        process = subprocess.Popen([uvicorn_path, 'main:app', '--host', '0.0.0.0', '--port', '8000'])
    else:
        # On Unix/Linux/Mac
        uvicorn_path = os.path.join(venv_dir, 'bin', 'uvicorn')
        process = subprocess.Popen([uvicorn_path, 'main:app', '--host', '0.0.0.0', '--port', '8000'])
    
    print("Backend server running at http://localhost:8000")
    return process

def start_frontend():
    """Start the React frontend application"""
    print("Starting frontend application...")
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    os.chdir(frontend_dir)
    
    # Check if node_modules exists, if not install dependencies
    if not os.path.exists(os.path.join(frontend_dir, 'node_modules')):
        print("Installing frontend dependencies...")
        subprocess.run(['npm', 'install'], check=True)
    
    # Start the React development server
    if sys.platform == 'win32':
        # On Windows
        process = subprocess.Popen('npm start', shell=True)
    else:
        # On Unix/Linux/Mac
        process = subprocess.Popen(['npm', 'start'], stdout=subprocess.PIPE)
    
    print("Frontend application running at http://localhost:3000")
    return process

def open_browser():
    """Open the application in the default web browser"""
    time.sleep(5)  # Give some time for servers to start
    print("Opening application in web browser...")
    webbrowser.open('http://localhost:3000')

if __name__ == "__main__":
    try:
        # Start backend in a separate thread
        backend_process = start_backend()
        
        # Start frontend
        frontend_process = start_frontend()
        
        # Open in browser
        browser_thread = Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("\nResume Screening Application is now running!")
        print("Backend API: http://localhost:8000")
        print("Frontend UI: http://localhost:3000")
        print("\nPress Ctrl+C to stop all services.\n")
        
        # Keep the script running
        frontend_process.wait()
    
    except KeyboardInterrupt:
        print("\nShutting down services...")
        # Cleanup processes on exit
        try:
            backend_process.terminate()
            frontend_process.terminate()
        except:
            pass
        print("Services stopped. Goodbye!")
