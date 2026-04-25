from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import re
import os

app = Flask(__name__)
CORS(app)

# --- FUNGSI FOTO (LOGIKA ASLI DARI KODE LAMA LU) ---
def get_ddg_images(query):
    # Menambahkan akhiran xxx otomatis sesuai permintaan lu
    final_query = f"{query} xxx"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    try:
        # Step 1: Ambil VQD Token dari DuckDuckGo (PAKAI POST SESUAI KODE LAMA)
        res = requests.post('https://duckduckgo.com/', data={'q': final_query}, headers=headers, timeout=10)
        vqd_match = re.search(r'vqd=([\d-]+)\&', res.text)
        
        if not vqd_match:
            return []
        
        vqd = vqd_match.group(1)

        # Step 2: Request data gambar dengan filter dimatikan (kp=-2, p=-1)
        search_url = 'https://duckduckgo.com/i.js'
        params = {
            'l': 'wt-wt',
            'o': 'json',
            'q': final_query,
            'vqd': vqd,
            'f': ',,,,',
            'p': '-1',    # Gak pake filter sama sekali
            'kp': '-2'    # SafeSearch Off
        }

        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        data = response.json()
        
        # Ambil hasil dan susun datanya
        results = []
        for result in data.get('results', []):
            results.append({
                'image': result.get('image'),
                'title': result.get('title'),
                'source': result.get('url') # URL asal website-nya
            })
        return results

    except Exception as e:
        print(f"Error pada sistem foto: {e}")
        return []

# --- FUNGSI VIDEO (LOGIKA YANG SUDAH MANTAP) ---
def get_eporner_videos(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    api_url = f"https://www.eporner.com/api/v2/video/search/?query={query}&per_page=30&thumbsize=big&order=relevance"
    
    try:
        res = requests.get(api_url, headers=headers, timeout=15)
        data = res.json()
        videos = []
        for v in data.get('videos', []):
            try:
                # Fix durasi (zfill) biar kaga crash
                m = str(v.get('length_min', 0))
                s = str(v.get('length_sec', 0)).zfill(2)
                
                videos.append({
                    'title': v['title'],
                    'embed': v['embed'].replace('http://', 'https://'),
                    'thumbnail': v['default_thumb']['src'].replace('http://', 'https://'),
                    'duration': f"{m}:{s}",
                    'views': v.get('views', '0'),
                    'rate': v.get('rate', '5.0'),
                    'url': v['url']
                })
            except:
                continue
        return videos
    except Exception as e:
        print(f"Error pada sistem video: {e}")
        return []

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

# API Pencarian Foto (Pakai Logika Lama Lu)
@app.route('/api/search')
def api_search():
    query = request.args.get('q')
    if not query: return jsonify([])
    print(f"[*] Menyerang target (FOTO): {query}")
    data = get_ddg_images(query)
    return jsonify(data)

# API Pencarian Video (Pakai Logika Mantap)
@app.route('/api/videos')
def api_videos():
    query = request.args.get('q')
    if not query: return jsonify([])
    print(f"[*] Menyerang target (VIDEO): {query}")
    data = get_eporner_videos(query)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
