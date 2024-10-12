import fitz  # PyMuPDF
import os
import hashlib
import schedule
import time

from fastapi_server.routes import upload_to_qdrant

PDF_DIRECTORY = '/app/example_pdf'  # Замените на ваш путь к папке с PDF
pdf_hashes = {}  # Словарь для хранения хешей PDF-файлов

# Шаг 1: Извлечение текста из PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    pages_text = []

    # Итерация по страницам PDF
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        pages_text.append({"page_num": page_num + 1, "text": text})

    return pages_text

# Шаг 2: Разбиение текста на фрагменты по количеству символов без скользящего окна
def split_text_into_chunks(text, chunk_size=512):
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        # Проверка, помещается ли текущее слово в текущий чанк
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

# Шаг 3: Подготовка данных для Qdrant (разбиение на страницы и фрагменты)
def prepare_data_for_qdrant(pages_text, chunk_size=200):
    data = []
    for page in pages_text:
        chunks = split_text_into_chunks(page['text'], chunk_size)
        for chunk in chunks:
            data.append({
                "text": chunk,
                "metadata": {
                    "page_num": page['page_num']
                }
            })
    return data

def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def update_data():
    global pdf_hashes

    for pdf_file in os.listdir(PDF_DIRECTORY):
        if pdf_file.endswith('.pdf'):
            full_path = os.path.join(PDF_DIRECTORY, pdf_file)
            current_hash = get_file_hash(full_path)

            if pdf_file not in pdf_hashes or pdf_hashes[pdf_file] != current_hash:
                pdf_hashes[pdf_file] = current_hash  # Обновляем хеш
                pages_text = extract_text_from_pdf(full_path)

                data = prepare_data_for_qdrant(pages_text)

                upload_to_qdrant(data)

                # Здесь можно добавить код для отправки данных в Qdrant
                # Например, с использованием requests
                # requests.post(f"{qdrant_url}/collections/your_collection/points", json=data)

# Функция для регулярного обновления в 2 часа ночи каждый день
def schedule_updates():
    schedule.every().day.at("02:00").do(update_data)  # Ежедневное обновление в 2 часа ночи
    while True:
        schedule.run_pending()
        time.sleep(1)
