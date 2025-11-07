# Makefile for autocare360-chatbot project

.PHONY: install build run stop clean db-init dev

# Install Python dependencies
install:
	pip install -r requirements.txt

# Build Docker image
build:
	docker-compose build

# Run the application with Docker
run:
	docker-compose up -d

# Stop the application
stop:
	docker-compose down

# Initialize database
db-init:
	docker-compose exec -T mysql mysql -u root -proot_password < docker/mysql/init/init-database.sql

# Clean up containers and images
clean:
	docker-compose down --volumes --remove-orphans
	docker system prune -f

# Development update after code changes: stop, clean, build, run, init DB
dev:
	make stop
	make clean
	make build
	make run
	make db-init