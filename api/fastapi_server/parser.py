import aiohttp
import asyncio
from bs4 import BeautifulSoup
import math
global HEADER

from pydantic import BaseModel
from typing import List, Dict

class Document(BaseModel):
    link: str
    filename: str
    title: str
    text: str

class DocumentCollection(BaseModel):
    documents: List[Dict]


HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}
def split_text_into_chunks(text, chunk_size=128):
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= chunk_size:  # +1 для пробела
            if current_chunk:  # Если текущий чанк не пустой, добавляем пробел
                current_chunk += " "
            current_chunk += word
        else:
            if current_chunk:  # Если текущий чанк не пустой, добавляем его в список чанков
                chunks.append(current_chunk)
            current_chunk = word  # Начинаем новый чанк с текущего слова

    # Добавляем последний чанк, если он не пустой
    if current_chunk:
        chunks.append(current_chunk)

    return chunks



async def fetch(session, url):
    async with session.get(url, headers=HEADER) as response:
        return await response.text()


async def parse_page_html(response_text, docs_dict):
    soup = BeautifulSoup(response_text, 'html.parser')
    table = soup.find("div", {"class": "table-wrap"}).find("table")
    rows = table.find_all("tr")[1:]
    for row in rows:
        columns = row.find_all("td")

        doc_name_tag = columns[0].find("a")
        doc_name = doc_name_tag.get_text(strip=True)
        doc_link = "https://company.rzd.ru" + doc_name_tag['href']
        docs_dict[doc_name] = doc_link


async def parse_main_page():
    main_url = "https://company.rzd.ru/ru/9353/page/105103?f3174_pagesize=10&&f_sortdir=&rubrics=&date_begin=&doc_name=&doc_num=&text_search_type=0&date_end=&text_search=&doc_type=&source=&f_sortcol=&f3174_pagenumber=1"

    async with aiohttp.ClientSession() as session:
        response_text = await fetch(session, main_url)
        docs_dict = {}
        await parse_page_html(response_text, docs_dict)

        num_of_pages = math.ceil(int(
            BeautifulSoup(response_text, 'html.parser').find("div", {"class": "main__content"}).find("div",
                                                                                                     "docs-found print-hide").get_text(
                strip=True).split()[-1]) / 10)

        tasks = []
        for i in range(2, num_of_pages + 1):
            url = f"https://company.rzd.ru/ru/9353/page/105103?f3174_pagesize=10&&f_sortdir=&rubrics=&date_begin=&doc_name=&doc_num=&text_search_type=0&date_end=&text_search=&doc_type=&source=&f_sortcol=&f3174_pagenumber={i}"
            tasks.append(fetch(session, url))

        responses = await asyncio.gather(*tasks)

        for response_text in responses:
            await parse_page_html(response_text, docs_dict)

    return docs_dict


async def parse_links(links):
    document_collection = DocumentCollection(documents=[])

    async with aiohttp.ClientSession() as session:
        tasks = []
        for name, link in links.items():
            tasks.append(parse_link(session, link, name, document_collection))

        results = await asyncio.gather(*tasks)

        for name, data in zip(links.keys(), results):
            if data == dict():
                print(f"Ошибка при парсинге {name}")

    return document_collection



async def parse_link(session, link, name, document_collection):
    response_text = await fetch(session, link)
    soup = BeautifulSoup(response_text, 'html.parser')
    docs_box = soup.find_all("div", {"class": "docs box-wrap doc-tab"})
    docs_box_names = docs_box[0].find_all("div", {"class": "nav-part"})
    if docs_box_names:
        titles = []
        for docs_box_name in docs_box_names:
            title = docs_box_name.get_text(strip=True)
            if title != "Приложения":
                titles.append(title)
        contents = soup.find_all("div", {"class": "onePartTextOut_text"})
        for i in range(len(titles)):
            document_text = contents[i].get_text(separator=" ").strip()
            if document_text == "":
                continue
            chunks = split_text_into_chunks(document_text)
            for chunk in chunks:
                document_collection.documents.append(
                    dict(link=link, filename=name, title=titles[i], text=chunk)
                )
        return
    else:
        texts = docs_box[0].find_all("div", {"class": "static-content"})
        assert len(texts) == 1, f"ссылка: {link}"
        if texts[0].find_all("p", {"class": "upper"}):
            title = None
            new_text = texts[0].find_all("p")
            helps_text = ""
            for i in range(len(new_text)):
                if new_text[i].get("class"):
                    if title:
                        if helps_text == "":
                            continue
                        chunks = split_text_into_chunks(helps_text)
                        for chunk in chunks:
                            document_collection.documents.append(
                                dict(link=link, filename=name, title=title, text=chunk)
                            )
                        document_text = new_text[i].get_text(separator=" ").strip()
                        title = document_text
                        helps_text = ""

                    else:
                        document_text = new_text[i].get_text(separator=" ").strip()
                        title = document_text
                else:
                    helps_text += new_text[i].get_text(separator=" ").strip() + "\n"
            return
        else:
            for i in range(len(texts)):
                document_text = texts[i].get_text(separator=" ").strip()
                if document_text == "":
                    continue
                chunks = split_text_into_chunks(document_text)
                for chunk in chunks:
                    document_collection.documents.append(
                        dict(link=link, filename=name, title="", text=chunk)
                    )
        return
