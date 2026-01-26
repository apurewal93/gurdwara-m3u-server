import time
import os
import requests
from flask import Flask, Response, abort, request
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
CACHE_DURATION = 1200 # 20 minutes for high reliability

def get_automated_live_url(video_index):
    now = time.time()
    if video_index in url_cache and now < url_cache[video_index]['expires']:
        return url_cache[video_index]['url']

    source_url = YOUTUBE_SOURCES[video_index]['url']
    proxy_url = os.environ.get('QUOTAGUARDSTATIC_URL')

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'proxy': proxy_url,
        'cookiefile': 'cookies.txt',
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(source_url, download=False)
            # We want the M3U8 manifest specifically
            direct_url = info.get('manifest_url') or info.get('url')
            if direct_url:
                url_cache[video_index] = {'url': direct_url, 'expires': now + CACHE_DURATION}
                return direct_url
    except Exception as e:
        print(f"Extraction Error: {e}")
        return None

@app.route('/')
def home():
    return "IPTV Server Active. Use /playlist.m3u"

@app.route('/playlist.m3u')
def generate_m3u():
    base_url = request.host_url.rstrip('/') 
    m3u_lines = ["#EXTM3U"]
    for i, item in enumerate(YOUTUBE_SOURCES):
        m3u_lines.append(f'#EXTINF:-1 group-title="Gurdwaras", {item["title"]}')
        m3u_lines.append(f"{base_url}/play/{i}")
    return Response("\n".join(m3u_lines), mimetype='audio/x-mpegurl')

@app.route('/play/<int:video_id>')
def play(video_id):
    if video_id >= len(YOUTUBE_SOURCES):
        abort(404)
        
    direct_link = get_automated_live_url(video_id)
    if not direct_link:
        return "Stream extraction failed", 503

    # PROXY TUNNEL LOGIC: Fetch from YouTube, Send to User
    def stream_proxy():
        # We use a custom user-agent so YouTube thinks Render is a browser
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Pulling the data through Render's connection
        with requests.get(direct_link, stream=True, headers=headers, timeout=15) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=1024*64): # 64kb chunks
                yield chunk

    return Response(stream_proxy(), mimetype='application/x-mpegURL')
