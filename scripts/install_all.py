import os
import sys
import subprocess


def main():
    req = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    req = os.path.abspath(req)
    if not os.path.exists(req):
        print("[x] requirements.txt not found:", req)
        sys.exit(1)

    print("=== LynkerAI Dependency Installer (Python) ===")
    print("[*] Upgrading pip/setuptools/wheel ...")
    subprocess.call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])

    print("\n[*] Installing from requirements.txt ...")
    code = subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', req])
    if code != 0:
        print("\n[x] Installation failed. Please review the errors above.")
        sys.exit(code)

    print("\n✅ All dependencies installed successfully.")
    print("   - Launch Admin Dashboard: run_app.bat")
    print("   - Run Orchestrator pipeline: run_orchestrator.bat")


if __name__ == '__main__':
    main()

