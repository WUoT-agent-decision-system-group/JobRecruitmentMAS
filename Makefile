.PHONY: format

format:
	black .
	isort --profile black .