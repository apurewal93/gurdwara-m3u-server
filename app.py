import os
import yt_dlp
import logging
from flask import Flask, Response, redirect, abort, request

# Setup logging - check the 'Logs' tab on Render to see errors
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# --- CONFIGURATION ---
PROXY_USER = os.environ.get('PROXY_USER', 'spy9i4a1mq')
PROXY_PASS = os.environ.get('PROXY_PASS', '=h7CQoid02HLgjp9tn')
PROXY_HOST = os.environ.get('PROXY_HOST', 'gate.decodo.com')
PROXY_PORT = os.environ.get('PROXY_PORT', '10001')

RESIDENTIAL_PROXY = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

YOUTUBE_SOURCES = [
    {"title": "Darbar Sahib Amritsar", "url": "https://www.youtube.com/@SGPCSriAmritsar/live"},
    {"title": "Dashmesh Calgary", "url": "https://www.youtube.com/@dashmeshculturecentrecalgary/live"},
    {"title": "Dukh Nivaran Surrey", "url": "https://www.youtube.com/@DukhNivaran/live"},
    {"title": "Ealing Gurdwara Uk", "url": "https://www.youtube.com/@EalingGurdwara/live"},
    {"title": "Dashmesh Darbar Surrey", "url": "https://www.youtube.com/@dasmeshdarbar3577/live"},
    {"title": "Dukh Niwaran Ludhiana", "url": "https://www.youtube.com/@gurdwaradukhniwaransahibldh/live"},
    {"title": "Hazur Sahib", "url": "https://www.youtube.com/@hazursahiblivechannel1059/live"},
    {"title": "Singh Sabha Malton", "url": "https://www.youtube.com/@maltongurdwara/live"},
    {"title": "Singh Sabha Seattle", "url": "https://www.youtube.com/@SinghsabhaseattleWA/live"},
    {"title": "Gursikh Sabha Scarborough", "url": "https://www.youtube.com/@GursikhSabhaCanadaScarborough/live"},
    {"title": "Guru Nanak Delta-Surrey", "url": "https://www.youtube.com/@GuruNanakSikhGurdwara/live"},
    {"title": "Singh Sabha Edmonton", "url": "https://www.youtube.com/@gurdwarasirigurusinghsabha3386/live"}
]

def get_working_link(youtube_url):
    ydl_opts = {
        'proxy': RESIDENTIAL_PROXY,
        'quiet': True,
        'no_warnings': True,
        # Ensures 720p with audio/video combined
        'format': 'best[height<=720]',
        'extractor_args': {
            'youtube': {
                # FEB 2026 FIX: Use default but subtract the broken android client
                'player_client': ['default', '-android_sdkless'],
                'skip': ['webpage', 'hls_manifest'],
            }
        },
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'socket_timeout': 10  # Prevents Render from hanging forever
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ONLY CALL THIS ONCE
            info = ydl.extract_info(youtube_url, download=False, process=True)
            return info.get('url')
    except Exception as e:
        logging.error(f"YouTube Extraction Error: {e}")
        return None

@app.route('/')
def home():
    return "Gurdwara Gateway Online. Playlist: /playlist.m3u"

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
    if video_id < 0 or video_id >= len(YOUTUBE_SOURCES):
        abort(404)
        
    source_url = YOUTUBE_SOURCES[video_id]['url']
    working_link = get_working_link(source_url)
    
    if not working_link:
        return "Extraction failed. Check logs.", 503

    return redirect(working_link)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
