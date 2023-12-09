import pandas as pd
import json
from typing import Dict
from datetime import datetime

from database.collections import db_movies_collection
from database.schemas import MovieWithEmbeddingSchema
from language_model import embedding_model


def is_db_movies_collection_initialized() -> bool:
    """
    Checks if the Movies collection is initialized.\n
    For the sake of simplicity, collection is considered as initialized if it contains documents.

    :return: True/False
    """
    return db_movies_collection.count_documents({}) > 0


def initialize_db_movies_collection_from_dataset() -> int:
    """
    Initialize Movies collection using TMDB 5000 Movie Dataset from Kaggle (https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)\n
    Already downloaded and placed in data_source folder

    :return movies_inserted: Number of inserted movies
    """
    # load the dataset
    df = pd.read_csv('data_source/tmdb_5000_movies.csv')

    # drop rows with missing mandatory data
    df.dropna(subset=['title', 'overview'], inplace=True)

    # drop duplicate title rows
    df.drop_duplicates(subset='title', keep='first', inplace=True)

    # pre-process fields
    df['homepage'].fillna('', inplace=True)
    df['genres'] = df['genres'].apply(lambda x: [genre['name'] for genre in json.loads(x)])
    df['release_date'].fillna('', inplace=True)
    df['release_date'] = df['release_date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d') if x else '')
    
    # calculate embeddings
    df['embedding'] = embedding_model.encode(df['title'].values + '. ' + df['overview'].values).tolist()

    # convert dataframe to list of dictionaries using Schema
    movies_data = [remove_empty_fields(movie) for movie in df.to_dict(orient='records')]
    movies_data = [MovieWithEmbeddingSchema(**data).model_dump() for data in movies_data]

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
