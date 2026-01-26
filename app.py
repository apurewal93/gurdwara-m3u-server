import time
import os  # Added to read environment variables
from flask import Flask, Response, redirect, abort, request
import yt_dlp

app = Flask(__name__)

# --- SOURCES ---
YOUTUBE_SOURCES = [
    {"title": "Darbar Sahib Gurdwara Amritsar", "url": "https://www.youtube.com/@SGPCSriAmritsar/live"},
    {"title": "Dashmesh Sikh Gurdwaras Calgary", "url": "https://www.youtube.com/@dashmeshculturecentrecalgary/live"},
    {"title": "Dukh Nivaran Sahib Gurdwara Surrey", "url": "https://www.youtube.com/@DukhNivaran/live"},
    {"title": "Ealing Gurdwara Uk", "url": "https://www.youtube.com/@EalingGurdwara/live"},
    {"title": "Gurdwara Dashmesh Darbar Surrey", "url": "https://www.youtube.com/@dasmeshdarbar3577/live"},
    {"title": "Gurdwara Dukh Niwaran Ludhiana", "url": "https://www.youtube.com/@gurdwaradukhniwaransahibldh/live"},
    {"title": "Gurdwaras Hazur Sahib", "url": "https://www.youtube.com/@hazursahiblivechannel1059/live"},
    {"title": "Gurdwara Singh Sabha Malton", "url": "https://www.youtube.com/@maltongurdwara/live"},
    {"title": "Gurdwara Singh Sabha Seattle", "url": "https://www.youtube.com/@SinghsabhaseattleWA/live"},
    {"title": "Gursikh Sabha Gurdwara Scarborough", "url": "https://www.youtube.com/@GursikhSabhaCanadaScarborough/live"},
    {"title": "Guru Nanak Sikh Gurdwara Delta-Surrey", "url": "https://www.youtube.com/@GuruNanakSikhGurdwara/live"},
    {"title": "Sri Guru Singh Sabha Edmonton", "url": "https://www.youtube.com/@gurdwarasirigurusinghsabha3386/live"}
]

url_cache = {}
CACHE_DURATION = 3600 

def get_automated_live_url(video_index):
    now = time.time()
    if video_index in url_cache and now < url_cache[video_index]['expires']:
        return url_cache[video_index]['url']

    source_url = YOUTUBE_SOURCES[video_index]['url']
    
    # --- PROXY CONFIGURATION ---
    # Looks for QUOTAGUARDSTATIC_URL in your Render settings
    proxy_url = os.environ.get('QUOTAGUARDSTATIC_URL')

    ydl_opts = {
        'format': 'best', 
        'quiet': True, 
        'no_warnings': True, 
        'playlist_items': '1',
        'proxy': proxy_url  # yt-dlp uses this to route traffic
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(source_url, download=False)
            direct_url = info.get('url')
            if direct_url:
                url_cache[video_index] = {'url': direct_url, 'expires': now + CACHE_DURATION}
                return direct_url
    except Exception as e:
        print(f"Extraction Error for {source_url}: {e}")
        return None

@app.route('/')
def home():
    return "Server is Live. Access /playlist.m3u for the list."

@app.route('/playlist.m3u')
def generate_m3u():
    base_url = request.host_url.rstrip('/') 
    m3u_lines = ["#EXTM3U"]
    for i, item in enumerate(YOUT
