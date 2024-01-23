import logging
import os 

from fastapi import FastAPI

from app.api import pokemon
from app.db import init_db

# OpenTelemetry Imports
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


# Initialize OpenTelemetry
trace.set_tracer_provider(
    TracerProvider(
            resource=Resource.create({SERVICE_NAME: "pokemon-service"})
        )
)

tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name=os.getenv("JAEGER_HOST", "localhost"),
    agent_port=int(os.getenv("JAEGER_PORT", 6831)),
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

def create_application() -> FastAPI:
    application = FastAPI(
        openapi_url="/pokemon/openapi.json",
        docs_url="/pokemon/docs")
    application.include_router(
        pokemon.router,
        tags=["pokemon"])
    
    # Instrument FastAPI app with OpenTelemetry
    FastAPIInstrumentor.instrument_app(application)

    return application


app = create_application()
log = logging.getLogger("uvicorn")


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
