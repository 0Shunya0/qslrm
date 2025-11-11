"""
QSLRM Backend - Flask Application with Complete CRUD Routes
"""
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR.parent / "database" / "qslrm.db"

print(f"🔍 Database path: {DATABASE_PATH}")
print(f"📁 Database exists: {DATABASE_PATH.exists()}")
if DATABASE_PATH.exists():
    print(f"📊 Database size: {DATABASE_PATH.stat().st_size} bytes")

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['JSON_SORT_KEYS'] = False

# Import db from models first
from models import db, Researcher, SimulationProject, QuantumSimulation, SimulationResult, ReproducibilityMetadata

# Initialize db with app
db.init_app(app)

# Enable CORS
CORS(app)

# Import and register Blueprint routes
from routes.researchers import researchers_bp
from routes.projects import projects_bp
from routes.simulations import simulations_bp
from routes.analytics import analytics_bp
from routes.export import export_bp
from routes.search import search_bp
from routes.auth import auth_bp
from routes.triggers import triggers_bp  # NEW

# Register all blueprints
app.register_blueprint(researchers_bp, url_prefix='/api/researchers')
app.register_blueprint(projects_bp, url_prefix='/api/projects')
app.register_blueprint(simulations_bp, url_prefix='/api/simulations')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(export_bp, url_prefix='/api/export')
app.register_blueprint(search_bp, url_prefix='/api/search')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(triggers_bp, url_prefix='/api/triggers')  # NEW

# Root endpoint
@app.route('/')
def index():
    return jsonify({
        'message': 'QSLRM API - Quantum Simulation Lab & Reproducibility Manager',
        'version': '2.0.0',
        'endpoints': {
            'health': '/api/health',
            'researchers': '/api/researchers',
            'projects': '/api/projects',
            'simulations': '/api/simulations',
            'analytics': '/api/analytics',
            'search': '/api/search',
            'export': '/api/export',
            'auth': '/api/auth',
            'triggers': '/api/triggers',  # NEW
            'dashboard': '/api/analytics/dashboard'
        }
    })

# Health check
@app.route('/api/health')
def health():
    try:
        with app.app_context():
            db.session.execute(db.text('SELECT 1'))
        return jsonify({'status': 'ok', 'database': 'connected', 'version': '2.0.0'})
    except Exception as e:
        return jsonify({'status': 'error', 'database': 'disconnected', 'error': str(e)}), 500

# Analytics dashboard endpoint
@app.route('/api/analytics/dashboard')
def dashboard():
    try:
        total_researchers = Researcher.query.count()
        total_projects = SimulationProject.query.count()
        active_projects = SimulationProject.query.filter_by(status='active').count()
        total_simulations = QuantumSimulation.query.count()
        completed_sims = QuantumSimulation.query.filter_by(status='completed').count()
        
        # Calculate averages
        results = SimulationResult.query.all()
        avg_fidelity = sum(r.fidelity for r in results if r.fidelity) / len(results) if results else 0
        
        metadata = ReproducibilityMetadata.query.all()
        avg_repro = sum(m.reproducibility_score for m in metadata if m.reproducibility_score) / len(metadata) if metadata else 0
        
        return jsonify({
            'total_researchers': total_researchers,
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_simulations': total_simulations,
            'completed_simulations': completed_sims,
            'avg_fidelity': round(avg_fidelity, 4),
            'avg_reproducibility': round(avg_repro, 4)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔬 QSLRM Backend Server v2.0 Starting...")
    print("="*60)
    print(f"📍 Server: http://localhost:5000")
    print(f"💚 Health: http://localhost:5000/api/health")
    print(f"🔐 Auth: http://localhost:5000/api/auth")
    print(f"👥 Researchers: http://localhost:5000/api/researchers")
    print(f"📊 Projects: http://localhost:5000/api/projects")
    print(f"⚛️  Simulations: http://localhost:5000/api/simulations")
    print(f"📈 Dashboard: http://localhost:5000/api/analytics/dashboard")
    print(f"🔍 Search: http://localhost:5000/api/search")
    print(f"📤 Export: http://localhost:5000/api/export")
    print(f"⚡ Triggers: http://localhost:5000/api/triggers")  # NEW
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')