

# Summary of Research & Lessons Learned

- **Introduction to OpenTelemetry**:
  - OpenTelemetry is a valuable tool used for gathering essential data such as traces, metrics, and logs from software applications.
  - It offers flexibility by supporting multiple programming languages and frameworks.
  - OpenTelemetry can be configured either automatically or manually, making it adaptable to various systems and requirements.
  - The collected data is sent to platforms like Jaeger for further analysis and visualization.

- **Introduction to Jaeger**:
  - Jaeger serves as a comprehensive observability platform designed for tracking and monitoring the flow of operations in distributed software systems.
  - It plays a crucial role in identifying performance bottlenecks, troubleshooting issues, and understanding dependencies between different services.
  - Jaeger seamlessly integrates with OpenTelemetry, providing a centralized location for storing, visualizing, and analyzing telemetry data.

- **Integration Possibilities**:
  - OpenTelemetry offers a wide array of integration possibilities:
    - It supports various programming languages, including Java, Python, .NET, and more.
    - It is compatible with major cloud platforms such as AWS, Azure, and Google Cloud.
    - Integration libraries are available for databases, messaging systems, and middleware.
  - Jaeger offers different components, including jaeger-all-in-one, jaeger-collector, and jaeger-query/service UI, making it versatile for different integration scenarios.

- **Key Takeaways**:
  - The presentation emphasized several key takeaways and lessons learned:
    - The flexibility of OpenTelemetry in adapting to diverse software environments.
    - The benefits of automatic instrumentation for collecting telemetry data.
    - The effectiveness of Jaeger All-in-One for local testing and debugging purposes.
    - The use of tracing as a powerful tool for bug identification and understanding complex software interactions.


# Integrating Jaeger  and OpenTelemtry into an existing Microservice Architecture

## Overview
This guide provides step-by-step instructions for integrating Jaeger into an existing Docker-compose setup, and explains the manual instrumentation of OpenTelemetry in the 'teams' service, along with automatic instrumentation in the 'pokemon' service.


## Jaeger Integration

### Step 1: Cloning the Repository
```bash
git clone https://github.com/GavriloviciEduard/fastapi-microservices
cd fastapi-microservices
```

### Step 2: Update Docker-compose File for Jaeger
Ensure your `docker-compose.yml` includes Jaeger as shown:

```yaml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
```

### Step 3: Linking Jaeger with Other Services
Ensure your application services are configured to communicate with Jaeger for tracing. For example, in your services, include environment variables like `JAEGER_HOST` and `JAEGER_PORT`:

```yaml
  pokemon-service:
    environment:
      - JAEGER_HOST=jaeger
      - JAEGER_PORT=6831
    # other configurations...

  team-service:
    environment:
      - JAEGER_HOST=jaeger
      - JAEGER_PORT=6831
    # other configurations...
```


## OpenTelemetry Integration

### Manual Instrumentation in the Teams Service

#### Install OpenTelemetry and Jaeger packages in Dockerfile
```
# Install OpenTelemetry and Jaeger packages
RUN pip install opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-instrumentation-fastapi \
    opentelemetry-instrumentation-tortoiseorm\
    opentelemetry-instrumentation-httpx \
    opentelemetry-exporter-jaeger
```

#### Setup in main.py
```python
# Import statements
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initializing Tracer Provider
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "team-service"}))
)

# Jaeger Exporter
jaeger_exporter = JaegerExporter(
    agent_host_name=os.getenv("JAEGER_HOST", "localhost"),
    agent_port=int(os.getenv("JAEGER_PORT", 6831)),
)

# Span Processor
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
```

#### Instrumenting the Teams Service in teams.py
```python
from opentelemetry import trace

# Tracer
tracer = trace.get_tracer(__name__)

# Example of a traced function
@router.get("/{id}/")
async def get_team(id: int):
    with tracer.start_as_current_span("get-id"):
        # Function logic
```

### Automatic Instrumentation in the Pokemon Service

#### Install OpenTelemetry and Jaeger packages in Dockerfile
```
# Install OpenTelemetry and Jaeger packages
RUN pip install opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-instrumentation-fastapi \
    opentelemetry-instrumentation-tortoiseorm\
    opentelemetry-instrumentation-httpx \
    opentelemetry-exporter-jaeger
```

#### Setup in main.py
```python
# Import statements
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Osame setup of tracing provider, jaeger exporter, ... as in manual instrumentation

# Instrumenting FastAPI app
FastAPIInstrumentor.instrument_app(application)
```

#### Instrumenting Database Operations in db.py
```python
from opentelemetry.instrumentation.tortoiseorm import TortoiseORMInstrumentor

# Tortoise ORM setup...

# Instrumenting Tortoise ORM
TortoiseORMInstrumentor().instrument()
```

#### Instrumenting HTTP Client Requests in interservice.py
```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# Instrumenting HTTPX client
HTTPXClientInstrumentor().instrument()
```

## Verifying and Using the Setup



### Step 1: Starting Services with Docker Compose
To start all services including Jaeger, run:
```bash
docker-compose up -d
```
### Step 2: Making Requests
Interact with your services as usual. 

The Swagger UI for the Pokemon Service is accessible at `http://localhost:8080/pokemon/docs`.

The Swagger UI for the Pokemon Service is accessible at `http://localhost:8080/teams/docs`.


### Step 3: Accessing Jaeger UI
The Jaeger UI is accessible at `http://localhost:16686`.


## Conclusion
You have now integrated Jaeger into your Docker-compose setup and added both manual and automatic OpenTelemetry instrumentation to your services. This enables powerful insights into your microservices architecture.
