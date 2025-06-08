# Makefile for MCP Server Docker Operations
# Usage: make <target>

# Variables
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_TEST = docker-compose -f docker-compose.yml -f docker-compose.test.yml
PROJECT_NAME = mcp-db-server
BUILD_DATE = $(shell date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF = $(shell git rev-parse --short HEAD)
VERSION = $(shell git describe --tags --always --dirty)

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help build up down logs clean test lint security-scan production-build

# Default target
help: ## Show this help message
	@echo "$(BLUE)MCP Server Docker Operations$(NC)"
	@echo "$(YELLOW)Usage: make <target>$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Development targets
build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build --build-arg BUILD_DATE=$(BUILD_DATE) --build-arg VCS_REF=$(VCS_REF) --build-arg VERSION=$(VERSION)

up: ## Start all services
	@echo "$(BLUE)Starting all services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Services started successfully!$(NC)"
	@echo "$(YELLOW)MCP Server: http://localhost:8000$(NC)"
	@echo "$(YELLOW)Health Check: http://localhost:8000/health$(NC)"

down: ## Stop and remove all containers
	@echo "$(BLUE)Stopping all services...$(NC)"
	$(DOCKER_COMPOSE) down -v
	@echo "$(GREEN)Services stopped successfully!$(NC)"

restart: down up ## Restart all services

logs: ## Show logs from all services
	$(DOCKER_COMPOSE) logs -f

logs-server: ## Show logs from MCP server only
	$(DOCKER_COMPOSE) logs -f mcp-server

status: ## Show status of all services
	$(DOCKER_COMPOSE) ps

# Testing targets
test: ## Run all tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(DOCKER_COMPOSE_TEST) up --build --exit-code-from test-runner test-runner
	$(DOCKER_COMPOSE_TEST) down -v

test-load: ## Run load tests
	@echo "$(BLUE)Running load tests...$(NC)"
	$(DOCKER_COMPOSE_TEST) up --build --exit-code-from load-tester load-tester
	$(DOCKER_COMPOSE_TEST) down -v

test-unit: ## Run unit tests locally
	@echo "$(BLUE)Running unit tests...$(NC)"
	python -m pytest tests/unit/ -v

# Code quality targets
lint: ## Run code linting
	@echo "$(BLUE)Running code linting...$(NC)"
	python -m black --check .
	python -m isort --check-only .
	python -m flake8 --max-line-length=100 --ignore=E203,W503 .

lint-fix: ## Fix code formatting
	@echo "$(BLUE)Fixing code formatting...$(NC)"
	python -m black .
	python -m isort .

type-check: ## Run type checking
	@echo "$(BLUE)Running type checking...$(NC)"
	python -m mypy . --ignore-missing-imports

security-scan: ## Run security scans
	@echo "$(BLUE)Running security scans...$(NC)"
	python -m safety check
	python -m bandit -r . -f json -o bandit-report.json
	@echo "$(GREEN)Security scan completed!$(NC)"

# Production targets
production-build: ## Build production-ready image
	@echo "$(BLUE)Building production image...$(NC)"
	docker build \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		--build-arg VCS_REF=$(VCS_REF) \
		--build-arg VERSION=$(VERSION) \
		--target runtime \
		-t $(PROJECT_NAME):$(VERSION) \
		-t $(PROJECT_NAME):latest \
		.
	@echo "$(GREEN)Production image built successfully!$(NC)"

production-push: production-build ## Build and push production image to registry
	@echo "$(BLUE)Pushing production image to registry...$(NC)"
	docker tag $(PROJECT_NAME):$(VERSION) your-registry.com/$(PROJECT_NAME):$(VERSION)
	docker tag $(PROJECT_NAME):latest your-registry.com/$(PROJECT_NAME):latest
	docker push your-registry.com/$(PROJECT_NAME):$(VERSION)
	docker push your-registry.com/$(PROJECT_NAME):latest
	@echo "$(GREEN)Production image pushed successfully!$(NC)"

# Database operations
db-reset: ## Reset all databases (WARNING: destroys all data)
	@echo "$(RED)WARNING: This will destroy all database data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)Resetting databases...$(NC)"; \
		$(DOCKER_COMPOSE) down -v; \
		docker volume prune -f; \
		$(DOCKER_COMPOSE) up -d; \
		echo "$(GREEN)Databases reset successfully!$(NC)"; \
	else \
		echo "$(YELLOW)Operation cancelled.$(NC)"; \
	fi

db-backup: ## Backup all databases
	@echo "$(BLUE)Creating database backups...$(NC)"
	mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	$(DOCKER_COMPOSE) exec postgres pg_dumpall -U postgres > backups/$(shell date +%Y%m%d_%H%M%S)/postgres_backup.sql
	$(DOCKER_COMPOSE) exec mongodb mongodump --archive > backups/$(shell date +%Y%m%d_%H%M%S)/mongodb_backup.archive
	@echo "$(GREEN)Database backups created successfully!$(NC)"

# Monitoring and debugging
health-check: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@curl -f http://localhost:8000/health && echo "$(GREEN)MCP Server: Healthy$(NC)" || echo "$(RED)MCP Server: Unhealthy$(NC)"
	@$(DOCKER_COMPOSE) exec postgres pg_isready -U postgres && echo "$(GREEN)PostgreSQL: Healthy$(NC)" || echo "$(RED)PostgreSQL: Unhealthy$(NC)"
	@$(DOCKER_COMPOSE) exec redis redis-cli ping && echo "$(GREEN)Redis: Healthy$(NC)" || echo "$(RED)Redis: Unhealthy$(NC)"
	@$(DOCKER_COMPOSE) exec mongodb mongosh --eval "db.adminCommand('ping')" && echo "$(GREEN)MongoDB: Healthy$(NC)" || echo "$(RED)MongoDB: Unhealthy$(NC)"
	@curl -f http://localhost:8086/ping && echo "$(GREEN)InfluxDB: Healthy$(NC)" || echo "$(RED)InfluxDB: Unhealthy$(NC)"

stats: ## Show resource usage statistics
	@echo "$(BLUE)Container resource usage:$(NC)"
	docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Cleanup targets
clean: ## Clean up Docker resources
	@echo "$(BLUE)Cleaning up Docker resources...$(NC)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f
	docker volume prune -f
	@echo "$(GREEN)Cleanup completed!$(NC)"

clean-all: ## Clean up everything including images
	@echo "$(RED)WARNING: This will remove all Docker images and containers!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)Cleaning up everything...$(NC)"; \
		$(DOCKER_COMPOSE) down -v --remove-orphans; \
		docker system prune -a -f; \
		docker volume prune -f; \
		echo "$(GREEN)Complete cleanup finished!$(NC)"; \
	else \
		echo "$(YELLOW)Operation cancelled.$(NC)"; \
	fi

# Development helpers
shell: ## Open shell in MCP server container
	$(DOCKER_COMPOSE) exec mcp-server /bin/bash

shell-postgres: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) exec postgres psql -U postgres

shell-mongodb: ## Open MongoDB shell
	$(DOCKER_COMPOSE) exec mongodb mongosh

shell-redis: ## Open Redis shell
	$(DOCKER_COMPOSE) exec redis redis-cli

# Environment setup
setup-dev: ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	python -m pip install -e .
	python -m pip install black isort flake8 mypy pytest pytest-asyncio safety bandit
	@echo "$(GREEN)Development environment setup completed!$(NC)"

# Information targets
info: ## Show project information
	@echo "$(BLUE)MCP Server Project Information$(NC)"
	@echo "$(YELLOW)Project Name:$(NC) $(PROJECT_NAME)"
	@echo "$(YELLOW)Version:$(NC) $(VERSION)"
	@echo "$(YELLOW)Build Date:$(NC) $(BUILD_DATE)"
	@echo "$(YELLOW)VCS Ref:$(NC) $(VCS_REF)"
	@echo "$(YELLOW)Docker Compose:$(NC) $(shell $(DOCKER_COMPOSE) version --short)"
	@echo "$(YELLOW)Docker:$(NC) $(shell docker version --format '{{.Server.Version}}')"

# Quick start
quick-start: build up health-check ## Quick start: build, start services, and check health
	@echo "$(GREEN)MCP Server is ready!$(NC)"
	@echo "$(YELLOW)Try: curl http://localhost:8000/health$(NC)"
