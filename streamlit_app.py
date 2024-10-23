from typing import Union

import streamlit as st
import requests

from database.schemas import MovieBaseSchema


### Configuration ###
st.set_page_config(page_title="MUG Belgrade", page_icon="./assets/mongodb_logo.svg")


### Initialize Session State ###
if "server_url" not in st.session_state:
    st.session_state.server_url = "http://127.0.0.1:8000"
    st.session_state.title_search_url = f"{st.session_state.server_url}/movies/title"
    st.session_state.semantic_search_url = f"{st.session_state.server_url}/movies/semantic-search"


### Helper functions ###
def find_movie_by_title(movie_title: str) -> list[MovieBaseSchema]:
    """
    Find Movie by Title

    :param movie_title: Movie Title
    :return: Movie Object
    """
    response = requests.get(url=f"{st.session_state.title_search_url}/?movie_title={movie_title}")

    if response.status_code == 200:
        return [MovieBaseSchema(**response.json())]
    else:
        return []


def semantic_search(query: str, limit: int) -> list[MovieBaseSchema]:
    """
    Perform Semantic Search

    :param query: Search Query
    :param limit: Number of returned documents
    :return: List of Movie Objects
    """
    response = requests.get(url=f"{st.session_state.semantic_search_url}/?prompt={query}&limit={limit}")

    if response.status_code == 200:
        return [MovieBaseSchema(**movie) for movie in response.json()]
    else:
        return []


### Sidebar ###
with st.sidebar:
    st.title("Semantic Search Application")
    st.header("🎬 TMDB 5000")

    st.markdown("---")  # Adds visual separator
    st.subheader("How to use")
    st.markdown("1. Select search type: \n"
                "   - Classic Search \n"
                "   - Semantic Search \n"
                "2. Provide your search query\n"
                "3. Get best matching movies based on their title and overview")

    st.markdown("#")  # Adds empty space
    st.markdown("#")  # Adds empty space
    with st.columns([1, 5, 1])[1]:
        st.image(image="./assets/mongodb_logo_round.svg", caption="MUG Belgrade", use_column_width=True)


### Main Screen ###
st.title("TMDB 5000 Movies Search 🎬")
st.caption("🍃 Powered by MongoDB Atlas")
st.markdown("")  # Adds empty space
st.markdown("")  # Adds empty space
st.markdown("")  # Adds empty space

col_1, _, col_3 = st.columns([2, 1, 1])

with col_1:
    search_type = st.radio(label="Search Type",
                           options=['Classic Search', 'Semantic Search'],
                           horizontal=True)

with col_3:
    n_search_results = st.selectbox(label="Search Results",
                                    options=[1, 3, 5, 10],
                                    index=0 if search_type == "Classic Search" else 1,
                                    disabled=(search_type == "Classic Search"))

st.markdown("")  # Adds empty space

search_query = st.text_input(label="Search Query" if search_type == "Semantic Search" else "Movie Title",
                             max_chars=64)

st.markdown("")  # Adds empty space

with st.columns([1, 1.2, 1])[1]:
    search_button = st.button(label="🔎  Find best matching Movies" if search_type == "Semantic Search" else "🔎  Find Movie",
                              type="primary",
                              use_container_width=True,
                              disabled=len(search_query) == 0)

st.markdown("")  # Adds empty space

if search_button:
    if len(search_query) > 0:
        with st.columns([1.2, 1.2, 1])[1]:
            with st.spinner('Searching... Please wait'):
                if search_type == "Classic Search":
                    found_movies = find_movie_by_title(search_query)
                else:
                    found_movies = semantic_search(search_query, n_search_results)

        if len(found_movies) == 0:
            st.error("No movies found. Please try again.")

        for movie in found_movies:
            with st.container(border=True):
                col_1, _, col_2 = st.columns([1.2, 0.1, 0.5])
                with col_1:
                    st.write(f"### {movie.title} ###")
                with col_2:
                    if movie.homepage:
                        st.link_button("🔗 View Homepage", movie.homepage, use_container_width=True)

                st.markdown("")  # Adds empty space
                st.write(f"{movie.overview}")
                st.markdown("")  # Adds empty space

                col_1, _, col_2, _, col_3 = st.columns([1.5, 0.1, 2, 0.1, 3])
                with col_1:
                    st.write(f"🕒 {movie.runtime} minutes")
                    st.write(f"📅 {movie.release_date.strftime('%d-%m-%Y')}")
                with col_2:
                    st.write(f"💰 Budget: {movie.budget / 1e6:.2f} M")
                    st.write(f"💵 Revenue: {movie.revenue / 1e6:.2f} M")
                with col_3:
                    st.write(f"🎭 {', '.join(movie.genres)}")

    else:
        st.error("Please enter a search query.")
