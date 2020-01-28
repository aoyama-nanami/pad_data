.PHONY: lint
lint:
	pylint pad_data test scripts

.PHONY: test
test:
	python -m unittest test.card
	python -m unittest test.skill
	python -m unittest test.leader_skill

.PHONY: mypy
mypy:
	MYPYPATH=./stub mypy pad_data test scripts
