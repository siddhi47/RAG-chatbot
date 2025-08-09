# Docker image settings
IMAGE_NAME=my-infer
IMAGE_TAG=local

# Kubernetes resource names for env files
CONFIGMAP_NAME=my-config
SECRET_NAME=my-secrets

# Paths to env files
ENV_FILE=.env
SECRETS_FILE=.env.secrets

# Deployment and Service names in Kubernetes
DEPLOYMENT_NAME=my-infer
SERVICE_NAME=my-infer

.PHONY: deploy build-image load-env apply print-url all

all: deploy

deploy: build-image load-env apply print-url

build-image:
	@echo ">>> Pointing Docker to Minikube and building image..."
	eval $$(minikube docker-env) && \
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) . && \
	eval $$(minikube docker-env -u)

load-env:
	@echo ">>> Creating/Updating ConfigMap from $(ENV_FILE)"
	kubectl create configmap $(CONFIGMAP_NAME) \
	  --from-env-file=$(ENV_FILE) \
	  --dry-run=client -o yaml | kubectl apply -f -

	@echo ">>> Creating/Updating Secret from $(SECRETS_FILE)"
	kubectl create secret generic $(SECRET_NAME) \
	  --from-env-file=$(SECRETS_FILE) \
	  --dry-run=client -o yaml | kubectl apply -f -

apply:
	@echo ">>> Applying deployment.yaml (includes NodePort service)"
	kubectl apply -f deployment.yaml

print-url:
	@echo ">>> Service URL:"
	@MINIKUBE_IP=$$(minikube ip); \
	NODE_PORT=$$(kubectl get svc $(SERVICE_NAME) -o jsonpath='{.spec.ports[0].nodePort}'); \
	echo "http://$$MINIKUBE_IP:$$NODE_PORT"

