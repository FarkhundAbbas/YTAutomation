import threading
import time
import webbrowser
import logging
from backend.models import init_db
from main import run_cycle
from app import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_backend_cycle():
    logger.info("Initializing DB setup...")
    init_db()
    
    logger.info("Running initial content generation cycle...")
    try:
        run_cycle()
        logger.info("Cycle completed successfully!")
    except Exception as e:
        logger.error(f"Cycle failed: {e}")

def open_browser():
    time.sleep(5)
    logger.info("Opening browser...")
    webbrowser.open("http://localhost:5000")

if __name__ == "__main__":
    # Start backend task in a separate thread so we can launch the server immediately
    t = threading.Thread(target=run_backend_cycle)
    t.start()
    
    # Start browser opener
    b = threading.Thread(target=open_browser)
    b.start()
    
    # Start Flask Server
    logger.info("Starting Flask Server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
