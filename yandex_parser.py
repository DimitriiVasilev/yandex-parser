from bs4 import BeautifulSoup
from html2text import HTML2Text
import requests
import json
import sys


def get_urls(key_word, number_pages):
    url = f'https://yandex.ru/search/?text={key_word}&p=0'
    link_class = 'link link_theme_normal organic__url link_cropped_no i-bem'
    links = []
    page_number = 0
    pages_found = False
    while not pages_found:
        search_result = requests.get(url)
        soup = BeautifulSoup(search_result.text, features='html.parser')
        for tag in soup.find_all('a', class_=link_class):
            link = tag.get('href')
            links.append(link)
            if len(links) >= number_pages:
                pages_found = True
                break
        page_number += 1
        url = url[:-1] + str(page_number)
    return links


def handle_line(line):
    conditions_any = [
        line.endswith('.'),
        line.endswith('!'),
        line.endswith('?'),
        line.endswith(';'),
    ]
    conditions_all = [
        len(line) > 50,
        not line.startswith('$'),
        not line.startswith('#'),
        not line.startswith('&'),
    ]
    if any(conditions_any) and all(conditions_all):
        return line
    return None


def get_text(link):
    page = requests.get(link)
    parser = HTML2Text()
    parser.ignore_links = True
    parser.body_width = False
    parser.ignore_images = True
    try:
        text = parser.handle(page.text)
    except:
        return 'page skipped'
    result = ''
    for line in text.split('\n'):
        line = line.strip()
        # additional check (can be skipped)
        line = handle_line(line)
        if not line:
            continue
        result += line + '\n'
    return result


def get_json_pages(query, number):
    urls = get_urls(query, number)
    pages = []
    for url in urls:
        print(url)
        page_text = get_text(url)
        pages.append({url: page_text})
        print(page_text)
    return json.dumps(pages)


if __name__ == '__main__':
    # example:
    # get_json_pages('IBGroup', 5)
    get_json_pages(sys.argv[1], int(sys.argv[2]))
