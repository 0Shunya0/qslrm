"""
Advanced Search and Pagination Routes for QSLRM
"""

from flask import Blueprint, jsonify, request
from models import db, Researcher, SimulationProject, QuantumSimulation
from sqlalchemy import or_, and_, func

search_bp = Blueprint('search', __name__)

# Global Search Across All Entities
@search_bp.route('', methods=['GET'])
def global_search():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        if len(query) < 2:
            return jsonify({'error': 'Query must be at least 2 characters'}), 400
        
        # Search researchers
        researchers = Researcher.query.filter(
            or_(
                Researcher.first_name.ilike(f'%{query}%'),
                Researcher.last_name.ilike(f'%{query}%'),
                Researcher.email.ilike(f'%{query}%'),
                Researcher.institution.ilike(f'%{query}%'),
                Researcher.department.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        # Search projects
        projects = SimulationProject.query.filter(
            or_(
                SimulationProject.title.ilike(f'%{query}%'),
                SimulationProject.description.ilike(f'%{query}%'),
                SimulationProject.field_of_study.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        # Search simulations
        simulations = QuantumSimulation.query.filter(
            or_(
                QuantumSimulation.simulation_id.ilike(f'%{query}%'),
                QuantumSimulation.description.ilike(f'%{query}%'),
                QuantumSimulation.algorithm_type.ilike(f'%{query}%'),
                QuantumSimulation.framework.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        return jsonify({
            'query': query,
            'results': {
                'researchers': {
                    'count': len(researchers),
                    'items': [
                        {
                            'id': r.researcher_id,
                            'name': f"{r.first_name} {r.last_name}",
                            'institution': r.institution,
                            'email': r.email,
                            'type': 'researcher'
                        }
                        for r in researchers
                    ]
                },
                'projects': {
                    'count': len(projects),
                    'items': [
                        {
                            'id': p.project_id,
                            'title': p.title,
                            'field': p.field_of_study,
                            'status': p.status,
                            'type': 'project'
                        }
                        for p in projects
                    ]
                },
                'simulations': {
                    'count': len(simulations),
                    'items': [
                        {
                            'id': s.run_id,
                            'simulation_id': s.simulation_id,
                            'framework': s.framework,
                            'algorithm': s.algorithm_type,
                            'status': s.status,
                            'type': 'simulation'
                        }
                        for s in simulations
                    ]
                }
            },
            'total_results': len(researchers) + len(projects) + len(simulations)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Advanced Simulation Search with Pagination
@search_bp.route('/simulations', methods=['GET'])
def search_simulations():
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # Max 100 items per page
        
        # Sort parameters
        sort_by = request.args.get('sort_by', 'execution_date')
        order = request.args.get('order', 'desc')
        
        # Filter parameters
        framework = request.args.get('framework')
        status = request.args.get('status')
        algorithm = request.args.get('algorithm')
        project_id = request.args.get('project_id', type=int)
        researcher_id = request.args.get('researcher_id', type=int)
        min_qubits = request.args.get('min_qubits', type=int)
        max_qubits = request.args.get('max_qubits', type=int)
        min_fidelity = request.args.get('min_fidelity', type=float)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build query
        query = QuantumSimulation.query
        
        # Apply filters
        if framework:
            query = query.filter(QuantumSimulation.framework == framework)
        if status:
            query = query.filter(QuantumSimulation.status == status)
        if algorithm:
            query = query.filter(QuantumSimulation.algorithm_type.ilike(f'%{algorithm}%'))
        if project_id:
            query = query.filter(QuantumSimulation.project_id == project_id)
        if researcher_id:
            query = query.filter(QuantumSimulation.researcher_id == researcher_id)
        if min_qubits:
            query = query.filter(QuantumSimulation.num_qubits >= min_qubits)
        if max_qubits:
            query = query.filter(QuantumSimulation.num_qubits <= max_qubits)
        if min_fidelity:
            query = query.join(QuantumSimulation.result).filter(
                db.SimulationResult.fidelity >= min_fidelity
            )
        if date_from:
            query = query.filter(QuantumSimulation.execution_date >= date_from)
        if date_to:
            query = query.filter(QuantumSimulation.execution_date <= date_to)
        
        # Apply sorting
        valid_sort_fields = {
            'execution_date': QuantumSimulation.execution_date,
            'num_qubits': QuantumSimulation.num_qubits,
            'circuit_depth': QuantumSimulation.circuit_depth,
            'simulation_id': QuantumSimulation.simulation_id
        }
        
        sort_field = valid_sort_fields.get(sort_by, QuantumSimulation.execution_date)
        if order == 'asc':
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())
        
        # Execute pagination
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_items': paginated.total,
            'total_pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev,
            'items': [s.to_dict(include_details=True) for s in paginated.items]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Search Researchers with Pagination
@search_bp.route('/researchers', methods=['GET'])
def search_researchers():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)
        
        query_text = request.args.get('q', '').strip()
        institution = request.args.get('institution')
        department = request.args.get('department')
        role = request.args.get('role')
        
        query = Researcher.query
        
        if query_text:
            query = query.filter(
                or_(
                    Researcher.first_name.ilike(f'%{query_text}%'),
                    Researcher.last_name.ilike(f'%{query_text}%'),
                    Researcher.email.ilike(f'%{query_text}%')
                )
            )
        
        if institution:
            query = query.filter(Researcher.institution.ilike(f'%{institution}%'))
        if department:
            query = query.filter(Researcher.department.ilike(f'%{department}%'))
        if role:
            query = query.filter(Researcher.role.ilike(f'%{role}%'))
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_items': paginated.total,
            'total_pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev,
            'items': [r.to_dict() for r in paginated.items]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Search Projects with Pagination
@search_bp.route('/projects', methods=['GET'])
def search_projects():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)
        
        query_text = request.args.get('q', '').strip()
        status = request.args.get('status')
        field = request.args.get('field')
        owner_id = request.args.get('owner_id', type=int)
        
        query = SimulationProject.query
        
        if query_text:
            query = query.filter(
                or_(
                    SimulationProject.title.ilike(f'%{query_text}%'),
                    SimulationProject.description.ilike(f'%{query_text}%')
                )
            )
        
        if status:
            query = query.filter(SimulationProject.status == status)
        if field:
            query = query.filter(SimulationProject.field_of_study.ilike(f'%{field}%'))
        if owner_id:
            query = query.filter(SimulationProject.owner_id == owner_id)
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_items': paginated.total,
            'total_pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev,
            'items': [p.to_dict(include_stats=True) for p in paginated.items]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get Available Filter Options
@search_bp.route('/filters', methods=['GET'])
def get_filter_options():
    try:
        # Get distinct values for common filters
        frameworks = db.session.query(QuantumSimulation.framework.distinct()).all()
        statuses = db.session.query(QuantumSimulation.status.distinct()).all()
        algorithms = db.session.query(QuantumSimulation.algorithm_type.distinct()).filter(
            QuantumSimulation.algorithm_type.isnot(None)
        ).all()
        institutions = db.session.query(Researcher.institution.distinct()).all()
        
        return jsonify({
            'frameworks': sorted([f[0] for f in frameworks if f[0]]),
            'statuses': sorted([s[0] for s in statuses if s[0]]),
            'algorithms': sorted([a[0] for a in algorithms if a[0]]),
            'institutions': sorted([i[0] for i in institutions if i[0]]),
            'qubit_range': {
                'min': db.session.query(func.min(QuantumSimulation.num_qubits)).scalar() or 0,
                'max': db.session.query(func.max(QuantumSimulation.num_qubits)).scalar() or 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500