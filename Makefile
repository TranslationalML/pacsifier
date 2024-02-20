.DEFAULT_GOAL := help

# Define the project directory
PROJECT_DIR = $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Set environment variables for the docker image name and tag
IMAGE_NAME=$(shell python get_container_name.py)

# Define the version tag 
TAG = $(shell python get_version.py)
$(info TAG = $(TAG))
# Replace +, /, _ with - to normalize the tag
# in case the tag includes a branch name
override TAG := $(subst +,-,$(TAG))
override TAG := $(subst /,-,$(TAG))
override TAG := $(subst _,-,$(TAG))
$(info TAG (Normalized) = $(TAG))

# Define the complete docker image tag 
<<<<<<< HEAD
IMAGE_TAG = $(if $(CI_REGISTRY),$(CI_REGISTRY)/tml/pacsifier:$(TAG),pacsifier:$(TAG)) 
=======
IMAGE_TAG=$(IMAGE_NAME):$(TAG)
>>>>>>> 8894ea1 (refactor(Makefile): set IMAGE_NAME with get_container_name.py)

# Define the build date and vcs reference
BUILD_DATE = $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF = $(shell git rev-parse --short HEAD)

# Define the user and user id for the docker container
USER = $(shell whoami)
USER_ID = $(shell id -u $(USER))
GROUP_ID = $(shell id -g $(USER))

# Force to use buildkit for building the Docker image
export DOCKER_BUILDKIT=0

#validate-zenodo: @ Validate the .zenodo.json file of the project
.PHONY: validate-zenodo
validate-zenodo:
	@echo "Validating .zenodo.json file..."
	python $(PROJECT_DIR)/utils/validate_dot_zenodo_json.py

#test: @ Run all tests
.PHONY: test
test:
	@echo "Launching dcmqrscp instance in separate container..."
	docker run -d --rm --network=host \
	    --name docker-dcmqrscp \
		--entrypoint "/usr/bin/dcmqrscp" \
		-v $(PROJECT_DIR)/tests:/tests \
		$(IMAGE_TAG) \
		-d -v -c /tests/config/dcmqrscp.cfg
	@echo "Waiting 5 seconds for dcmqrscp instance to start.."
	sleep 5
	@echo "Send initial data to dcmqrscp instance with storescu in separate container..."
	docker run --rm --network=host \
	    --name docker-storescu \
		--entrypoint "/usr/bin/storescu" \
		-v $(PROJECT_DIR)/tests:/tests \
		$(IMAGE_TAG) \
		-v \
		-d \
		--scan-directories \
		--aetitle PACSIFIER_SCU \
		--call SCU_STORE \
		localhost 4444 \
		/tests/test_data/dicomseries
	@echo "Running pytest tests..."
	docker run --rm --network=host \
	    --name docker-pytest \
		--entrypoint "/entrypoint_pytest.sh" \
		-v $(PROJECT_DIR)/tests:/tests \
		$(IMAGE_TAG) \
		/tests
	@echo "Stopping dcmqrscp instance..."
	make kill-dcmqrscp
	@echo "Fix ownership in tests..."
	sudo chown -R $(USER_ID):$(GROUP_ID) $(PROJECT_DIR)/tests
	@echo "Fix path in coverage xml report..."
	sed -i -r  \
		"s|/app/pacsifier/pacsifier|$(PROJECT_DIR)/pacsifier|g" \
		$(PROJECT_DIR)/tests/report/cov.xml

#kill-dcmqrscp: @ Kill the docker-dcmqrscp container
.PHONY: kill-dcmqrscp
kill-dcmqrscp:
	docker kill docker-dcmqrscp

#clean-test: @ Clean the directories generated by the tests
.PHONY: clean-test
clean-test:
	sudo rm -rf $(PROJECT_DIR)/tests/report
	sudo rm -rf $(PROJECT_DIR)/tests/tmp
	sudo rm -rf $(PROJECT_DIR)/tests/logs

#bash: @ Run bash in the container
.PHONY: bash
bash:
	@echo "Running pytest tests..."
	docker run -it --rm \
		--entrypoint "/bin/bash" \
		-v $(PROJECT_DIR)/tests:/tests \
		-v $(PROJECT_DIR)/pacsifier:/app/pacsifier/pacsifier \
		$(IMAGE_TAG)

#build-docker: @ Builds the Docker image
build-docker:
	docker build \
	-t $(IMAGE_TAG) \
	--build-arg BUILD_DATE=$(BUILD_DATE) \
	--build-arg VCS_REF=$(VCS_REF) \
	--build-arg VERSION=$(TAG) .

# #push-docker-ci: @ Push the Docker image with TAG to the CI registry
# push-docker-ci:
# 	if $(CI_REGISTRY); then \
# 		docker login -u $(CI_REGISTRY_USER) -p $(CI_REGISTRY_PASSWORD) $(CI_REGISTRY); \
# 		docker push $(CI_REGISTRY)/tml/pacsifier:$(TAG); 
# 	fi

# #rm-docker-ci: @ Remove the Docker image with TAG to the CI registry
# # from https://docs.gitlab.com/ee/user/packages/container_registry/delete_container_registry_images.html#use-gitlab-cicd
# rm-docker-ci:
# 	./reg rm -d \
# 		--auth-url $(CI_REGISTRY) \
# 		-u $(CI_REGISTRY_USER) \
# 		-p $(CI_REGISTRY_PASSWORD) \
# 		$(CI_PROJECT_PATH):$(TAG)

#python-install: @ Installs the python package
install-python:
	pip install -e .[all]

#build-python-wheel: @ Builds the python wheel
build-python-wheel:
	python setup.py sdist bdist_wheel

#install-python-wheel: @ Installs the python wheel
install-python-wheel: build-python-wheel
	pip install dist/pacsifier-*.whl

#test-python-install: @ Tests the python package installation
test-python-install: install-python build-python-wheel install-python-wheel	
	pacsifier --version

#build-docs: @ Builds the documentation
build-docs: install-python
	cd docs && make clean && make -B html

#clean: @ Clean the project
clean:
	rm -rf build dist pacsifier.egg-info

#help:	@ List available tasks on this project
help:
	@grep -E '[a-zA-Z\.\-]+:.*?@ .*$$' $(MAKEFILE_LIST)| tr -d '#'  | awk 'BEGIN {FS = ":.*?@ "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
