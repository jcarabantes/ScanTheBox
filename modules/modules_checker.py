import sys
import subprocess

required_modules = ['argparse', 'os', 'yaml', 'termcolor', 'cmd']

def check_required_modules(modules):
    missing_modules = []
    for module in modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print(f"Error: Los siguientes módulos no están instalados: {', '.join(missing_modules)}")
        print("Instálalos ejecutando: pip install <module>")
        sys.exit(1)

check_required_modules(required_modules)