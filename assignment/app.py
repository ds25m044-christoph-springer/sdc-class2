import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from image_generator import ImageGenerator

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
print("API key loaded:", bool(os.getenv("STABILITY_API_KEY")))

app = FastAPI()


IMAGE_DIR = Path("images")
IMAGE_DIR.mkdir(exist_ok=True)

images = {}


class ImageRequest(BaseModel):
    prompt: str


def gen_image_task(image_id: str, prompt: str):
    """
    Generate an image in the background and save it to disk.
    """

    try:
        # Get the API key from the environment.
        api_key = os.getenv("STABILITY_API_KEY")

        if not api_key:
            raise RuntimeError(
                "STABILITY_API_KEY environment variable is not set"
            )

        # using given API for ImageGenerator 
        image_generator = ImageGenerator(api_key)

        # image generation
        image_binary = image_generator.generate_image(prompt)

        if image_binary is None:
            raise RuntimeError(
                "ImageGenerator did not return an image"
            )

        # Save image ID
        image_path = IMAGE_DIR / f"{image_id}.png"

        with open(image_path, "wb") as file:
            file.write(image_binary)

        # Update job status
        images[image_id] = {
            "status": "ready",
            "path": str(image_path)
        }

    except Exception as error:
        print(f"Image generation failed: {error}")

        images[image_id] = {
            "status": "failed",
            "error": str(error)
        }


@app.post("/images", status_code=202)
async def create_image(
    request: ImageRequest,
    background_tasks: BackgroundTasks
):
    """
    Start an asynchronous image-generation job.
    """

    # unique image ID
    image_id = str(uuid.uuid4())

    images[image_id] = {
        "status": "processing"
    }

    background_tasks.add_task(
        gen_image_task,
        image_id,
        request.prompt
    )

    return {
        "image_id": image_id,
        "status": "processing"
    }


@app.get("/image/{image_id}")
async def get_image(image_id: str):
    """
    Retrieve an image or its current generation status.
    """

    # Check if image ID exists and the state
    if image_id not in images:
        raise HTTPException(
            status_code=404,
            detail="Image not found"
        )

    image = images[image_id]

    if image["status"] == "processing":
        return {
            "image_id": image_id,
            "status": "processing"
        }

    if image["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail={
                "image_id": image_id,
                "status": "failed",
                "error": image["error"]
            }
        )

    if image["status"] == "ready":

        image_path = image["path"]

        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=404,
                detail="Image file not found"
            )

        return FileResponse(
            path=image_path,
            media_type="image/png",
            filename=f"{image_id}.png"
        )

    raise HTTPException(
        status_code=500,
        detail="Unknown image status"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.0",
        port=8000
    )