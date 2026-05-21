.PHONY: help install hooks-install hooks-run format lint lint-fix type-check test test-cov check docker-build

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
	docker build -t backend:local .
