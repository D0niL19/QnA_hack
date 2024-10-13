import os
import hashlib
import fitz  # PyMuPDF
from .models import Document

PDF_DIRECTORY = '/app/fastapi_server/example_pdf'


def extract_documents_from_pdf(pdf_file):
    """
    Извлекает текст из заданного PDF файла и организует его в список экземпляров Document.

    Args:
        pdf_file (str): Путь к PDF файлу.

    Returns:
        list[Document]: Список экземпляров Document, где каждый документ представляет собой страницу в PDF.
    """
    doc = fitz.open(pdf_file)
    documents = []
    filename = pdf_file.split('/')[-1]  # Имя файла без пути
    metadata = doc.metadata
    title = metadata.get("title", filename)  # Используем заголовок из метаданных или имя файла

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")

        document = Document(
            link=f"{page_num + 1}",
            filename=filename,
            title=title,
            text=text.strip()
        )
        documents.append(document)

    return documents


def get_file_hash(file_path):
    """
    Вычисляет MD5 хеш файла для обнаружения изменений.

    Args:
        file_path (str): Полный путь к файлу.

    Returns:
        str: MD5 хеш файла.
    """
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def documents_data_from_pdf():
    """
    Перебирает PDF файлы в заданном каталоге, проверяет, изменился ли их хеш, и извлекает текст
    из обновленных файлов.

    Returns:
        list[Document]: Список извлеченных экземпляров Document, или None, если обновленных файлов нет.
    """
    global pdf_hashes
    pdf_hashes = {}
    for pdf_file in os.listdir(PDF_DIRECTORY):
        if pdf_file.endswith('.pdf'):
            full_path = os.path.join(PDF_DIRECTORY, pdf_file)
            current_hash = get_file_hash(full_path)

            if pdf_file not in pdf_hashes or pdf_hashes[pdf_file] != current_hash:
                pdf_hashes[pdf_file] = current_hash  # Обновляем хеш
                return extract_documents_from_pdf(full_path)

    return None  # Возвращаем None, если нет обновленных файлов
