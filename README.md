# JARVIS Brain API

A FastAPI-based module identification API for JARVIS assistant, deployable on Vercel.

## Features

- Module identification for user queries
- 7 possible modules: AUTOMATION, AI_BASED, VISION, MEMORY, INTERNET, SECURITY, UNKNOWN
- RESTful API endpoints
- CORS support for frontend integration

## API Endpoints

### GET /
Returns API information and available endpoints.

### GET /health
Health check endpoint.

### GET /modules
Returns all possible modules with descriptions:
```json
{
  "possible_modules": ["AUTOMATION", "AI_BASED", "VISION", "MEMORY", "INTERNET", "SECURITY", "UNKNOWN"],
  "module_descriptions": {...},
  "count": 7
}