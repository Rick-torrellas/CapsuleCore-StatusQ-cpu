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