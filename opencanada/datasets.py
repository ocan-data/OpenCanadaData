import pandas as pd

_OPEN_CANADA_URL = 'https://open.canada.ca'
_OPEN_DATASET_ID = '4ed351cf-95d8-4c10-97ac-6b3511f359b7'
_OPEN_RESOURCE_ID = 'd0df95a8-31a9-46c9-853b-6952819ec7b4'
_INVENTORY_URL = f'https://open.canada.ca/data/dataset/{_OPEN_DATASET_ID}/resource/{_OPEN_RESOURCE_ID}/download/inventory.csv'
#https://open.canada.ca/data/dataset/4ed351cf-95d8-4c10-97ac-6b3511f359b7/resource/d0df95a8-31a9-46c9-853b-6952819ec7b4/download/inventory.csv

inventory = pd.read_csv(_INVENTORY_URL).rename(columns={'program_alignment_architecture': 'program'})
_EN_COLS = [col for col in inventory.columns if not col.endswith('_fr')]
_FR_COLS = [col for col in inventory.columns if not col.endswith('_en')]
inventory_en = inventory[_EN_COLS]
inventory_en.columns = [col.replace('_en', '') for col in _EN_COLS]
inventory_fr = inventory[_FR_COLS]
inventory_fr.columns = [col.replace('_fr','') for col in _FR_COLS]
