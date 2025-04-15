# The MIT License (MIT)
# Copyright © 2025 Quant by OpenGradient

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
import sys
import time
import signal
import socket
import subprocess
import atexit
import requests
import bittensor as bt
import traceback

# Global variable to store the Quant agent server process
quant_agent_process = None

# Default Flask server port
QUANT_AGENT_SERVER_PORT = 5000

def is_port_in_use(port):
    """
    Check if a port is already in use.
    
    Args:
        port (int): The port number to check.
        
    Returns:
        bool: True if the port is in use, False otherwise.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def is_quant_agent_server_running():
    """
    Check if the Quant agent server is already running.
    
    Returns:
        bool: True if the server is running, False otherwise.
    """
    # First check if the port is in use
    if not is_port_in_use(QUANT_AGENT_SERVER_PORT):
        return False
    
    # Then try to make a request to the server's health endpoint
    try:
        response = requests.get(f"http://localhost:{QUANT_AGENT_SERVER_PORT}/health", timeout=2)
        # If we get a successful response with the expected content, it's our server
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('service') == 'quant-agent-server':
                    bt.logging.info("Found existing Quant agent server running.")
                    return True
            except ValueError:
                pass  # Not JSON or not our expected format
        
        # Port is in use but not by our server, or server gave unexpected response
        bt.logging.warning(f"Port {QUANT_AGENT_SERVER_PORT} is in use, but it doesn't appear to be our Quant agent server.")
        bt.logging.warning("Another service (possibly AirPlay Receiver on macOS) may be using this port.")
        return False
    except requests.RequestException:
        # If we can connect to the port but can't get a response from the server,
        # something else might be using the port.
        bt.logging.warning(f"Port {QUANT_AGENT_SERVER_PORT} is in use, but it might not be the Quant agent server.")
        bt.logging.warning("Another service may be using this port.")
        return False

def start_quant_agent_server():
    """
    Start the Quant agent server as a subprocess.
    
    Returns:
        subprocess.Popen: The process object for the Quant agent server.
    """
    global quant_agent_process
    
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path to the BitQuant main.py script
    quant_agent_script = os.path.join(base_dir, "quant", "BitQuant", "main.py")
    # BitQuant directory (to be used as working directory)
    quant_agent_dir = os.path.join(base_dir, "quant", "BitQuant")
    
    bt.logging.info(f"Starting Quant agent server from: {quant_agent_script}")
    bt.logging.info(f"Using working directory: {quant_agent_dir}")
    
    # Start the Quant agent server as a subprocess
    quant_agent_process = subprocess.Popen(
        [sys.executable, quant_agent_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        cwd=quant_agent_dir  # Set the working directory to the BitQuant directory
    )
    
    bt.logging.info(f"Quant agent server started with PID: {quant_agent_process.pid}")
    
    # Give the server a moment to start up
    time.sleep(2)
    
    return quant_agent_process

def cleanup_quant_agent_server():
    """
    Clean up the Quant agent server process by terminating it gracefully.
    If it doesn't respond to SIGTERM, force kill it.
    """
    global quant_agent_process
    
    if quant_agent_process:
        bt.logging.info(f"Stopping Quant agent server (PID: {quant_agent_process.pid})")
        
        # Try to terminate gracefully
        if quant_agent_process.poll() is None:  # If process is still running
            # Send SIGTERM
            quant_agent_process.terminate()
            
            # Wait for a bit to allow for graceful shutdown
            try:
                quant_agent_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # If it doesn't shut down within timeout, force kill
                bt.logging.warning("Quant agent server did not terminate gracefully, forcing shutdown")
                quant_agent_process.kill()
        
        bt.logging.info("Quant agent server stopped")

def signal_handler(sig, frame):
    """
    Handle signals (SIGINT, SIGTERM) to ensure clean shutdown.
    
    Args:
        sig: The signal number
        frame: The current stack frame
    """
    bt.logging.info(f"Received signal {sig}, cleaning up and exiting")
    cleanup_quant_agent_server()
    sys.exit(0)

def get_quant_agent_server():
    """
    Get a Quant agent server process - either use an existing one or start a new one.
    
    Returns:
        subprocess.Popen or None: The process object for the Quant agent server if newly started,
                                  or None if using an existing server.
    """
    global quant_agent_process
    
    # Check if a server is already running
    if is_quant_agent_server_running():
        bt.logging.info("Quant agent server is already running. Using the existing server.")
        return None
    
    # Check if port is in use by something else before trying to start our server
    if is_port_in_use(QUANT_AGENT_SERVER_PORT):
        bt.logging.error(f"Port {QUANT_AGENT_SERVER_PORT} is already in use by another application.")
        bt.logging.error("Cannot start Quant agent server. Please free up the port and try again.")
        bt.logging.error("On macOS, try disabling the 'AirPlay Receiver' service from System Preferences -> General -> AirDrop & Handoff.")
        raise RuntimeError(f"Port {QUANT_AGENT_SERVER_PORT} is already in use by another application.")
    
    # If no server is running and port is free, start a new one
    bt.logging.info("Starting a new Quant agent server...")
    server_process = start_quant_agent_server()
    
    # Check if the server started successfully
    if server_process.poll() is not None:
        bt.logging.error(f"Quant agent server failed to start! Exit code: {server_process.returncode}")
        stdout_output = server_process.stdout.read()
        stderr_output = server_process.stderr.read()
        bt.logging.error(f"STDOUT: {stdout_output}")
        bt.logging.error(f"STDERR: {stderr_output}")
        return None
    
    # Server started successfully, wait a bit more to ensure it's ready
    server_running = False
    for i in range(10):  # Try for longer (10 seconds)
        if is_quant_agent_server_running():
            bt.logging.info("Quant agent server is now running and accepting connections.")
            server_running = True
            break
        bt.logging.info(f"Waiting for server to start... ({i+1}/10)")
        time.sleep(1)
    
    if not server_running:
        bt.logging.warning("Quant agent server started but health check is not responding.")
        bt.logging.warning("Continuing anyway, but the server may not be fully functional.")
    
    return server_process

def setup_quant_agent_server():
    """
    Set up the Quant agent server, including signal handlers and cleanup.
    
    Returns:
        subprocess.Popen or None: The process object for the Quant agent server,
                                  or None if using an existing server.
    """
    # Register cleanup function to be called when program exits
    atexit.register(cleanup_quant_agent_server)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Get or start the Quant agent server
        quant_agent_server = get_quant_agent_server()
        return quant_agent_server
    except RuntimeError as e:
        # Handle the case where the port is already in use
        bt.logging.error(f"Failed to set up Quant agent server: {e}")
        bt.logging.info("Continuing without a Quant agent server. Some functionality may be limited.")
        # Return None to indicate we're not managing a server
        return None
    except Exception as e:
        # Handle other unexpected errors
        bt.logging.error(f"Unexpected error setting up Quant agent server: {e}")
        bt.logging.debug(f"Stack trace: {traceback.format_exc()}")
        bt.logging.info("Continuing without a Quant agent server. Some functionality may be limited.")
        return None

def check_quant_agent_server(quant_agent_server):
    """
    Check if the Quant agent server is still running.
    
    Args:
        quant_agent_server (subprocess.Popen or None): The process object for the Quant agent server,
                                                     or None if using an existing server.
        
    Returns:
        bool: True if the server is running, False if it has stopped.
    """
    # If we're using an existing server, just check if it's still running
    if quant_agent_server is None:
        return is_quant_agent_server_running()
    
    # Otherwise, check the process we started
    if quant_agent_server.poll() is not None:
        bt.logging.error(f"Quant agent server exited unexpectedly with code {quant_agent_server.returncode}")
        stdout_output = quant_agent_server.stdout.read()
        stderr_output = quant_agent_server.stderr.read()
        bt.logging.error(f"STDOUT: {stdout_output}")
        bt.logging.error(f"STDERR: {stderr_output}")
        return False
    
    return True 