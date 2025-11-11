"""
Researchers API Routes - Complete CRUD
"""

from flask import Blueprint, jsonify, request
from models import db, Researcher, QuantumSimulation
from sqlalchemy import or_

researchers_bp = Blueprint('researchers', __name__)

# LIST - Get all researchers with filtering
@researchers_bp.route('', methods=['GET'])
def get_researchers():
    try:
        # Query parameters for filtering
        institution = request.args.get('institution')
        department = request.args.get('department')
        role = request.args.get('role')
        search = request.args.get('search')
        
        query = Researcher.query
        
        # Apply filters
        if institution:
            query = query.filter(Researcher.institution.ilike(f'%{institution}%'))
        if department:
            query = query.filter(Researcher.department.ilike(f'%{department}%'))
        if role:
            query = query.filter(Researcher.role.ilike(f'%{role}%'))
        if search:
            query = query.filter(
                or_(
                    Researcher.first_name.ilike(f'%{search}%'),
                    Researcher.last_name.ilike(f'%{search}%'),
                    Researcher.email.ilike(f'%{search}%')
                )
            )
        
        researchers = query.all()
        return jsonify([r.to_dict() for r in researchers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET ONE - Get single researcher with stats
@researchers_bp.route('/<int:id>', methods=['GET'])
def get_researcher(id):
    try:
        researcher = Researcher.query.get_or_404(id)
        data = researcher.to_dict()
        
        # Add detailed statistics
        data['statistics'] = {
            'total_simulations': researcher.simulations.count(),
            'completed_simulations': researcher.simulations.filter_by(status='completed').count(),
            'failed_simulations': researcher.simulations.filter_by(status='failed').count(),
            'running_simulations': researcher.simulations.filter_by(status='running').count(),
            'projects_owned': researcher.owned_projects.count(),
            'projects_involved': len(researcher.project_memberships)
        }
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# CREATE - Add new researcher
@researchers_bp.route('', methods=['POST'])
def create_researcher():
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['first_name', 'last_name', 'email']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check for duplicate email
        existing = Researcher.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'error': 'Email already exists'}), 409
        
        # Validate ORCID format if provided
        if 'orcid_id' in data and data['orcid_id']:
            orcid = data['orcid_id']
            if not (len(orcid) == 19 and orcid.count('-') == 3):
                return jsonify({'error': 'Invalid ORCID format. Use: 0000-0000-0000-0000'}), 400
        
        # Create researcher
        researcher = Researcher(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            orcid_id=data.get('orcid_id'),
            institution=data.get('institution'),
            department=data.get('department'),
            role=data.get('role', 'Researcher')
        )
        
        db.session.add(researcher)
        db.session.commit()
        
        return jsonify({
            'message': 'Researcher created successfully',
            'researcher': researcher.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# UPDATE - Update researcher
@researchers_bp.route('/<int:id>', methods=['PUT'])
def update_researcher(id):
    try:
        researcher = Researcher.query.get_or_404(id)
        data = request.get_json()
        
        # Update fields if provided
        if 'first_name' in data:
            researcher.first_name = data['first_name']
        if 'last_name' in data:
            researcher.last_name = data['last_name']
        if 'email' in data:
            # Check if new email already exists
            existing = Researcher.query.filter(
                Researcher.email == data['email'],
                Researcher.researcher_id != id
            ).first()
            if existing:
                return jsonify({'error': 'Email already exists'}), 409
            researcher.email = data['email']
        if 'orcid_id' in data:
            researcher.orcid_id = data['orcid_id']
        if 'institution' in data:
            researcher.institution = data['institution']
        if 'department' in data:
            researcher.department = data['department']
        if 'role' in data:
            researcher.role = data['role']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Researcher updated successfully',
            'researcher': researcher.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# DELETE - Remove researcher
@researchers_bp.route('/<int:id>', methods=['DELETE'])
def delete_researcher(id):
    try:
        researcher = Researcher.query.get_or_404(id)
        
        # Check if researcher owns any projects
        if researcher.owned_projects.count() > 0:
            return jsonify({
                'error': 'Cannot delete researcher who owns projects',
                'owned_projects': researcher.owned_projects.count()
            }), 409
        
        # Check if researcher has simulations
        sim_count = researcher.simulations.count()
        if sim_count > 0:
            return jsonify({
                'error': 'Cannot delete researcher with simulations',
                'simulation_count': sim_count
            }), 409
        
        name = f"{researcher.first_name} {researcher.last_name}"
        db.session.delete(researcher)
        db.session.commit()
        
        return jsonify({
            'message': f'Researcher {name} deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# EXTRA - Get researcher's simulations
@researchers_bp.route('/<int:id>/simulations', methods=['GET'])
def get_researcher_simulations(id):
    try:
        researcher = Researcher.query.get_or_404(id)
        simulations = [s.to_dict(include_details=True) for s in researcher.simulations.all()]
        return jsonify({
            'researcher': researcher.to_dict(),
            'simulation_count': len(simulations),
            'simulations': simulations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# EXTRA - Get researcher's projects
@researchers_bp.route('/<int:id>/projects', methods=['GET'])
def get_researcher_projects(id):
    try:
        researcher = Researcher.query.get_or_404(id)
        
        owned = [p.to_dict(include_stats=True) for p in researcher.owned_projects.all()]
        
        participated = []
        for membership in researcher.project_memberships:
            project_dict = membership.project.to_dict(include_stats=True)
            project_dict['role_in_project'] = membership.role
            project_dict['joined_date'] = membership.joined_date.isoformat() if membership.joined_date else None
            participated.append(project_dict)
        
        return jsonify({
            'researcher': researcher.to_dict(),
            'owned_projects': owned,
            'participated_projects': participated
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500