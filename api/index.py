from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="JARVIS Brain API", description="Module Identification API")

# Define request/response models
class QueryRequest(BaseModel):
    query: str

class ModuleResponse(BaseModel):
    user_query: str  # This will now contain the corrected/refined query
    module: str
    possible_modules: List[str]
    status: str
    ai_based: Optional[bool] = False  # New field to indicate if module is AI_BASED
    ai_response: Optional[str] = None  # New field for AI-generated response

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
        temperature=0.7,  # Increased for creative responses
        model_name="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
except Exception as e:
    print(f"Error initializing LLM: {e}")
    llm = None

# Function to generate AI response for AI_BASED modules
def generate_ai_response(query: str, refined_query: str) -> str:
    """Generate response for AI_BASED module queries"""
    
    if llm is None:
        return "AI service is not available. Please check GROQ_API_KEY configuration."
    
    # Different prompts based on query type
    system_prompt = SystemMessage(content="""You are JARVIS, an intelligent AI assistant. 
Your task is to directly fulfill the user's request without any explanation about modules or identification.

IMPORTANT RULES:
1. For story generation: Write a creative, engaging story based on the user's request
2. For poem generation: Write a beautiful poem matching the requested style/topic
3. For code generation: Provide working code with brief comments
4. For summarization: Provide a concise summary of the given text
5. For translation: Provide accurate translation
6. For general questions: Provide helpful, accurate answers
7. Be direct and conversational
8. Don't mention that you're identifying modules or anything about the API
9. Just fulfill the request naturally

Examples:
- User: "generate a short story about a dragon" → You: Write a short story about a dragon
- User: "write a poem about love" → You: Write a poem about love
- User: "what is artificial intelligence" → You: Explain AI simply
- User: "summarize this text: [text]" → You: Provide summary""")
    
    user_prompt = HumanMessage(content=f"User Request: {refined_query}\nOriginal Query: {query}\n\nFulfill this request directly:")
    
    try:
        response = llm.invoke([system_prompt, user_prompt])
        return response.content.strip()
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return f"I encountered an error while processing your request: {str(e)}"

# Function to correct spelling and refine query based on module
def refine_query(query: str, module: str) -> str:
    """Correct spelling mistakes and refine the query based on module type"""
    
    if llm is None:
        return query
    
    # Different refinement prompts based on module
    if module == "AUTOMATION":
        system_prompt = SystemMessage(content="""You are a query refiner for automation tasks.
Your job is to:
1. Correct any spelling mistakes in the user's query
2. Convert the query into a clear, actionable command without extra words like "I want to", "I need to", "please", etc.
3. Keep only the essential action and target

Examples:
- "i want to open chrome" → "open chrome"
- "i need to send email to john" → "send email to john"
- "please schedule meeting for tomorrow" → "schedule meeting for tomorrow"
- "can you close the calculator app" → "close calculator app"

Return ONLY the refined query, no additional text.""")

    elif module == "INTERNET":
        system_prompt = SystemMessage(content="""You are a query refiner for internet/search tasks.
Your job is to:
1. Correct any spelling mistakes in the user's query
2. Convert questions into direct search queries by removing question words (what, who, where, when, why, how)
3. Keep the core information need

Examples:
- "What is the capital of pakistan" → "capital of pakistan"
- "Who is the president of usa" → "president of usa"
- "Where is taj mahal located" → "taj mahal location"
- "How to make pizza" → "make pizza"

Return ONLY the refined query, no additional text.""")

    elif module == "AI_BASED":
        system_prompt = SystemMessage(content="""You are a query refiner for AI-based tasks.
Your job is to:
1. Correct any spelling mistakes in the user's query
2. Keep the original request for generation/creation
3. Make the request clear and specific

Examples:
- "generat a short story about a brave knight" → "generate a short story about a brave knight"
- "write me a poem about nature" → "write a poem about nature"
- "creat python code for calculator" → "create python code for a calculator"
- "sumarize this text: [text]" → "summarize this text: [text]"

Return ONLY the refined query, no additional text.""")

    else:
        # For other modules, just correct spelling mistakes
        system_prompt = SystemMessage(content="""You are a query refiner that corrects spelling and grammar mistakes.
Your job is to:
1. Correct any spelling mistakes in the user's query
2. Fix grammatical errors
3. Keep the original meaning intact

Examples:
- "what is teh captial of france" → "what is the capital of france"
- "tell me abot AI tecnology" → "tell me about AI technology"
- "how to progrm in python" → "how to program in python"

Return ONLY the corrected query, no additional text.""")

    user_prompt = HumanMessage(content=f"Original Query: {query}")
    
    try:
        response = llm.invoke([system_prompt, user_prompt])
        refined_query = response.content.strip()
        return refined_query if refined_query else query
    except Exception as e:
        print(f"Error refining query: {e}")
        return query

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

2. "AI_BASED" - Tasks like:
   - Text generation or writing (stories, poems, essays)
   - Summarization or analysis
   - Translation between languages
   - Code generation or debugging
   - Creative writing or content creation
   - Answering questions that need reasoning
   - Any request asking to "generate", "write", "create", "tell a story", "compose"

3. "VISION" - Tasks like:
   - Image recognition or classification
   - Object detection in images/videos
   - OCR (text extraction from images)
   - Face recognition
   - Video analysis

4. "MEMORY" - Tasks like:
   - Remembering information for later
   - Recalling past conversations
   - Storing user preferences
   - Contextual recall of previous interactions

5. "INTERNET" - Tasks like:
   - Searching the web for information
   - Scraping data from websites
   - Checking news or updates
   - Retrieving real-time information

6. "SECURITY" - Tasks like:
   - Password management
   - Encryption or decryption
   - Authentication or authorization
   - Security monitoring
   - Vulnerability checking

7. "UNKNOWN" - Tasks that don't fit any of the above or are unclear

IMPORTANT RULES:
- Select ONLY ONE module that BEST fits the query
- Respond in this exact format: "MODULE: [module_name]"
- Do not add any other text or explanation""")
    
    user_prompt = HumanMessage(content=f"User Query: {query}")
    
    try:
        response = llm.invoke([system_prompt, user_prompt])
        module_name = response.content.strip().replace("MODULE:", "").strip()
        
        if module_name not in POSSIBLE_MODULES:
            module_name = "UNKNOWN"
    except Exception as e:
        print(f"Error in LLM invocation: {e}")
        module_name = "UNKNOWN"
    
    return module_name

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "JARVIS Brain API",
        "version": "1.2.0",
        "description": "Module Identification API with AI Response Generation for JARVIS",
        "features": [
            "Spelling correction",
            "Query refinement based on module type",
            "AI response generation for AI_BASED modules",
            "Removes question words for search queries",
            "Converts requests to actionable commands for automation"
        ],
        "endpoints": [
            {"path": "/", "method": "GET", "description": "API information"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/identify", "method": "POST", "description": "Identify module and generate AI response if needed"},
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
        original_query = request.query.strip()
        
        # First identify the module
        module = module_identifier_node(original_query)
        
        # Then refine the query based on the identified module
        refined_query = refine_query(original_query, module)
        
        # Initialize response
        response_data = {
            "user_query": refined_query,
            "module": module,
            "possible_modules": POSSIBLE_MODULES,
            "status": "success",
            "ai_based": (module == "AI_BASED"),
            "ai_response": None
        }
        
        # If module is AI_BASED, generate AI response
        if module == "AI_BASED" and llm is not None:
            ai_response = generate_ai_response(original_query, refined_query)
            response_data["ai_response"] = ai_response
        elif module == "AI_BASED" and llm is None:
            response_data["ai_response"] = "AI service unavailable. Please check configuration."
        
        return ModuleResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")