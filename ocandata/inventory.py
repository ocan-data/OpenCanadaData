from functools import lru_cache

import ipywidgets as widgets
import pandas as pd
from jinja2 import Template
from bs4 import BeautifulSoup
from .text import get_language
from .core import get
from typing import List
from .text import Bm25Index
from .core import parallel
import re
import os

_INVENTORY_URL = 'https://open.canada.ca/data/dataset/4ed351cf-95d8-4c10-97ac-6b3511f359b7/resource/d0df95a8-31a9-46c9-853b-6952819ec7b4/download/inventory.csv'

_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
_EXPIRED_DATASETS = os.path.join(_DATA_DIR, 'ExpiredDatasets.txt')


class Inventory:
    """
    The Open Canada Data Inventory
    """

    def __init__(self, data: pd.DataFrame = None, language: str = 'en', sort_by_date=True):
        self.language = language
        if data is None:
            data = self.read_inventory(drop_expired=True)
        data = data.dropna(subset=['released'])
        data = data[data.released.str.match('20[0-9]{2}')]
        if 'portal_url_en' in data.columns:
            data = data.dropna(subset=['portal_url_en'])
            data = data[data['portal_url_en'].str.match('http://')]
        self.data = data
        if sort_by_date:
            self.data = self.data.sort_values(['released'], ascending=False).reset_index(drop=True)

        self.english_cols = [col for col in data.columns if not col.endswith("_fr")]
        self.french_cols = [col for col in data.columns if not col.endswith("_en")]
        self.sort_by_date = sort_by_date

    def create_search_indexes(self):
        """
        Create the search indexes for the inventory
        """

        print("Creating search indexes")
        description_col = 'description' if 'description' in self.data.columns else f'description_{self.language}'
        self.search_indexes = {'description': Bm25Index(self.data[description_col])}

    def search(self, search_term: str):
        if not hasattr(self, 'search_indexes'):
            self.create_search_indexes()
        bm25_index = self.search_indexes['description']
        index, scores = bm25_index.get_scores(search_term, 10)
        results = self.data.iloc[index].copy().reset_index(drop=True)
        return Inventory(results, language=self.language, sort_by_date=False)

    @lru_cache(maxsize=2)
    def read_inventory(self, drop_expired: bool = True):
        """
        Read the inventory dataset from the Open Canada website
        :param drop_expired:
        :return:
        """
        data = pd.read_csv(_INVENTORY_URL) \
            .drop(columns=['ref_number', 'size', 'eligible_for_release', 'user_votes']) \
            .rename(columns={'date_released': 'released', 'date_published': 'published'})
        data.portal_url_en = data.portal_url_en.astype(str)
        ## Remove expired datasets
        if drop_expired:
            with open(_EXPIRED_DATASETS, 'r') as f:
                expired_datasets = [l.strip() for l in f.readlines()]
            data = data[~(data.portal_url_en.isin(expired_datasets) | (data.portal_url_fr.isin(expired_datasets)))]
        return data

    @property
    def en(self):
        return self.EN

    @property
    def EN(self):
        cols = [col for col in self.english_cols if not col in ['owner_org', 'owner_org_title']]
        view = self.data[cols].rename(columns={col: col.replace("_en", "") for col in self.english_cols})
        return Inventory(data=view, language='en', sort_by_date=self.sort_by_date)

    def _view(self):
        if self.language == 'fr':
            return self.fr
        return self.en

    @property
    def fr(self):
        return self.FR

    @property
    def FR(self):
        cols = [col for col in self.french_cols if not col in ['owner_org', 'owner_org_title']]
        view = self.data[cols].rename(columns={col: col.replace("_fr", "") for col in self.french_cols})
        return Inventory(data=view, language='fr', sort_by_date=self.sort_by_date)

    def query(self, query_str):
        """
        Query the data in this inventory object by passing the query down to the dataframe query method
        :param query_str: A dataframe query string
        :return: A new Inventory instance with the results of the query
        """
        results = self.data.query(query_str)
        return Inventory(results)

    def _create_dataset(self, record):
        if 'title_en' in self.data.columns:
            return Dataset(title=record.title_en, description=record.description_en,
                           released=record.released, published=record.published,
                           publisher=record.publisher_en, url=record.portal_url_en)
        elif 'title_fr' in self.data.columns:
            return Dataset(title=record.title_fr, description=record.description_fr,
                           released=record.released, published=record.published,
                           publisher=record.publisher_fr, url=record.portal_url_fr)
        else:
            return Dataset(title=record.title, description=record.description,
                           released=record.released, published=record.published,
                           publisher=record.publisher, url=record.portal_url)



    def get_active_inactive_datasets(self, inventory_data: pd.DataFrame):
        indexes = range(len(inventory_data))
        def _get_dataset(index):
            obj = inventory_data.iloc[index]
            dataset: Dataset = self._create_dataset(obj)
            return dataset

        datasets = parallel(_get_dataset, indexes)
        return [dataset for dataset in datasets if dataset.is_active()], \
               [dataset for dataset in datasets if not dataset.is_active()],

    def get_active_dataset_urls(self, inventory_data: pd.DataFrame):
        active_datasets, inactive_datasets = self.get_active_inactive_datasets(inventory_data)
        return list(set([dataset.url for dataset in active_datasets]))

    def get_inactive_dataset_urls(self, inventory_data: pd.DataFrame):
        active_datasets, inactive_datasets = self.get_active_inactive_datasets(inventory_data)
        return list(set([dataset.url for dataset in inactive_datasets]))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        record = self.data.iloc[item]
        return self._create_dataset(record)

    def __repr__(self):
        repr_data = self._view()
        return repr_data.data.__repr__()

    def _repr_html_(self):
        repr_obj = self._view()
        repr_data = repr_obj.data.drop(columns=['portal_url', 'language', 'program_alignment_architecture'])
        html = '<h3>Open Canada Data Inventory</h3>'
        html = html + repr_data.to_html(index=False)
        return html


class DataFrameHolder:

    def __init__(self, data: pd.DataFrame, item_getter=None, display_columns: List[str] = None):
        self.data = data
        self.item_getter = item_getter
        if display_columns:
            self.display_columns = [col for col in data.columns if col in display_columns]
        else:
            self.display_columns = data.columns
        self._set_attributes(data)

    def _set_attributes(self, data):
        if len(data) == 1:
            for column in data:
                setattr(self, column, data[column][0])
        else:
            for column in data:
                setattr(self, column, data[column])

    @staticmethod
    def value_to_dataframe(series_value):
        df = series_value.to_frame()
        df.columns = ['Value']
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
        return DataFrameHolder(result)

    def view(self):
        return self.data[self.display_columns]

    def __repr__(self):
        return self.view().__repr__()

    def _repr_html_(self):
        return self.view()._repr_html_()


class Resource(DataFrameHolder):

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
    """
    Represents a single Open Canada Dataset
    Datasets ontain resources
    """

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
        self.resources = DataFrameHolder(resources,
                                         item_getter=Resource.from_series
                                         )

    def is_active(self):
        """
        :return: True if this dataset is deleted
        """
        if self.resources is None or len(self.resources) == 0:
            return False
        if self.resources.data.loc[0, 'Status'] == 'Active':
            return True

        return False

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
                df = df.drop(df.index[0]).reset_index(drop=True)
                if 'Links' in df.columns:
                    df = df.rename(columns={'Links': 'Link'})
                df['Status'] = 'Active'
            tables.append(df)

    return tables


def get_deleted_message(soup: BeautifulSoup):
    """
    Looks for text on the page that indicates if the dataset is deleted
    :param soup: The BeautifulSoup for the page
    :return:
    """
    h1 = soup.find('h1')
    if h1:
        if h1.text == 'Dataset Deleted' or h1.text == 'Dossier supprimé':
            return 'Deleted'
    elif soup.title.text == 'Dataset Deleted - Open Government Portal' \
            or soup.title.text == 'Dossier supprimé - Portail du gouvernement ouvert':
        return 'Deleted'


_RESOURCE_COLUMNS = ['Resource Name', 'Resource Type', 'Format', 'Language', 'Link', 'Status']


@lru_cache(maxsize=512)
def load_dataset_resources(dataset):
    try:
        if dataset.url.endswith('csv'):
            return pd.DataFrame([(dataset.title, 'Dataset', 'CSV', dataset.language, dataset.url, 'Active')],
                                columns=_RESOURCE_COLUMNS)
        if dataset.url.endswith('xlsx'):
            print('Excel dataset', dataset.url)
            return pd.DataFrame([(dataset.title, 'Dataset', 'XLSX', dataset.language, dataset.url, 'Active')],
                                columns=_RESOURCE_COLUMNS)
        else:
            html = get(dataset.url)
            resource_table = find_dataset_resource_table(html)
            if resource_table is not None:
                return resource_table
            else:
                soup = BeautifulSoup(html, features='lxml')
                deleted_message = get_deleted_message(soup)
                if deleted_message:
                    return pd.DataFrame([(dataset.title, '', '', '', dataset.url, deleted_message)],
                                        columns=_RESOURCE_COLUMNS)
                else:
                    dataset_link = find_dataset_link(soup)
                    html = get(dataset_link)
                    resource_table = find_dataset_resource_table(html)
                    if resource_table is not None:
                        return resource_table
                    else:
                        return pd.DataFrame([(dataset.title, 'Dataset', 'Unknown', dataset.language, dataset.url, 'Error')],
                                        columns=_RESOURCE_COLUMNS)
    except Exception as e:
        # TODO: log error
        return pd.DataFrame([(dataset.title, 'Dataset', 'Unknown', dataset.language, dataset.url, 'Error')],
                            columns=_RESOURCE_COLUMNS)


def find_dataset_resource_table(html: str):
    tables = get_tables(html)
    if len(tables) > 0:
        for table in tables:
            if 'Resource Name' in table.columns:
                return table


def find_resource_urls(html: str):
    return None


_DATASET_URL = '(http://(open|ouvert)\.canada\.ca)?/data/(en|fr)/dataset/(\w[\w\-]{16,})$'
dataset_re = re.compile(_DATASET_URL)


def get_dataset_links(html_or_soup):
    """
    Find the dataset links on a page
    :param html_or_soup: a html string or a BeautifulSoup
    :return: a generator with all the links on a page
    """
    if isinstance(html_or_soup, str):
        soup = BeautifulSoup(html_or_soup, features='lxml')
    else:
        soup = html_or_soup
    for link in soup.find_all('a'):
        href = link.get('href', '')
        if dataset_re.match(href):
            yield href


def find_dataset_link(html_or_soup):
    """
    Find a dataset link on a page
    :param html_or_soup: a html string or a BeautifulSoup
    :return: a single dataset url on a page if there is one
    """
    links = list(get_dataset_links(html_or_soup))
    if len(links) > 0:
        return links[0]