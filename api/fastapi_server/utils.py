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
