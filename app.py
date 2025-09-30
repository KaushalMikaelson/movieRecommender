import pickle
import streamlit as st
import requests
import pandas as pd

# --- Set page wide so posters cover full screen ---
st.set_page_config(layout="wide")

# --- Global CSS Styling ---
st.markdown("""
    <style>
        /* Vibrant gradient background */
        .stApp {
            background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #ffffff;
            font-family: 'Trebuchet MS', sans-serif;
        }

        /* Animate gradient for dynamic effect */
        @keyframes gradientBG {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        /* Film grain overlay */
        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url("https://www.transparenttextures.com/patterns/asfalt-light.png");
            opacity: 0.15;
            z-index: -1;
        }

        /* --- HEADER / NAVBAR --- */
        header[data-testid="stHeader"] {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            height: 65px;
            color: white;
            box-shadow: 0 4px 20px rgba(0,0,0,0.6);
        }
        header[data-testid="stHeader"] div {
            background: transparent !important;
        }

        /* Inject Title Text inside Header on the LEFT */
        header[data-testid="stHeader"]::before {
            content: "🍿🎬 Movie Recommender System";
            position: absolute;
            left: 20px;   /* distance from left edge */
            top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
            text-shadow: 0px 0px 10px rgba(255,255,255,0.7);
        }

        /* Hide default Streamlit footer/menu */
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}

        /* Body Header Titles */
        h1, h2, h3 {
            color: #fff;
            text-align: center;
            font-weight: bold;
            text-shadow: 0px 0px 20px rgba(255,255,255,0.8);
        }

        /* Dropdown + Button */
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

        /* Poster styling (bigger and full column) */
        img {
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.9);
            height: 300px !important;   /* taller movie cards */
            width: 100% !important;     /* make image fill full column */
            object-fit: cover;          /* no squish, crop nicely */
        }

        /* Movie title under posters */
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

# --- App Main Title (kept in the main screen too) ---
st.markdown("<h1>🍿🎬 Movie Recommender System</h1>", unsafe_allow_html=True)

# --- Fetch poster from TMDb ---
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

# --- Recommend movies ---
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]]['movie_id']
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]]['title'])
    return recommended_movie_names, recommended_movie_posters

# --- Load movie data + similarity matrix ---
movies = pickle.load(open('model/movie_list.pkl', 'rb'))
movies = movies.rename(columns={'id': 'movie_id'})
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

# --- Movie Selection ---
movie_list = movies['title'].values
selected_movie = st.selectbox("🎥 Pick a Movie", movie_list)

# --- Show Recommendations (5 posters across full page) ---
if st.button('🎞️ Show Recommendations'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    # 5 equal-width columns spanning full page
    cols = st.columns(5)

    for col, name, poster in zip(cols, recommended_movie_names, recommended_movie_posters):
        with col:
            st.image(poster, width="stretch")   # new API (replaces use_container_width)
            st.markdown(f"<div class='movie-title'>{name}</div>", unsafe_allow_html=True)