all: test
	
publish: test
	python setup.py sdist upload -r pypi

env:
	@if [ ! -d "virtualenv" ]; then virtualenv virtualenv; fi

deps: env
	@virtualenv/bin/pip install -e .

test:
	trial txghserf.tests

run:
	twistd -n web --class run.resource
