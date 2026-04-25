from flask import Flask, request, jsonify, render_template
import requests
import re

app = Flask(__name__)

def get_ddg_images(query):
    final_query = f"{query} xxx"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    try:
        res = requests.post('https://duckduckgo.com/', data={'q': final_query}, headers=headers)
        vqd = re.search(r'vqd=([\d-]+)\&', res.text).group(1)
        params = {'l': 'wt-wt', 'o': 'json', 'q': final_query, 'vqd': vqd, 'f': ',,,,', 'p': '-1', 'kp': '-2'}
        img_res = requests.get('https://duckduckgo.com/i.js', headers=headers, params=params)
        return img_res.json().get('results', [])
    except:
        return []

# Router buat nampilin halaman utama
@app.route('/')
def home():
    return render_template('index.html')

# Router API (sekarang pake path relatif /search)
@app.route('/search')
def api_search():
    q = request.args.get('q')
    return jsonify(get_ddg_images(q)) if q else jsonify([])

if __name__ == '__main__':
    # Lu dengerin di 0.0.0.0 biar tunnel bisa masuk
    app.run(host='0.0.0.0', port=5000)
