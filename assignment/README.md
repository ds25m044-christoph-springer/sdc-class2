### Project Description: Building a FastAPI Application with Stable Diffusion Image Generation

**Objective**: Develop a FastAPI application from scratch that integrates the Stable Diffusion model, provided by Stability AI for custom image generation. You will create an asynchronous API that accepts unique prompts, processes them using Stable Diffusion, and generates corresponding images.

#### Background:
- Stable Diffusion is a powerful AI model capable of creating detailed images from textual descriptions.
- For now we'll simply integrate their sdk and access the model using their SaaS offering.
- Your task is to understand how to effectively utilize a ml model in a FastAPI context.

#### Resources Provided:
- Access to the `ImageGenerator` API that uses Stable Diffusion.
- A GPT-Service Implementation + API for optional profanity checking.
- An API key for the `ImageGenerator` service.
- Documentation on Stable Diffusion and its prompt-handling capabilities.


The API is **asynchronous**: image generation runs in the background so the client does not have to wait for the Stable Diffusion API to finish.

## How It Works

1. The client sends a text prompt to `POST /images`.
2. The API creates a unique image ID and returns immediately with status `processing`.
3. FastAPI's `BackgroundTasks` runs the image generation in the background.
4. The generated PNG image is saved locally in the `images/` directory.
5. The client uses `GET /image/{image_id}` to check the status.
6. Once generation is complete, the endpoint returns the generated PNG image.

The application keeps the current job status in memory and stores generated images as PNG files.

## Requirements

* Python 3.11+
* `uv`
* Stability AI API key

## Setup

Install the dependencies:

```bash
uv sync
```

Create a `.env` file in the project root:

```env
STABILITY_API_KEY=your_api_key_here
```

Start the API:

```bash
uv run uvicorn app:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation is available at:

```text
http://localhost:8000/docs
```

## API Endpoints

### `POST /images`

Starts a new image-generation job.

Request:

```json
{
  "prompt": "a person being very happy that the program works. he can now upload the assignment and eat lunch"
}
```

Response:

```json
{
  "image_id": "217366e9-3e00-4a73-8dfa-d2fab783d53a",
  "status": "processing"
}
```

### `GET /image/{image_id}`

Checks the status of a generation job.

While the image is being generated:

```json
{
  "image_id": "217366e9-3e00-4a73-8dfa-d2fab783d53a",
  "status": "processing"
}
```

When generation is complete, the endpoint returns the generated PNG image.

If the image ID does not exist, the API returns `404 Not Found`.

## Example

Create an image:

```bash
curl -X POST http://localhost:8000/images \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"a person being very happy that the program works. he can now upload the assignment and eat lunch\"}"
```

The response contains an `image_id`.

Then request:

```text
GET /image/{image_id}
```

Initially, the response may show `processing`. After the background task finishes, the same request returns the generated image.
For this example, it gives this image as output:
![alt text](assignment\images\217366e9-3e00-4a73-8dfa-d2fab783d53a.png)

## Project Structure

```text
assignment/
├── app.py
├── image_generator/
│   ├── __init__.py
│   ├── image_generator.py
│   └── stability_api.py
├── images/
├── pyproject.toml
└── README.md
```

The `image_generator` package contains the provided Stable Diffusion integration, while `app.py` provides the FastAPI endpoints and background processing.