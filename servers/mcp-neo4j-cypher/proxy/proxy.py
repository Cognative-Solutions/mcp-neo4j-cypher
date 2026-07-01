import os
import logging
from flask import Flask, request, Response
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
TOKEN = os.environ.get("MCP_AUTH_TOKEN", "")
UPSTREAM = "http://neo4j-cypher.railway.internal:8000"

@app.route("/", defaults={"path": ""}, methods=["POST", "GET", "DELETE", "PUT"])
@app.route("/<path:path>", methods=["POST", "GET", "DELETE", "PUT"])
def proxy(path):
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {TOKEN}":
        return Response(
            '{"jsonrpc":"2.0","id":"auth-error","error":{"code":-32600,"message":"Unauthorized"}}',
            status=401,
            content_type="application/json"
        )

    url = f"{UPSTREAM}/{path}"
    if request.query_string:
        url += f"?{request.query_string.decode()}"

    logger.info(f"Forwarding {request.method} {url}")

    try:
        forward_headers = {
            "Content-Type": request.headers.get("Content-Type", "application/json"),
            "Accept": request.headers.get("Accept", "application/json, text/event-stream"),
        }

        resp = httpx.request(
            request.method,
            url,
            content=request.data,
            headers=forward_headers,
            timeout=60.0,
        )

        excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
        response_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}

        return Response(resp.content, status=resp.status_code, headers=response_headers)

    except httpx.ConnectError as e:
        logger.error(f"Connection error to {url}: {e}")
        return Response(
            '{"jsonrpc":"2.0","id":"proxy-error","error":{"code":-32600,"message":"Cannot connect to upstream MCP server"}}',
            status=502,
            content_type="application/json"
        )
    except Exception as e:
        logger.error(f"Proxy error: {type(e).__name__}: {e}")
        return Response(
            f'{{"jsonrpc":"2.0","id":"proxy-error","error":{{"code":-32600,"message":"Proxy error: {type(e).__name__}"}}}}',
            status=502,
            content_type="application/json"
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)