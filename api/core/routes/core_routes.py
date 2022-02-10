from config import Settings, get_settings
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from neomodel import db

router = APIRouter(tags={"Core"}, prefix="/dev")


@router.get("/ping")
async def pong():
    return JSONResponse({"ping": "pong"})


@router.get("/env")
async def env(settings: Settings = Depends(get_settings)):
    return JSONResponse({
        "environment": settings.environment,
        "testing": settings.testing,
        "neo4j_host": settings.neo4j_host
    })


@router.get("/db")
async def db_test_endpoint():
    results, meta = db.cypher_query(
        'MERGE (n {name: "test"}) RETURN n', None)
    return results[0][0]  # Should return {"name": "test"}
