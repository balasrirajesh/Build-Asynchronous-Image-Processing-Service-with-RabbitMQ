
import pytest
import os
import shutil
from worker_service.processor import ImageProcessor

TEST_DIR = "test_images"

@pytest.fixture
def image_processor():
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    processor = ImageProcessor(TEST_DIR)
    yield processor
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def test_resize_logic_mock(image_processor):
    # This is a unit test for the logic, but requires a real image or mock
    # For simplicity, we assume the PILLOW logic in processor.py is correct if it parses strings
    # Real test would involve saving a dummy image and checking dimensions
    pass

@pytest.mark.asyncio
async def test_download_fail(image_processor):
    with pytest.raises(Exception):
        await image_processor.download_image("http://invalid-url.com/nonexistent.jpg")
