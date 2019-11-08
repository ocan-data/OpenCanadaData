import numpy as np
import pandas as pd
import os
import re
from .repo import Repo
import logging
from chardet import detect

logger = logging.getLogger("ocandata")


def optimize_statscan(statscan_data: pd.DataFrame):
    statscan_data.Element = statscan_data.Element.astype("category")


CONTROL_COLS = [
    "VECTOR",
    "COORDINATE",
    "DECIMALS",
    "STATUS",
    "SYMBOL",
    "TERMINATED",
    "SCALAR_FACTOR",
    "SCALAR_ID",
    "DGUID",
    "UOM",
    "UOM_ID",
]
STATSCAN_TYPES = {
    "Age group": "category",
    "Sex": "category",
    "UOM": "category",
    "UOM_ID": "category",
    "GEO": "category",
    "SCALAR_FACTOR": "category",
    "SCALAR_ID": "category",
    "STATUS": "category",
    "SYMBOL": "category",
}


def read_statscan_csv(statcan_fn: str):
    return pd.read_csv(statcan_fn, dtype=STATSCAN_TYPES, low_memory=False)


def to_wide_format(statscan_data: pd.DataFrame, pivot_column):
    """
    Converts statscan data to wide format
    :param statscan_data:
    :return: a dataframe with the statscan data converted to wide format
    """
    base = statscan_data.copy()
    group_cols = [
        col
        for col in base.columns.tolist()
        if col not in CONTROL_COLS + [pivot_column, "VALUE"]
    ]
    # Assign a group number
    base["group"] = base.groupby(group_cols).ngroup()

    # Pivot on the group, turning the element into columns
    values = base.pivot_table(
        index="group",
        columns=pivot_column,
        values="VALUE",
        aggfunc=np.max,
        dropna=False,
    )
    # Drop Element and VALUE columns and drop duplicates
    base = base.drop(columns=[pivot_column, "VALUE"]).drop_duplicates(subset=group_cols)
    # Now merge with values
    return base.merge(values, on="group").drop(columns="group")


_STATSCAN_DATASET_RE = re.compile("(\d+)(\-(eng|fra))?\.(\w+)+")


class StatscanUrl:
    def __init__(
        self,
        baseurl: str,
        file: str,
        resourceid: str,
        extension: str,
        data: str,
        metadata: str,
        language: str = None,
    ):
        self.baseurl = baseurl
        self.file = file
        self.resourceid = resourceid
        self.language = language
        self.partitions = [language]
        self.extension = extension
        self.data = data
        self.metadata = metadata

    @classmethod
    def parse_from_filename(cls, url: str):
        filename = os.path.basename(url)
        baseurl = url[: url.index(filename)]
        match = _STATSCAN_DATASET_RE.match(filename)
        if match:
            file = match.group(0)
            resourceid = match.group(1)
            language = match.group(3)
            extension = match.group(4)
            data = f"{match.group(1)}.csv"
            metadata = f"{match.group(1)}_MetaData.csv"
            return StatscanUrl(
                baseurl=baseurl,
                file=file,
                resourceid=resourceid,
                extension=extension,
                data=data,
                metadata=metadata,
                language=language,
            )
        else:
            raise ValueError("Does not seem to be a valid statscan dataset url: " + url)

    def id(self):
        return f"{self.baseurl}{self.resourceid}"

    def __repr__(self):
        return f"StatscanUrl {self.__dict__}"


statscan_zipurl_re = re.compile(r".*[0-9]+(\-(en|fr)\w+?)?\.zip.*?")


class StatscanZip(object):
    def __init__(self, url: str, repo: Repo = None):
        assert statscan_zipurl_re.fullmatch(url)
        self.url: str = url
        self.url_info: StatscanUrl = StatscanUrl.parse_from_filename(url)
        self.repo: Repo = repo or Repo.at_user_home()

    def dimensions(self):
        return self.get_metadata().dimensions

    def primary_dimension(self):
        return self.get_metadata().pivot_column()

    def get_units_of_measure(self):
        return self.units_of_measure

    @classmethod
    def _apply_dtypes(cls, data: pd.DataFrame):
        for col in data:
            if col in ["REF_DATE"]:
                data[col] = pd.to_datetime(data[col]).dt.normalize()

    def _fetch_data(self):
        resource_id: str = self.url_info.resourceid
        data_file, metadata_file = self.repo.unzip(self.url, resource_id=resource_id)
        return data_file, metadata_file

    def transform_statscan_data(
        self,
        data: pd.DataFrame,
        wide=True,
        index_col: str = None,
        drop_control_cols=True,
    ):
        primary_dimension = self.primary_dimension()
        units_of_measure = (
            data[[primary_dimension, "UOM"]]
            .drop_duplicates()
            .set_index(primary_dimension)
            .sort_index()
        )
        setattr(self, "units_of_measure", units_of_measure)
        if wide:
            data = to_wide_format(data, pivot_column=self.primary_dimension())
        if index_col:
            data = data.set_index(index_col)

        if drop_control_cols:
            drop_cols = [col for col in CONTROL_COLS if col in data.columns]
            data = data.drop(columns=drop_cols)

        # Convert types
        if 'REF_DATE' in data:
            if not data['REF_DATE'].isnull().any():
                data['REF_DATE'] = pd.to_datetime(data['REF_DATE'])

        data = data.rename(columns={'REF_DATE': 'Date', 'GEO':'Geo'})
        return data

    def _set_metadata(self, metadata_file):
        metadata: StatscanMetadata = StatscanMetadata(metadata_file)
        setattr(self, "metadata", metadata)

    def get_metadata(self):
        if not hasattr(self, "metadata"):
            data_file, metadata_file = self._fetch_data()
            self._set_metadata(metadata_file)
        return self.metadata

    def get_data(
        self,
        wide=True,
        index_col: str = None,
        drop_control_cols=True
    ):
        """
        Get the data from this zipfile
        :param wide: whether to make this a wide dataset
        :param index_col: the column to use as the index
        :param drop_control_cols: whether to drop the control columns
        :return: a Dataframe containing the data
        """
        if not hasattr(self, "data"):
            data_file, metadata_file = self._fetch_data()
            self._set_metadata(metadata_file)
            data_raw = read_statscan_csv(data_file)
            data = self.transform_statscan_data(
                data_raw,
                wide=wide,
                index_col=index_col,
                drop_control_cols=drop_control_cols,
            )
            setattr(self, "data", data)
        return self.data

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.url}>"


class StatscanMetadata(object):

    def __init__(self, metadata_file):
        self.sections = StatscanMetadata.parse_metadata(metadata_file)

    @property
    def notes(self):
        return self.sections['Notes']

    @property
    def cube_info(self):
        return self.sections['CubeInfo']

    @property
    def dimensions(self):
        return self.sections['Dimensions']

    @classmethod
    def parse_sections(cls, metadata_file):
        encoding = get_encoding_type(metadata_file)
        with open(metadata_file, 'r', encoding=encoding) as f:
            start_section = True
            for line in f.readlines():
                line = line.strip()
                if len(line) > 0:
                    parts = [p.replace('"', '') for p in line.split(',')]
                    if start_section:
                        columns = parts
                        rows = []
                        start_section = False
                    else:
                        rows.append(tuple(parts))
                else:
                    start_section = True
                    row_widths = [len(row) for row in rows]
                    if row_widths == []:
                        continue
                    row_width = max(row_widths)
                    if row_width > len(columns):
                        rows = [row[:len(columns)] for row in rows]
                    elif len(columns) > row_width:
                        columns = columns[:row_width]
                    df = pd.DataFrame(data=rows, columns=columns)
                    yield df

    @classmethod
    def parse_metadata(cls, metadata_file: str):
        metadata_sections = cls.parse_sections(metadata_file)
        sections = {}
        for df in metadata_sections:
            if list_contains(df.columns, ['Cube Title', 'Product Id']):
                sections['CubeInfo'] = df
            elif list_contains(df.columns, ['Dimension ID', 'Dimension name']):
                sections['Dimensions'] = df
            elif list_contains(df.columns, ['Dimension ID', 'Member Name']):
                sections['DimensionValues'] = df
            elif list_contains(df.columns, ['Note ID', 'Note']):
                sections['Notes'] = df

        return sections

    def pivot_column(self):
        return self.dimensions.tail(1)["Dimension name"].values[0]

    def __repr__(self):
        return f"<{self.name}>"

    def _repr_html_(self):
        """
        This is for Jupyter notebooks to automatically display the metadata
        :return:
        """
        _html = f"<h2>{self.name}</h2>"
        _html += self.cube_info._repr_html_()
        _html += "<h3>Dimensions</h3>"
        _html += self.dimensions._repr_html_()
        _html += "<h3>Notes</h3>"
        _html += self.notes._repr_html_()
        return _html


def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
        return detect(rawdata)['encoding'].lower()


def list_contains(alist, values):
    return all([v in alist for v in values])