from mcp.server.fastmcp import FastMCP
import signal 
import sys 

SERVER_NAME = "sqlite_mcp_server"
PORT = 5000
HOST = "127.0.0.1"

def signal_handler(sig, frame):
    print("Shutting down server...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler) # Ctrl+c

mcp = FastMCP(
    name=SERVER_NAME,
    host=HOST,
    port=PORT,
    timeout=30 
)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    try:
        print(f"Starting MCP server {SERVER_NAME} on {HOST}:{PORT}")
        mcp.run()
    except Exception as e:
        print(f"Error: {e}")
