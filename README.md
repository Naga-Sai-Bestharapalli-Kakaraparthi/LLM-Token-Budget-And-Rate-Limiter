# LLM Token Budget & Rate Limiter

A high-performance Python/FastAPI microservice designed to enforce real-time token bucket rate limiting and budget control for AI agent workloads, preventing API token exhaustion and traffic spikes.

## Architectural Highlights
- **Token Bucket Algorithm:** Dynamically tracks user requests and replenishes token budgets over time based on elapsed intervals.
- **FastAPI Framework:** Lightweight, asynchronous API endpoints optimized for low-latency request interception.
- **Budget Enforcement:** Automatically blocks rogue scripts or excessive token consumption by returning structured HTTP 429 errors when thresholds are exceeded.
