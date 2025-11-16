#!/bin/sh

echo "Waiting for backend services to be ready..."

# Function to check if a service is ready
wait_for_service() {
    local service_name=$1
    local max_attempts=30
    local attempt=1

    echo "Checking $service_name..."

    while [ $attempt -le $max_attempts ]; do
        if nslookup $service_name >/dev/null 2>&1; then
            echo "$service_name is resolvable"
            return 0
        fi

        echo "Attempt $attempt/$max_attempts: $service_name not ready yet, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "ERROR: $service_name not ready after $max_attempts attempts"
    return 1
}

# Wait for each service
wait_for_service "backend" || exit 1
wait_for_service "frontend" || exit 1
wait_for_service "ml-service" || exit 1

echo "All services are ready! Starting nginx..."