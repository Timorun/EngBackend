import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
RESOURCES_DIR = os.path.join(ROOT_DIR, 'resources')

# LGBMCLASS = os.path.join(RESOURCES_DIR, 'lgbmclass')
LGBMCLASS = os.path.join(RESOURCES_DIR, 'lgbmbuilds')
MODEL_DIR = os.path.join(RESOURCES_DIR, 'models')

DATA_DIR = os.path.join(RESOURCES_DIR, 'data')
OULAD_DATA_DIR = os.path.join(DATA_DIR, 'oulad')
SQL_DIR = os.path.join(DATA_DIR, 'sql')
DATABASE = os.path.join(DATA_DIR, 'database')

