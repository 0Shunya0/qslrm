"""
Authentication API Routes
Handles login, logout, and session management
"""

from flask import Blueprint, jsonify, request
from models import db, Researcher, AccessLog
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a researcher"""
    try:
        data = request.get_json()
        
        if 'email' not in data:
            return jsonify({'error': 'Missing email'}), 400
        
        researcher = Researcher.query.filter_by(email=data['email']).first()
        
        if not researcher:
            return jsonify({'error': 'Researcher not found'}), 404
        
        # Log the login action
        log = AccessLog(
            researcher_id=researcher.researcher_id,
            action_type='login',
            target_entity='researcher',
            target_id=researcher.researcher_id,
            timestamp=datetime.utcnow(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'researcher': researcher.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout a researcher"""
    try:
        data = request.get_json()
        
        if 'researcher_id' not in data:
            return jsonify({'error': 'Missing researcher_id'}), 400
        
        log = AccessLog(
            researcher_id=data['researcher_id'],
            action_type='logout',
            target_entity='researcher',
            target_id=data['researcher_id'],
            timestamp=datetime.utcnow(),
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user"""
    return jsonify({
        'message': 'Authentication endpoint',
        'note': 'JWT authentication to be implemented'
    }), 200