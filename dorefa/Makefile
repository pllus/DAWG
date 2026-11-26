PYTHON := ../.venv/bin/python
SCRIPT := cifar_train_eval.py
ARGS :=
CIFAR10_ARCHIVE := data/cifar-10-python.tar.gz
CIFAR10_URL := https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz

.PHONY: run dev run-dev setup download-cifar10

setup:
	uv pip install --system-certs torch torchvision tensorboardX

download-cifar10:
	mkdir -p data
	@if [ ! -f "$(CIFAR10_ARCHIVE)" ]; then curl --fail --location --output "$(CIFAR10_ARCHIVE)" "$(CIFAR10_URL)"; fi

run: download-cifar10
	$(PYTHON) $(SCRIPT) $(ARGS)

run-dev: run

dev: run
