from http.server import BaseHTTPRequestHandler
import json

def identify_module(user_input):
    """
    Identify the module based on user input
    Returns module details with ai_based field
    """
    
    # Your existing module detection logic
    result = {
        "module": None,
        "confidence": 0.0,
        "intent": None,
        "parameters": {},
        "ai_based": False
    }
    
    user_input_lower = user_input.lower()
    
    # AI-BASED MODULES (ai_based = True)
    if "generate a short story" in user_input_lower or "tell me a story" in user_input_lower:
        result["module"] = "story_generator"
        result["confidence"] = 0.95
        result["intent"] = "generate_story"
        result["parameters"] = {"type": "story"}
        result["ai_based"] = True
        
    elif "generate a poem" in user_input_lower or "write a poem" in user_input_lower:
        result["module"] = "poem_generator"
        result["confidence"] = 0.95
        result["intent"] = "generate_poem"
        result["parameters"] = {"type": "poem"}
        result["ai_based"] = True
        
    elif "write code" in user_input_lower or "generate code" in user_input_lower:
        result["module"] = "code_generator"
        result["confidence"] = 0.95
        result["intent"] = "generate_code"
        result["parameters"] = {}
        result["ai_based"] = True
    
    # NON AI-BASED MODULES (ai_based = False)
    elif "weather" in user_input_lower:
        result["module"] = "weather"
        result["confidence"] = 0.90
        result["intent"] = "get_weather"
        result["parameters"] = {}
        result["ai_based"] = False
        
    elif "time" in user_input_lower:
        result["module"] = "time"
        result["confidence"] = 0.90
        result["intent"] = "get_time"
        result["parameters"] = {}
        result["ai_based"] = False
        
    elif "calculator" in user_input_lower or "calculate" in user_input_lower:
        result["module"] = "calculator"
        result["confidence"] = 0.90
        result["intent"] = "calculate"
        result["parameters"] = {}
        result["ai_based"] = False
    
    return result


# Vercel requires this handler function
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "active",
            "message": "Jarvis Brain API is running",
            "endpoints": {
                "POST /": "Send user input to identify module"
            }
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            user_input = data.get('user_input', '')
            
            if not user_input:
                response = {
                    "error": "Missing 'user_input' field",
                    "status": "failed"
                }
            else:
                result = identify_module(user_input)
                response = {
                    "status": "success",
                    "result": result
                }
                
        except Exception as e:
            response = {
                "error": str(e),
                "status": "failed"
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()