import pickle
import streamlit as st
import requests
import pandas as pd
import numpy as np
import time

# -------------------------------
# ⚙️ PAGE CONFIGURATION
# -------------------------------
st.set_page_config(layout="wide")

# -------------------------------
# 💅 GLOBAL CSS STYLING
# -------------------------------
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #ffffff;
            font-family: 'Trebuchet MS', sans-serif;
        }

        @keyframes gradientBG {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url("https://www.transparenttextures.com/patterns/asfalt-light.png");
            opacity: 0.15;
            z-index: -1;
        }

        header[data-testid="stHeader"] {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            height: 65px;
            color: white;
            box-shadow: 0 4px 20px rgba(0,0,0,0.6);
        }
        header[data-testid="stHeader"] div {
            background: transparent !important;
        }

        header[data-testid="stHeader"]::before {
            content: "🍿🎬 Movie Recommender System";
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
            text-shadow: 0px 0px 10px rgba(255,255,255,0.7);
        }

        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}

        h1, h2, h3 {
            color: #fff;
            text-align: center;
            font-weight: bold;
            text-shadow: 0px 0px 20px rgba(255,255,255,0.8);
        }

        .stSelectbox label, .stButton>button {
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
        }
        .stButton>button {
            background: linear-gradient(135deg, #ff512f, #dd2476);
            border-radius: 12px;
            padding: 10px 20px;
            border: none;
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease-in-out;
            box-shadow: 0px 4px 15px rgba(255,82,47,0.6);
        }
        .stButton>button:hover {
            transform: scale(1.08);
            background: linear-gradient(135deg, #dd2476, #ff512f);
            box-shadow: 0px 6px 20px rgba(221,36,118,0.9);
        }

        img {
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.9);
            height: 300px !important;
            width: 100% !important;
            object-fit: cover;
        }

        .movie-title {
            text-align: center;
            font-size: 17px;
            font-weight: bold;
            margin-top: 5px;
            color: #fff;
            text-shadow: 2px 2px 8px black;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# 🎬 APP TITLE
# -------------------------------
st.markdown("<h1>🍿🎬 Movie Recommender System</h1>", unsafe_allow_html=True)


# -------------------------------
# 📦 CACHED DATA LOAD
# -------------------------------
@st.cache_resource
def load_data():
    movies = pickle.load(open('model/movie_list.pkl', 'rb'))
    movies = movies.rename(columns={'id': 'movie_id'})
    similarity = pickle.load(open('model/similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()


# -------------------------------
# 🖼️ CACHED POSTER FETCH
# -------------------------------
@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8772dfc69b99d1fa093d7284ce3604f6&language=en-US"
    try:
        data = requests.get(url, timeout=5).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750?text=No+Image"


# -------------------------------
# ⚡ OPTIMIZED RECOMMENDATION
# -------------------------------
@st.cache_data
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]

    # ✅ Faster: Only get top 6 indices (instead of sorting everything)
    top_indices = np.argpartition(distances, -6)[-6:]
    top_indices = top_indices[np.argsort(distances[top_indices])[::-1]]

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in top_indices:
        if i != index:
            movie_id = movies.iloc[i]['movie_id']
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i]['title'])

    return recommended_movie_names[:5], recommended_movie_posters[:5]


# -------------------------------
# 🎥 MOVIE SELECTION + LOADER
# -------------------------------
movie_list = movies['title'].values
selected_movie = st.selectbox("🎥 Pick a Movie", movie_list)

if st.button('🎞️ Show Recommendations'):
    # Use spinner and progress bar for smooth loading
    with st.spinner("🔄 Please wait!"):
        progress = st.progress(0)
        for percent_complete in range(0, 100, 10):
            time.sleep(0.05)
            progress.progress(percent_complete + 10)

        # 🧠 Important: Capture output inside spinner, don't display it automatically
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

        # Clear the progress bar once done
        progress.empty()

    cols = st.columns(5)
    for col, name, poster in zip(cols, recommended_movie_names, recommended_movie_posters):
        with col:
            st.image(poster)
            st.markdown(f"<div class='movie-title'>{name}</div>", unsafe_allow_html=True)
