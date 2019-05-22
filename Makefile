.PHONY: lint test

lint:
	pylint *.py pad_data test

test:
	python -m unittest test.card
	python -m unittest test.skill
	python -m unittest test.leader_skill

