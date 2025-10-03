import os
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Health check endpoint"""
        # Get Gemini keys
        gemini_keys = [
            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2"), 
            os.getenv("GEMINI_API_KEY_3"),
            os.getenv("GEMINI_API_KEY_4")
        ]
        gemini_keys = [key for key in gemini_keys if key]  # Remove None values
        
        # Get current key index from timestamp (simple rotation)
        current_key_index = int(datetime.now().timestamp()) % len(gemini_keys) if gemini_keys else 0
        
        response_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "current_key": f"gemini_{current_key_index + 1}" if gemini_keys else "none",
            "bible_api_configured": bool(os.getenv("BIBLE_API_KEY")),
            "gemini_keys_count": len(gemini_keys)
        }
        
        # Set response headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Send response
        self.wfile.write(json.dumps(response_data).encode())