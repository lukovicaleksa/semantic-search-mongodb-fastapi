from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from database.collections import mongodb_connection
from routes.movies import movies_router
from utils import initialize_db_movies_collection_from_dataset


logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # application startup
    logger.info('Initializing Movies collection from dataset ...')
    movies_inserted = initialize_db_movies_collection_from_dataset()
    logger.info(f'Successfully initialized the collection with {movies_inserted} movies')

    yield

    # application shutdown
    mongodb_connection.close_connection()
    logger.info('MongoDB connection closed!')


app = FastAPI(lifespan=lifespan)


# routers
app.include_router(movies_router)
