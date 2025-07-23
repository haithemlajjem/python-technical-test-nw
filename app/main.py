from fastapi import FastAPI
from routes.group import router as group_router
from routes.site import router as site_router

app = FastAPI(title="Python Technical Test")

# Routers
app.include_router(site_router)
app.include_router(group_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Python Technical Test API"}
