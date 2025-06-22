import httpx
from fastapi import FastAPI, Request, Response
import os

app = FastAPI(title="API Gateway")

BOOKING_SERVICE_URL = os.environ.get("BOOKING_SERVICE_URL", "http://booking_service:8000")
INVENTORY_SERVICE_URL = os.environ.get("INVENTORY_SERVICE_URL", "http://inventory_service:8000")

client = httpx.AsyncClient()

async def _reverse_proxy(request: Request, service_url: str):
    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    rp_req = client.build_request(
        request.method, url, headers=request.headers.raw, content=await request.body()
    )
    # The service is internal, so we replace the host
    rp_req.url = httpx.URL(f"{service_url}{request.url.path}?{request.url.query}")

    rp_resp = await client.send(rp_req, stream=True)
    return Response(
        content=rp_resp.content,
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        media_type=rp_resp.headers.get("content-type"),
    )

@app.api_route("/booking/{path:path}")
async def booking_proxy(request: Request, path: str):
    return await _reverse_proxy(request, BOOKING_SERVICE_URL)

@app.api_route("/inventory/{path:path}")
async def inventory_proxy(request: Request, path: str):
    return await _reverse_proxy(request, INVENTORY_SERVICE_URL)

@app.get("/")
def read_root():
    return {"message": "API Gateway is running"} 