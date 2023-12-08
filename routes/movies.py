from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Path, HTTPException, status

from database.schemas import MovieBaseSchema, MovieSchema
from database.collections import db_movies_collection


movies_router = APIRouter(prefix='/movies', tags=['movies'])


@movies_router.post(path='/', response_description='Create a new movie', status_code=status.HTTP_201_CREATED, response_model=MovieSchema)
def insert_movie(movie: MovieBaseSchema = Body(...)) -> MovieSchema:
    res = db_movies_collection.insert_one(movie.model_dump())
    if res.inserted_id:
        # get inserted movie and return it
        inserted_movie = db_movies_collection.find_one({'_id': res.inserted_id})
        return MovieSchema(**inserted_movie)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to insert movie')


@movies_router.get(path='/id/{movie_id}', response_description='Get movie by ID', response_model=MovieSchema)
def get_movie_by_id(movie_id: str = Path(...)) -> MovieSchema:
    movie = db_movies_collection.find_one({'_id': ObjectId(movie_id)})
    if movie:
        return MovieSchema(**movie)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.get(path='/title/{movie_title}', response_description='Get movie by title', response_model=MovieSchema)
def get_movie_by_title(movie_title: str = Path(...)) -> MovieSchema:
    movie = db_movies_collection.find_one({'title': movie_title})
    if movie:
        return MovieSchema(**movie)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.put(path='/id/{movie_id}', response_description='Update movie by ID', response_model=MovieSchema)
def update_movie_by_id(movie_id: str = Path(...), updated_movie: MovieBaseSchema = Body(...)) -> MovieSchema:
    existing_movie = db_movies_collection.find_one({'_id': ObjectId(movie_id)})
    if existing_movie:
        db_movies_collection.update_one({'_id': ObjectId(movie_id)}, {'$set': updated_movie.model_dump()})
        # get updated movie and return it
        updated_movie = db_movies_collection.find_one({'_id': ObjectId(movie_id)})
        return MovieSchema(**updated_movie)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.put(path='/title/{movie_title}', response_description='Update movie by title', response_model=MovieSchema)
def update_movie_by_title(movie_title: str = Path(...), updated_movie: MovieBaseSchema = Body(...)) -> MovieSchema:
    existing_movie = db_movies_collection.find_one({'title': movie_title})
    if existing_movie:
        db_movies_collection.update_one({'title': movie_title}, {'$set': updated_movie.model_dump()})
        # get updated movie and return it
        updated_movie = db_movies_collection.find_one({'title': movie_title})
        return MovieSchema(**updated_movie)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.delete(path='/id/{movie_id}', response_description='Delete movie by ID', status_code=status.HTTP_204_NO_CONTENT)
def delete_movie_by_id(movie_id: str = Path(...)):
    res = db_movies_collection.delete_one({'_id': ObjectId(movie_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')


@movies_router.delete(path='/title/{movie_title}', response_description='Delete movie by title', status_code=status.HTTP_204_NO_CONTENT)
def delete_movie_by_title(movie_title: str = Path(...)):
    res = db_movies_collection.delete_one({'title': movie_title})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Movie not found')
