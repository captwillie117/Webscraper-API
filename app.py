from flask import Flask, request, jsonify
import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"\+?\d[\d\-\(\) ]{7,}\d"
SOCIALS = {
    'facebook': r"(https?:\/\/(www\.)?facebook\.com\/[^\s\"\'<>]*)",
    'twitter': r"(https?:\/\/(www\.)?(twitter|x)\.com\/[^\s\"\'<>]*)",
    'instagram': r"(https?:\/\/(www\.)?instagram\.com\/[^\s\"\'<>]*)",
}

def save_to_file(data, url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('.', '_')
    filename = f"scrape_results_{domain}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return filename

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        emails = re.findall(EMAIL_REGEX, text)
        phones = [re.sub(r'\s+', '', p) for p in re.findall(PHONE_REGEX, text)]

        socials = {}
        for name, pattern in SOCIALS.items():
            links = re.findall(pattern, response.text, re.IGNORECASE)
            socials[name] = list(set([l[0] for l in links]))

        result = {
            "url": url,
            "emails": list(set(emails)),
            "phone_numbers": list(set(phones)),
            "socials": socials
        }

        filename = save_to_file(result, url)
        result["saved_to_file"] = filename

        return jsonify(result)

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)