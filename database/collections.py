from pymongo import ASCENDING

from database.connection import MongoDBAtlasConnection
from config import settings


mongodb_connection = MongoDBAtlasConnection(username=settings.MONGODB_ATLAS_USERNAME,
                                            password=settings.MONGODB_ATLAS_PASSWORD,
                                            host=settings.MONGODB_ATLAS_HOST,
                                            db_name=settings.MONGODB_ATLAS_DB_NAME)
# connect to database
mongodb_connection.connect()

# database object
db = mongodb_connection.get_db()

# collections
db_movies_collection = db.get_collection('movies')

# indexes
db_movies_collection.create_index([('title', ASCENDING)], unique=True)
