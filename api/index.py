from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import asyncio

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="JARVIS Brain API", description="Module Identification API")

# Define request/response models
class QueryRequest(BaseModel):
    query: str

class ModuleResponse(BaseModel):
    user_query: str
    module: str
    possible_modules: List[str]
    status: str

class HealthResponse(BaseModel):
    status: str
    message: str

# Define all possible modules
POSSIBLE_MODULES = [
    "AUTOMATION",
    "AI_BASED", 
    "VISION",
    "MEMORY",
    "INTERNET",
    "SECURITY",
    "UNKNOWN"
]

# Module descriptions for documentation
MODULE_DESCRIPTIONS = {
    "AUTOMATION": "Email, messages, scheduling, file operations, scripts, workflows",
    "AI_BASED": "Text generation, summarization, translation, code generation, analysis",
    "VISION": "Image recognition, object detection, OCR, face recognition, video analysis",
    "MEMORY": "Information storage, recall, preferences, context retention",
    "INTERNET": "Web search, data scraping, news, real-time information",
    "SECURITY": "Password management, encryption, authentication, monitoring",
    "UNKNOWN": "Queries that don't fit any category or are unclear"
}

# Initialize Groq LLM (with error handling)
try:
    llm = ChatGroq(
        temperature=0,
        model_name="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
except Exception as e:
    print(f"Error initializing LLM: {e}")
    llm = None

# Node 1: Module Identifier
def module_identifier_node(query: str) -> str:
    if llm is None:
        return "UNKNOWN"
    
    system_prompt = SystemMessage(content="""You are JARVIS, an AI assistant that identifies which module a user's query belongs to.

Your task is to classify the user's query into ONE of these modules:

1. "AUTOMATION" - Tasks like:
   - Sending emails, messages, or notifications
   - Scheduling events or reminders
   - Automating file operations
   - Running scripts or commands
   - Setting up workflows
   - Any task that involves automation of processes

2. "AI_BASED" - Tasks like:
   - Text generation or writing
   - Summarization or analysis
   - Translation between languages
   - Code generation or debugging
   - Creative writing or content creation
   - Data analysis or predictions
   - Any task that requires AI/ML capabilities

3. "VISION" - Tasks like:
   - Image recognition or classification
   - Object detection in images/videos
   - OCR (text extraction from images)
   - Face recognition
   - Video analysis
   - Any task involving visual processing

4. "MEMORY" - Tasks like:
   - Remembering information for later
   - Recalling past conversations
   - Storing user preferences
   - Contextual recall of previous interactions
   - Any task that requires memory storage/retrieval

5. "INTERNET" - Tasks like:
   - Searching the web for information
   - Scraping data from websites
   - Checking news or updates
   - Retrieving real-time information
   - Any task that requires internet access

6. "SECURITY" - Tasks like:
   - Password management
   - Encryption or decryption
   - Authentication or authorization
   - Security monitoring
   - Vulnerability checking
   - Any task related to security

7. "UNKNOWN" - Tasks that don't fit any of the above or are unclear

IMPORTANT RULES:
- Select ONLY ONE module that BEST fits the query
- If multiple modules could apply, choose the PRIMARY one
- Respond in this exact format: "MODULE: [module_name]"
- Do not add any other text or explanation
- Keep the module name exactly as written above (UPPERCASE)""")
    
    user_prompt = HumanMessage(content=f"User Query: {query}")
    
    try:
        response = llm.invoke([system_prompt, user_prompt])
        module_name = response.content.strip().replace("MODULE:", "").strip()
        
        # Ensure valid module name
        if module_name not in POSSIBLE_MODULES:
            module_name = "UNKNOWN"
    except Exception as e:
        print(f"Error in LLM invocation: {e}")
        module_name = "UNKNOWN"
    
    return module_name

# Root endpoint - API info
@app.get("/")
async def root():
    return {
        "name": "JARVIS Brain API",
        "version": "1.0.0",
        "description": "Module Identification API for JARVIS",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "API information"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/identify", "method": "POST", "description": "Identify module for a query"},
            {"path": "/modules", "method": "GET", "description": "List all possible modules"}
        ]
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    status = "healthy" if llm is not None else "degraded"
    return HealthResponse(
        status=status,
        message="API is running" if llm else "LLM not initialized - check GROQ_API_KEY"
    )

# Get all possible modules
@app.get("/modules")
async def get_modules():
    return {
        "possible_modules": POSSIBLE_MODULES,
        "module_descriptions": MODULE_DESCRIPTIONS,
        "count": len(POSSIBLE_MODULES)
    }

# Identify module endpoint
@app.post("/identify", response_model=ModuleResponse)
async def identify_module(request: QueryRequest):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Process query
        query = request.query.strip()
        module = module_identifier_node(query)
        
        return ModuleResponse(
            user_query=query,
            module=module,
            possible_modules=POSSIBLE_MODULES,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Vercel serverless handler
async def handler(request, *args, **kwargs):
    """Vercel serverless function handler"""
    from fastapi.responses import JSONResponse
    
    # Handle OPTIONS for CORS
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )
    
    # Regular request handling
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # This is for Vercel serverless
    return await app(request, *args, **kwargs)

# Export for Vercel serverless
app = app
