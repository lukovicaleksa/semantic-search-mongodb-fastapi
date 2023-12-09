from typing import Optional, List, Any

from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime

from language_model import embedding_model, embedding_vector_length, TorchDevice


class MovieBaseSchema(BaseModel):
    """
    Base Movie Schema
    """
    title: str = Field(...)
    overview: str = Field(...)
    homepage: Optional[str] = Field(None)
    genres: Optional[List[str]] = Field(None)
    runtime: Optional[int] = Field(None)
    release_date: Optional[datetime] = Field(None)
    budget: Optional[int] = Field(None)
    revenue: Optional[int] = Field(None)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "The Lord of the Rings: The Rise of a New Power",
                "overview": "As Middle-earth rebuilds after the War of the Ring, a new threat emerges, "
                            "and the fellowship must reunite to face a power that threatens to plunge the world into darkness.",
                "homepage": None,
                "genres": ["Adventure", "Fantasy"],
                "release_date": "2009-12-10T00:00:00.000+00:00",
                "runtime": 160,
                "budget": 280000000,
                "revenue": None
            }
        }


class MovieWithEmbeddingSchema(MovieBaseSchema):
    """
    Movie Schema with Embedding Vector
    """
    embedding: List[float] = Field(..., min_items=embedding_vector_length, max_items=embedding_vector_length)

    def __init__(self, **data: Any):
        # calculate movie embedding based on movie title and overview
        if 'embedding' not in data:
            if 'title' in data and 'overview' in data:
                data['embedding'] = embedding_model.encode(data['title'] + '. ' + data['overview'], device=TorchDevice.CPU.value)
            else:
                data['embedding'] = None

        super().__init__(**data)

    @classmethod
    def from_base_schema(cls, movie: MovieBaseSchema) -> 'MovieWithEmbeddingSchema':
        """
        Construct MovieWithEmbeddingSchema from MovieBaseSchema

        :param movie: Movie object as MovieBaseSchema
        """
        # calculate movie embedding based on movie title and overview
        if movie.title and movie.overview:
            movie_embedding = embedding_model.encode(movie.title + '. ' + movie.overview, device=TorchDevice.CPU.value)
        else:
            movie_embedding = None

        # Create an instance of MovieWithEmbeddingSchema
        instance = cls(title=movie.title,
                       overview=movie.overview,
                       homepage=movie.homepage,
                       genres=movie.genres,
                       runtime=movie.runtime,
                       release_date=movie.release_date,
                       budget=movie.budget,
                       revenue=movie.revenue,
                       embedding=movie_embedding)

        return instance


class MovieSchema(MovieBaseSchema):
    """
    Movie Schema with ID
    """
    id: str = Field(..., alias='_id')

    def __init__(self, **data: Any):
        # convert ObjectID to str
        if isinstance(data.get('_id'), ObjectId):
            data['_id'] = str(data['_id'])

        super().__init__(**data)
