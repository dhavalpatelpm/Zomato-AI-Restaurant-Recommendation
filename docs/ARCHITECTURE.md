# AI Restaurant Recommendation Service
## Architecture Document

---

## 1. Executive Overview

The AI Restaurant Recommendation Service is a production-grade system that ingests restaurant data from a curated Hugging Face dataset, applies structured filtering based on user preferences, and leverages a Large Language Model (LLM) to generate ranked, contextual restaurant recommendations for Bangalore city. The system exposes a frontend with five distinct input components that map directly to backend filtering and recommendation logic. The architecture follows a phased, layered design with clear separation between data acquisition, processing, API services, and LLM inference.

---

## 2. System Goals

- Ingest and maintain restaurant data from the Hugging Face dataset (ManikaSaini/zomato-restaurant-recommendation) for Bangalore localities.
- Accept user preferences through five UI components: Select Locality, Price Range, Cuisines (Multi-select), Min Rating, and the Get Recommendations action.
- Perform structured filtering and optional vector search before LLM invocation to reduce token usage and latency.
- Produce clear, ranked restaurant recommendations with explanations via LLM.
- Support horizontal scaling, containerization, and cloud deployment.
- Provide observability through logging, metrics, and monitoring.

---

## 3. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND INTERACTION LAYER                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ ┌────────────┐          │
│  │ Select       │ │ Price        │ │ Cuisines         │ │ Min Rating │          │
│  │ Locality     │ │ Range        │ │ (Multi-select)   │ │            │          │
│  └──────┬───────┘ └──────┬───────┘ └────────┬─────────┘ └─────┬──────┘          │
│         │                │                  │                  │                 │
│         └────────────────┴──────────────────┴──────────────────┘                 │
│                                      │                                            │
│                         ┌────────────▼────────────┐                              │
│                         │ Get Recommendations     │                              │
│                         │ Button                  │                              │
│                         └────────────┬────────────┘                              │
└─────────────────────────────────────┼───────────────────────────────────────────┘
                                      │
                                      │ HTTP/HTTPS
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY                                          │
│  (Rate Limiting | Auth | Request Routing | TLS Termination)                       │
└─────────────────────────────────────┬───────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          BACKEND SERVICE LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  Request Handler: { locality, price_range, cuisines[], min_rating }      │    │
│  └─────────────────────────────────────┬───────────────────────────────────┘    │
└────────────────────────────────────────┼────────────────────────────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────────┐
│  DATA LAYER           │  │  EMBEDDING LAYER      │  │  CACHE LAYER              │
│  Hugging Face         │  │  Vector Store /       │  │  Recommendation Cache     │
│  Dataset Ingestion    │  │  Embedding Index      │  │  (Redis/Memcached)        │
└──────────┬────────────┘  └──────────┬────────────┘  └────────────┬──────────────┘
           │                          │                            │
           └──────────────────────────┼────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  STRUCTURED FILTERING & CANDIDATE RETRIEVAL                                       │
│  (Locality filter | Price filter | Cuisine filter | Min rating filter)            │
│  Optional: Vector similarity for semantic cuisine/locality matching               │
└─────────────────────────────────────┬───────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  LLM RECOMMENDATION ENGINE                                                        │
│  (Structured prompt | Ranked output | Explanation generation)                     │
└─────────────────────────────────────┬───────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  RESPONSE FORMATTING & RANKING                                                    │
│  (Validation | Normalization | API Response shaping)                              │
└─────────────────────────────────────┬───────────────────────────────────────────┘
                                      │
                                      ▼
                         Frontend (Ranked Recommendations Display)
```

---

## 4. Phase-Based Architecture Breakdown

### Phase 1: Data Acquisition

- **Source:** Hugging Face dataset at `https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation`
- **Mechanism:** Scheduled or on-demand ingestion via Hugging Face Datasets API
- **Scope:** Bangalore-specific restaurant records including locality, cuisines, price range, ratings, and metadata
- **Storage:** Persisted to structured storage (relational DB or document store) for querying
- **Refresh Strategy:** Periodic sync (e.g., daily/weekly) or event-driven on dataset update
- **Failure Handling:** Retry with backoff; alert on repeated ingestion failures

### Phase 2: Data Processing & Feature Engineering

- **Structured Fields:** Extract and normalize locality, price range, cuisines, rating for filtering
- **Embedding Generation:** Produce embeddings for restaurant names, cuisines, and descriptions using a chosen embedding model (e.g., sentence-transformers, OpenAI embeddings)
- **Vector Index:** Build and maintain a vector index (e.g., FAISS, Pinecone, pgvector) for semantic search
- **Data Quality:** Validation, deduplication, and handling of missing values
- **Metadata Enrichment:** Optional enrichment for ranking (e.g., popularity signals, review counts)

### Phase 3: API & Backend Service Layer

- **Request Contract:** Accept payload with `locality`, `price_range`, `cuisines` (array), `min_rating` corresponding to UI blocks
- **Validation:** Server-side validation of all five inputs; reject malformed or out-of-range values
- **API Gateway:** Central entry point for rate limiting, authentication, request routing, and TLS termination
- **Service Orchestration:** Coordinate filtering, embedding lookup (if used), and LLM call within a single request flow

### Phase 4: LLM Recommendation Engine

Groq LLM will be used as the primary inference engine.

- **Provider:** Groq LLM via Groq API
- **Rationale:** Ultra-low latency inference and high-speed generation to meet sub-second response requirements for recommendation requests
- **Integration:** API-based integration; backend service issues HTTP requests to Groq API endpoints; no self-hosted model deployment
- **Input:** Filtered candidate restaurants (from Phase 3) plus user preferences
- **Prompt Construction Pipeline:** System prompt (role, constraints, output schema) and user prompt (preferences, candidate list) assembled before Groq call; token truncation if context exceeds limit
- **Structured JSON Output:** Enforce structured JSON output via prompt instructions; parse and validate response schema on receipt
- **Error Handling:** Retry with exponential backoff on transient failures (5xx, rate limits); circuit breaker on sustained failures; fallback message on unrecoverable errors
- **Retry Logic:** Configurable max retries; idempotent request design; no duplicate recommendations on retry
- **Extensibility:** Provider abstraction layer to support future multi-LLM providers (e.g., OpenAI, Anthropic) without changing downstream consumers
- **Role:** Rank and explain recommendations; optionally summarize or personalize
- **Output:** Structured recommendation list with ranking, names, and reasoning

### Phase 5: Response Formatting & Ranking

- **Schema:** Enforce consistent JSON schema for recommendations
- **Normalization:** Map LLM output to API response format; handle parsing errors
- **Ranking:** Preserve or post-process LLM-provided order; optionally re-rank with deterministic rules

### Phase 6: Frontend Interaction Layer

Phase 6 includes the complete UI Page architecture and frontend service communication.

**UI Page:** AI Restaurant Recommendation Web Interface

The UI must include these blocks exactly:

- **Select Locality:** Dropdown populated from dataset localities; sends `locality` to backend
- **Price Range:** Dropdown with predefined ranges; sends `price_range` to backend
- **Cuisines (Multi-select):** Multi-select dropdown from dataset cuisines; sends `cuisines[]` array
- **Min Rating:** Numeric input with min/max bounds; sends `min_rating`
- **Get Recommendations Button:** Triggers API call with above four inputs

**UI to Backend API Interaction:** Frontend issues POST request to recommendation endpoint with JSON payload `{ locality, price_range, cuisines, min_rating }`; receives ranked recommendations with explanations; no direct LLM or dataset access from client.

**Form Validation Layer:** Client-side validation before submit; required fields (locality, price range) enforced; cuisines and min rating validated against allowed ranges; invalid submissions blocked with inline error messaging.

**Loading State Handling:** Disable form and button during request; show loading indicator; prevent duplicate submissions while in flight.

**Error State Handling:** Display user-facing error message on API failure (timeout, 4xx, 5xx); retain form values for retry; optional retry button; log errors for debugging.

**Recommendation Display Layout:** Dedicated results section below form; clear separation from input area; scrollable if many results.

**Ranked Results Display:** Ordered list (1, 2, 3, ...) with restaurant name, locality, price, rating; each item linkable or expandable for details.

**Explanation Display from LLM:** Each recommendation shows LLM-generated explanation or reasoning; displayed inline with ranked result or in expandable section.

**Responsive Design Support:** Layout adapts to mobile, tablet, desktop viewports; form stacks or reflows appropriately; touch-friendly controls.

**Future Scalability for Filters:** UI structure designed to accommodate additional filter blocks (e.g., dietary preferences, distance) without major refactor; extensible form schema and API contract.

### Phase 7: Deployment & Infrastructure

- **Containerization:** Application packaged in Docker images; multi-stage builds for minimal image size
- **Orchestration:** Kubernetes (EKS, GKE, AKS) or container service (ECS, Cloud Run) for scaling and resilience
- **Cloud:** AWS, GCP, or Azure for compute, storage, and managed services
- **Secrets:** API keys and credentials stored in cloud secret managers (e.g., AWS Secrets Manager, GCP Secret Manager)
- **Infrastructure as Code:** Terraform or CloudFormation for reproducible deployments
- **CI/CD:** Automated build, test, and deployment pipeline; run unit and integration tests before promotion; deploy to staging then production

### Phase 8: Monitoring & Logging

- **Logging:** Centralized logging (e.g., CloudWatch, Stackdriver, ELK); structured logs with request IDs and timestamps
- **Metrics:** Request latency, error rates, LLM token usage, cache hit ratio, ingestion status
- **Tracing:** Distributed tracing for request flow across API, filtering, and LLM
- **Alerting:** Alerts on high error rate, latency SLO breaches, and ingestion failures

---

## 5. LLM Integration Design

- **Abstraction:** LLM client abstraction supporting multiple providers and model types
- **Input Construction:** System prompt with dataset schema; user prompt with preferences and filtered candidate list
- **Token Management:** Truncate or summarize candidate list if exceeding model context; use structured output formats (JSON mode where supported)
- **Fallback:** Graceful degradation if primary LLM is unavailable
- **Cost Control:** Token budgeting per request; optional caching of similar recommendation responses

---

## 6. Prompt Engineering Strategy

- **System Prompt:** Define role (restaurant recommendation expert), output format (ranked list with explanations), and constraints (e.g., only recommend from provided list)
- **User Prompt:** Include locality, price range, cuisines, min rating, and the filtered restaurant set
- **Structure:** Explicit JSON or markdown structure for parsing; few-shot examples if needed for consistency
- **Versioning:** Prompt versions tracked for A/B testing and rollback
- **Evaluation:** Log inputs and outputs for quality evaluation and prompt iteration

---

## 7. Caching Strategy

- **Request-Level Cache:** Cache responses keyed by normalized `(locality, price_range, cuisines_sorted, min_rating)` to avoid redundant LLM calls
- **TTL:** Configurable TTL; shorter for dynamic data, longer for static recommendations
- **Cache Invalidation:** Invalidate on dataset refresh or manual flush
- **Storage:** Redis or Memcached for low-latency access
- **Embedding Cache:** Cache embeddings for restaurants to avoid recomputation

---

## 8. Scalability Strategy

- **Horizontal Scaling:** Stateless API and service instances; scale based on request volume
- **Async Processing:** Optional async path for heavy embedding or ingestion jobs
- **Database:** Indexed queries on locality, price range, cuisines, rating for fast filtering
- **Vector Search:** Use scalable vector DB for large datasets; approximate nearest neighbor for low latency
- **LLM:** Connection pooling and batch requests where supported; consider model-specific scaling (e.g., replicas)

---

## 9. Security & Validation Layer

- **Input Validation:** Validate locality, price range, cuisines, and min rating; reject injection patterns and oversized payloads
- **Authentication:** API key or OAuth for backend API; no sensitive data in frontend
- **Rate Limiting:** Per-user or per-IP limits at API gateway
- **Secrets:** No hardcoded keys; use environment variables or secret managers
- **Data Privacy:** Do not log PII; anonymize or hash where necessary for analytics

---

## 10. Future Enhancements

- **Personalization:** User history and preferences for personalized ranking
- **Real-Time Data:** Integration with live availability or wait times
- **Multi-City:** Extend beyond Bangalore with locality-aware data
- **Feedback Loop:** Collect user feedback on recommendations to improve ranking and prompts
- **A/B Testing:** Framework for testing prompt variants and model choices
- **GraphQL:** Optional GraphQL API for flexible frontend queries
- **Webhooks:** Notify external systems on dataset updates or recommendation events
