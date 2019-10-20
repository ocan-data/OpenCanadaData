from functools import lru_cache

import ipywidgets as widgets
import pandas as pd
from jinja2 import Template
from bs4 import BeautifulSoup
from .text import get_language
from .core import get
from typing import List

_INVENTORY_URL = 'https://open.canada.ca/data/dataset/4ed351cf-95d8-4c10-97ac-6b3511f359b7/resource/d0df95a8-31a9-46c9-853b-6952819ec7b4/download/inventory.csv'


class Inventory:

    def __init__(self, data: pd.DataFrame = None, language: str = 'en'):
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
        return pd.read_csv(_INVENTORY_URL) \
            .drop(columns=['ref_number', 'size', 'eligible_for_release', 'user_votes']) \
            .rename(columns={'date_released': 'released', 'date_published': 'published'})

    @property
    def en(self):
        return self.EN

    @property
    def EN(self):
        cols = [col for col in self.english_cols if not col in ['owner_org', 'owner_org_title']]
        view = self.data[cols].rename(columns={col: col.replace("_en", "") for col in self.english_cols})
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


class DataHolder:

    def __init__(self, data: pd.DataFrame, item_getter=None, display_columns: List[str] = None):
        self.data = data
        self.item_getter = item_getter
        if display_columns:
            self.display_columns = [col for col in data.columns if col in display_columns]
        else:
            self.display_columns = data.columns

    @staticmethod
    def value_to_dataframe(series_value):
        df = series_value.to_frame()
        df.columns=['Value']
        df.index.name = 'Column'
        return df

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        if isinstance(item, list):
            return self.data[item]
        value = self.data.iloc[item]
        if self.item_getter:
            return self.item_getter(value)
        return value

    def query(self, query_str: str):
        result = self.data.query(query_str)
        return DataHolder(result)

    def view(self):
        return self.data[self.display_columns]

    def __repr__(self):
        return self.view().__repr__()

    def _repr_html_(self):
        return self.view()._repr_html_()


class Resource(DataHolder):

    def __init__(self, data):
        super().__init__(data)

    @classmethod
    def from_series(cls, series_value):
        data = series_value.to_frame().T.reset_index(drop=True)
        return cls(data)


_DATASET_HTML = """
<h3>{{title}}</h3>
<p>Published on <strong>{{published}}</strong> by <strong>{{publisher}}</strong></p>
<h3>Description</h3>
<p>{{description}}</p>
<h3>Resources</h3>
{{resources}}
"""


class Dataset:

    def __init__(self, title: str,
                 description: str,
                 released=None,
                 published=None,
                 publisher: str = None,
                 url: str = None,
                 langauge: str = 'en'):
        self.title = title
        self.description = description
        self.released = released
        self.published = published
        self.publisher = publisher
        self.url = url
        self.language = get_language(langauge)
        resources = load_dataset_resources(self)
        self.resources = DataHolder(resources,
                                    item_getter=Resource.from_series
                                    )

    def link(self):
        return widgets.HTML(f'<a href="{self.url}" target="_blank">{self.title}</a>')

    def __len__(self):
        if self.resources is None:
            return 0
        return len(self.resources)

    def __getitem__(self, item):
        return self.resources[item]

    def _repr_html_(self):
        template = Template(_DATASET_HTML)
        return template.render(title=self.title,
                               description=self.description,
                               published=self.published,
                               publisher=self.publisher,
                               resources='' if self.resources is None else self.resources.data.to_html(index=False,
                                                                                                       render_links=True))




def get_tables(html):
    if html:
        soup = BeautifulSoup(html, features='lxml')
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                row_values = []
                cells = tr.find_all('td')
                if len(cells) == 0:
                    cells = tr.find_all('th')
                for td in cells:
                    anchor = td.find('a')
                    if anchor:
                        row_values.append(anchor['href'])
                    else:
                        row_values.append(td.text.strip())
                rows.append(tuple(row_values))
                df = pd.DataFrame(rows)
                df.columns = df.iloc[0]
                df = df.drop(df.index[0])
                if 'Links' in df.columns:
                    df = df.rename(columns={'Links': 'Link'})
                df['Status'] = 'Active'
            tables.append(df)

    return tables


def get_deleted_message(soup):
    h1 = soup.find('h1')
    if h1 and h1.text == 'Dataset Deleted' or soup.title.text == 'Dataset Deleted - Open Government Portal':
        return 'Deleted'


@lru_cache(maxsize=32)
def load_dataset_resources(dataset):
    columns = ['Resource Name', 'Resource Type', 'Format', 'Language', 'Link', 'Status']

    try:
        if dataset.url.endswith('csv'):
            return pd.DataFrame([(dataset.title, 'Dataset', 'CSV', dataset.language, dataset.url, 'Active')],
                                columns=columns)
        else:
            html = get(dataset.url)
            soup = BeautifulSoup(html, features='lxml')
            tables = get_tables(html)
            if len(tables) == 1:
                return tables[0]
            elif len(tables) > 1:
                print(len(tables), 'tables found')
                return tables[0]
            else:
                deleted_message = get_deleted_message(soup)
                resources = pd.DataFrame([tuple([''] * len(columns))], columns=columns)
                resources['Status'] = deleted_message
                return resources
    except Exception as e:
        print('error', e)
        raise

