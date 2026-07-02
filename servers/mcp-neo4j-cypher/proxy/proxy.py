import os
import logging
from urllib.parse import urljoin
from flask import Flask, request, Response
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TOKEN = os.environ["MCP_AUTH_TOKEN"]
UPSTREAM = os.environ["UPSTREAM_MCP_URL"]

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def proxy(path):
    auth = request.headers.get("Authorization", "")
    x_api_key = request.headers.get("X-API-Key", "")

    if auth != f"Bearer {TOKEN}" and x_api_key != TOKEN:
        return Response(
            '{"jsonrpc":"2.0","id":"auth-error","error":{"code":-32600,"message":"Unauthorized"}}',
            status=401,
            content_type="application/json"
        )

    forwarded_path = path or ""
    if forwarded_path == "mcp":
        forwarded_path = ""
    elif forwarded_path.startswith("mcp/"):
        forwarded_path = forwarded_path[4:]

    url = urljoin(UPSTREAM, forwarded_path)
    if request.query_string:
        url += f"?{request.query_string.decode()}"

    try:
        forward_headers = {
            "Accept": request.headers.get("Accept", "application/json, text/event-stream"),
        }

        if request.headers.get("Content-Type"):
            forward_headers["Content-Type"] = request.headers["Content-Type"]

        resp = httpx.request(
            request.method,
            url,
            content=request.get_data(),
            headers=forward_headers,
            timeout=60.0,
        )

        excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
        response_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}

        return Response(resp.content, status=resp.status_code, headers=response_headers)

    except httpx.ConnectError:
        return Response(
            '{"jsonrpc":"2.0","id":"proxy-error","error":{"code":-32600,"message":"Cannot connect to upstream MCP server"}}',
            status=502,
            content_type="application/json"
        )
    except Exception as e:
        logger.exception("Proxy error")
        return Response(
            f'{{"jsonrpc":"2.0","id":"proxy-error","error":{{"code":-32600,"message":"Proxy error: {type(e).__name__}"}}}}',
            status=502,
            content_type="application/json"
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)