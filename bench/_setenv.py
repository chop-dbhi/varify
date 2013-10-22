import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'varify.conf.settings')
os.environ.setdefault('PYTHON_EGG_CACHE', '/tmp')
