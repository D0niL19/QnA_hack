from pydantic import BaseModel

class Document(BaseModel):
    link: str  # Ссылка на документ
    filename: str  # Имя файла документа
    title: str  # Заголовок документа
    text: str  # Текстовое содержимое документа

class DocumentRequest(BaseModel):
    text: str  # Текст документа для обработки или добавления

class QuestionRequest(BaseModel):
    question: str  # Вопрос, на который нужно получить ответ

class AnswerResponse(BaseModel):
    answer: str  # Ответ на заданный вопрос

class MarkRequest(BaseModel):
    question: str  # Вопрос, к которому относится оценка
    answer: str  # Ответ, к которому относится оценка
    mark: int  # Оценка, данная ответу (например, по шкале от 1 до 5)
