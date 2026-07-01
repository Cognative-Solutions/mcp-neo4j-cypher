FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir "mcp-neo4j-cypher==0.6.0"

# Transport defaults (safe to hardcode in Dockerfile)
ENV NEO4J_TRANSPORT=http
ENV NEO4J_MCP_SERVER_HOST=0.0.0.0
ENV NEO4J_MCP_SERVER_PORT=8000
ENV NEO4J_MCP_SERVER_PATH=/api/mcp/

# Production defaults (override in Railway Variables if needed)
ENV NEO4J_READ_ONLY=true
ENV NEO4J_RESPONSE_TOKEN_LIMIT=4000
ENV NEO4J_READ_TIMEOUT=30

EXPOSE 8000

CMD ["mcp-neo4j-cypher"]