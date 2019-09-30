.PHONY: lint test

lint:
	pylint pad_data test scripts

test:
	python -m unittest test.card
	python -m unittest test.skill
	python -m unittest test.leader_skill

