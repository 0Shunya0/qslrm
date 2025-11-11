"""
Projects API Routes - Complete CRUD
"""

from flask import Blueprint, jsonify, request
from models import db, SimulationProject, ProjectResearcher, Researcher
from datetime import datetime

projects_bp = Blueprint('projects', __name__)

# LIST - Get all projects
@projects_bp.route('', methods=['GET'])
def get_projects():
    try:
        status = request.args.get('status')
        field = request.args.get('field')
        owner_id = request.args.get('owner_id')
        
        query = SimulationProject.query
        
        if status:
            query = query.filter_by(status=status)
        if field:
            query = query.filter(SimulationProject.field_of_study.ilike(f'%{field}%'))
        if owner_id:
            query = query.filter_by(owner_id=owner_id)
        
        projects = query.all()
        return jsonify([p.to_dict(include_stats=True) for p in projects])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET ONE
@projects_bp.route('/<int:id>', methods=['GET'])
def get_project(id):
    try:
        project = SimulationProject.query.get_or_404(id)
        data = project.to_dict(include_stats=True)
        
        # Add team members
        data['team'] = [
            {
                'researcher_id': member.researcher_id,
                'researcher_name': f"{member.researcher.first_name} {member.researcher.last_name}",
                'role': member.role,
                'joined_date': member.joined_date.isoformat() if member.joined_date else None
            }
            for member in project.team_members.all()
        ]
        
        # Add recent simulations
        recent_sims = project.simulations.order_by(
            db.desc('execution_date')
        ).limit(10).all()
        data['recent_simulations'] = [s.to_dict() for s in recent_sims]
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# CREATE
@projects_bp.route('', methods=['POST'])
def create_project():
    try:
        data = request.get_json()
        
        required = ['title', 'owner_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Verify owner exists
        owner = Researcher.query.get(data['owner_id'])
        if not owner:
            return jsonify({'error': 'Owner not found'}), 404
        
        # Validate status
        valid_statuses = ['active', 'completed', 'archived', 'on-hold']
        status = data.get('status', 'active')
        if status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        project = SimulationProject(
            title=data['title'],
            description=data.get('description'),
            field_of_study=data.get('field_of_study'),
            owner_id=data['owner_id'],
            status=status,
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if 'start_date' in data else datetime.utcnow().date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if 'end_date' in data else None
        )
        
        db.session.add(project)
        db.session.commit()
        
        # Add owner as lead team member
        team_member = ProjectResearcher(
            project_id=project.project_id,
            researcher_id=data['owner_id'],
            role='lead',
            joined_date=datetime.utcnow().date()
        )
        db.session.add(team_member)
        db.session.commit()
        
        return jsonify({
            'message': 'Project created successfully',
            'project': project.to_dict(include_stats=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# UPDATE
@projects_bp.route('/<int:id>', methods=['PUT'])
def update_project(id):
    try:
        project = SimulationProject.query.get_or_404(id)
        data = request.get_json()
        
        if 'title' in data:
            project.title = data['title']
        if 'description' in data:
            project.description = data['description']
        if 'field_of_study' in data:
            project.field_of_study = data['field_of_study']
        if 'status' in data:
            valid_statuses = ['active', 'completed', 'archived', 'on-hold']
            if data['status'] not in valid_statuses:
                return jsonify({'error': 'Invalid status'}), 400
            project.status = data['status']
        if 'start_date' in data:
            project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            project.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data['end_date'] else None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': project.to_dict(include_stats=True)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# DELETE
@projects_bp.route('/<int:id>', methods=['DELETE'])
def delete_project(id):
    try:
        project = SimulationProject.query.get_or_404(id)
        
        title = project.title
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'message': f'Project "{title}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# TEAM MANAGEMENT
@projects_bp.route('/<int:id>/team', methods=['GET'])
def get_team(id):
    try:
        project = SimulationProject.query.get_or_404(id)
        team = [
            {
                'researcher_id': member.researcher_id,
                'researcher_name': f"{member.researcher.first_name} {member.researcher.last_name}",
                'email': member.researcher.email,
                'role': member.role,
                'joined_date': member.joined_date.isoformat() if member.joined_date else None
            }
            for member in project.team_members.all()
        ]
        return jsonify(team)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/<int:id>/team', methods=['POST'])
def add_team_member(id):
    try:
        project = SimulationProject.query.get_or_404(id)
        data = request.get_json()
        
        if 'researcher_id' not in data:
            return jsonify({'error': 'Missing researcher_id'}), 400
        
        researcher = Researcher.query.get(data['researcher_id'])
        if not researcher:
            return jsonify({'error': 'Researcher not found'}), 404
        
        # Check if already a member
        existing = ProjectResearcher.query.filter_by(
            project_id=id,
            researcher_id=data['researcher_id']
        ).first()
        if existing:
            return jsonify({'error': 'Researcher is already a team member'}), 409
        
        team_member = ProjectResearcher(
            project_id=id,
            researcher_id=data['researcher_id'],
            role=data.get('role', 'collaborator'),
            joined_date=datetime.utcnow().date()
        )
        
        db.session.add(team_member)
        db.session.commit()
        
        return jsonify({
            'message': 'Team member added successfully',
            'member': {
                'researcher_id': team_member.researcher_id,
                'researcher_name': f"{researcher.first_name} {researcher.last_name}",
                'role': team_member.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/<int:id>/team/<int:researcher_id>', methods=['DELETE'])
def remove_team_member(id, researcher_id):
    try:
        project = SimulationProject.query.get_or_404(id)
        
        if project.owner_id == researcher_id:
            return jsonify({'error': 'Cannot remove project owner from team'}), 409
        
        team_member = ProjectResearcher.query.filter_by(
            project_id=id,
            researcher_id=researcher_id
        ).first_or_404()
        
        name = f"{team_member.researcher.first_name} {team_member.researcher.last_name}"
        db.session.delete(team_member)
        db.session.commit()
        
        return jsonify({
            'message': f'{name} removed from project team'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500