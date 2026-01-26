import time
from flask import Flask, Response, redirect, abort, request

app = Flask(__name__)

# --- SOURCES ---
# Using the standard channel live URLs. 
YOUTUBE_SOURCES = [
    {"title": "Darbar Sahib Gurdwara Amritsar", "url": "https://www.youtube.com/SGPCSriAmritsar/live"},
    {"title": "Dashmesh Sikh Gurdwaras Calgary", "url": "https://www.youtube.com/dashmeshculturecentrecalgary/live"},
    {"title": "Dukh Nivaran Sahib Gurdwara Surrey", "url": "https://www.youtube.com/DukhNivaran/live"},
    {"title": "Ealing Gurdwara Uk", "url": "https://www.youtube.com/EalingGurdwara/live"},
    {"title": "Gurdwara Dashmesh Darbar Surrey", "url": "https://www.youtube.com/dasmeshdarbar3577/live"},
    {"title": "Gurdwara Dukh Niwaran Ludhiana", "url": "https://www.youtube.com/gurdwaradukhniwaransahibldh/live"},
    {"title": "Gurdwaras Hazur Sahib", "url": "https://www.youtube.com/hazursahiblivechannel1059/live"},
    {"title": "Gurdwara Singh Sabha Malton", "url": "https://www.youtube.com/maltongurdwara/live"},
    {"title": "Gurdwara Singh Sabha Seattle", "url": "https://www.youtube.com/SinghsabhaseattleWA/live"},
    {"title": "Gursikh Sabha Gurdwara Scarborough", "url": "https://www.youtube.com/GursikhSabhaCanadaScarborough/live"},
    {"title": "Guru Nanak Sikh Gurdwara Delta-Surrey", "url": "https://www.youtube.com/GuruNanakSikhGurdwara/live"},
    {"title": "Sri Guru Singh Sabha Edmonton", "url": "https://www.youtube.com/gurdwarasirigurusinghsabha3386/live"}
]

@app.route('/')
def home():
    return "IPTV Gateway Active. Access your playlist at /playlist.m3u"

@app.route('/playlist.m3u')
def generate_m3u():
    # Detects the host URL automatically (e.g., your-app.onrender.com)
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
        
    # Redirect directly to the YouTube Live URL.
    # This allows the PLAYER (VLC/Phone) to handle the extraction.
    target_url = YOUTUBE_SOURCES[video_id]['url']
    return redirect(target_url)

# Gunicorn runs the 'app' object directly on Render/Railway
