"""
Simple Phoenix Setup for Real-time Observability
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_phoenix():
    """Start Phoenix observability server"""
    try:
        import phoenix as px
        
        # Launch Phoenix UI
        session = px.launch_app(port=6006)
        print("🔥 Phoenix UI launched successfully at: http://localhost:6006")
        print("📊 Ready for real-time tracing!")
        
        # Keep the server running
        import time
        while True:
            time.sleep(1)
            
    except ImportError:
        print("❌ Phoenix not installed. Installing now...")
        os.system("pip install arize-phoenix")
        print("✅ Phoenix installed! Please restart.")
        return False
    except Exception as e:
        print(f"❌ Error starting Phoenix: {e}")
        return False

if __name__ == "__main__":
    print("🔥 Starting Phoenix Observability Server...")
    print("=" * 50)
    start_phoenix()

