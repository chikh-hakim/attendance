# setup_db.py
import sys
import os

# Add project root to path (same as in app.py)
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Now safely import and create tables
from teacher.app import create_app
from models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("✅ All tables created successfully!")