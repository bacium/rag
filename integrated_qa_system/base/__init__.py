import os
import sys

modules_path = os.path.dirname(os.path.abspath(__file__))
# print(f"modules_path========>{modules_path}")
if modules_path not in sys.path:
    sys.path.append(modules_path)

project_path = os.path.dirname(modules_path)
# print(f"project_path========>{project_path}")
if project_path not in sys.path:
    sys.path.append(project_path)
# print(f"sys.path========>{sys.path}")

from config import Config
from logger import logger
