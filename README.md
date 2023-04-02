# LangChain as an AIPlugin

## Introduction

[LangChain](https://python.langchain.com/en/latest/index.html) can flexibly integrate with the ChatGPT AI plugin ecosystem.
 
LangChain chains and agents can themselves be deployed as a plugin that can communicate with other agents or with ChatGPT itself.

For more information on AI Plugins, see OpenAI's [example retrieval plugin](https://github.com/openai/chatgpt-retrieval-plugin/tree/main) repository.

## Quickstart

Follow these steps to quickly set up and run a LangChain AI Plugin:

1. Install Python 3.10, if not already installed.
2. Clone the repository: `git clone git@github.com:langchain-ai/langchain-aiplugin.git`
3. Navigate to the example plugin directory: `cd langchain-aiplugin`
4. Install poetry: `pip install poetry`
5. Create a new virtual environment with Python 3.10: `poetry env use python3.10`
6. Activate the virtual environment: `poetry shell`
7. Install app dependencies: `poetry install`
8. Set up the chain you want to run (see detailed instructions below). For an example, run `export LANGCHAIN_DIRECTORY_PATH=r
etrieval_qa` and `export OPENAI_API_KEY=...` and `export BEARER_TOKEN=...` (the Bearer Token can be anything you want for local testing purposes).
9. Run the API locally: `poetry run app --port 8080`
10. Access the API documentation at `http://0.0.0.0:8080/docs` and test the API endpoints (make sure to add your bearer token).

For more detailed information on setting up, developing, and deploying the ChatGPT Retrieval Plugin, refer to the full Development section below.

## Development

### Environment Setup

This app uses Python 3.10, and [poetry](https://python-poetry.org/) for dependency management.

Install Python 3.10 on your machine if it isn't already installed. It can be downloaded from the official [Python website](https://www.python.org/downloads/) or with a package manager like `brew` or `apt`, depending on your system.

**Note:** If adding dependencies in the `pyproject.toml`, make sure to run `poetry lock` and `poetry install`.

### Setup a Chain

To setup a chain to be a plugin, you will need to do the following steps:

1. Create a new folder
2. Create a `chain.py` file in that folder, and fill it out appropriately (see instructions below)
3. Create a `constants.py` file in that folder, and fill it out appropriately (see instructions below)
4. Add an environment variable `export LANGCHAIN_DIRECTORY_PATH=$PATH_TO_FOLDER`

#### Setup `chain.py`

In order to setup `chain.py` all you need to do is expose a function with the following signature:

```python
from langchain.chains.base import Chain


def load_chain() -> Chain:
    """Load your chain here."""
```

To get started, you can copy the file in `template/chain.py`

#### Setup `constants.py`

In order to setup `constants.py`, you need to have a Python file with the following variables exposed:

```python
# The description of the chain you are exposing. This will be used by ChatGPT to decide when to call it.
ENDPOINT_DESCRIPTION = ""
# The name of your endpoint that you are exposing.
ENDPOINT_NAME = ""
# The input key for the chain. The user input will get mapped to this key.
INPUT_NAME = ""
# The output key for the chain. The final response will take this key from the chain output.
OUTPUT_KEY = ""
# Name of the overall service to expose to the model.
NAME_FOR_MODEL = ""
# Name of the overall service to expose to humans.
NAME_FOR_HUMAN = ""
# Description of the overall service to expose to the model.
DESCRIPTION_FOR_MODEL = ""
# Description of the overall service to expose to humans.
DESCRIPTION_FOR_HUMAN = ""
```

To get started, you can copy the file in `template/constants.py`

## Examples

To help get started we've set up two examples.

- `retrieval_qa`: Exposes a [RetrievalQA Chain](https://python.langchain.com/en/latest/modules/chains/index_examples/vector_db_qa.html) set up with LangChain Documentation. See the [README](retrieval_qa/README.md) in that folder for more information.
- `agent`: Exposes a simple agent equipped with a calculator. See the [README](agent/README.md) in that folder for more information.



### Deploying to Fly.io

We have included a `make` command to deploy your app to Fly.io using their CLI. To run, type

```
make deploy_to_flyctl BEARER_TOKEN="your-plugin's-bearer-token" OPENAI_API_KEY="your-openai-key"
```

and select NOT to deploy right now (as we include deployment in subsequent steps).

That's it! 

**Manual deployment on Fly.io** 

What follows is an explanation of what goes on within the `make` command, should you wish to do the deployment manually.



To deploy the Docker container from this repository to Fly.io, follow
these steps:

[Install Docker](https://docs.docker.com/engine/install/) on your local machine if it is not already installed.

Install the [Fly.io CLI](https://fly.io/docs/getting-started/installing-flyctl/) on your local machine.

Clone the repository from GitHub:

```
git clone https://github.com/openai/chatgpt-retrieval-plugin.git
```

Navigate to the cloned repository directory:

```
cd path/to/chatgpt-retrieval-plugin
```

Log in to the Fly.io CLI:

```
flyctl auth login
```

Create and launch your Fly.io app:

```
flyctl launch
```

Follow the instructions in your terminal:

- Choose your app name
- Choose your app region
- Don't add any databases
- Don't deploy yet (if you do, the first deploy might fail as the environment variables are not yet set)

Set the required environment variables (*assuming $OPEN_API_KEY is set locally*):


```
export LANGCHAIN_DIRECTORY_PATH="agent" # or retrieval_qa
export OPENAI_API_KEY=<your key> # Or whatever auth is required for the selected LLM
export PLUGIN_BEARER_TOKEN="" # The bearer token you'll assign to your app
<Add additional environment variables here>
flyctl secrets set OPENAI_AI_KEY=$OPENAI_API_KEY \
   LANGCHAIN_DIRECTORY_PATH=$LANGCHAIN_DIRECTORY_PATH \
   BEARER_TOKEN=$PLUGIN_BEARER_TOKEN \
   PUBLIC_API_URL=https://$(flyctl status | awk '/Hostname/ {print $3}')
```

Alternatively, you could set environment variables in the [Fly.io Console](https://fly.io/dashboard).

At this point, you can change the plugin url in your plugin manifest file [here](/.well-known/ai-plugin.json), and in your OpenAPI schema [here](/.well-known/openapi.yaml) to the url for your Fly.io app, which will be `https://your-app-name.fly.dev`.

Deploy your app with:

```
flyctl deploy
```

After completing these steps, your Docker container should be deployed to Fly.io and running with the necessary environment variables set. You can view your app by running:

```
flyctl open
```

which will open your app url. You should be able to find the OpenAPI schema at `<your_app_url>/.well-known/openapi.yaml` and the manifest at `<your_app_url>/.well-known/ai-plugin.json`.

To view your app logs:

```
flyctl logs
```

Now, make sure you have changed the plugin url in your plugin manifest file [here](/.well-known/ai-plugin.json), and in your OpenAPI schema [here](/.well-known/openapi.yaml), and redeploy with `flyctl deploy`. This url will be `https://<your-app-name>.fly.dev`.

**Debugging tips:**
Fly.io uses port 8080 by default.

If your app fails to deploy, check if the environment variables are set correctly, and then check if your port is configured correctly. You could also try using the [`-e` flag](https://fly.io/docs/flyctl/launch/) with the `flyctl launch` command to set the environment variables at launch.

<!-- 
## Deploying to Modal

Below outlines the steps to deploy the Retrieval QA AI Plugin to [Modal](https://modal.com/docs/guide) -->