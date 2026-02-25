# Cargar variables desde el archivo .env si existe
set dotenv-load := true

# Comando por defecto
default:
    @just --list
# para construir el paquete
build:
    uv build
# para publicar el paquete en PyPI
publish:
    uv publish
# Run the test suite with verbose output using pytest
test:
	uv run pytest -v  
check: format-check lint-check
	# Run all code quality checks (formatting and linting)

format-check:
	# Check code formatting compliance without making changes
	# Exits with non-zero status if formatting issues are found
	uv run ruff format --check .

format:
	# Automatically format code according to ruff rules
	uv run ruff format .

lint-check:
	# Run linting checks to identify code quality issues without fixing
	uv run ruff check .
# Run linting checks and automatically fix issues where possible  
lint:
	uv run ruff check --fix .
# Generate a changelog from git commit history using git-chglog Output is saved to CHANGELOG.md
changelog:
	uv run gitchangelog > CHANGELOG.md