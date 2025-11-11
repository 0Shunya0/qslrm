"""
Simulations API Routes - Complete CRUD
"""

from flask import Blueprint, jsonify, request
from models import db, QuantumSimulation, SimulationResult, ReproducibilityMetadata, Parameter
from datetime import datetime

simulations_bp = Blueprint('simulations', __name__)

# LIST - Get all simulations with filtering
@simulations_bp.route('', methods=['GET'])
def get_simulations():
    try:
        status = request.args.get('status')
        framework = request.args.get('framework')
        project_id = request.args.get('project_id')
        researcher_id = request.args.get('researcher_id')
        min_qubits = request.args.get('min_qubits', type=int)
        max_qubits = request.args.get('max_qubits', type=int)
        algorithm = request.args.get('algorithm')
        
        query = QuantumSimulation.query
        
        if status:
            query = query.filter_by(status=status)
        if framework:
            query = query.filter_by(framework=framework)
        if project_id:
            query = query.filter_by(project_id=project_id)
        if researcher_id:
            query = query.filter_by(researcher_id=researcher_id)
        if min_qubits:
            query = query.filter(QuantumSimulation.num_qubits >= min_qubits)
        if max_qubits:
            query = query.filter(QuantumSimulation.num_qubits <= max_qubits)
        if algorithm:
            query = query.filter(QuantumSimulation.algorithm_type.ilike(f'%{algorithm}%'))
        
        simulations = query.order_by(db.desc(QuantumSimulation.execution_date)).all()
        return jsonify([s.to_dict(include_details=True) for s in simulations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET ONE
@simulations_bp.route('/<int:id>', methods=['GET'])
def get_simulation(id):
    try:
        simulation = QuantumSimulation.query.get_or_404(id)
        data = simulation.to_dict(include_details=True)
        
        # Add parameters
        data['parameters'] = [p.to_dict() for p in simulation.parameters.all()]
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# CREATE
@simulations_bp.route('', methods=['POST'])
def create_simulation():
    try:
        data = request.get_json()
        
        required = ['project_id', 'simulation_id', 'researcher_id', 'framework', 'num_qubits']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate framework
        valid_frameworks = ['Qiskit', 'Cirq', 'PennyLane', 'ProjectQ', 'QuTiP', 'Other']
        if data['framework'] not in valid_frameworks:
            return jsonify({'error': f'Invalid framework. Must be one of: {", ".join(valid_frameworks)}'}), 400
        
        # Check for duplicate simulation_id within project
        existing = QuantumSimulation.query.filter_by(
            project_id=data['project_id'],
            simulation_id=data['simulation_id']
        ).first()
        if existing:
            return jsonify({'error': 'Simulation ID already exists in this project'}), 409
        
        # Validate num_qubits
        if data['num_qubits'] < 1 or data['num_qubits'] > 1000:
            return jsonify({'error': 'num_qubits must be between 1 and 1000'}), 400
        
        simulation = QuantumSimulation(
            project_id=data['project_id'],
            simulation_id=data['simulation_id'],
            researcher_id=data['researcher_id'],
            framework=data['framework'],
            num_qubits=data['num_qubits'],
            circuit_depth=data.get('circuit_depth'),
            algorithm_type=data.get('algorithm_type'),
            description=data.get('description'),
            status=data.get('status', 'pending'),
            execution_date=datetime.utcnow()
        )
        
        db.session.add(simulation)
        db.session.commit()
        
        return jsonify({
            'message': 'Simulation created successfully',
            'simulation': simulation.to_dict(include_details=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# UPDATE
@simulations_bp.route('/<int:id>', methods=['PUT'])
def update_simulation(id):
    try:
        simulation = QuantumSimulation.query.get_or_404(id)
        data = request.get_json()
        
        if 'description' in data:
            simulation.description = data['description']
        if 'status' in data:
            valid_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
            if data['status'] not in valid_statuses:
                return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
            simulation.status = data['status']
        if 'circuit_depth' in data:
            simulation.circuit_depth = data['circuit_depth']
        if 'algorithm_type' in data:
            simulation.algorithm_type = data['algorithm_type']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Simulation updated successfully',
            'simulation': simulation.to_dict(include_details=True)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# DELETE
@simulations_bp.route('/<int:id>', methods=['DELETE'])
def delete_simulation(id):
    try:
        simulation = QuantumSimulation.query.get_or_404(id)
        
        sim_id = simulation.simulation_id
        db.session.delete(simulation)
        db.session.commit()
        
        return jsonify({
            'message': f'Simulation {sim_id} deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# RESULTS - Add/Update
@simulations_bp.route('/<int:id>/results', methods=['POST', 'PUT'])
def save_results(id):
    try:
        simulation = QuantumSimulation.query.get_or_404(id)
        data = request.get_json()
        
        result = simulation.result
        
        if result:
            # Update existing
            if 'execution_time_seconds' in data:
                result.execution_time_seconds = data['execution_time_seconds']
            if 'success_probability' in data:
                if not (0 <= data['success_probability'] <= 1):
                    return jsonify({'error': 'success_probability must be between 0 and 1'}), 400
                result.success_probability = data['success_probability']
            if 'fidelity' in data:
                if not (0 <= data['fidelity'] <= 1):
                    return jsonify({'error': 'fidelity must be between 0 and 1'}), 400
                result.fidelity = data['fidelity']
            if 'error_rate' in data:
                if not (0 <= data['error_rate'] <= 1):
                    return jsonify({'error': 'error_rate must be between 0 and 1'}), 400
                result.error_rate = data['error_rate']
            if 'output_data' in data:
                result.output_data = str(data['output_data'])
        else:
            # Create new
            result = SimulationResult(
                run_id=id,
                execution_time_seconds=data.get('execution_time_seconds'),
                success_probability=data.get('success_probability'),
                fidelity=data.get('fidelity'),
                error_rate=data.get('error_rate'),
                output_data=str(data.get('output_data', ''))
            )
            db.session.add(result)
        
        # Auto-update simulation status
        if simulation.status == 'running':
            simulation.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Results saved successfully',
            'result': result.to_dict()
        }), 201 if not result.result_id else 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# RESULTS - Get
@simulations_bp.route('/<int:id>/results', methods=['GET'])
def get_results(id):
    try:
        simulation = QuantumSimulation.query.get_or_404(id)
        if not simulation.result:
            return jsonify({'message': 'No results available'}), 404
        
        return jsonify(simulation.result.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# METADATA - Add/Update
@simulations_bp.route('/<int:id>/metadata', methods=['POST', 'PUT'])
def save_metadata(id):
    try:
        simulation = QuantumSimulation.query.get_or_404(id)
        data = request.get_json()
        
        metadata = simulation.repro_metadata
        
        if metadata:
            # Update
            if 'random_seed' in data:
                metadata.random_seed = data['random_seed']
            if 'hardware_backend' in data:
                metadata.hardware_backend = data['hardware_backend']
            if 'framework_version' in data:
                metadata.framework_version = data['framework_version']
            if 'reproducibility_score' in data:
                if not (0 <= data['reproducibility_score'] <= 1):
                    return jsonify({'error': 'reproducibility_score must be between 0 and 1'}), 400
                metadata.reproducibility_score = data['reproducibility_score']
            if 'verified_by' in data:
                metadata.verified_by = data['verified_by']
                metadata.verification_date = datetime.utcnow()
        else:
            # Create
            metadata = ReproducibilityMetadata(
                run_id=id,
                random_seed=data.get('random_seed'),
                hardware_backend=data.get('hardware_backend'),
                framework_version=data.get('framework_version'),
                reproducibility_score=data.get('reproducibility_score'),
                verified_by=data.get('verified_by'),
                verification_date=datetime.utcnow() if data.get('verified_by') else None
            )
            db.session.add(metadata)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Metadata saved successfully',
            'metadata': metadata.to_dict()
        }), 201 if not metadata.metadata_id else 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# METADATA - Get
@simulations_bp.route('/<int:id>/metadata', methods=['GET'])
def get_metadata(id):
    try:
        simulation = QuantumSimulation.query.get_or_404(id)
        if not simulation.repro_metadata:
            return jsonify({'message': 'No metadata available'}), 404
        
        return jsonify(simulation.repro_metadata.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PARAMETERS - Add
@simulations_bp.route('/<int:id>/parameters', methods=['POST'])
def add_parameter(id):
    try:
        simulation = QuantumSimulation.query.get_or_404(id)
        data = request.get_json()
        
        if 'parameter_name' not in data or 'parameter_value' not in data:
            return jsonify({'error': 'Missing parameter_name or parameter_value'}), 400
        
        # Check duplicate
        existing = Parameter.query.filter_by(
            run_id=id,
            parameter_name=data['parameter_name']
        ).first()
        if existing:
            return jsonify({'error': 'Parameter with this name already exists'}), 409
        
        parameter = Parameter(
            run_id=id,
            parameter_name=data['parameter_name'],
            parameter_value=str(data['parameter_value']),
            parameter_unit=data.get('parameter_unit'),
            parameter_type=data.get('parameter_type', 'string')
        )
        
        db.session.add(parameter)
        db.session.commit()
        
        return jsonify({
            'message': 'Parameter added successfully',
            'parameter': parameter.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# PARAMETERS - Get all
@simulations_bp.route('/<int:id>/parameters', methods=['GET'])
def get_parameters(id):
    try:
        simulation = QuantumSimulation.query.get_or_404(id)
        parameters = [p.to_dict() for p in simulation.parameters.all()]
        return jsonify(parameters)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PARAMETERS - Delete
@simulations_bp.route('/<int:id>/parameters/<int:param_id>', methods=['DELETE'])
def delete_parameter(id, param_id):
    try:
        parameter = Parameter.query.filter_by(
            parameter_id=param_id,
            run_id=id
        ).first_or_404()
        
        name = parameter.parameter_name
        db.session.delete(parameter)
        db.session.commit()
        
        return jsonify({
            'message': f'Parameter {name} deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500