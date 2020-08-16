PYTHONDIRS=pad_data test scripts downloader/*.py

.PHONY: lint
lint:
	pylint $(PYTHONDIRS)

.PHONY: test
test:
	python -m unittest test.card
	python -m unittest test.skill
	python -m unittest test.leader_skill

.PHONY: mypy
mypy:
	MYPYPATH=./stub mypy $(PYTHONDIRS)
