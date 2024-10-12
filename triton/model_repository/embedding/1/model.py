import os

os.environ["TRANSFORMERS_CACHE"] = "/opt/tritonserver/model_repository/embedding/hf-cache"

import json

import numpy as np
import torch
import triton_python_backend_utils as pb_utils
from transformers import AutoTokenizer, AutoModel


class TritonPythonModel:
    def initialize(self, args):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2').to(self.device)
        print(self.model.device)

    def execute(self, requests):
        responses = []
        for request in requests:
            # Assume input named "prompt", specified in autocomplete above
            input_tensor = pb_utils.get_input_tensor_by_name(request, "text_input")
            prompt = input_tensor.as_numpy()[0].decode("utf-8")

            response = self.get_question_embed(prompt)
            responses.append(response)

        return responses

    def mean_pooling(self, model_output, attention_mask):

        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def get_question_embed(self, prompt):
        if isinstance(prompt, str):
            prompt = [prompt]

        # Токенизируем входной текст
        encoded_input = self.tokenizer(prompt, padding=True, truncation=True, return_tensors='pt').to(self.device)

        # Получаем выход модели
        with torch.no_grad():
            model_output = self.model(**encoded_input)

        # Пулирование
        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])

        # Переносим тензор на CPU и преобразуем в numpy
        sentence_embeddings = sentence_embeddings.cpu().numpy()

        # Создаем тензор для ответа с правильным типом данных (например, float32)
        output_tensors = [pb_utils.Tensor("text_output", sentence_embeddings.astype(np.float32))]

        # Возвращаем ответ
        response = pb_utils.InferenceResponse(output_tensors=output_tensors)
        return response

    def finalize(self):
        print("Cleaning up...")
