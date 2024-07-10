from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    search_term = data.get('search_term')
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        url = f"https://www.newegg.ca/p/pl?d={search_term}&N=4131"
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Will raise an HTTPError for bad responses
        page = response.text
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 400

    try:
        doc = BeautifulSoup(page, "html.parser")
        page_text = doc.find(class_="list-tool-pagination-text")
        if page_text:
            strong = page_text.find("strong")
            if strong:
                pages = int(str(strong).split("/")[-2].split(">")[-1][:-1])
            else:
                pages = 1
        else:
            pages = 1

        items_found = []

        for page_number in range(1, pages + 1):
            url = f"https://www.newegg.ca/p/pl?d={search_term}&N=4131&page={page_number}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Will raise an HTTPError for bad responses
            page = response.text
            doc = BeautifulSoup(page, "html.parser")

            div = doc.find("div", {"class": "item-cells-wrap"})
            if not div:
                continue

            items = div.find_all(text=re.compile(search_term, re.I))

            for item in items:
                parent = item.parent
                if parent.name != "a":
                    continue

                link = parent['href']
                next_parent = item.find_parent(class_="item-container")
                try:
                    price = next_parent.find(class_="price-current").find("strong").string
                    items_found.append({
                        "title": item,
                        "price": int(price.replace(",", "")),
                        "link": link
                    })
                except AttributeError:
                    pass

        items_found = sorted(items_found, key=lambda x: x['price'])

        return jsonify({'content': items_found})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
