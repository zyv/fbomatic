import importlib.machinery
import importlib.util
import os
import sys
from pathlib import Path

APP_DIRECTORY = Path(__file__).resolve().parent / "src"
VENV_DIRECTORY = APP_DIRECTORY.parent / ".venv" / "bin"
VENV_PYTHON = VENV_DIRECTORY / "python"

if sys.executable != str(VENV_PYTHON):
    os.execl(VENV_PYTHON, VENV_PYTHON, *sys.argv)

sys.path.insert(0, str(APP_DIRECTORY))
sys.path.insert(0, str(VENV_DIRECTORY))

os.chdir(APP_DIRECTORY)

env = Path(APP_DIRECTORY.parent / "fbomatic.env").read_text().splitlines(keepends=False)
for line in (line for line in env if line.strip()):
    name, value = [item.strip() for item in line.split("=", maxsplit=1)]
    os.environ[name] = value.lstrip('"').rstrip('"') if value.startswith('"') and value.endswith('"') else value


def load_source(modname, filename):
    loader = importlib.machinery.SourceFileLoader(modname, filename)
    spec = importlib.util.spec_from_file_location(modname, filename, loader=loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


wsgi = load_source("wsgi", "config/wsgi.py")
application = wsgi.application
