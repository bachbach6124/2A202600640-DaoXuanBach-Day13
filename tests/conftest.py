import os
import sys
from pathlib import Path

os.environ["LANGFUSE_PUBLIC_KEY"] = ""
os.environ["LANGFUSE_SECRET_KEY"] = ""
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
