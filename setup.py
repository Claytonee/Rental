import os
import subprocess
import sys

def setup_project():
    # Create virtual environment
    subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Activate virtual environment and install requirements
    if os.name == 'nt':  # Windows
        subprocess.run(["venv\\Scripts\\pip", "install", "-r", "requirements.txt"])
        subprocess.run(["venv\\Scripts\\django-admin", "startproject", "moshi_rental", "."])
    else:  # Unix/Linux/MacOS
        subprocess.run(["venv/bin/pip", "install", "-r", "requirements.txt"])
        subprocess.run(["venv/bin/django-admin", "startproject", "moshi_rental", "."])
    
    # Create apps
    # apps = ['accounts', 'rentals', 'bookings', 'payments', 'reviews', 'api']
    apps = ['accounts', 'rentals', 'bookings', 'payments']
    for app in apps:
        if os.name == 'nt':
            subprocess.run(["venv\\Scripts\\python", "manage.py", "startapp", app])
        else:
            subprocess.run(["venv/bin/python", "manage.py", "startapp", app])
    
    print("Project setup completed successfully!")

if __name__ == "__main__":
    setup_project() 