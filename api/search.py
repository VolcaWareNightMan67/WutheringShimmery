from flask import Flask, request, jsonify
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

@app.route('/api/search')
def search():
    q = request.args.get('q')
    return jsonify(get_ddg_images(q))

# Vercel butuh handler ini
def handler(request):
    return app(request)
