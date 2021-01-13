#!/bin/bash
set -e

#python ./update_docker_compose.py | true

docker-compose down -v
docker-compose pull
docker-compose up -d
