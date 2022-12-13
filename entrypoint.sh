#!/bin/bash
export PATH=${PATH}:~/.local/bin/

cat << EOF > /opt/.env
API_TOKEN=${API_TOKEN}
CHAT_ID=${API_TOKEN}
IP_TO_CHECK=${IP_TO_CHECK}
EOF

poetry run electricitybot