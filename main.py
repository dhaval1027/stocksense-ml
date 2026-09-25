import sys
from pathlib import Path

# Ensure api directory is accessible on sys.path
root_dir = Path(__file__).resolve().parent
api_dir = root_dir / "api"
if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))

from api.index import app
