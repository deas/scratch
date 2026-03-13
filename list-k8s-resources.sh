#!/bin/bash

# Check if root key argument is provided
# if [ $# -eq 0 ]; then
#   echo "Usage: $0 <root_key>" >&2
#   exit 1
# fi

# ROOT_KEY="$1"

# Initialize JSON structure
# result="{\"$ROOT_KEY\":{"

function items_json() {
  ## customer/type/instance
  local ctx
  local result
  local item
  local entries
  local item_type
  local fields
  ctx=$1
  # result="{\"$ctx\":{"
  result="{"
  item=$2
  item_type=$3
  fields=$4
  # set -x
  entries=$(kubectl --context $ctx get $item --all-namespaces -o json |
    jq -r '.items[] | "'$fields"\"" 2>/dev/null | paste -sd ',' -)
  # jq -r '.items[] | "\"\(.metadata.name)\":{\"namespace\":\"\(.metadata.namespace)\"}"' 2>/dev/null | paste -sd ',' -)
  if [ -n "$entries" ]; then
    result="${result}\"$item_type\":{${entries}}}"
  else
    result="${result}\"$item_type\":{}}"
  fi
  echo "$result"
}
fields='\"\(.metadata.name)\":{\"namespace\":\"\(.metadata.namespace)\"}'
# echo $fields
for c in kind-kind; do
  bar=$(items_json $c svc srv $fields)
  echo $bar
done
# items_json kind-kind svc srv $fields
# items_json r deployment $fields
# echo $(items_json s svc "foo")
# echo $result
# # Add comma between resource types
# result="${result},"
#
# # Get deployments from all namespaces
# deployments_json=$(kubectl get deployments --all-namespaces -o json 2>/dev/null)
# if [ $? -eq 0 ]; then
#   deployments_entries=$(echo "$deployments_json" | jq -r '.items[] | "\"\(.metadata.name)\":{\"namespace\":\"\(.metadata.namespace)\"}"' 2>/dev/null | paste -sd ',' -)
#   if [ -n "$deployments_entries" ]; then
#     result="${result}\"deployments\":{${deployments_entries}}"
#   else
#     result="${result}\"deployments\":{}"
#   fi
# else
#   result="${result}\"deployments\":{}"
# fi
#
# # Close JSON structure
# result="${result}}}"
#
# # Output formatted JSON
# echo "$result" | jq .
