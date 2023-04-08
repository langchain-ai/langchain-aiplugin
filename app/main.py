""""Example LangChain Plugin."""
import json
import logging
import os
import shutil
from typing import Optional, cast
import importlib
from importlib.machinery import SourceFileLoader
from pathlib import Path

import uvicorn
import yaml
from app.api import ConversationRequest, ConversationResponse
from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from langchain.chains.base import Chain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

### Load Chain and Constants ###
DIR_PATH = Path(__file__).parent
# List all files in current directory
FILES = [f for f in DIR_PATH.iterdir()]
# Create a loader for the "constants.py" file.
REQUIRED_ENV_VARS = [
    "LANGCHAIN_DIRECTORY_PATH",
    "BEARER_TOKEN",
]
DIRECTORY_PATH = os.environ.get("LANGCHAIN_DIRECTORY_PATH", "")
if not DIRECTORY_PATH.strip():
    raise ValueError("LANGCHAIN_DIRECTORY_PATH must be set")

loader = SourceFileLoader(
    "_langchain_constants", str(Path(DIRECTORY_PATH) / "constants.py")
)
spec = importlib.util.spec_from_loader("_langchain_constants", loader)
if spec is None:
    raise ValueError("could not load spec")
CONSTANTS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CONSTANTS)

# Create a loader for the "chain.py" file.
loader = SourceFileLoader("_langchain_chain", str(Path(DIRECTORY_PATH) / "chain.py"))
spec = importlib.util.spec_from_loader("_langchain_chain", loader)
if spec is None:
    raise ValueError("could not load spec")
CHAIN = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CHAIN)

### Setup the PLUGIN_INFORMATION ###

BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
assert BEARER_TOKEN is not None
API_VERSION = os.environ.get("API_VERSION", "1.0.0")
API_PORT = int(os.environ.get("PORT", os.environ.get("WEBSITES_PORT", 8080)))
API_URL = os.environ.get("API_URL", "0.0.0.0")
# Can set to "https://your-app-url.com" when deploying
PUBLIC_API_URL = os.environ.get("PUBLIC_API_URL", f"http://{API_URL}:{API_PORT}")

PLUGIN_INFORMATION = {
    "schema_version": "v1",
    "name_for_model": CONSTANTS.NAME_FOR_MODEL,
    "name_for_human": CONSTANTS.NAME_FOR_HUMAN,
    "description_for_model": CONSTANTS.DESCRIPTION_FOR_MODEL,
    "description_for_human": CONSTANTS.DESCRIPTION_FOR_HUMAN,
    "auth": {
        "type": "service_http",
        "authorization_type": "bearer",
        "verification_tokens": {"openai": BEARER_TOKEN},
    },
    "api": {
        "type": "openapi",
        # Update to https if using an SSL certificate
        "url": f"{PUBLIC_API_URL}/.well-known/openapi.yaml",
        # In production, you will likely need user-based authentication
        "has_user_authentication": False,
    },
    "logo_url": f"{PUBLIC_API_URL}/.well-known/logo.png",
    "contact_email": "support@langchain.com",
    "legal_info_url": f"{PUBLIC_API_URL}/legal",
}


### APP Setup ###

bearer_scheme = HTTPBearer()


def validate_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """Validate the 'Bearer' token."""
    if credentials.scheme != "Bearer" or credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return credentials


_APP_DEPENDENCIES = [Depends(validate_token)] if BEARER_TOKEN else []
_CHAIN: Optional[Chain] = None


app = FastAPI(
    title=PLUGIN_INFORMATION["name_for_human"],
    description=PLUGIN_INFORMATION["description_for_model"],
    version=API_VERSION,
    dependencies=_APP_DEPENDENCIES,
)


async def arun_chain(request: ConversationRequest = Body(...)) -> ConversationResponse:
    print("Request:", request)
    chain = cast(Chain, _CHAIN)

    chain_input = {CONSTANTS.INPUT_NAME: request.message}
    try:
        # Note: This chain doesn't disambiguate between users.
        # When using a chain with memory, it would be important to
        # route requests to user-specific chain.
        try:
            result = await chain.acall(chain_input)
            return await result
        except NotImplementedError:
            # The integrations for certain LLM providers don't yet support async
            # In production, this exception block should be removed.
            result = chain(chain_input)
        return ConversationResponse(response=result[CONSTANTS.OUTPUT_KEY])
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")


@app.post(
    f"/{CONSTANTS.ENDPOINT_NAME}",
    response_model=ConversationResponse,
    description=CONSTANTS.ENDPOINT_DESCRIPTION,
)
async def chat(
    request: ConversationRequest = Body(...),
):
    """Generate chain responses."""
    return await arun_chain(request)


@app.on_event("startup")
async def startup():
    """Load the chain on startup."""
    global _CHAIN
    _CHAIN = CHAIN.get_chain()


def generate_plugin_docs():
    """Generate the .well-known/* docs to expose endpoint's interface."""
    openapi_schema = app.openapi()
    openapi_schema["servers"] = [{"url": PUBLIC_API_URL}]
    path = Path(".well-known")
    path.mkdir(exist_ok=True)
    with open(".well-known/openapi.yaml", "w") as f:
        yaml.dump(openapi_schema, f)
    with open(".well-known/ai-plugin.json", "w") as f:
        json.dump(PLUGIN_INFORMATION, f, indent=3)


Path(".well-known").mkdir(exist_ok=True)
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")


def start():
    """Start the API server."""
    # The static files are used by the LLM to infer how to interoperate with the plugin.
    # These are auto-generated from the descriptions provided above and the API schema.
    try:
        generate_plugin_docs()
        uvicorn.run("app.main:app", host=API_URL, port=API_PORT, reload=True)
    finally:
        # Remove the generated files
        shutil.rmtree(".well-known")
        pass
