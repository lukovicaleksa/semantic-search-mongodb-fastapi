from fastapi import FastAPI

from database.collections import mongodb_connection
from routes.movies import movies_router


app = FastAPI()


@app.on_event('shutdown')
def shutdown_event():
    """
    Shutdown Event is triggered
    """
    # close MongoDB connection
    mongodb_connection.close_connection()


# routers
app.include_router(movies_router)
