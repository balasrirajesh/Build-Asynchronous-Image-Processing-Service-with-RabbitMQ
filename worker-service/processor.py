import os
import io
import aiohttp
from PIL import Image, ImageOps

class ImageProcessor:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)

    async def download_image(self, url: str) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download image: {response.status}")
                return await response.read()

    def process_image(self, image_data: bytes, transformations: list, job_id: str) -> str:
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Idempotency: Overwriting file is fine as transformations are deterministic.
            # However, logic is needed to handle sequence.
            
            for trans in transformations:
                if trans.startswith("resize:"):
                    # format resize:100x100
                    try:
                        dimensions = trans.split(":")[1]
                        width, height = map(int, dimensions.split("x"))
                        image = image.resize((width, height))
                    except ValueError:
                        print(f"Invalid resize format: {trans}")
                elif trans == "grayscale":
                    image = ImageOps.grayscale(image)

            # Save
            filename = f"{job_id}.png"
            file_path = os.path.join(self.storage_path, filename)
            image.save(file_path, format="PNG")
            
            return file_path
        except Exception as e:
            raise Exception(f"Image processing failed: {str(e)}")
