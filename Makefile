.PHONY: deploy_to_flyctl

deploy_to_flyctl:
ifndef BEARER_TOKEN
	$(error BEARER_TOKEN is not set)
endif
ifndef OPENAI_API_KEY
	$(error OPENAI_API_KEY is not set)
endif
	export LANGCHAIN_DIRECTORY_PATH=retrieval_qa
	flyctl auth login
	flyctl launch
	echo "Choose your app name and region"
	echo "Don't add any databases"
	echo "Don't deploy yet"
	flyctl secrets set OPENAI_AI_KEY=$$OPENAI_API_KEY \
		LANGCHAIN_DIRECTORY_PATH=$$LANGCHAIN_DIRECTORY_PATH \
		BEARER_TOKEN=$$BEARER_TOKEN \
		PUBLIC_API_URL=https://$$(flyctl status | awk '/Hostname/ {print $$3}')

	echo "You can track the deployment progress at the admin console: https://fly.io/dashboard"
	echo "Deploying to flyctl"
	flyctl deploy
	open https://fly.io/dashboard
	DOCS_PATH=https://$$(flyctl status | awk '/Hostname/ {print $$3}')/docs
	open $DOCS_PATH