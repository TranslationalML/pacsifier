.DEFAULT_GOAL := help

# Define the project directory
PROJECT_DIR = $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

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
IMAGE_TAG = $(if $(CI_REGISTRY),$(CI_REGISTRY)/tml/pacsman:$(TAG),pacsman:$(TAG)) 

# Define the build date and vcs reference
BUILD_DATE = $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF = $(shell git rev-parse --short HEAD)

# Define the user and user id for the docker container
USER = $(shell whoami)
USER_ID = $(shell id -u $(USER))
GROUP_ID = $(shell id -g $(USER))

# Force to use buildkit for building the Docker image
export DOCKER_BUILDKIT=0

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
		--aetitle PACSMAN_SCU \
		--call SCU_STORE \
		localhost 4444 \
		/tests/test_data/dicomseries
	@echo "Running pytest tests..."
	docker run --rm --network=host \
	    --name docker-pytest \
		--entrypoint "/entrypoint_pytest.sh" \
		-v $(PROJECT_DIR)/tests:/tests \
		-v $(PROJECT_DIR)/pacsman:/app/pacsman/pacsman \
		$(IMAGE_TAG) \
		/tests
	@echo "Stopping dcmqrscp instance..."
	docker kill docker-dcmqrscp
	@echo "Fix path in coverage xml report..."
	sed -i -r  \
		"s|/app/pacsman/pacsman|$(PROJECT_DIR)/pacsman|g" \
		$(PROJECT_DIR)/tests/report/cov.xml

#bash: @ Run bash in the container
.PHONY: bash
bash:
	@echo "Running pytest tests..."
	docker run -it --rm \
		--entrypoint "/bin/bash" \
		-v $(PROJECT_DIR)/tests:/tests \
		-v $(PROJECT_DIR)/pacsman:/app/pacsman/pacsman \
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
# 		docker push $(CI_REGISTRY)/tml/pacsman:$(TAG); 
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
	pip install pacsman

#test-python-install: @ Tests the python package installation
test-python-install: install-python build-python-wheel install-python-wheel	
	pacsman --version

#build-docs: @ Builds the documentation
build-docs: install-python
	cd docs && make clean && make -B html

#clean: @ Clean the project
clean:
	rm -rf build dist pacsman.egg-info

#help:	@ List available tasks on this project
help:
	@grep -E '[a-zA-Z\.\-]+:.*?@ .*$$' $(MAKEFILE_LIST)| tr -d '#'  | awk 'BEGIN {FS = ":.*?@ "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'