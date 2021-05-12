generate_files:
	@python gen_contents.py

clean:
	@rm hekate.bin.js
	@rm lockpick.bin.js
	@rm tegraexplorer.bin.js
	@rm index.html

.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
