"""
QSLRM Database Models
SQLAlchemy ORM models matching the database schema
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import CheckConstraint

db = SQLAlchemy()

class Researcher(db.Model):
    __tablename__ = 'researcher'
    
    researcher_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    orcid_id = db.Column(db.String(19), unique=True)
    institution = db.Column(db.String(255))
    department = db.Column(db.String(255))
    role = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owned_projects = db.relationship('SimulationProject', backref='owner', lazy='dynamic')
    simulations = db.relationship('QuantumSimulation', backref='researcher', lazy='dynamic')
    
    def to_dict(self):
        return {
            'researcher_id': self.researcher_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'email': self.email,
            'orcid_id': self.orcid_id,
            'institution': self.institution,
            'department': self.department,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SimulationProject(db.Model):
    __tablename__ = 'simulation_project'
    
    project_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    field_of_study = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('researcher.researcher_id'), nullable=False)
    status = db.Column(db.String(20), default='active')
    start_date = db.Column(db.Date, default=datetime.utcnow)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    simulations = db.relationship('QuantumSimulation', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    team_members = db.relationship('ProjectResearcher', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_stats=False):
        data = {
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'field_of_study': self.field_of_study,
            'owner_id': self.owner_id,
            'owner_name': f"{self.owner.first_name} {self.owner.last_name}",
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_stats:
            data['team_size'] = self.team_members.count()
            data['simulation_count'] = self.simulations.count()
        return data

class ProjectResearcher(db.Model):
    __tablename__ = 'project_researchers'
    
    project_id = db.Column(db.Integer, db.ForeignKey('simulation_project.project_id'), primary_key=True)
    researcher_id = db.Column(db.Integer, db.ForeignKey('researcher.researcher_id'), primary_key=True)
    role = db.Column(db.String(50), default='collaborator')
    joined_date = db.Column(db.Date, default=datetime.utcnow)
    
    researcher = db.relationship('Researcher', backref='project_memberships')

class QuantumSimulation(db.Model):
    __tablename__ = 'quantum_simulation'
    
    run_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('simulation_project.project_id'), nullable=False)
    simulation_id = db.Column(db.String(50), nullable=False)
    researcher_id = db.Column(db.Integer, db.ForeignKey('researcher.researcher_id'), nullable=False)
    framework = db.Column(db.String(50), nullable=False)
    num_qubits = db.Column(db.Integer, nullable=False)
    circuit_depth = db.Column(db.Integer)
    algorithm_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    execution_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    parameters = db.relationship('Parameter', backref='simulation', lazy='dynamic', cascade='all, delete-orphan')
    result = db.relationship('SimulationResult', backref='simulation', uselist=False, cascade='all, delete-orphan')
    repro_metadata = db.relationship('ReproducibilityMetadata', backref='simulation', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self, include_details=False):
        data = {
            'run_id': self.run_id,
            'project_id': self.project_id,
            'simulation_id': self.simulation_id,
            'researcher_id': self.researcher_id,
            'researcher_name': f"{self.researcher.first_name} {self.researcher.last_name}",
            'framework': self.framework,
            'num_qubits': self.num_qubits,
            'circuit_depth': self.circuit_depth,
            'algorithm_type': self.algorithm_type,
            'description': self.description,
            'status': self.status,
            'execution_date': self.execution_date.isoformat() if self.execution_date else None
        }
        if include_details and self.result:
            data['result'] = self.result.to_dict()
        if include_details and self.repro_metadata:
            data['metadata'] = self.repro_metadata.to_dict()
        return data

class Parameter(db.Model):
    __tablename__ = 'parameter'
    
    parameter_id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('quantum_simulation.run_id'), nullable=False)
    parameter_name = db.Column(db.String(100), nullable=False)
    parameter_value = db.Column(db.Text, nullable=False)
    parameter_unit = db.Column(db.String(50))
    parameter_type = db.Column(db.String(20), default='numeric')
    
    def to_dict(self):
        return {
            'parameter_id': self.parameter_id,
            'run_id': self.run_id,
            'parameter_name': self.parameter_name,
            'parameter_value': self.parameter_value,
            'parameter_unit': self.parameter_unit,
            'parameter_type': self.parameter_type
        }

class SimulationResult(db.Model):
    __tablename__ = 'simulation_result'
    
    result_id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('quantum_simulation.run_id'), unique=True, nullable=False)
    output_data = db.Column(db.Text)
    execution_time_seconds = db.Column(db.Float)
    success_probability = db.Column(db.Float)
    fidelity = db.Column(db.Float)
    energy_value = db.Column(db.Float)
    measurement_counts = db.Column(db.Text)
    error_rate = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'result_id': self.result_id,
            'run_id': self.run_id,
            'execution_time_seconds': self.execution_time_seconds,
            'success_probability': self.success_probability,
            'fidelity': self.fidelity,
            'error_rate': self.error_rate
        }

class ReproducibilityMetadata(db.Model):
    __tablename__ = 'reproducibility_metadata'
    
    metadata_id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('quantum_simulation.run_id'), unique=True, nullable=False)
    random_seed = db.Column(db.Integer)
    hardware_backend = db.Column(db.String(100))
    framework_version = db.Column(db.String(50))
    reproducibility_score = db.Column(db.Float)
    verified_by = db.Column(db.Integer)
    verification_date = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'metadata_id': self.metadata_id,
            'run_id': self.run_id,
            'random_seed': self.random_seed,
            'hardware_backend': self.hardware_backend,
            'framework_version': self.framework_version,
            'reproducibility_score': self.reproducibility_score
        }

# NEW MODEL - Add this at the end
class AccessLog(db.Model):
    __tablename__ = 'access_log'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    researcher_id = db.Column(db.Integer, db.ForeignKey('researcher.researcher_id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    target_entity = db.Column(db.String(50))
    target_id = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    
    # Relationship
    researcher = db.relationship('Researcher', backref='access_logs')
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'researcher_id': self.researcher_id,
            'action_type': self.action_type,
            'target_entity': self.target_entity,
            'target_id': self.target_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }