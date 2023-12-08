import pandas as pd
import json
from typing import Dict
from datetime import datetime

from database.collections import db_movies_collection
from database.schemas import MovieBaseSchema


def initialize_db_movies_collection_from_dataset() -> int:
    """
    Initialize Movies collection using TMDB 5000 Movie Dataset from Kaggle (https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)\n
    Already downloaded and placed in data folder

    :return movies_inserted: Number of inserted movies
    """
    # load the dataset
    df = pd.read_csv('data/tmdb_5000_movies.csv')

    # drop rows with missing mandatory data
    df = df.dropna(subset=['title', 'overview'])

    # pre-process fields
    df['homepage'].fillna('', inplace=True)
    df['genres'] = df['genres'].apply(lambda x: [genre['name'] for genre in json.loads(x)])
    df['release_date'].fillna('', inplace=True)
    df['release_date'] = df['release_date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d') if x else '')

    # convert dataframe to list of dictionaries using Movie Schema
    movies_data = [remove_empty_fields(movie) for movie in df.to_dict(orient='records')]
    movies_data = [MovieBaseSchema(**data).model_dump() for data in movies_data]

    # empty movies collection
    db_movies_collection.delete_many({})
    # insert the data
    db_movies_collection.insert_many(movies_data)

    return db_movies_collection.count_documents({})


def remove_empty_fields(input_dict: Dict) -> Dict:
    """
    Remove key-value pairs from dictionary where value is empty

    :param input_dict: Input Dictionary
    :return output_dict: Processed Dictionary
    """
    return {key: value for key, value in input_dict.items() if value not in ('', [], None)}
