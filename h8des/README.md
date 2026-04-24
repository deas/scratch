```bash
USERNAME=
PASSWORD=
FQN=
DEPLOYMENT_NAME=
DEPLOYMENT_ID=
TOKEN=

curl -X 'POST' \
  "https://${FQN}/csp/gateway/am/api/login?access_token=thing" \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "${USERNAME}",
  "password": "${PASSWORD}"
}'


curl -X 'GET' \
  "https://${FQN}/deployment/api/deployments?page=0&size=20&sort=&name=${DEPLOYMENT_NAME}&%24top=1" \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer ${TOKEN}'

curl -X 'GET' \
  "https://${FQN}/deployment/api/deployments/${DEPLOYMENT_ID}/resources?page=0&size=20&sort= \
  -H "accept: application/json" \
  -H "Authorization: Bearer ${TOKEN}"

```

## Exposed Metrics

The exporter exposes VPC quota metrics based on data retrieved from the VMware Aria API.

| Metric name | Description | Labels |
|---|---|---|
| `h8des_vpc_vm_quota_cpu_cores` | VM CPU quota in cores | `vpc_name`, `vpc_id` |
| `h8des_vpc_vm_quota_memory_mb` | VM memory quota in MB | `vpc_name`, `vpc_id` |
| `h8des_vpc_s3_storage_quota_mb` | S3 storage quota in MB | `vpc_name`, `vpc_id` |
| `h8des_vpc_vm_quota_storage_mb` | VM storage quota in MB | `vpc_name`, `vpc_id` |
| `h8des_vpc_file_storage_quota_mb` | File storage quota in MB | `vpc_name`, `vpc_id` |
| `h8des_vpc_namespace_quota_cpu_mhz` | Namespace CPU quota in MHz | `vpc_name`, `vpc_id` |
| `h8des_vpc_namespace_quota_memory_mb` | Namespace memory quota in MB | `vpc_name`, `vpc_id` |
| `h8des_vpc_namespace_quota_storage_mb` | Namespace storage quota in MB | `vpc_name`, `vpc_id` |
