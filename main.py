import streamlit as st
import pandas as pd
import plotly.express as px
from scrape import get_image_from_imdb
st.set_page_config(layout="wide")


@st.cache_data
def get_data():
    meta = pd.read_csv("datasets/streamlit_meta.csv", index_col=0)
    user = pd.read_csv("datasets/streamlit_user.csv", nrows=60000)

    return meta, user


def home(tab):
    container = tab.container()
    container.image(
        "https://cdn.shopify.com/s/files/1/1057/4964/t/27/assets/star-wars-banner.jpeg?v=80624120874934922901668841836")
    container.audio("http://soundfxcenter.com/movies/star-wars/8d82b5_Star_Wars_The_Imperial_March_Theme_Song.mp3")
    container.header("Nedir ?")
    container.markdown("Kullanıcının seçtiği filme göre ona en uygun filmleri öneren bir film öneri sistemi.")


def visualizations(tab, meta, user):
    col1, col2 = tab.columns(2)

    # col1.dataframe(meta.head())
    # col2.dataframe(user.head())

    # TOP 10 REVENUE
    fig = px.bar(data_frame=meta.sort_values(by='revenue', ascending=False).head(10),
                 x='revenue',
                 y='original_title',
                 orientation='h',
                 hover_data=["release_date"],
                 color='vote_average',
                 color_continuous_scale='blues')

    col1.plotly_chart(fig,
                      use_container_width=True)

    # Correlation Matrix
    corr = meta.corr()
    fig = px.imshow(corr, color_continuous_scale='Blues')
    col2.plotly_chart(fig,
                      use_container_width=True)

    col1.divider()
    col2.divider()

    # TOP 10 MOVIES BY GENRES
    genres = ["Adventure", "Animation", "Children", "Comedy", "Fantasy", "Action", "Crime", "Thriller", "Romance"]
    selected_genre = col1.selectbox("Film kategorisi seçiniz.", genres)
    col1.markdown(f"Seçilen kategori: **{selected_genre}.**")

    col1.dataframe(meta.loc[meta.genres_x.str.contains(selected_genre), ['title',
                                                                         'genres_x',
                                                                         'release_date',
                                                                         'original_language',
                                                                         'vote_average']].sort_values(by='vote_average', ascending=False).head(10))

    # MOVIE COUNTS BY LANGUAGE

    selected_langs = col2.multiselect("Dil seçiniz.", meta.original_language.unique())
    grouped = meta.groupby("original_language").count().sort_values(by='title', ascending=False)

    if len(selected_langs) == 0:
        selected_langs = grouped.index[1:10]

    fig = px.bar(data_frame=grouped.loc[selected_langs, :], y='title', x=grouped.loc[selected_langs, :].index)
    col2.plotly_chart(fig, use_container_width=True)


def recommender(tab, meta, user):
    col1, col2, col3 = tab.columns([1, 2, 1])

    selected_movie = col2.selectbox("Film seçiniz.", meta.title.unique())
    recommendations = user.corrwith(user[selected_movie]).sort_values(ascending=False)[1:6]

    movie_one, movie_two, movie_three, movie_four, movie_five = tab.columns(5)

    for index, movie_col in enumerate([movie_one, movie_two, movie_three, movie_four, movie_five]):
        movie = meta.loc[meta.title == recommendations.index[index]]
        movie_col.subheader(movie.original_title.values[0])
        movie_col.image(get_image_from_imdb(movie.imdb_id.values[0]))
        movie_col.markdown(f"**{movie.vote_average.values[0]}**")


def main():
    meta, user = get_data()
    st.title(":blue[Movie] Recommendation :blue[System] 🎬")

    home_tab, vis_tab, recommender_tab = st.tabs(["Home", "Visualizations", "Recommender"])

    # Home Tab
    home(home_tab)

    # Visualizations Tab
    visualizations(vis_tab, meta, user)

    # Recommender Tab
    recommender(recommender_tab, meta, user)


if __name__ == "__main__":
    main()
