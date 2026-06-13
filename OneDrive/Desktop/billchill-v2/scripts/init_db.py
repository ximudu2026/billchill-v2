import sys
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app import app
from extensions import db

with app.app_context():
    db.create_all()
    print("Database initialized.")