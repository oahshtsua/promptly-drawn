import torch
from diffusers import StableDiffusionPipeline
from PIL import Image


class TextToImage:
    pipe: StableDiffusionPipeline | None = None

    def load_model(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pipe = StableDiffusionPipeline.from_pretrained("segmind/tiny-sd")
        pipe.to(device)
        self.pipe = pipe

    def generate(
        self,
        prompt: str,
        *,
        negative_prompt: str | None = None,
        inference_steps: int = 50,
    ) -> Image.Image:
        if not self.pipe:
            raise RuntimeError("Pipeline is not loaded.")
        return self.pipe(
            prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=inference_steps,
            guidance_scale=9.0,
        ).images[0]


image_gen_service = TextToImage()
