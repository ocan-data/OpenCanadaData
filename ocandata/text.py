import pandas as pd


def get_language(language: str):
    if language:
        language = language.lower()
        if language == 'french' or language == 'fr' or language.startswith('fran'):
            return 'French'

class Index:

    def __init__(self, column: pd.Series):
        pass
