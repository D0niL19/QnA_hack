import os

os.environ["TRANSFORMERS_CACHE"] = "/opt/tritonserver/model_repository/generate/hf-cache"

import json

import numpy as np
import torch
import transformers
import triton_python_backend_utils as pb_utils



class TritonPythonModel:
    def initialize(self, args):

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipeline = transformers.pipeline(
            "text-generation",
            model="BSC-LT/salamandra7b_rag_prompt_ca-en-es",
            torch_dtype=torch.float16,
            device_map=self.device,
        )
        self.model_config = json.loads(args["model_config"])
        self.model_params = self.model_config.get("parameters", {})
        default_max_gen_length = "15"

        self.max_output_length = int(
            self.model_params.get("max_output_length", {}).get(
                "string_value", default_max_gen_length
            )
        )

    def execute(self, requests):
        responses = []
        for request in requests:
            input_tensor = pb_utils.get_input_tensor_by_name(request, "text_input")
            prompt = input_tensor.as_numpy()[0].decode("utf-8")

            response = self.generate(prompt)
            responses.append(response)

        return responses

    def generate(self, prompt):
        sequences = self.pipeline(
            prompt
        )

        output_tensors = []
        texts = []
        for i, seq in enumerate(sequences):
            text = seq["generated_text"]
            texts.append(text)

        tensor = pb_utils.Tensor("text_output", np.array(texts, dtype=np.object_))
        output_tensors.append(tensor)
        response = pb_utils.InferenceResponse(output_tensors=output_tensors)
        return response

    def finalize(self):
        print("Cleaning up...")
