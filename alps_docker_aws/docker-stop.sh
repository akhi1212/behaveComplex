#!/bin/bash

echo "Removing Docker instances and volumes. Also delete the downloaded images to save space"
docker-compose down -v --rmi all --remove-orphans
docker-compose rm -f