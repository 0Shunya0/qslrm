"""
Advanced Analytics Routes for QSLRM
"""

from flask import Blueprint, jsonify, request
from models import db, Researcher, SimulationProject, QuantumSimulation, SimulationResult, ReproducibilityMetadata
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

# Framework Performance Comparison
@analytics_bp.route('/frameworks', methods=['GET'])
def framework_analysis():
    try:
        frameworks = db.session.query(
            QuantumSimulation.framework,
            func.count(QuantumSimulation.run_id).label('total_runs'),
            func.avg(SimulationResult.fidelity).label('avg_fidelity'),
            func.avg(SimulationResult.execution_time_seconds).label('avg_time'),
            func.avg(ReproducibilityMetadata.reproducibility_score).label('avg_reproducibility'),
            func.avg(QuantumSimulation.num_qubits).label('avg_qubits')
        ).outerjoin(SimulationResult).outerjoin(ReproducibilityMetadata)\
         .group_by(QuantumSimulation.framework)\
         .all()
        
        results = []
        for fw in frameworks:
            results.append({
                'framework': fw.framework,
                'total_simulations': fw.total_runs,
                'avg_fidelity': round(fw.avg_fidelity, 4) if fw.avg_fidelity else 0,
                'avg_execution_time': round(fw.avg_time, 3) if fw.avg_time else 0,
                'avg_reproducibility': round(fw.avg_reproducibility, 4) if fw.avg_reproducibility else 0,
                'avg_qubits': round(fw.avg_qubits, 2) if fw.avg_qubits else 0
            })
        
        return jsonify(sorted(results, key=lambda x: x['total_simulations'], reverse=True))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Algorithm Performance Analysis
@analytics_bp.route('/algorithms', methods=['GET'])
def algorithm_analysis():
    try:
        algorithms = db.session.query(
            QuantumSimulation.algorithm_type,
            func.count(QuantumSimulation.run_id).label('count'),
            func.avg(SimulationResult.fidelity).label('avg_fidelity'),
            func.avg(SimulationResult.success_probability).label('avg_success'),
            func.min(QuantumSimulation.num_qubits).label('min_qubits'),
            func.max(QuantumSimulation.num_qubits).label('max_qubits')
        ).outerjoin(SimulationResult)\
         .filter(QuantumSimulation.algorithm_type.isnot(None))\
         .group_by(QuantumSimulation.algorithm_type)\
         .all()
        
        results = []
        for algo in algorithms:
            results.append({
                'algorithm': algo.algorithm_type,
                'total_runs': algo.count,
                'avg_fidelity': round(algo.avg_fidelity, 4) if algo.avg_fidelity else 0,
                'avg_success_rate': round(algo.avg_success, 4) if algo.avg_success else 0,
                'qubit_range': f"{algo.min_qubits}-{algo.max_qubits}"
            })
        
        return jsonify(sorted(results, key=lambda x: x['total_runs'], reverse=True))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Researcher Performance Leaderboard
@analytics_bp.route('/leaderboard', methods=['GET'])
@analytics_bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Fixed query with explicit joins
        researchers = db.session.query(
            Researcher.researcher_id,
            Researcher.first_name,
            Researcher.last_name,
            Researcher.institution,
            db.func.count(QuantumSimulation.run_id).label('total_simulations'),
            db.func.avg(SimulationResult.fidelity).label('avg_fidelity')
        ).outerjoin(
            QuantumSimulation, 
            Researcher.researcher_id == QuantumSimulation.researcher_id
        ).outerjoin(
            SimulationResult,
            QuantumSimulation.run_id == SimulationResult.run_id
        ).group_by(
            Researcher.researcher_id
        ).order_by(
            db.desc('total_simulations')
        ).limit(limit).all()
        
        results = []
        for rank, r in enumerate(researchers, 1):
            results.append({
                'rank': rank,
                'researcher_id': r.researcher_id,
                'name': f"{r.first_name} {r.last_name}",
                'institution': r.institution,
                'total_simulations': r.total_simulations,
                'avg_fidelity': round(r.avg_fidelity, 4) if r.avg_fidelity else None
            })
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Project Health Score
@analytics_bp.route('/project-health/<int:id>', methods=['GET'])
def project_health(id):
    try:
        project = SimulationProject.query.get_or_404(id)
        
        total_sims = project.simulations.count()
        if total_sims == 0:
            return jsonify({
                'project_id': id,
                'health_score': 0,
                'status': 'no_data',
                'message': 'No simulations yet'
            })
        
        completed = project.simulations.filter_by(status='completed').count()
        failed = project.simulations.filter_by(status='failed').count()
        running = project.simulations.filter_by(status='running').count()
        
        completion_rate = completed / total_sims if total_sims > 0 else 0
        failure_rate = failed / total_sims if total_sims > 0 else 0
        
        # Calculate average quality metrics
        completed_sims = project.simulations.filter_by(status='completed').all()
        avg_fidelity = sum([s.result.fidelity for s in completed_sims if s.result and s.result.fidelity]) / len(completed_sims) if completed_sims else 0
        avg_repro = sum([s.repro_metadata.reproducibility_score for s in completed_sims if s.repro_metadata and s.repro_metadata.reproducibility_score]) / len(completed_sims) if completed_sims else 0
        
        # Health score calculation (0-100)
        health_score = (
            completion_rate * 30 +
            (1 - failure_rate) * 20 +
            avg_fidelity * 25 +
            avg_repro * 25
        )
        
        # Determine status
        if health_score >= 80:
            status = 'excellent'
        elif health_score >= 60:
            status = 'good'
        elif health_score >= 40:
            status = 'fair'
        else:
            status = 'poor'
        
        return jsonify({
            'project_id': id,
            'project_name': project.title,
            'health_score': round(health_score, 2),
            'status': status,
            'metrics': {
                'total_simulations': total_sims,
                'completed': completed,
                'failed': failed,
                'running': running,
                'completion_rate': round(completion_rate, 4),
                'failure_rate': round(failure_rate, 4),
                'avg_fidelity': round(avg_fidelity, 4),
                'avg_reproducibility': round(avg_repro, 4)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Trend Analysis
@analytics_bp.route('/trends', methods=['GET'])
def trends():
    try:
        period = request.args.get('period', '30d')
        
        # Parse period
        if period.endswith('d'):
            days = int(period[:-1])
        else:
            days = 30
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get simulations in period
        sims = QuantumSimulation.query.filter(
            QuantumSimulation.execution_date >= cutoff_date
        ).order_by(QuantumSimulation.execution_date).all()
        
        # Group by date
        daily_stats = {}
        for sim in sims:
            date_key = sim.execution_date.date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    'date': date_key,
                    'count': 0,
                    'fidelities': [],
                    'repro_scores': []
                }
            
            daily_stats[date_key]['count'] += 1
            if sim.result and sim.result.fidelity:
                daily_stats[date_key]['fidelities'].append(sim.result.fidelity)
            if sim.repro_metadata and sim.repro_metadata.reproducibility_score:
                daily_stats[date_key]['repro_scores'].append(sim.repro_metadata.reproducibility_score)
        
        # Calculate averages
        trend_data = []
        for date_key, stats in sorted(daily_stats.items()):
            trend_data.append({
                'date': stats['date'],
                'simulation_count': stats['count'],
                'avg_fidelity': round(sum(stats['fidelities']) / len(stats['fidelities']), 4) if stats['fidelities'] else None,
                'avg_reproducibility': round(sum(stats['repro_scores']) / len(stats['repro_scores']), 4) if stats['repro_scores'] else None
            })
        
        return jsonify({
            'period': period,
            'total_days': len(trend_data),
            'trends': trend_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Qubit Scaling Analysis
@analytics_bp.route('/qubit-scaling', methods=['GET'])
def qubit_scaling():
    try:
        results = db.session.query(
            QuantumSimulation.num_qubits,
            func.count(QuantumSimulation.run_id).label('count'),
            func.avg(SimulationResult.fidelity).label('avg_fidelity'),
            func.avg(SimulationResult.execution_time_seconds).label('avg_time')
        ).outerjoin(SimulationResult)\
         .group_by(QuantumSimulation.num_qubits)\
         .order_by(QuantumSimulation.num_qubits)\
         .all()
        
        data = []
        for r in results:
            data.append({
                'qubits': r.num_qubits,
                'simulations': r.count,
                'avg_fidelity': round(r.avg_fidelity, 4) if r.avg_fidelity else 0,
                'avg_execution_time': round(r.avg_time, 3) if r.avg_time else 0
            })
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Institution Statistics
@analytics_bp.route('/institutions', methods=['GET'])
def institution_stats():
    try:
        stats = db.session.query(
            Researcher.institution,
            func.count(func.distinct(Researcher.researcher_id)).label('researcher_count'),
            func.count(QuantumSimulation.run_id).label('total_simulations'),
            func.avg(SimulationResult.fidelity).label('avg_fidelity')
        ).outerjoin(QuantumSimulation)\
         .outerjoin(SimulationResult)\
         .group_by(Researcher.institution)\
         .order_by(desc('total_simulations'))\
         .all()
        
        results = []
        for s in stats:
            results.append({
                'institution': s.institution,
                'researchers': s.researcher_count,
                'total_simulations': s.total_simulations or 0,
                'avg_fidelity': round(s.avg_fidelity, 4) if s.avg_fidelity else 0
            })
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enhanced Dashboard with More Metrics
@analytics_bp.route('/dashboard/enhanced', methods=['GET'])
def enhanced_dashboard():
    try:
        # Basic counts
        total_researchers = Researcher.query.count()
        total_projects = SimulationProject.query.count()
        total_simulations = QuantumSimulation.query.count()
        
        # Status breakdown
        status_counts = db.session.query(
            QuantumSimulation.status,
            func.count(QuantumSimulation.run_id)
        ).group_by(QuantumSimulation.status).all()
        
        status_breakdown = {status: count for status, count in status_counts}
        
        # Framework breakdown
        framework_counts = db.session.query(
            QuantumSimulation.framework,
            func.count(QuantumSimulation.run_id)
        ).group_by(QuantumSimulation.framework).all()
        
        framework_breakdown = {fw: count for fw, count in framework_counts}
        
        # Quality metrics
        results = SimulationResult.query.all()
        metadata = ReproducibilityMetadata.query.all()
        
        avg_fidelity = sum(r.fidelity for r in results if r.fidelity) / len(results) if results else 0
        avg_repro = sum(m.reproducibility_score for m in metadata if m.reproducibility_score) / len(metadata) if metadata else 0
        
        # Recent activity (last 7 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        recent_sims = QuantumSimulation.query.filter(
            QuantumSimulation.execution_date >= recent_cutoff
        ).count()
        
        return jsonify({
            'overview': {
                'total_researchers': total_researchers,
                'total_projects': total_projects,
                'total_simulations': total_simulations,
                'recent_activity': recent_sims
            },
            'status_breakdown': status_breakdown,
            'framework_breakdown': framework_breakdown,
            'quality_metrics': {
                'avg_fidelity': round(avg_fidelity, 4),
                'avg_reproducibility': round(avg_repro, 4)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500