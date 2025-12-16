from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.endpoints import authors, books, categories


class NoCacheMiddleware(BaseHTTPMiddleware):
    """Middleware to disable caching for OpenAPI and docs endpoints"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path in ["/openapi.json", "/docs", "/redoc"]:
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0"
            )
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


app = FastAPI(
    title="Books Management API",
    description="API for managing books",
    version="1.0.0",
)

# Add middleware to disable caching for docs
app.add_middleware(NoCacheMiddleware)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routes
app.include_router(authors.router, prefix="/authors", tags=["Authors"])
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])

# Static files for cover images


@app.get("/")  # 127.0.0.1:5000
def read_root():
    return {"message": "Books Management API is running"}
