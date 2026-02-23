# AI Restaurant Recommendation Service – Infrastructure

Docker-based deployment for the AI Restaurant Recommendation Service.

## Prerequisites

- Docker
- Docker Compose

## Setup

Run all commands from the `infrastructure/` directory:

```bash
cd infrastructure
```

1. Copy the example environment file and add your Groq API key:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set `GROQ_API_KEY` to your key.

## Build

```bash
make build
```

Or:

```bash
docker compose build
```

## Run Locally

```bash
make up
```

Or:

```bash
docker compose up -d
```

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Stop

```bash
make down
```

Or:

```bash
docker compose down
```

## Logs

```bash
make logs
```

Or:

```bash
docker compose logs -f
```

## Scaling

Scale backend instances:

```bash
docker compose up -d --scale backend=3
```

Note: Use a load balancer in front for production. The frontend nginx proxies `/api` to the backend service; scaling backend replicas works with the default Compose networking.

## Cloud Deployment

### AWS (ECS / EC2)

1. Build and push images to ECR.
2. Use ECS Task Definitions or EC2 with docker-compose.
3. Set `GROQ_API_KEY` in the task definition or environment.
4. Use ALB for HTTPS and routing.
5. Ensure the backend has access to load the Hugging Face dataset on first request.

### GCP (Cloud Run)

1. Build and push images to Artifact Registry.
2. Deploy backend and frontend as separate Cloud Run services.
3. Configure the frontend service to proxy `/api` to the backend URL, or use the same-origin pattern.
4. Set `GROQ_API_KEY` as a Cloud Run secret.

### Azure (Container Apps)

1. Build and push images to ACR.
2. Create Container Apps for backend and frontend.
3. Use Azure Front Door or Application Gateway for routing.
4. Store `GROQ_API_KEY` in Key Vault and reference from Container App.

### General

- Run from the project root or ensure build contexts point to `ai-restaurant-recommender` and `frontend`.
- Use secrets management for `GROQ_API_KEY`.
- Configure health checks for the backend `/health` endpoint.
- Enable HTTPS in production.
