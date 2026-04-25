from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import re
import os

app = Flask(__name__)
CORS(app)

# --- FUNGSI SCRAPER (LOGIKA UTAMA) ---
def get_ddg_images(query):
    # Menambahkan akhiran xxx otomatis sesuai permintaan lu
    final_query = f"{query} xxx"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    try:
        # Step 1: Ambil VQD Token dari DuckDuckGo
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
        print(f"Error pada sistem: {e}")
        return []

# --- ROUTES (JALUR AKSES) ---

# Route Halaman Utama
@app.route('/')
def home():
    # Flask bakal nyari index.html di folder 'templates'
    return render_template('index.html')

# Route API Pencarian
@app.route('/api/search')
def api_search():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    
    print(f"[*] Menyerang target: {query}")
    data = get_ddg_images(query)
    return jsonify(data)

# Support untuk Vercel (Production)
if __name__ == '__main__':
    # Localhost pake port 5000
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
