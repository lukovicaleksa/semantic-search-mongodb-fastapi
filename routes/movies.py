from bson.objectid import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Body, Path, Query, HTTPException, status
from fastapi.responses import PlainTextResponse
from pymongo.errors import DuplicateKeyError

from config import settings
from database.collections import db_movies_collection
from database.schemas import MovieBaseSchema, MovieWithEmbeddingSchema, MovieWithIDSchema, \
    MoviesSemanticSearchPromptSchema, MoviesSemanticSearchResponseSchema


movies_router = APIRouter(prefix='/movies', tags=['movies'])


@movies_router.post(
    path='/',
    response_class=PlainTextResponse,
    status_code=status.HTTP_201_CREATED
)
def insert_movie(movie: MovieBaseSchema = Body(...)):
    """
    Insert Movie into MongoDB
    """
    movie_with_embedding = MovieWithEmbeddingSchema.from_base_schema(movie)

    try:
        res = db_movies_collection.insert_one(movie_with_embedding.model_dump())
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Movie with the same title already exists')
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to insert movie')
    else:
        return PlainTextResponse(content=str(res.inserted_id))


@movies_router.get(
    path='/id/{movie_id}',
    response_model=MovieBaseSchema,
    status_code=status.HTTP_200_OK
)
def get_movie_by_id(movie_id: str = Path(...)):
    """
    Get Movie by ID from MongoDB
    """
    if not ObjectId.is_valid(movie_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid movie ID')

    movie = db_movies_collection.find_one({'_id': ObjectId(movie_id)})

    if movie:
        return MovieBaseSchema(**movie)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.put(
    path='/id/{movie_id}',
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK
)
def update_movie_by_id(movie_id: str = Path(...),
                       updated_movie: MovieBaseSchema = Body(...)):
    """
    Update Movie by ID in MongoDB
    """
    if not ObjectId.is_valid(movie_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid movie ID')

    existing_movie = db_movies_collection.find_one({'_id': ObjectId(movie_id)})
    if not existing_movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')

    updated_movie_with_embedding = MovieWithEmbeddingSchema.from_base_schema(updated_movie)
    res = db_movies_collection.update_one({'_id': ObjectId(movie_id)},
                                          {'$set': updated_movie_with_embedding.model_dump(exclude={'id', 'created_at'})})

    if res.matched_count == 0 or res.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to update movie')

    return PlainTextResponse(content='Movie updated successfully')


@movies_router.delete(
    path='/id/{movie_id}',
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK
)
def delete_movie_by_id(movie_id: str = Path(...)):
    """
    Delete Movie by ID from MongoDB
    """
    if not ObjectId.is_valid(movie_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid movie ID')

    res = db_movies_collection.delete_one({'_id': ObjectId(movie_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')

    return PlainTextResponse(content='Movie deleted successfully')


@movies_router.get(
    path='/title',
    response_model=MovieBaseSchema,
    status_code=status.HTTP_200_OK
)
def get_movie_by_title(movie_title: str = Query(...)):
    """
    Get Movie by Title from MongoDB
    """
    movie = db_movies_collection.find_one({'title': movie_title})

    if movie:
        return MovieBaseSchema(**movie)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.put(
    path='/title',
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK
)
def update_movie_by_title(movie_title: str = Query(...),
                          updated_movie: MovieBaseSchema = Body(...)):
    """
    Update Movie by Title in MongoDB
    """
    existing_movie = db_movies_collection.find_one({'title': movie_title})

    if not existing_movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')

    updated_movie_with_embedding = MovieWithEmbeddingSchema.from_base_schema(updated_movie)
    res = db_movies_collection.update_one({'title': movie_title},
                                          {'$set': updated_movie_with_embedding.model_dump(exclude={'id', 'created_at'})})

    if res.matched_count == 0 or res.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to update movie')

    return PlainTextResponse(content='Movie updated successfully')


@movies_router.delete(
    path='/title',
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK
)
def delete_movie_by_title(movie_title: str = Query(...)):
    """
    Delete Movie by Title from MongoDB
    """
    res = db_movies_collection.delete_one({'title': movie_title})

    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')
    else:
        return PlainTextResponse(content='Movie deleted successfully')


@movies_router.get(
    path='/semantic-search',
    response_model=MoviesSemanticSearchResponseSchema,
    status_code=status.HTTP_200_OK
)
def movies_semantic_search(prompt: str = Query(..., title='Search Prompt', max_length=64),
                           limit: int = Query(..., title='Limit returned documents', ge=1, le=10)):
    """
    Perform Semantic Search on Movies collection
    """
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
