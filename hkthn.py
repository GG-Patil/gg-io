import os
import logging
import json
import sqlite3
from functools import wraps
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ServiceIntegration:
    """Main class to manage all external service integrations."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize with configuration from JSON file."""
        self.config = self._load_config(config_path)
        self.gemini_api_key = self.config.get("GEMINI_API_KEY")
        self.gmail_credentials_path = self.config.get("GMAIL_CREDENTIALS", "credentials.json")
        
        # Initialize database
        self._init_db()
        
        # Initialize service connections
        self.gmail_service = None
        if os.path.exists(self.gmail_credentials_path):
            self._init_gmail_service()
    
    def _load_config(self, config_path: str):
        """Load configuration from JSON file with error handling."""
        try:
            with open(config_path, "r") as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file: {config_path}")
            return {}
    
    def _init_gmail_service(self):
        """Initialize Gmail API service."""
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.gmail_credentials_path, 
                scopes=["https://www.googleapis.com/auth/gmail.readonly"]
            )
            self.gmail_service = build("gmail", "v1", credentials=creds)
            logger.info("Gmail service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {str(e)}")
    
    def _init_db(self):
        """Initialize the SQLite database and create tasks table."""
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            description TEXT
                        )''')
        conn.commit()
        conn.close()

    def add_task(self, name: str, description: str):
        """Add a new task to the database."""
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Task created successfully"}

    def get_tasks(self):
        """Retrieve all tasks from the database."""
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        conn.close()
        return [{"id": task[0], "name": task[1], "description": task[2]} for task in tasks]

    def delete_task(self, task_id: int):
        """Delete a task from the database."""
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Task deleted successfully"}

# Create Flask application
app = Flask(__name__)
integration = ServiceIntegration()

def handle_errors(f):
    """Decorator to handle exceptions in route handlers."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Route error: {str(e)}")
            return jsonify({"error": str(e)}), 500
    return decorated_function

@app.route("/create_task", methods=["POST"])
@handle_errors
def create_task():
    """Create a new task."""
    data = request.json
    task_name = data.get("task_name", "")
    description = data.get("description", "")
    if not task_name:
        return jsonify({"error": "Task name is required"}), 400
    result = integration.add_task(task_name, description)
    return jsonify(result)

@app.route("/get_tasks", methods=["GET"])
@handle_errors
def get_tasks():
    """Retrieve all tasks."""
    return jsonify(integration.get_tasks())

@app.route("/delete_task", methods=["DELETE"])
@handle_errors
def delete_task():
    """Delete a task by ID."""
    data = request.json
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "Task ID is required"}), 400
    return jsonify(integration.delete_task(task_id))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
@app.route('/')
@handle_errors
def index():
    return render_template("index.html")