from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
import logging
import time

from database.collections import mongodb_connection
from routes.movies import movies_router
from utils import is_db_movies_collection_initialized, initialize_db_movies_collection_from_dataset


logger = logging.getLogger("uvicorn")


def app_startup_event_handler():
    """
    Function called at application startup - before receiving requests
    """
    logger.info('Initializing Movies collection from TMDB 5000 Movie dataset ...')

    if is_db_movies_collection_initialized():
        logger.info('Collection already initialized')
    else:
        start_time = time.time()
        movies_inserted = initialize_db_movies_collection_from_dataset()

        logger.info(f'Successfully initialized the collection with {movies_inserted} movies, '
                    f'elapsed time: {time.time() - start_time:.2f} seconds')


def app_shutdown_event_handler():
    """
    Function called after application shutdown
    """
    mongodb_connection.close_connection()
    logger.info('MongoDB connection closed!')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app_startup_event_handler()
    # lifetime
    yield
    # shutdown
    app_shutdown_event_handler()


app = FastAPI(
    title="MongoDB Atlas Semantic Search",
    description="Demo Application - Semantic Search with MongoDB Atlas and FastAPI",
    version="0.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# routers
app.include_router(movies_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, log_level='info', reload=True)
