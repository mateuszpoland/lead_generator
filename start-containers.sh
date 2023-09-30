#!/bin/bash

# Start the infrastructure containers
docker-compose -f docker-compose.yaml up
if [ $? -ne 0 ]; then
    echo "Failed to start the infrastructure containers."
    exit 1
fi

cd generate_leads_interface || exit
# Start the application containers
docker-compose up
# Print a message indicating that all containers have been started
echo "All containers have been started."