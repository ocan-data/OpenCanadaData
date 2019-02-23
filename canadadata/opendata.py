import pandas as pd


class OpenDataInventory(object):

    def __init__(self, inventory_fn: str):
        self.inventory = pd.read_csv(inventory_fn,
                                     index_col='ref_number',
                                     parse_dates=['date_published', 'date_released']) \
            .drop(columns='eligible_for_release').rename(columns={'program_alignment_architecture': 'program'})
        # self.inventory.size = self.inventory.size / 1000

    def get_cols(self, language='en'):
        if language == 'en':
            cols = [col for col in self.inventory.columns if not col.endswith('_fr')]
        elif language == 'fr':
            cols = [col for col in self.inventory.columns if not col.endswith('_en')]
        else:
            cols = self.inventory.columns
        return cols

    def get_inventory(self, language='en', owner: str = None):
        cols = self.get_cols(language)
        inventory_df = self.inventory[cols].copy()
        suffix = '_' + language
        inventory_df.columns = [col.replace(suffix, '') for col in inventory_df.columns]
        if owner:
            inventory_df = inventory_df[inventory_df.owner_org == owner]
        return inventory_df