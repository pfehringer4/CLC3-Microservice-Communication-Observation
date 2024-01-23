from typing import List
from fastapi import APIRouter, status, Path, HTTPException
from app.api import crud
from models.team import TeamSchema
from app.models.pydantic import TeamPayloadSchema, TeamResponseSchema
import asyncio
from opentelemetry import trace

router = APIRouter(prefix="/teams")
tracer = trace.get_tracer(__name__)

@router.get("/{id}/", response_model=TeamSchema)
async def get_team(id: int = Path(..., gt=0)) -> TeamSchema:
    with tracer.start_as_current_span("get-id"):
        with tracer.start_as_current_span("db-query-get-id"):
            team = await crud.get(id)
        with tracer.start_as_current_span("http-response-get-id"):
            if not team:
                raise HTTPException(status_code=404, detail="Team not found!")
            return team

    
@router.get("/", response_model=List[TeamSchema])
async def get_all_teams() -> List[TeamSchema]:
    with tracer.start_as_current_span("get-all"):
        with tracer.start_as_current_span("db-query-get-all"):
            # simulate a delay in the db operation
            # await asyncio.sleep(10) # simulated bug
            teams = await crud.get_all()
        with tracer.start_as_current_span("http-response-get-all"):
            # Simulate a delay in the HTTP response
            await asyncio.sleep(10)
            return teams


@router.post("/", response_model=TeamResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_team(payload: TeamPayloadSchema) -> TeamResponseSchema:
    with tracer.start_as_current_span("post"):
        with tracer.start_as_current_span("db-query-post-team"):
            team_id = await crud.post(payload)
        with tracer.start_as_current_span("http-response-post-team"):
            return {"id": team_id, "name": payload.name}


@router.delete("/{id}/")
async def delete_team(id: int = Path(..., gt=0)) -> int:
    team = await crud.get(id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found!")
    await crud.delete(id)
    return id


@router.put("/{id}/", response_model=TeamSchema)
async def update_team(payload: TeamPayloadSchema, id: int = Path(..., gt=0)) -> TeamSchema:
    team = await crud.put(id, payload)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found!")
    return team
