#!/bin/bash

function items_json() {
  ## customer/type/instance
  local ctx
  local item
  local entries
  local fields
  ctx=$1
  item=$2
  fields=$3
  # set -x
  entries=$(kubectl --context $ctx get $item --all-namespaces -o json |
    jq -r '.items[] | "'$fields"\"" 2>/dev/null | paste -sd ',' -)
  # jq -r '.items[] | "\"\(.metadata.name)\":{\"namespace\":\"\(.metadata.namespace)\"}"' 2>/dev/null | paste -sd ',' -)
  if [ -n "$entries" ]; then
    echo "{${entries}}"
    # result="${result}\"$item_type\":{${entries}}}"
  else
    echo "{}"
    # result="${result}\"$item_type\":{}}"
  fi
}
fields='\"\(.metadata.name)\":{\"namespace\":\"\(.metadata.namespace)\"}'
# echo $fields
for c in kind-kind; do
  cat <<EOF
{"$c": {
  "adb":$(items_json $c svc $fields),
  "bdb":$(items_json $c svc $fields)
  }
}
EOF
done
