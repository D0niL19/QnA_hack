from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.http.models import PointStruct, VectorParams
import numpy as np
import tritonclient.grpc as grpcclient
import time

from fastapi_server.utils import get_embedding

qdrant_client = QdrantClient("qdrant", port=6333)


def connect_to_qdrant(max_attempts=5, delay=5):
    """
    Подключается к серверу Qdrant с заданным количеством попыток и задержкой.

    Args:
        max_attempts (int): Максимальное количество попыток подключения.
        delay (int): Задержка между попытками подключения в секундах.

    Returns:
        QdrantClient: Подключенный клиент Qdrant.

    Raises:
        ResponseHandlingException: Если не удается подключиться после максимального количества попыток.
    """
    for attempt in range(max_attempts):
        try:
            client = QdrantClient("qdrant", port=6333)
            client.get_collections()  # Проверка подключения
            return client
        except ResponseHandlingException:
            if attempt < max_attempts - 1:
                time.sleep(delay)
            else:
                raise


def create_qdrant_collection():
    """
    Создает коллекцию 'documents' в Qdrant, если она еще не существует.

    Raises:
        Exception: Если не удается получить информацию о коллекции.
    """
    try:
        qdrant_client.get_collection("documents")
    except Exception:
        qdrant_client.create_collection(
            "documents",
            vectors_config=VectorParams(size=768, distance="Cosine")
        )



def upload_to_qdrant(data, triton_client, collection_name='documents', ):
    """
    Загружает данные в коллекцию Qdrant, создавая эмбеддинги для каждого текста.

    Args:
        data (list[dict]): Список словарей с данными для загрузки.
        collection_name (str): Название коллекции для загрузки данных (по умолчанию 'documents').
    """
    vectors = []
    for item in data:
        text = item['text']
        embedding = get_embedding(text, "embedding", triton_client=triton_client)

        vectors.append(embedding)
        payload = {"text": text, "metadata": {"link": item["link"], "title": item["title"],
                                              "filename": item["filename"]}}  # Метаданные

        collection_info = qdrant_client.get_collection(collection_name="documents")
        point = PointStruct(id=collection_info.points_count + 1, vector=embedding, payload=payload)
        qdrant_client.upsert("documents", [point])


def split_text_into_chunks(text, chunk_size=512):
    """
    Разбивает текст на чанки заданного размера без использования скользящего окна.

    Args:
        text (str): Входной текст для разбиения.
        chunk_size (int): Максимальный размер чанка в символах.

    Returns:
        list[str]: Список чанков текста.
    """
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


def prepare_data_for_qdrant(documents, chunk_size=512):
    """
    Подготавливает данные для загрузки в Qdrant, разбивая текст документов на фрагменты.

    Args:
        documents (list[Document]): Список документов для подготовки данных.
        chunk_size (int): Максимальный размер чанка в символах.

    Returns:
        list[dict]: Список подготовленных данных для загрузки в Qdrant.
    """
    data = []
    for document in documents:
        chunks = split_text_into_chunks(document.text, chunk_size)
        for chunk in chunks:
            data.append({
                "text": chunk,
                "link": document.link,
                "filename": document.filename,
                "title": document.title,
            })
    return data


def refresh_qdrant():
    """
    Очищает коллекцию 'documents' в Qdrant и создает ее заново.
    """
    qdrant_client.delete_collection(collection_name="documents")
    create_qdrant_collection()
