from flask import Flask, render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup
import re
import csv
import os

app = Flask(__name__)

def get_page_content(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return None

def parse_page(content, base_url):
    soup = BeautifulSoup(content, 'html.parser')
    data = []

    meta_description = soup.find('meta', attrs={'name': 'description'})
    meta_description = meta_description['content'] if meta_description else None

    main_header = soup.find('h1')
    main_header = main_header.get_text(strip=True) if main_header else None

    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href')
        text = link.get_text(strip=True)
        if not re.match(r'^https?://', href):
            href = requests.compat.urljoin(base_url, href)
        data.append({
            'link_text': text,
            'link_url': href,
            'meta_description': meta_description,
            'main_header': main_header
        })
    return data

def save_to_csv(data, filename='scraped_data.csv'):
    if not data:
        return None
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['link_text', 'link_url', 'meta_description', 'main_header']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    return filename

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        content = get_page_content(url)
        if content:
            data = parse_page(content, url)
            file_path = save_to_csv(data)
            return render_template('result.html', data=data, file_path=file_path)
        return render_template('index.html', error="Failed to fetch the content. Please check the URL.")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
