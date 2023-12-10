from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Path, Query, HTTPException, status
from pymongo.errors import DuplicateKeyError

from config import settings
from database.collections import db_movies_collection
from database.schemas import MovieBaseSchema, MovieWithEmbeddingSchema, MovieWithIDSchema, \
    MoviesSemanticSearchPromptSchema, MoviesSemanticSearchResponseSchema


movies_router = APIRouter(prefix='/movies', tags=['movies'])


@movies_router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=MovieWithIDSchema
)
def insert_movie(movie: MovieBaseSchema = Body(...)) -> MovieWithIDSchema:
    movie_with_embedding = MovieWithEmbeddingSchema.from_base_schema(movie)
    try:
        res = db_movies_collection.insert_one(movie_with_embedding.model_dump())
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Movie with the same title already exists')

    if res.inserted_id:
        # get inserted movie and return it
        inserted_movie = db_movies_collection.find_one({'_id': res.inserted_id})
        return MovieWithIDSchema(**inserted_movie)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to insert movie')


@movies_router.get(
    path='/id/{movie_id}',
    response_model=MovieWithIDSchema
)
def get_movie_by_id(movie_id: str = Path(...)) -> MovieWithIDSchema:
    movie = db_movies_collection.find_one({'_id': ObjectId(movie_id)})

    if movie:
        return MovieWithIDSchema(**movie)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.put(
    path='/id/{movie_id}',
    response_model=MovieWithIDSchema
)
def update_movie_by_id(movie_id: str = Path(...),
                       updated_movie: MovieBaseSchema = Body(...)) -> MovieWithIDSchema:
    existing_movie = db_movies_collection.find_one({'_id': ObjectId(movie_id)})

    if existing_movie:
        updated_movie_with_embedding = MovieWithEmbeddingSchema.from_base_schema(updated_movie)
        db_movies_collection.update_one({'_id': ObjectId(movie_id)},
                                        {'$set': updated_movie_with_embedding.model_dump()})
        # get updated movie and return it
        updated_movie = db_movies_collection.find_one({'_id': ObjectId(movie_id)})
        return MovieWithIDSchema(**updated_movie)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.delete(
    path='/id/{movie_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_movie_by_id(movie_id: str = Path(...)):
    res = db_movies_collection.delete_one({'_id': ObjectId(movie_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.get(
    path='/title',
    response_model=MovieWithIDSchema
)
def get_movie_by_title(movie_title: str = Query(...)) -> MovieWithIDSchema:
    movie = db_movies_collection.find_one({'title': movie_title})

    if movie:
        return MovieWithIDSchema(**movie)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.put(
    path='/title',
    response_model=MovieWithIDSchema
)
def update_movie_by_title(movie_title: str = Query(...), updated_movie: MovieBaseSchema = Body(...)) -> MovieWithIDSchema:
    existing_movie = db_movies_collection.find_one({'title': movie_title})

    if existing_movie:
        updated_movie_with_embedding = MovieWithEmbeddingSchema.from_base_schema(updated_movie)
        db_movies_collection.update_one({'title': movie_title},
                                        {'$set': updated_movie_with_embedding.model_dump()})
        # get updated movie and return it
        updated_movie = db_movies_collection.find_one({'_id': existing_movie['_id']})
        return MovieWithIDSchema(**updated_movie)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.delete(
    path='/title',
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_movie_by_title(movie_title: str = Query(...)):
    res = db_movies_collection.delete_one({'title': movie_title})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.get(
    path='/semantic-search',
    response_model=MoviesSemanticSearchResponseSchema
)
def movies_semantic_search(prompt: str = Query(..., title='Search Prompt', max_length=64),
                           limit: int = Query(..., title='Limit returned documents', ge=1, le=10)) -> MoviesSemanticSearchResponseSchema:
    semantic_search_prompt = MoviesSemanticSearchPromptSchema(prompt=prompt, limit=limit)

    # perform vector search
    res = db_movies_collection.aggregate([
        {
            '$vectorSearch': {
                'index': settings.MONGODB_ATLAS_MOVIES_VECTOR_SEARCH_INDEX_NAME,
                'path': 'embedding',
                'queryVector': semantic_search_prompt.generate_embedding_vector(),
                'numCandidates': semantic_search_prompt.get_optimal_number_of_search_candidates(),
                'limit': semantic_search_prompt.limit,
            }
        },
        {
            '$project': {
                'title': 1,
                'overview': 1,
                'genres': 1
            }
        }
    ])

    movies_semantic_search_response = {'movies': [movie for movie in res]}
    return MoviesSemanticSearchResponseSchema(**movies_semantic_search_response)
