.PHONY: deploy_to_flyctl

open_fly_docs_path:
	DOCS_PATH=https://$$(flyctl status | awk '/Hostname/ {print $$3}')/docs ; \
		echo "Deployed to flyctl at $$DOCS_PATH" ; \
		open $$DOCS_PATH \

deploy_to_flyctl:
ifndef BEARER_TOKEN
	$(error BEARER_TOKEN is not set)
endif
ifndef OPENAI_API_KEY
	$(error OPENAI_API_KEY is not set)
endif
	export LANGCHAIN_DIRECTORY_PATH=retrieval_qa
	flyctl auth login
	echo "Choose your app name and region, but don't add databases or deploy yet."
	flyctl launch
	LANGCHAIN_DIRECTORY_PATH=retrieval_qa; \
	flyctl secrets set OPENAI_API_KEY=$$OPENAI_API_KEY \
		LANGCHAIN_DIRECTORY_PATH=$$LANGCHAIN_DIRECTORY_PATH \
		BEARER_TOKEN=$$BEARER_TOKEN \
		PUBLIC_API_URL=https://$$(flyctl status | awk '/Hostname/ {print $$3}') \

	echo "You can track the deployment progress at the admin console: https://fly.io/dashboard"
	echo "Deploying to flyctl"
	flyctl deploy
	open https://fly.io/dashboard
