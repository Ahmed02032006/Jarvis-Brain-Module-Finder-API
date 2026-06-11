import re
import json
from typing import Dict, List, Optional, Any

class JarvisBrainAPI:
    def __init__(self):
        """Initialize Jarvis Brain API with module patterns"""
        self.modules = self._initialize_modules()
        
    def _initialize_modules(self) -> Dict:
        """Define all modules with their patterns, intents, and AI-based flag"""
        return {
            # AI-Based Modules (ai_based = True)
            "story_generator": {
                "patterns": [
                    r"generate (?:a )?(?:short )?story",
                    r"tell (?:me )?(?:a )?story",
                    r"create (?:a )?story",
                    r"write (?:a )?story"
                ],
                "intent": "generate_story",
                "ai_based": True,
                "parameters": {
                    "length": ["short", "long", "medium"],
                    "genre": ["sci-fi", "fantasy", "romance", "horror", "adventure"]
                }
            },
            "poem_generator": {
                "patterns": [
                    r"generate (?:a )?poem",
                    r"write (?:a )?poem",
                    r"create (?:a )?poem",
                    r"tell (?:me )?(?:a )?poem"
                ],
                "intent": "generate_poem",
                "ai_based": True,
                "parameters": {
                    "style": ["haiku", "sonnet", "free verse", "limerick"],
                    "topic": ["love", "nature", "life", "friendship"]
                }
            },
            "code_generator": {
                "patterns": [
                    r"generate (?:a )?code",
                    r"write (?:a )?code for",
                    r"create (?:a )?(?:python|javascript|java|cpp) code",
                    r"code to"
                ],
                "intent": "generate_code",
                "ai_based": True,
                "parameters": {
                    "language": ["python", "javascript", "java", "cpp", "html", "css"]
                }
            },
            "email_composer": {
                "patterns": [
                    r"write (?:an )?email",
                    r"compose (?:an )?email",
                    r"draft (?:an )?email",
                    r"generate (?:an )?email"
                ],
                "intent": "compose_email",
                "ai_based": True,
                "parameters": {
                    "purpose": ["professional", "casual", "formal", "friendly"]
                }
            },
            "summarizer": {
                "patterns": [
                    r"summarize",
                    r"summary of",
                    r"brief (?:me )?about",
                    r"tl;dr"
                ],
                "intent": "summarize_text",
                "ai_based": True,
                "parameters": {
                    "length": ["short", "medium", "detailed"]
                }
            },
            "translator": {
                "patterns": [
                    r"translate (?:to|from)",
                    r"convert to (?:[a-z]+) language",
                    r"meaning in (?:[a-z]+)"
                ],
                "intent": "translate_text",
                "ai_based": True,
                "parameters": {
                    "target_language": ["spanish", "french", "german", "japanese", "chinese"]
                }
            },
            "qa_engine": {
                "patterns": [
                    r"who is",
                    r"what is",
                    r"why is",
                    r"how to",
                    r"explain (?:me )?"
                ],
                "intent": "answer_question",
                "ai_based": True,
                "parameters": {
                    "context": ["general", "technical", "scientific", "historical"]
                }
            },
            "creative_writer": {
                "patterns": [
                    r"write (?:a )?(?:letter|essay|article|blog)",
                    r"create (?:a )?(?:content|article|blog post)",
                    r"generate (?:a )?(?:paragraph|sentence|title)"
                ],
                "intent": "generate_content",
                "ai_based": True,
                "parameters": {
                    "type": ["letter", "essay", "article", "blog", "paragraph", "title"]
                }
            },
            
            # Non AI-Based Modules (ai_based = False)
            "weather": {
                "patterns": [
                    r"weather (?:in|at|for)",
                    r"temperature (?:in|at|for)",
                    r"rain|sunny|cloudy|forecast"
                ],
                "intent": "get_weather",
                "ai_based": False,
                "parameters": {
                    "location": None
                }
            },
            "calculator": {
                "patterns": [
                    r"calculate",
                    r"what is (\d+[\+\-\*/]\d+)",
                    r"math",
                    r"(\d+ (?:plus|minus|times|divided by) \d+)"
                ],
                "intent": "calculate",
                "ai_based": False,
                "parameters": {
                    "expression": None
                }
            },
            "alarm": {
                "patterns": [
                    r"set (?:an )?alarm",
                    r"wake me up at",
                    r"remind me at"
                ],
                "intent": "set_alarm",
                "ai_based": False,
                "parameters": {
                    "time": None
                }
            },
            "reminder": {
                "patterns": [
                    r"remind (?:me )?to",
                    r"set (?:a )?reminder",
                    r"remember to"
                ],
                "intent": "set_reminder",
                "ai_based": False,
                "parameters": {
                    "task": None,
                    "time": None
                }
            },
            "search": {
                "patterns": [
                    r"search (?:for|on google)",
                    r"find (?:information about|details of)",
                    r"look up"
                ],
                "intent": "web_search",
                "ai_based": False,
                "parameters": {
                    "query": None
                }
            },
            "music": {
                "patterns": [
                    r"play (?:song|music|track)",
                    r"play (?:some )?music",
                    r"play (?:a )?song"
                ],
                "intent": "play_music",
                "ai_based": False,
                "parameters": {
                    "song_name": None,
                    "artist": None
                }
            },
            "news": {
                "patterns": [
                    r"news (?:today|headlines)",
                    r"what'?s (?:the )?news",
                    r"tell (?:me )?(?:the )?news"
                ],
                "intent": "get_news",
                "ai_based": False,
                "parameters": {
                    "category": ["top", "tech", "sports", "entertainment"]
                }
            },
            "datetime": {
                "patterns": [
                    r"what'?s (?:the )?time",
                    r"current time",
                    r"what'?s (?:the )?date",
                    r"today'?s date"
                ],
                "intent": "get_datetime",
                "ai_based": False,
                "parameters": {}
            },
            "note_taker": {
                "patterns": [
                    r"take (?:a )?note",
                    r"save this",
                    r"remember that",
                    r"note down"
                ],
                "intent": "save_note",
                "ai_based": False,
                "parameters": {
                    "content": None
                }
            },
            "timer": {
                "patterns": [
                    r"set (?:a )?timer",
                    r"start (?:a )?timer for",
                    r"countdown"
                ],
                "intent": "set_timer",
                "ai_based": False,
                "parameters": {
                    "duration": None
                }
            }
        }
    
    def extract_parameters(self, user_input: str, module_config: Dict) -> Dict[str, Any]:
        """Extract parameters from user input"""
        parameters = {}
        
        for param_name, param_values in module_config.get("parameters", {}).items():
            if param_values:
                # Check if any of the possible values appear in the input
                for value in param_values:
                    if value.lower() in user_input.lower():
                        parameters[param_name] = value
                        break
            
            # Extract numbers for time/duration
            if param_name in ["time", "duration"]:
                time_match = re.search(r'(\d+)\s*(?:minutes?|mins?|hours?)', user_input.lower())
                if time_match:
                    parameters[param_name] = int(time_match.group(1))
            
            # Extract location
            if param_name == "location":
                location_match = re.search(r'(?:in|at|for)\s+([a-zA-Z\s]+?)(?:\?|\.|$)', user_input)
                if location_match:
                    parameters[param_name] = location_match.group(1).strip()
        
        return parameters
    
    def identify_module(self, user_input: str) -> Dict[str, Any]:
        """
        Identify the module based on user input
        
        Args:
            user_input (str): User's voice/text command
            
        Returns:
            Dict containing module information, confidence, intent, parameters, and ai_based flag
        """
        result = {
            "module": None,
            "confidence": 0.0,
            "intent": None,
            "parameters": {},
            "ai_based": False,
            "raw_input": user_input
        }
        
        user_input_lower = user_input.lower()
        
        # Find matching module
        for module_name, module_config in self.modules.items():
            for pattern in module_config["patterns"]:
                if re.search(pattern, user_input_lower, re.IGNORECASE):
                    result["module"] = module_name
                    result["confidence"] = 0.95  # High confidence for direct match
                    result["intent"] = module_config["intent"]
                    result["ai_based"] = module_config["ai_based"]
                    result["parameters"] = self.extract_parameters(user_input, module_config)
                    
                    # Adjust confidence based on parameter extraction
                    if result["parameters"]:
                        result["confidence"] = 0.98
                    
                    return result
        
        # If no module found, try fallback AI-based reasoning
        result["module"] = "general_ai"
        result["confidence"] = 0.60
        result["intent"] = "general_conversation"
        result["ai_based"] = True  # Use AI for general conversation
        result["parameters"] = {"original_query": user_input}
        
        return result
    
    def process_request(self, user_input: str) -> Dict[str, Any]:
        """
        Process user request and return complete response
        
        Args:
            user_input (str): User's command or query
            
        Returns:
            Dict with identification result and execution instructions
        """
        identification = self.identify_module(user_input)
        
        response = {
            "status": "success",
            "identification": identification,
            "execution_plan": {
                "requires_ai": identification["ai_based"],
                "module_handler": identification["module"],
                "priority": "high" if identification["ai_based"] else "normal"
            }
        }
        
        # Add module-specific instructions
        if identification["ai_based"]:
            response["execution_plan"]["ai_prompt"] = self._build_ai_prompt(identification)
        else:
            response["execution_plan"]["action"] = f"execute_{identification['module']}"
        
        return response
    
    def _build_ai_prompt(self, identification: Dict) -> str:
        """Build prompt for AI-based modules"""
        module = identification["module"]
        intent = identification["intent"]
        params = identification["parameters"]
        raw_input = identification["raw_input"]
        
        prompts = {
            "story_generator": f"Generate a {params.get('length', 'short')} story based on: {raw_input}",
            "poem_generator": f"Write a {params.get('style', 'beautiful')} poem about {params.get('topic', 'any topic')}",
            "code_generator": f"Generate {params.get('language', 'python')} code to: {raw_input}",
            "email_composer": f"Compose a {params.get('purpose', 'professional')} email about: {raw_input}",
            "summarizer": f"Summarize this text {params.get('length', 'short')}: {raw_input}",
            "translator": f"Translate to {params.get('target_language', 'spanish')}: {raw_input}",
            "qa_engine": f"Answer this question with {params.get('context', 'general')} context: {raw_input}",
            "creative_writer": f"Generate {params.get('type', 'content')} about: {raw_input}"
        }
        
        return prompts.get(module, f"Process this AI request: {raw_input}")
    
    def get_all_modules(self, ai_based_only: bool = False) -> List[Dict]:
        """Get list of all available modules"""
        modules = []
        for name, config in self.modules.items():
            if not ai_based_only or config["ai_based"]:
                modules.append({
                    "name": name,
                    "intent": config["intent"],
                    "ai_based": config["ai_based"],
                    "patterns": config["patterns"]
                })
        return modules


# Example usage and test function
def test_jarvis_brain():
    """Test the Jarvis Brain API with various inputs"""
    jarvis = JarvisBrainAPI()
    
    test_inputs = [
        "generate a short story about a dragon",
        "what's the weather in New York?",
        "write a poem about love",
        "calculate 25 * 4",
        "summarize this article for me",
        "set an alarm for 7 AM",
        "translate hello to Spanish",
        "play some music",
        "who is Albert Einstein?",
        "create a python code to reverse a string",
        "compose an email to my boss",
        "what time is it?"
    ]
    
    print("=" * 60)
    print("JARVIS BRAIN API - MODULE IDENTIFICATION TEST")
    print("=" * 60)
    
    for test in test_inputs:
        print(f"\n📝 User Input: {test}")
        result = jarvis.process_request(test)
        
        ident = result["identification"]
        print(f"🎯 Module: {ident['module']}")
        print(f"📊 Confidence: {ident['confidence']:.2%}")
        print(f"🎬 Intent: {ident['intent']}")
        print(f"🤖 AI-Based: {ident['ai_based']}")
        print(f"⚙️ Parameters: {ident['parameters']}")
        print(f"📋 Execution Plan: {result['execution_plan']}")
        print("-" * 40)


if __name__ == "__main__":
    # Initialize Jarvis Brain
    jarvis = JarvisBrainAPI()
    
    # Run test
    test_jarvis_brain()
    
    # Interactive mode
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE - Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        user_input = input("\n🎤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        
        if user_input:
            result = jarvis.process_request(user_input)
            ident = result["identification"]
            
            print(f"\n🤖 Jarvis: Module identified - {ident['module']}")
            print(f"   AI-Based: {ident['ai_based']}")
            print(f"   Intent: {ident['intent']}")
            print(f"   Confidence: {ident['confidence']:.2%}")
            
            if ident['parameters']:
                print(f"   Parameters: {ident['parameters']}")
            
            if ident['ai_based']:
                print(f"   ✨ This requires AI generation!")
                print(f"   📝 AI Prompt: {result['execution_plan'].get('ai_prompt', 'Processing...')}")