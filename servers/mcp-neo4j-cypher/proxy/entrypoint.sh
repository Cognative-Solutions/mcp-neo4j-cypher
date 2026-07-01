#!/bin/sh
sed -i "s|__MCP_AUTH_TOKEN__|${MCP_AUTH_TOKEN}|" /etc/nginx/conf.d/default.conf
nginx -g "daemon off;"