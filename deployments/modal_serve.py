"""Example LangChain Plugin deployment on Modal."""
import os
from pathlib import Path
import modal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
client = modal.Client()
# Infer the deployment URL
_PREV_SET = "PUBLIC_API_URL" in os.environ
_LABEL = "langchain-plugin"
modal_workspace = os.environ["MODAL_WORKSPACE"]  # TODO: get this programatically
os.environ["PUBLIC_API_URL"] = f"https://{modal_workspace}--{_LABEL}.modal.run"
if _PREV_SET:
    logging.warning(
        "PUBLIC_API_URL is ignored when serving on Modal."
        f" Newly set to {os.environ['PUBLIC_API_URL']}"
    )
from app.main import app, REQUIRED_ENV_VARS

_IMAGE = (
    modal.Image.debian_slim()
    .env({var: os.environ[var] for var in REQUIRED_ENV_VARS})
    .from_dockerfile(
        Path(__file__).parents[1] / "Dockerfile",
    )
    )
    # .poetry_install_from_file("pyproject.toml")
)
# stub = modal.aio.AioStub()
stub = modal.stub.AioStub()


@stub.asgi(image=_IMAGE, label=_LABEL)
def fastapi_app():
    """FastAPI app."""
    return app
