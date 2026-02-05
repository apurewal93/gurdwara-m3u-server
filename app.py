import os
import yt_dlp
from flask import Flask, Response, redirect, abort, request

app = Flask(__name__)

# --- CONFIGURATION ---
# Replace these with your actual Residential Proxy credentials
PROXY_USER = os.environ.get('PROXY_USER', 'spy9i4a1mq')
PROXY_PASS = os.environ.get('PROXY_PASS', '=h7CQoid02HLgjp9tn')
PROXY_HOST = os.environ.get('PROXY_HOST', 'gate.decodo.com') # e.g., IPRoyal or Decodo
PROXY_PORT = os.environ.get('PROXY_PORT', '10001')

RESIDENTIAL_PROXY = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

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

def get_working_link(youtube_url):
    ydl_opts = {
        'proxy': RESIDENTIAL_PROXY,
        'quiet': True,
        'no_warnings': True,
        # THE 2026 FIX: Disables the client YouTube is currently blocking
        'extractor_args': {
            'youtube': {
                'player_client': ['default', '-android_sdkless']
            }
        },
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            return info.get('url')
    except Exception as e:
        # This prevents the "Internal Server Error" screen
        print(f"CRITICAL ERROR: {str(e)}")
        return None

@app.route('/')
def home():
    return "IPTV Gateway Online. Playlist at /playlist.m3u"

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
        
    source_url = YOUTUBE_SOURCES[video_id]['url']
    working_link = get_working_link(source_url)
    
    if not working_link:
        return "Streaming Error: Check Proxy Credits", 503

    # Redirect the player to the final video URL
    return redirect(working_link)

if __name__ == "__main__":
    app.run()
