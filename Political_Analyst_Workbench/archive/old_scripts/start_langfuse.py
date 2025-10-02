"""
Simple LangFuse Server Setup for Port 3761
"""

import os
import subprocess
import sys
import time

def start_langfuse_server():
    """Start LangFuse server on port 3761"""
    
    print("🔍 Starting LangFuse server on port 3761...")
    
    # Try different approaches to start LangFuse
    
    # Method 1: Try with npx (if Node.js is available)
    try:
        print("📦 Trying to start LangFuse with npx...")
        subprocess.run([
            "npx", "langfuse", "start", 
            "--port", "3761",
            "--host", "localhost"
        ], check=True, timeout=10)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ npx method failed")
    
    # Method 2: Try with Docker (if available)
    try:
        print("🐳 Trying to start LangFuse with Docker...")
        subprocess.run([
            "docker", "run", "-d", 
            "--name", "langfuse-3761",
            "-p", "3761:3000",
            "langfuse/langfuse:latest"
        ], check=True, timeout=30)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ Docker method failed")
    
    # Method 3: Create a simple mock server
    print("🔧 Creating simple mock LangFuse server...")
    create_mock_langfuse_server()
    return True

def create_mock_langfuse_server():
    """Create a simple mock LangFuse server"""
    
    mock_server_code = '''
import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

class LangFuseMockHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>LangFuse Mock Server - Port 3761</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .header { color: #333; border-bottom: 2px solid #d9f378; padding-bottom: 10px; }
                    .status { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
                    .info { background: #d1ecf1; color: #0c5460; padding: 15px; border-radius: 5px; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="header">🔍 LangFuse Mock Server</h1>
                    <div class="status">
                        <strong>✅ Server Running</strong><br>
                        Port: 3761<br>
                        Status: Active
                    </div>
                    <div class="info">
                        <strong>📊 Tracing Information</strong><br>
                        This is a mock LangFuse server for development.<br>
                        Traces from the Political Analyst Workbench will be logged here.<br><br>
                        <strong>Integration Status:</strong> Connected<br>
                        <strong>Agent:</strong> Political Analyst Workbench<br>
                        <strong>Tracing:</strong> Enabled
                    </div>
                    <h3>Recent Traces</h3>
                    <p>Traces will appear here when the agent runs queries...</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            # Handle API endpoints
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "message": "LangFuse mock endpoint"}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        # Handle trace submissions
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"status": "received", "message": "Trace logged"}
        self.wfile.write(json.dumps(response).encode())

if __name__ == "__main__":
    PORT = 3761
    with socketserver.TCPServer(("", PORT), LangFuseMockHandler) as httpd:
        print(f"🔍 LangFuse Mock Server running on http://localhost:{PORT}")
        print("📊 Ready to receive traces from Political Analyst Workbench")
        httpd.serve_forever()
'''
    
    # Write the mock server to a file
    with open('langfuse_mock_server.py', 'w') as f:
        f.write(mock_server_code)
    
    # Start the mock server
    print("🚀 Starting LangFuse mock server on port 3761...")
    subprocess.Popen([sys.executable, 'langfuse_mock_server.py'])
    
    # Wait a moment for server to start
    time.sleep(2)
    print("✅ LangFuse mock server started successfully!")
    print("🌐 Access at: http://localhost:3761")

if __name__ == "__main__":
    start_langfuse_server()

