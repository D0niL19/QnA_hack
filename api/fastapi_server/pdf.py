import fitz  # PyMuPDF

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
def split_text_into_chunks(text, chunk_size=200):
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



# Пример использования
if __name__ == "__main__":
    pdf_file = 'Коллективный договор.pdf'  # Укажите путь к вашему PDF файлу

    # Извлекаем текст из PDF
    pages_text = extract_text_from_pdf(pdf_file)

    # Разбиваем текст на фрагменты и готовим для Qdrant
    data = prepare_data_for_qdrant(pages_text, chunk_size=200)

    print(data)

    # Загружаем данные и векторы в Qdrant
    # upload_to_qdrant(data, collection_name='pdf_collection')

    print("PDF успешно обработан и загружен в Qdrant.")