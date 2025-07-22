#!/usr/bin/env python3
"""
Applyst Setup and Run Script
Cross-platform script to set up virtual environment, install dependencies, and start the application
"""

import os
import sys
import subprocess
import platform
import time
import signal
import threading
from pathlib import Path

class ApplystLauncher:
    def __init__(self):
        self.system = platform.system().lower()
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.processes = []
        
        # Platform-specific commands
        if self.system == "windows":
            self.python_cmd = "python"
            self.pip_cmd = "pip"
            self.venv_activate = self.venv_path / "Scripts" / "activate.bat"
            self.venv_python = self.venv_path / "Scripts" / "python.exe"
            self.venv_pip = self.venv_path / "Scripts" / "pip.exe"
        else:  # Linux/Mac
            self.python_cmd = "python3"
            self.pip_cmd = "pip3"
            self.venv_activate = self.venv_path / "bin" / "activate"
            self.venv_python = self.venv_path / "bin" / "python"
            self.venv_pip = self.venv_path / "bin" / "pip"

    def run_command(self, command, cwd=None, shell=True):
        """Run a command and return the result"""
        try:
            result = subprocess.run(
                command, 
                shell=shell, 
                check=True, 
                capture_output=True, 
                text=True,
                cwd=cwd
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
        except FileNotFoundError:
            return False, f"Command not found: {command}"

    def check_python(self):
        """Check if Python is available"""
        print("🔍 Checking Python installation...")
        success, output = self.run_command(f"{self.python_cmd} --version")
        if success:
            print(f"✅ Python found: {output.strip()}")
            return True
        else:
            print(f"❌ Python not found. Please install Python 3.8+ first.")
            return False

    def create_venv(self):
        """Create virtual environment if it doesn't exist"""
        if self.venv_path.exists():
            print(f"📁 Virtual environment already exists at {self.venv_path}")
            return True
        
        print("🔨 Creating virtual environment...")
        success, output = self.run_command(f"{self.python_cmd} -m venv venv")
        if success:
            print("✅ Virtual environment created successfully")
            return True
        else:
            print(f"❌ Failed to create virtual environment: {output}")
            return False

    def install_requirements(self):
        """Install requirements in virtual environment"""
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print("❌ requirements.txt not found!")
            return False
        
        print("📦 Installing requirements...")
        success, output = self.run_command(f'"{self.venv_pip}" install -r requirements.txt')
        if success:
            print("✅ Requirements installed successfully")
            return True
        else:
            print(f"❌ Failed to install requirements: {output}")
            return False

    def check_env_file(self):
        """Check if .env file exists and required environment variables are set"""
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env-example"
        
        if not env_file.exists():
            print("❌ .env file not found in root directory")
            if env_example.exists():
                print(f"💡 Copy {env_example} to .env and add the three API keys")
            else:
                print("💡 Create .env with the three API keys")
            print("🛑 Application cannot start without proper environment configuration")
            return False
        
        # Load environment variables manually (since dotenv might not be available in current env)
        env_vars = {}
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Remove quotes if present
                        value = value.strip().strip('"').strip("'")
                        env_vars[key.strip()] = value
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
            return False
        
        # Check required environment variables
        required_vars = {
            'GMAIL_CLIENT_ID': 'Gmail OAuth Client ID',
            'GMAIL_CLIENT_SECRET': 'Gmail OAuth Client Secret', 
            'GEMINI_API_KEY': 'Google Gemini API Key'
        }
        
        missing_vars = []
        for var_name, description in required_vars.items():
            value = env_vars.get(var_name, '').strip()
            if not value or value == "''":
                missing_vars.append(f"  - {var_name}: {description}")
        
        if missing_vars:
            print("❌ Required environment variables are missing or empty:")
            for var in missing_vars:
                print(var)
            print(f"\n💡 Please edit {env_file} and set all required values")
            print("🛑 Application cannot start without proper environment configuration")
            return False
        
        print("✅ All required environment variables are set")
        return True

    def start_backend(self):
        """Start Flask backend in a separate process"""
        print("🚀 Starting Flask backend on http://localhost:5000...")
        server_dir = self.project_root / "server"
        
        if self.system == "windows":
            # Windows - use subprocess with shell
            process = subprocess.Popen(
                f'"{self.venv_python}" app.py',
                shell=True,
                cwd=server_dir,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0
            )
        else:
            # Linux/Mac
            process = subprocess.Popen(
                [str(self.venv_python), "app.py"],
                cwd=server_dir
            )
        
        self.processes.append(("backend", process))
        return process

    def start_frontend(self):
        """Start Streamlit frontend in a separate process"""
        print("🚀 Starting Streamlit frontend on http://localhost:8501...")
        client_dir = self.project_root / "client"
        
        if self.system == "windows":
            # Windows - use subprocess with shell
            process = subprocess.Popen(
                f'"{self.venv_python}" -m streamlit run client.py',
                shell=True,
                cwd=client_dir,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0
            )
        else:
            # Linux/Mac
            process = subprocess.Popen(
                [str(self.venv_python), "-m", "streamlit", "run", "client.py"],
                cwd=client_dir
            )
        
        self.processes.append(("frontend", process))
        return process

    def wait_for_services(self):
        """Wait for services to start"""
        print("⏳ Waiting for services to start...")
        time.sleep(3)
        
        # Check if backend is running
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:5000/api/health", timeout=5)
            print("✅ Backend is running on http://localhost:5000")
        except:
            print("⚠️  Backend might still be starting...")
        
        print("✅ Frontend should be available at http://localhost:8501")

    def cleanup(self):
        """Clean up processes"""
        print("\n🛑 Shutting down services...")
        for name, process in self.processes:
            try:
                if self.system == "windows":
                    # Windows - send CTRL_BREAK_EVENT
                    process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    # Linux/Mac - send SIGTERM
                    process.terminate()
                print(f"✅ {name} stopped")
            except:
                try:
                    process.kill()
                    print(f"🔴 {name} force killed")
                except:
                    print(f"⚠️  Could not stop {name}")

    def setup_signal_handlers(self):
        """Setup signal handlers for clean shutdown"""
        def signal_handler(signum, frame):
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)

    def run(self):
        """Main run method"""
        print("🚀 Applyst - Auto Job Application Tracker")
        print("=" * 50)
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Check Python
        if not self.check_python():
            return False
        
        # Create virtual environment
        if not self.create_venv():
            return False
        
        # Install requirements
        if not self.install_requirements():
            return False
        
        # Check environment file and required variables
        if not self.check_env_file():
            return False
        
        print("\n🎯 Starting Applyst services...")
        print("-" * 30)
        
        # Start backend
        backend_process = self.start_backend()
        
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Start frontend
        frontend_process = self.start_frontend()
        
        # Wait for services
        self.wait_for_services()
        
        print("\n🎉 Applyst is now running!")
        print("📊 Dashboard: http://localhost:8501")
        print("🔧 API: http://localhost:5000")
        print("\n💡 To stop the application, press Ctrl+C")
        
        try:
            # Keep the main process alive
            while True:
                time.sleep(1)
                # Check if processes are still running
                for name, process in self.processes:
                    if process.poll() is not None:
                        print(f"⚠️  {name} process stopped unexpectedly")
                        return False
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
        
        return True

if __name__ == "__main__":
    launcher = ApplystLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1) 