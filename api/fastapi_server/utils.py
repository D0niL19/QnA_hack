import numpy as np
from fastapi_server.router import grpcclient


def find_intervals(indexies):
    """
    Находит интервалы индексов с учетом значений на -2, -1, +1 и +2 от каждого исходного индекса.

    Для каждого индекса добавляются значения на 2 позиции влево и вправо, после чего находят
    последовательные смежные интервалы.

    :param indexies: Список исходных индексов
    :return: Список интервалов в виде пар [начало, конец]
    """
    numbers = []
    # Создание расширенного списка индексов с добавлением -2, -1, +1, +2
    for i in indexies:
        numbers += [i - 2, i - 1, i, i + 1, i + 2]

    # Удаление дубликатов и сортировка
    numbers = list(set(numbers))
    numbers.sort()

    intervals = []
    start = numbers[0]

    # Поиск последовательных интервалов
    for i in range(1, len(numbers)):
        # Если текущее число не является последовательным с предыдущим, завершаем интервал
        if numbers[i] != numbers[i - 1] + 1:
            intervals.append([start, numbers[i - 1]])
            start = numbers[i]

    # Добавление последнего интервала
    intervals.append([start, numbers[-1]])

    return intervals

def get_embedding(text: str, model_name: str, triton_client):
    """
    Получает векторное представление (эмбеддинг) текста с использованием модели на сервере Triton.

    Args:
        text (str): Входной текст для получения эмбеддинга.
        model_name (str): Название модели для получения эмбеддинга.
        triton_client: Клиент Triton для выполнения запроса.

    Returns:
        np.ndarray: Эмбеддинг текста.
    """
    input_tensors = [grpcclient.InferInput("text_input", [1], "BYTES")]
    input_tensors[0].set_data_from_numpy(np.array([text], dtype=object))

    results = triton_client.infer(model_name=model_name, inputs=input_tensors)
    return results.as_numpy("text_output")[0]