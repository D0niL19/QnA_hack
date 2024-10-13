import asyncio
import numpy as np
import schedule
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import tritonclient.grpc as grpcclient
from .parser import parse_main_page, parse_links
from .pdf_utils import extract_documents_from_pdf, documents_data_from_pdf
from .qdrant_utils import upload_to_qdrant, get_embedding, create_qdrant_collection, qdrant_client, \
    prepare_data_for_qdrant, refresh_qdrant
from .utils import find_intervals
from .xlsx_utils import append_data, update_mark, init_workbook
from .models import DocumentRequest, QuestionRequest, AnswerResponse, MarkRequest

router = APIRouter()

file_path = "/app/fastapi_server/data.xlsx"

init_workbook()
create_qdrant_collection()

triton_client = grpcclient.InferenceServerClient(url="triton:8001")

prompt = "Ты ассистент РЖД,тебе предоставится контекст и вопрос на который тебе следует ответить, исходя из данного контекста. Напиши ответ, который отвечает на вопрос, используя только информацию, предоставленную в контексте,по возможностипиши название документа, откуда взята ифнормация для ответа, будь вежливым. Дайте ответ на русском языке. Если ответа нет или вопрос не по теме, то напиши: К сожалению я не знаю ответ на ваш вопрос, спросите что-то другое"


def schedule_updates():
    """
    Обновляет данные в Qdrant, извлекая информацию из PDF и загружая её.
    """
    data = documents_data_from_pdf()
    refresh_qdrant()
    upload_to_qdrant(data)


async def schedule_checker():
    """
    Проверяет и запускает задачи, запланированные с помощью schedule.
    """
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


schedule.every().day.at("02:00").do(schedule_updates)


@router.on_event("startup")
async def startup_event():
    """
    Запускает фоновую задачу для проверки планировщика при старте FastAPI приложения.
    """
    asyncio.create_task(schedule_checker())


@router.post("/add_document")
def add_document(document_request: DocumentRequest):
    """
    Добавляет документ в Qdrant, извлекая текст из PDF.

    :param document_request: запрос с текстом документа
    :return: сообщение о результате операции
    """
    text = document_request.text
    pdf_file = 'fastapi_server/doc.pdf'
    pages_text = extract_documents_from_pdf(pdf_file)
    data = prepare_data_for_qdrant(pages_text, chunk_size=512)
    upload_to_qdrant(data)
    return {"message": "Document added successfully"}


@router.post("/question", response_model=AnswerResponse)
async def ask_question(question_request: QuestionRequest):
    """
    Обрабатывает вопрос, извлекая контекст из базы данных и отправляя его в модель Triton для генерации ответа.

    :param question_request: запрос с вопросом
    :return: сгенерированный ответ на вопрос
    """
    question = question_request.question
    question_embedding = get_embedding(question, "embedding", triton_client=triton_client)

    search_results = qdrant_client.search("documents", question_embedding, limit=5)

    search_idx = [r.id for r in search_results]
    context_idx = find_intervals(search_idx)
    context_points = [qdrant_client.retrieve("documents", range(group[0], group[1] + 1)) for group in context_idx]

    context = ""
    for group_points in context_points:
        context += f" Название документа: {group_points[0].payload['metadata']['filename']}\n"
        context += f" Заголовок: {group_points[0].payload['metadata']['title']}\n"
        context += " ".join([point.payload["text"].strip() for point in group_points])

    input_tensors = [
        grpcclient.InferInput("text_input", [1], "BYTES"),
    ]

    full_request = f"Контекст:\n{context}\n\nВопрос:\n{question}\n\n"
    input_tensors[0].set_data_from_numpy(np.array([f'{prompt}____{full_request}'], dtype=object))

    results = triton_client.infer(model_name="generate", inputs=input_tensors)
    answer = results.as_numpy("text_output")[0].decode("utf-8")[:]

    append_data(question, answer, -1,
                f"{qdrant_client.retrieve('documents', search_idx)[0].payload['metadata']['filename']}")

    if answer.strip() == "":
        return AnswerResponse(
            answer="К сожалению, этой информации нет в моей базе данных, задайте другой вопрос и я отвечу на него")
    return AnswerResponse(answer=answer.strip())


@router.post("/update_mark", response_model=dict)
async def update_data(data: MarkRequest):
    """
    Обновляет оценку ответа для заданного вопроса.

    :param data: запрос с вопросом, ответом и оценкой
    :return: статус обновления
    """
    try:
        update_mark(data.question, data.answer, data.mark)
        return {"status": "mark updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download")
async def download_file():
    """
    Позволяет скачать файл с данными в формате .xlsx.

    :return: файл с данными или сообщение об ошибке, если файл не найден
    """
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            filename="data.xlsx")
    else:
        raise HTTPException(status_code=404, detail="File not found")


@router.post("/update")
async def manual_update():
    """
    Обновляет данные, загруженные с веб-сайта, и обновляет базу данных Qdrant.

    :return: сообщение об успешной операции или сообщение об ошибке
    """
    try:
        link_list = await parse_main_page()
        document_collection = await parse_links(link_list)
        data_web = document_collection.documents
        data = documents_data_from_pdf()

        upload_to_qdrant(data_web)
        return {"message": "База данных обновлена"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
