import os

os.environ["TRANSFORMERS_CACHE"] = "/opt/tritonserver/model_repository/generate/hf-cache"

import json

import numpy as np
import torch
import transformers
import triton_python_backend_utils as pb_utils

from transformers import AutoTokenizer, AutoModelForCausalLM


class TritonPythonModel:
    def initialize(self, args):

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        #self.pipeline = transformers.pipeline(
         #   "text-generation",
          #  model="IlyaGusev/saiga_llama3_8b",
           # torch_dtype=torch.float16,
            #device_map="auto",
            #max_new_tokens=708,
        #)
        model_id = "IlyaGusev/saiga_llama3_8b"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map=self.device,
                torch_dtype=torch.bfloat16
        )
        self.generation_config = transformers.GenerationConfig.from_pretrained(model_id)

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
        #sequences = self.pipeline(
         #   prompt
        #)
        prompt, question = prompt.split("____")
        prompt = self.tokenizer.apply_chat_template([{
        "role": "system",
        "content": prompt
         }, {
        "role": "user",
        "content": question
        }], tokenize=False, add_generation_prompt=True)
        #prompt = self.tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        #eos_tokens = [self.tokenizer.eos_token_id, self.tokenizer.convert_tokens_to_ids("<|im_end|>"),]
        data = self.tokenizer(prompt, add_special_tokens=False, return_tensors="pt")
        data = {k: v.to(self.model.device) for k, v in data.items()}
        #print(inputs.shape)
        #with torch.no_grad():
         #   outputs = self.model.generate(input_ids=inputs.to(self.device), eos_token_id=eos_tokens, max_new_tokens=708)
        output_tensors = []
        output_ids = self.model.generate(**data, generation_config=self.generation_config)[0]
        output_ids = output_ids[len(data["input_ids"][0]):]
        output = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()
        #generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        #answer = generated_text.split("Question:")[1].strip() if "Question:" in generated_text else generated_text.strip()
        #texts = []
        #for i, seq in enumerate(sequences):
            #text = seq['generated_text']
            #texts.append(text)

        tensor = pb_utils.Tensor("text_output", np.array([output], dtype=np.object_))
        output_tensors.append(tensor)
        response = pb_utils.InferenceResponse(output_tensors=output_tensors)
        return response

    def finalize(self):
        print("Cleaning up...")
