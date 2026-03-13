#!/bin/bash

# Check if root key argument is provided
if [ $# -eq 0 ]; then
	echo "Usage: $0 <root_key>" >&2
	exit 1
fi

ROOT_KEY="$1"

# Initialize JSON structure
result="{\"$ROOT_KEY\":{"

# Get services from all namespaces
services_json=$(kubectl get services --all-namespaces -o json 2>/dev/null)
if [ $? -eq 0 ]; then
	services_entries=$(echo "$services_json" | jq -r '.items[] | "\"\(.metadata.name)\":{\"namespace\":\"\(.metadata.namespace)\"}"' 2>/dev/null | paste -sd ',' -)
	if [ -n "$services_entries" ]; then
		result="${result}\"services\":{${services_entries}}"
	else
		result="${result}\"services\":{}"
	fi
else
	result="${result}\"services\":{}"
fi

# Add comma between resource types
result="${result},"

# Get deployments from all namespaces
deployments_json=$(kubectl get deployments --all-namespaces -o json 2>/dev/null)
if [ $? -eq 0 ]; then
	deployments_entries=$(echo "$deployments_json" | jq -r '.items[] | "\"\(.metadata.name)\":{\"namespace\":\"\(.metadata.namespace)\"}"' 2>/dev/null | paste -sd ',' -)
	if [ -n "$deployments_entries" ]; then
		result="${result}\"deployments\":{${deployments_entries}}"
	else
		result="${result}\"deployments\":{}"
	fi
else
	result="${result}\"deployments\":{}"
fi

# Close JSON structure
result="${result}}}"

# Output formatted JSON
echo "$result" | jq .
