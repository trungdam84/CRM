from django.test import TestCase
import os
from pathlib import Path
# Create your tests here.
def print_dir():
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # path = Path(BASE_DIR).parents[0]
    path = os.path.join(Path(BASE_DIR).parents[0], 'logs')
    print(path)

