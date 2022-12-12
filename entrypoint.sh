#!/bin/bash

cat << EOF > /opt/.env
API_TOKEN=${API_TOKEN}
CHAT_ID=${API_TOKEN}
IP_TO_CHECK=${API_TOKEN}
EOF

poetry run electricitybot