PYTHON_BASE_IMAGE ?= python:3.11-slim
UV_BASE_IMAGE ?= ghcr.io/astral-sh/uv:0.11.3

export PYTHON_BASE_IMAGE
export UV_BASE_IMAGE

.PHONY: help install hooks-install hooks-run format lint lint-fix type-check test test-cov check docker-build docker-local-check

help:
	@echo "可用命令："
	@echo "  make install       安装项目依赖"
	@echo "  make hooks-install 安装本地 Git pre-commit hooks"
	@echo "  make hooks-run     对全量文件执行 pre-commit hooks"
	@echo "  make format        使用 ruff 格式化 Python 代码"
	@echo "  make lint          使用 ruff 执行 lint 检查"
	@echo "  make lint-fix      使用 ruff 自动修复可修复 lint 问题"
	@echo "  make type-check    使用 mypy 执行类型检查"
	@echo "  make test          执行 pytest"
	@echo "  make test-cov      执行 pytest 并输出覆盖率"
	@echo "  make check         执行 lint、type-check、test"
	@echo "  make docker-build  构建本地 Docker 镜像"
	@echo "  make docker-local-check 构建、启动、联调、测试并清理本地 Docker 资源"

install:
	uv sync

hooks-install:
	uv run pre-commit install

hooks-run:
	uv run pre-commit run --all-files

format:
	uv run ruff format .

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check . --fix

type-check:
	uv run mypy src

test:
	uv run pytest

test-cov:
	uv run pytest --cov=app --cov-report=term-missing

check: lint type-check test

docker-build:
	docker build \
		--build-arg PYTHON_BASE_IMAGE=$(PYTHON_BASE_IMAGE) \
		--build-arg UV_BASE_IMAGE=$(UV_BASE_IMAGE) \
		-t backend:local .

docker-local-check:
	@set -e; \
	created_env=0; \
	postgres_image_exists=0; \
	redis_image_exists=0; \
	python_image_exists=0; \
	uv_image_exists=0; \
	docker image inspect postgres:16-alpine >/dev/null 2>&1 && postgres_image_exists=1 || true; \
	docker image inspect redis:7-alpine >/dev/null 2>&1 && redis_image_exists=1 || true; \
	docker image inspect "$(PYTHON_BASE_IMAGE)" >/dev/null 2>&1 && python_image_exists=1 || true; \
	docker image inspect "$(UV_BASE_IMAGE)" >/dev/null 2>&1 && uv_image_exists=1 || true; \
	cleanup() { \
		status=$$?; \
		BACKEND_IMAGE=backend:local-check docker compose down -v --remove-orphans >/dev/null 2>&1 || true; \
		docker image rm backend:local-check >/dev/null 2>&1 || true; \
		if [ "$$postgres_image_exists" = "0" ]; then docker image rm postgres:16-alpine >/dev/null 2>&1 || true; fi; \
		if [ "$$redis_image_exists" = "0" ]; then docker image rm redis:7-alpine >/dev/null 2>&1 || true; fi; \
		if [ "$$python_image_exists" = "0" ]; then docker image rm "$(PYTHON_BASE_IMAGE)" >/dev/null 2>&1 || true; fi; \
		if [ "$$uv_image_exists" = "0" ]; then docker image rm "$(UV_BASE_IMAGE)" >/dev/null 2>&1 || true; fi; \
		if [ "$$created_env" = "1" ]; then rm -f .env; fi; \
		exit $$status; \
	}; \
	trap cleanup EXIT INT TERM; \
	if [ ! -f .env ]; then cp .env.example .env; created_env=1; fi; \
	attempt=1; \
	until BACKEND_IMAGE=backend:local-check docker compose up -d --build; do \
		if [ "$$attempt" -ge 3 ]; then exit 1; fi; \
		BACKEND_IMAGE=backend:local-check docker compose down -v --remove-orphans >/dev/null 2>&1 || true; \
		attempt=$$((attempt + 1)); \
		echo "Docker Compose 构建启动失败，重试 $$attempt/3"; \
		sleep 3; \
	done; \
	i=0; \
	until curl -fsS http://127.0.0.1:8000/api/v1/health >/dev/null; do \
		i=$$((i + 1)); \
		if [ "$$i" -ge 30 ]; then echo "后端健康检查超时"; exit 1; fi; \
		sleep 1; \
	done; \
	curl -fsSI http://127.0.0.1:8000/docs >/dev/null; \
	BACKEND_IMAGE=backend:local-check docker compose exec -T redis redis-cli ping >/dev/null; \
	BACKEND_IMAGE=backend:local-check docker compose exec -T postgres pg_isready -U postgres -d backend >/dev/null; \
	BACKEND_IMAGE=backend:local-check docker compose config >/dev/null; \
	uv run mypy src; \
	uv run pytest
