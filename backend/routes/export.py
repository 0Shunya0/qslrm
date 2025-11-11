"""
Data Export Routes for QSLRM
"""

from flask import Blueprint, jsonify, Response, request
from models import db, Researcher, SimulationProject, QuantumSimulation
import csv
import io
import json

export_bp = Blueprint('export', __name__)

# Export Simulations as CSV
@export_bp.route('/simulations/csv', methods=['GET'])
def export_simulations_csv():
    try:
        # Get filters
        project_id = request.args.get('project_id', type=int)
        framework = request.args.get('framework')
        status = request.args.get('status')
        
        query = QuantumSimulation.query
        
        if project_id:
            query = query.filter_by(project_id=project_id)
        if framework:
            query = query.filter_by(framework=framework)
        if status:
            query = query.filter_by(status=status)
        
        simulations = query.all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Run ID', 'Simulation ID', 'Project ID', 'Researcher ID',
            'Framework', 'Algorithm', 'Qubits', 'Circuit Depth',
            'Status', 'Execution Date', 'Fidelity', 'Success Rate',
            'Reproducibility Score', 'Execution Time (s)'
        ])
        
        # Data rows
        for sim in simulations:
            writer.writerow([
                sim.run_id,
                sim.simulation_id,
                sim.project_id,
                sim.researcher_id,
                sim.framework,
                sim.algorithm_type or '',
                sim.num_qubits,
                sim.circuit_depth or '',
                sim.status,
                sim.execution_date.isoformat() if sim.execution_date else '',
                sim.result.fidelity if sim.result else '',
                sim.result.success_probability if sim.result else '',
                sim.repro_metadata.reproducibility_score if sim.repro_metadata else '',
                sim.result.execution_time_seconds if sim.result else ''
            ])
        
        # Prepare response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=simulations.csv'}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Export Project Report as JSON
@export_bp.route('/project/<int:id>/report', methods=['GET'])
def export_project_report(id):
    try:
        project = SimulationProject.query.get_or_404(id)
        
        # Gather comprehensive data
        simulations = project.simulations.all()
        team = project.team_members.all()
        
        report = {
            'project': {
                'id': project.project_id,
                'title': project.title,
                'description': project.description,
                'field_of_study': project.field_of_study,
                'status': project.status,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'owner': {
                    'id': project.owner.researcher_id,
                    'name': f"{project.owner.first_name} {project.owner.last_name}",
                    'email': project.owner.email,
                    'institution': project.owner.institution
                }
            },
            'team': [
                {
                    'researcher_id': member.researcher_id,
                    'name': f"{member.researcher.first_name} {member.researcher.last_name}",
                    'role': member.role,
                    'institution': member.researcher.institution
                }
                for member in team
            ],
            'statistics': {
                'total_simulations': len(simulations),
                'completed': len([s for s in simulations if s.status == 'completed']),
                'failed': len([s for s in simulations if s.status == 'failed']),
                'running': len([s for s in simulations if s.status == 'running']),
                'avg_fidelity': sum([s.result.fidelity for s in simulations if s.result and s.result.fidelity]) / len([s for s in simulations if s.result and s.result.fidelity]) if simulations else 0,
                'avg_reproducibility': sum([s.repro_metadata.reproducibility_score for s in simulations if s.repro_metadata and s.repro_metadata.reproducibility_score]) / len([s for s in simulations if s.repro_metadata and s.repro_metadata.reproducibility_score]) if simulations else 0
            },
            'simulations': [
                {
                    'run_id': sim.run_id,
                    'simulation_id': sim.simulation_id,
                    'framework': sim.framework,
                    'algorithm': sim.algorithm_type,
                    'qubits': sim.num_qubits,
                    'status': sim.status,
                    'execution_date': sim.execution_date.isoformat() if sim.execution_date else None,
                    'fidelity': sim.result.fidelity if sim.result else None,
                    'reproducibility': sim.repro_metadata.reproducibility_score if sim.repro_metadata else None
                }
                for sim in simulations
            ],
            'generated_at': db.func.current_timestamp()
        }
        
        # Format as pretty JSON
        json_str = json.dumps(report, indent=2, default=str)
        
        return Response(
            json_str,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=project_{id}_report.json'}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Export Researcher Portfolio
@export_bp.route('/researcher/<int:id>/portfolio', methods=['GET'])
def export_researcher_portfolio(id):
    try:
        researcher = Researcher.query.get_or_404(id)
        
        simulations = researcher.simulations.all()
        owned_projects = researcher.owned_projects.all()
        
        portfolio = {
            'researcher': {
                'id': researcher.researcher_id,
                'name': f"{researcher.first_name} {researcher.last_name}",
                'email': researcher.email,
                'orcid': researcher.orcid_id,
                'institution': researcher.institution,
                'department': researcher.department,
                'role': researcher.role
            },
            'statistics': {
                'total_simulations': len(simulations),
                'completed_simulations': len([s for s in simulations if s.status == 'completed']),
                'projects_owned': len(owned_projects),
                'avg_fidelity': sum([s.result.fidelity for s in simulations if s.result and s.result.fidelity]) / len([s for s in simulations if s.result and s.result.fidelity]) if simulations else 0
            },
            'owned_projects': [
                {
                    'id': p.project_id,
                    'title': p.title,
                    'status': p.status,
                    'simulations_count': p.simulations.count()
                }
                for p in owned_projects
            ],
            'recent_simulations': [
                {
                    'run_id': sim.run_id,
                    'simulation_id': sim.simulation_id,
                    'project': sim.project.title,
                    'framework': sim.framework,
                    'status': sim.status,
                    'execution_date': sim.execution_date.isoformat() if sim.execution_date else None
                }
                for sim in sorted(simulations, key=lambda x: x.execution_date, reverse=True)[:10]
            ],
            'generated_at': db.func.current_timestamp()
        }
        
        json_str = json.dumps(portfolio, indent=2, default=str)
        
        return Response(
            json_str,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=researcher_{id}_portfolio.json'}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Bulk Export All Data
@export_bp.route('/all/json', methods=['GET'])
def export_all_data():
    try:
        data = {
            'researchers': [r.to_dict() for r in Researcher.query.all()],
            'projects': [p.to_dict(include_stats=True) for p in SimulationProject.query.all()],
            'simulations': [s.to_dict(include_details=True) for s in QuantumSimulation.query.all()],
            'export_timestamp': db.func.current_timestamp()
        }
        
        json_str = json.dumps(data, indent=2, default=str)
        
        return Response(
            json_str,
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=qslrm_full_export.json'}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500