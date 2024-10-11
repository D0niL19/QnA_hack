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

    def execute(self, requests):
        responses = []
        for request in requests:
            # Assume input named "prompt", specified in autocomplete above
            input_tensor = pb_utils.get_input_tensor_by_name(request, "text_input")
            prompt = input_tensor.as_numpy()[0].decode("utf-8")

            response = self.get_question_embed(prompt)
            responses.append(response)

        return responses

    def mean_pooling(model_output, attention_mask):

        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def get_question_embed(self, prompt):
        if type(prompt) == str:
            prompt = [prompt]
        encoded_input = self.tokenizer(prompt, padding=True, truncation=True, return_tensors='pt')
        encoded_input = {key:value.to(self.device) for key, value in encoded_input.items()}
        with torch.no_grad():
            model_output = self.model(**encoded_input)

        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        output_tensors = []
        texts = []
        for i, seq in enumerate(sentence_embeddings):
            text = seq
            texts.append(text)

        tensor = pb_utils.Tensor("text_output", np.array(texts, dtype=np.object_))
        output_tensors.append(tensor)
        response = pb_utils.InferenceResponse(output_tensors=output_tensors)
        return response

    def finalize(self):
        print("Cleaning up...")
