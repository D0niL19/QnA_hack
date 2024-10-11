import time

import numpy as np
from fastapi import APIRouter, HTTPException
import tritonclient.grpc as grpcclient
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.http.models import PointStruct, VectorParams

from fastapi_server.pdf import extract_text_from_pdf, prepare_data_for_qdrant

router = APIRouter()

triton_client = grpcclient.InferenceServerClient(url="localhost:8001")

def connect_to_qdrant(max_attempts=5, delay=5):
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

qdrant_client = connect_to_qdrant()
# qdrant_client = QdrantClient("qdrant", port=6333)

prompt = "Here is a question that you should answer based on the given context. Write a response that answers the question using only information provided in the context. Provide the answer in Russia."



class DocumentRequest(BaseModel):
    text: str

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str

def get_embedding(text: str, model_name: str):
    input_tensors = [grpcclient.InferInput("text_input", [1], "BYTES")]
    input_tensors[0].set_data_from_numpy(np.array([text], dtype=object))

    results = triton_client.infer(model_name=model_name, inputs=input_tensors)
    embedding = results.as_numpy("text_output")[0]
    return embedding


def upload_to_qdrant(data, collection_name='documents'):
    vectors = []
    payloads = []

    for item in data:
        text = item['text']
        # vector = model.encode(text).tolist()  # Преобразование текста в вектор
        embedding = get_embedding(text, "embedding")
        vectors.append(embedding)
        payloads.append(item['metadata'])  # Метаданные (например, номер страницы)

    # Загрузка векторов и данных в Qdrant
    qdrant_client.upload_collection(
        collection_name=collection_name,
        vectors=vectors,
        payload=payloads,
        ids=None  # Если не указывается, Qdrant автоматически сгенерирует ID
    )


@router.post("/add_document")
def add_document(document_request: DocumentRequest):
    text = document_request.text

    pdf_file = '/home/d0nil/PythonProjects/QnA/fastapi_server/Коллективный договор.pdf'  # Укажите путь к вашему PDF файлу

    # Извлекаем текст из PDF
    pages_text = extract_text_from_pdf(pdf_file)
    data = prepare_data_for_qdrant(pages_text, chunk_size=200)

    print(data)

    # upload_to_qdrant(data)

    # collection_info = qdrant_client.get_collection(collection_name="documents")

    # point = PointStruct(id=collection_info.points_count+1,vector=embedding, payload={"text": text})
    # qdrant_client.upsert("documents", [point])
    return {"message": "Document added successfully"}

@router.post("/question", response_model=AnswerResponse)
async def ask_question(question_request: QuestionRequest):
    question = question_request.question
    question_embedding = await get_embedding(question, "embedding")

    search_results = qdrant_client.search("documents", question_embedding, limit=5)
    context = " ".join([result.payload["text"] for result in search_results])

    input_tensors = [
        grpcclient.InferInput("text_input", [1], "BYTES"),
    ]
    input_tensors[0].set_data_from_numpy(np.array([f"{context} + {question}"], dtype=object))

    results = triton_client.infer(model_name="generate", inputs=input_tensors)
    answer = results.as_numpy("text_output")[0].decode("utf-8")

    return AnswerResponse(answer=answer)

# Ensure Qdrant collection exists
def create_qdrant_collection():
    try:
        qdrant_client.get_collection("documents")
    except Exception:
         qdrant_client.create_collection(
            "documents",
            vectors_config=VectorParams(size=768, distance="Cosine")
        )

create_qdrant_collection()

