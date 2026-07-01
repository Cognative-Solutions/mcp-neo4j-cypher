FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir "mcp-neo4j-cypher"
ENV NEO4J_TRANSPORT=http
ENV NEO4J_MCP_SERVER_HOST=0.0.0.0
ENV NEO4J_MCP_SERVER_PORT=8000
ENV NEO4J_MCP_SERVER_PATH=/api/mcp/
EXPOSE 8000
CMD ["mcp-neo4j-cypher"]