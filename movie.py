import telebot
import requests
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from difflib import get_close_matches
import random

# Telegram Bot's API Token (Get it from BotFather)
API_TOKEN = '8181965642:AAGXxWUJ9sram6JEgRV5xj4czmyXyqnd4ZQ'  # Replace with your actual API token
bot = telebot.TeleBot(API_TOKEN)

# OMDb and TMDb API Keys
OMDB_API_KEY = '709e4d46'  # Replace with your actual OMDb API key
TMDB_API_KEY = '866dbcad5e6b708bd1f9e280f320d0a7'  # Replace with your actual TMDb API key

# Helper function: create keyboard
def main_menu_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    trending_button = KeyboardButton('/trending')
    random_button = KeyboardButton('/random')
    help_button = KeyboardButton('/help')
    markup.add(trending_button, random_button, help_button)
    return markup

# Function to fetch trending movies from TMDb
def get_trending_movies_from_tmdb():
    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            movies = data.get('results', [])
            
            if not movies:
                return "Sorry, no trending movies found at the moment."

            trending_movies = "🎥 *Trending Movies Right Now:*\n\n"
            for i, movie in enumerate(movies[:5], start=1):  # Show top 5 trending movies
                trending_movies += f"{i}. 🌟 _{movie['title']}_ ({movie['release_date']})\n"
            
            trending_movies += "\nCatch these top blockbusters now! 🎞️🍿"
            return trending_movies
        else:
            return "Sorry, could not fetch trending movies at the moment."
    
    except requests.exceptions.RequestException:
        return "Error fetching trending movies."

# Function to fetch currently releasing movies (in theaters) from TMDb
def get_releasing_movies_from_tmdb():
    url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=en-US&page=1"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            movies = data.get('results', [])
            
            if not movies:
                return "Sorry, no currently releasing movies found at the moment."

            releasing_movies = "🍿 *Movies Now Playing in Theaters:*\n\n"
            for i, movie in enumerate(movies[:5], start=1):  # Show top 5 movies now playing
                releasing_movies += f"{i}. 🎬 _{movie['title']}_ ({movie['release_date']})\n"
            
            releasing_movies += "\nDon’t miss out on these cinematic hits! 🎥"
            return releasing_movies
        else:
            return "Sorry, could not fetch currently releasing movies at the moment."
    
    except requests.exceptions.RequestException:
        return "Error fetching currently releasing movies."

# Welcome message handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    greeting_message = (f"🎬🎥 *Welcome to the Ultimate Movie Explorer!* 🎥🎬\n\n"
                        f"🎉 Hey there, *{message.from_user.first_name}*! 🎉\n\n"
                        "🌟 This bot is designed solely for movie enthusiasts! 🎥\n"
                        "🤖 I'm here to provide you with information about:\n"
                        "   - Trending movies 🎬\n"
                        "   - Movies currently releasing in theaters 🍿\n\n"
                        "Thank you for joining me on this cinematic journey! 🌍🎥\n\n")

    # Send the welcome message with keyboard
    bot.reply_to(message, greeting_message, reply_markup=main_menu_keyboard(), parse_mode='Markdown')

# OMDb API: Fetch movie information
def get_movie_info_from_omdb(movie_name):
    url = "http://www.omdbapi.com/"
    params = {
        't': movie_name,
        'apikey': OMDB_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == 'True':
                return data
            else:
                return None
        else:
            return None
    except requests.exceptions.RequestException:
        return None

# Suggesting corrections for movie names
def suggest_movie_name(movie_name):
    # A list of movie titles for suggestions
    available_movies = ["Inception", "The Matrix", "Interstellar", "Titanic", 
                        "The Shawshank Redemption", "Pulp Fiction", "Avengers: Endgame", 
                        "Joker", "La La Land", "The Dark Knight", "Forrest Gump", 
                        "Fight Club", "The Godfather", "Gladiator", "The Silence of the Lambs"]
    suggestions = get_close_matches(movie_name, available_movies, n=1)
    return suggestions[0] if suggestions else None

# Handling user input (movie name)
@bot.message_handler(func=lambda message: message.text not in ['/trending', '/random', '/help'])
def send_movie_details(message):
    movie_name = message.text.strip()
    if not movie_name:
        bot.reply_to(message, "⚠️ Please *enter a valid movie name* to get movie information.", parse_mode='Markdown')
        return

    bot.reply_to(message, "🔄 Fetching movie details, please wait...")

    movie_info = get_movie_info_from_omdb(movie_name)

    if movie_info:
        movie_details_message = (f"🎬 *{movie_info.get('Title', 'N/A')}* ({movie_info.get('Year', 'N/A')})\n\n"
                                 f"📝 *Plot:* {movie_info.get('Plot', 'N/A')}\n"
                                 f"⭐ *IMDb Rating:* {movie_info.get('imdbRating', 'N/A')}/10\n"
                                 f"📅 *Released:* {movie_info.get('Released', 'N/A')}\n"
                                 f"🎭 *Genre:* {movie_info.get('Genre', 'N/A')}\n"
                                 f"👥 *Actors:* {movie_info.get('Actors', 'N/A')}\n"
                                 f"🎥 *Director:* {movie_info.get('Director', 'N/A')}\n"
                                 f"🕰️ *Runtime:* {movie_info.get('Runtime', 'N/A')}\n"
                                 f"🗣️ *Language:* {movie_info.get('Language', 'N/A')}\n"
                                 f"🎥 [Watch Trailer](https://www.youtube.com/results?search_query={movie_info.get('Title', '').replace(' ', '+')}+trailer)\n")

        # Send the movie poster
        poster_url = movie_info.get('Poster')
        if poster_url and poster_url != "N/A":
            bot.send_photo(message.chat.id, poster_url)

        # Send movie details message
        bot.reply_to(message, movie_details_message, parse_mode='Markdown')

        # Unique greeting
        unique_greeting = (f"🌟 *Fantastic choice, {message.from_user.first_name}!* 🌟\n"
                           "🎉 You’ve just explored another cinematic gem! ✨🎥\n\n"
                           "What’s next on your watchlist? 🔍🍿\n"
                           "Let me know if you want to search for more movies, get trending picks, or dive into random suggestions! 🚀")
        bot.reply_to(message, unique_greeting, parse_mode='Markdown')

        # Encourage to search for another movie
        encouragement_message = "📽️ Feeling inspired? Why not search for another movie? 🎬✨"
        bot.send_message(message.chat.id, encouragement_message, parse_mode='Markdown')

    else:
        # Suggest a correct movie name
        suggested_name = suggest_movie_name(movie_name)
        if suggested_name:
            not_found_message = (f"🚨 *Oh no!* We couldn't find the movie *'{movie_name}'* 😱🎬\n\n"
                                 f"It seems you may have typed it incorrectly. Did you mean *'{suggested_name}'*? 🎬\n"
                                 "Keep searching, *Hollywood's full of hidden gems!* 💎🎬")
        else:
            not_found_message = (f"🚨 *Oh no!* We couldn't find the movie *'{movie_name}'* 😱🎬\n\n"
                                 "It seems like this title is *hiding in the shadows* or maybe lost in the archives! 😅🕵️‍♂️\n\n"
                                 "🔍 _Pro Tip_: Make sure you've typed the name correctly or try another movie!\n\n"
                                 "🎥 *Why not give these blockbusters a go?*\n"
                                 "   - 🌟 _Avengers: Endgame_\n"
                                 "   - 🎭 _Joker_\n"
                                 "   - 💖 _La La Land_\n"
                                 "   - 🚀 _Interstellar_\n\n"
                                 "Keep searching, *Hollywood's full of hidden gems!* 💎🎬")
        bot.reply_to(message, not_found_message, parse_mode='Markdown')

# Help command handler
@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = (f"🆘 *Help Section* 🆘\n\n"
                    "Here are the commands you can use:\n\n"
                    "1. `/trending` - Get the list of trending movies 🎬\n"
                    "2. `/random` - Get a random movie suggestion 🍿\n"
                    "3. *Just type the name of any movie* to get information about it! 🎥\n\n"
                    "🎥 Feel free to ask about any movie you want to know! 🌟")
    bot.reply_to(message, help_message, parse_mode='Markdown')

# Random movie suggestion handler
@bot.message_handler(commands=['random'])
def send_random_movie(message):
    random_movies = ["Inception", "The Matrix", "Interstellar", "Titanic", 
                     "The Shawshank Redemption", "Pulp Fiction", "Avengers: Endgame", 
                     "Joker", "La La Land", "The Dark Knight", "Forrest Gump", 
                     "Fight Club", "The Godfather", "Gladiator", "The Silence of the Lambs"]
    
    random_movie = random.choice(random_movies)
    movie_info = get_movie_info_from_omdb(random_movie)

    if movie_info:
        movie_details_message = (f"🎬 *{movie_info.get('Title', 'N/A')}* ({movie_info.get('Year', 'N/A')})\n\n"
                                 f"📝 *Plot:* {movie_info.get('Plot', 'N/A')}\n"
                                 f"⭐ *IMDb Rating:* {movie_info.get('imdbRating', 'N/A')}/10\n"
                                 f"📅 *Released:* {movie_info.get('Released', 'N/A')}\n"
                                 f"🎭 *Genre:* {movie_info.get('Genre', 'N/A')}\n"
                                 f"👥 *Actors:* {movie_info.get('Actors', 'N/A')}\n"
                                 f"🎥 *Director:* {movie_info.get('Director', 'N/A')}\n"
                                 f"🕰️ *Runtime:* {movie_info.get('Runtime', 'N/A')}\n"
                                 f"🗣️ *Language:* {movie_info.get('Language', 'N/A')}\n"
                                 f"🎥 [Watch Trailer](https://www.youtube.com/results?search_query={movie_info.get('Title', '').replace(' ', '+')}+trailer)\n")

        # Send the movie poster
        poster_url = movie_info.get('Poster')
        if poster_url and poster_url != "N/A":
            bot.send_photo(message.chat.id, poster_url)
            

        # Send movie details message
        bot.reply_to(message, movie_details_message, parse_mode='Markdown')
        

        # Unique greeting
        unique_greeting = (f"🌟 *Fantastic choice, {message.from_user.first_name}!* 🌟\n"
                           "🎉 You’ve just explored another cinematic gem! ✨🎥\n\n"
                           "What’s next on your watchlist? 🔍🍿\n"
                           "Let me know if you want to search for more movies, get trending picks, or dive into random suggestions! 🚀")
        bot.reply_to(message, unique_greeting, parse_mode='Markdown')

    else:
        bot.reply_to(message, "Sorry, I couldn't fetch details for the random movie. 😅")

# Trending movies command handler
@bot.message_handler(commands=['trending'])
def send_trending_movies(message):
    trending_movies_message = get_trending_movies_from_tmdb()
    bot.reply_to(message, trending_movies_message, parse_mode='Markdown')

# Running the bot
if __name__ == "__main__":
    bot.polling(none_stop=True)
