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
  -H 'Authorization: Bearer ${TOKEN}"

curl -X 'GET' \
  "https://${FQN}/deployment/api/deployments/${DEPLOYMENT_ID}/resources?page=0&size=20&sort= \
  -H "accept: application/json" \
  -H "Authorization: Bearer ${TOKEN}"

```
