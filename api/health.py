import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Health check endpoint"""
        
        # Simulate key rotation
        current_timestamp = int(datetime.now().timestamp())
        current_key_index = current_timestamp % 4 + 1
        
        response_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "current_key": f"gemini_{current_key_index}",
            "bible_api_configured": True,
            "gemini_keys_count": 4,
            "deployment": "vercel_active"
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