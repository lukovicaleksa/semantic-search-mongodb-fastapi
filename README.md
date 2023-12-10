# Semantic Search with MongoDB and FastAPI

## Description

This project demonstrates how you can enhance standard CRUD operations in your application using Semantic Search mechanism.

[MongoDB hosted on Atlas](https://www.mongodb.com/atlas/database) is used as a primary Database, leveraging its [Vector Search](https://www.mongodb.com/products/platform/atlas-vector-search) feature to perform Semantic Search.

Open-Source [Sentence Transformers from Hugging Face](https://huggingface.co/sentence-transformers) are used for creation of Embedding Vectors, which are stored directly in MongoDB documents and are used in Semantic Search.

Application implementation is done in Python using [FastAPI framework](https://fastapi.tiangolo.com/), it heavily relies on [Pymongo](https://www.mongodb.com/docs/drivers/pymongo/) for communication with MongoDB and on [Pydantic](https://docs.pydantic.dev/latest/) for data modeling and validation.
All neccessary data processing needed for Semantic Search like data vectorization and storage managing is encapsulated and hidden from the API user, which makes standard CRUD operations easy to use.

This project works with the data from [TMDB 5000 Movie Dataset from Kaggle](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata).

## Prerequisites

- Python Environment management tool like conda or venv
- MongoDB Atlas account

## Setup

The steps to get the project up and running are:

1. Clone the repository to your local machine
2. MongoDB Atlas Cluster setup
   1. Create account on MongoDB Atlas (if you don't already have one) and log in
   2. Create a new project and deploy a free cluster
   3. Add database user and save credentials (username and password)
   4. Get connection string, should look like this: `mongodb+srv://<username>:<password>@<host>/?retryWrites=true&w=majority`, part after host is optional
3. MongoDB Atlas Vector Search setup
   1. Find deployed cluster in the Database section and create a database called 'semantic_search' with 'movies' collection in it
   2. Create a vector search index with name 'moviesVectorSearch' and link it to created collection. For Index definition use the following JSON Editor:
   ```json
   {
     "mappings": {
       "dynamic": true,
       "fields": {
         "embedding": {
           "dimensions": 384,
           "similarity": "cosine",
           "type": "knnVector"
         }
       }
     }
   }
   ```
4. Create a .env file in project root and fill in with your user credentials and host from the MongoDB connection string. Fill in the DB name, movies collection name and search index name as you named them in MongoDB Atlas
   ``` dotenv
   # MongoDB Atlas Credentials
   MONGODB_ATLAS_USERNAME=<username>
   MONGODB_ATLAS_PASSWORD=<password>
   MONGODB_ATLAS_HOST=<host>
   
   # MongoDB Atlas Database
   MONGODB_ATLAS_DB_NAME=semantic_search
   MONGODB_ATLAS_MOVIES_COLLECTION_NAME=movies
   
   # MongoDB Atlas Vector Search
   MONGODB_ATLAS_MOVIES_VECTOR_SEARCH_INDEX_NAME=moviesVectorSearch
   ```
5. Create Python virtual environment with version 3.11 (should work with older versions like 3.10 and 3.9)
   ``` commandline
   conda create --name your_environment_name python=3.11
   ```
6. Activate the environment and install the packages
   ``` commandline
   conda activate your_environment_name
   pip install -r requirements.txt
   ```

## Usage

To run the application, navigate to project root folder, activate your environment and run [main.py](main.py) script.
```commandline
python main.py
```