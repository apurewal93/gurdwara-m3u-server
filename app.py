import time
from flask import Flask, Response, redirect, abort
import yt_dlp

app = Flask(__name__)

# CONFIGURATION
BASE_IP = "10.0.0.220" 
PORT = 8001

# --- PERMANENT GURDWARA SOURCES (Channel Handles) ---
# These links never change, even if the Gurdwara starts a new stream.
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
CACHE_DURATION = 3600 # Check for new stream every 1 hour

def get_automated_live_url(video_index):
    now = time.time()
    
    # Return cached link if it's fresh
    if video_index in url_cache and now < url_cache[video_index]['expires']:
        return url_cache[video_index]['url']

    source_url = YOUTUBE_SOURCES[video_index]['url']
    
    # yt-dlp options to find the active stream on a channel page
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'playlist_items': '1', # Grabs the current live video
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"[*] Auto-discovering live stream for: {YOUTUBE_SOURCES[video_index]['title']}")
            info = ydl.extract_info(source_url, download=False)
            
            # If channel has a live stream, yt-dlp finds the direct .m3u8 manifest
            direct_url = info.get('url')
            
            if direct_url:
                url_cache[video_index] = {'url': direct_url, 'expires': now + CACHE_DURATION}
                return direct_url
    except Exception as e:
        print(f"[!] {YOUTUBE_SOURCES[video_index]['title']} might be offline: {e}")
        return None

@app.route('/playlist.m3u')
def generate_m3u():
    base_url = f"http://{BASE_IP}:{PORT}" 
    m3u_lines = ["#EXTM3U"]
    for i, item in enumerate(YOUTUBE_SOURCES):
        m3u_lines.append(f'#EXTINF:-1 group-title="Gurdwaras" tvg-name="{item["title"]}", {item["title"]}')
        m3u_lines.append(f"{base_url}/play/{i}")
    return Response("\n".join(m3u_lines), mimetype='audio/x-mpegurl')

@app.route('/play/<int:video_id>')
def play(video_id):
    if video_id >= len(YOUTUBE_SOURCES):
        abort(404)
    
    # The script now automatically finds the new "watch" link if it changed
    direct_link = get_automated_live_url(video_id)
    if direct_link:
        return redirect(direct_link)
    else:
        return "Stream is currently offline. The channel link is still valid.", 500

if __name__ == '__main__':
    print(f"--- 100% Hands-Off M3U Server ---")
    print(f"Playlist: http://{BASE_IP}:{PORT}/playlist.m3u")
    app.run(host='0.0.0.0', port=PORT, debug=False)
