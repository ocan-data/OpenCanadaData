import pandas as pd
from jinja2 import Template
from functools import lru_cache

_INVENTORY_URL = 'https://open.canada.ca/data/dataset/4ed351cf-95d8-4c10-97ac-6b3511f359b7/resource/d0df95a8-31a9-46c9-853b-6952819ec7b4/download/inventory.csv'


class Inventory:

    def __init__(self, data: pd.DataFrame=None, language: str = 'en'):
        self.language = language
        if data is None:
            data = self.read_inventory()
        data = data.dropna(subset=['released'])
        data = data[data.released.str.match('20[0-9]{2}')]
        if 'portal_url_en' in data.columns:
            data = data.dropna(subset=['portal_url_en'])
            data = data[data['portal_url_en'].str.match('http://')]
        self.data = data.sort_values(['released'], ascending=False)
        self.english_cols = [col for col in data.columns if not col.endswith("_fr")]
        self.french_cols = [col for col in data.columns if not col.endswith("_en")]

    @lru_cache(maxsize=2)
    def read_inventory(self):
        return pd.read_csv(_INVENTORY_URL)\
                .drop(columns=['ref_number', 'size', 'eligible_for_release', 'user_votes']) \
                .rename(columns={'date_released': 'released', 'date_published': 'published'})

    @property
    def en(self):
        return self.EN

    @property
    def EN(self):
        cols = [col for col in self.english_cols if not col in['owner_org', 'owner_org_title']]
        view = self.data[cols].rename(columns={col: col.replace("_en", "") for col in self.english_cols })
        return Inventory(view, language='en')

    @property
    def fr(self):
        return self.FR

    @property
    def FR(self):
        cols = [col for col in self.french_cols if not col in ['owner_org', 'owner_org_title']]
        view = self.data[cols].rename(columns={col: col.replace("_fr", "") for col in self.french_cols})
        return Inventory(view, language='fr')

    def query(self, query_str):
        results = self.data.query(query_str)
        return Inventory(results)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        record = self.data.iloc[item]
        if 'title_en' in self.data.columns:
            return Dataset(title=record.title_en,
                           description=record.description_en,
                           released=record.released,
                           published=record.published,
                           publisher=record.publisher_en,
                           url=record.portal_url_en)
        else:
            return Dataset(title=record.title,
                           description=record.description,
                           released=record.released,
                           published=record.published,
                           publisher=record.publisher,
                           url=record.portal_url)

    def _repr_html_(self):
        repr_data = self.FR if self.language == 'fr' else self.EN
        html = '<h3>Open Canada Data Inventory</h3>'
        html = html + repr_data.data.to_html(index=False)
        return html


_DATASET_HTML = """
<h3>{{title}}</h3>
<p>{{description}}</p>
<h4>Published</h4> 
{{published}}
<h4>Publisher</h4>
{{publisher}}
"""


class Dataset:

    def __init__(self, title: str,
                       description: str,
                       released = None,
                       published = None,
                       publisher: str = None,
                       url: str = None):
        self.title = title
        self.description = description
        self.released = released
        self.published = published
        self.publisher = publisher
        self.url = url

    def _repr_html_(self):
        template = Template(_DATASET_HTML)
        return template.render(title=self.title,
                               description=self.description,
                               published=self.published,
                               publisher=self.publisher)


