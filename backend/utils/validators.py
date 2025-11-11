"""
Data Validation Utilities for QSLRM
"""

import re
from datetime import datetime

class ValidationError(Exception):
    """Custom validation error"""
    pass

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}")
    return True

def validate_orcid(orcid_id):
    """Validate ORCID ID format (0000-0000-0000-0000)"""
    if not orcid_id:
        return True  # Optional field
    
    pattern = r'^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$'
    if not re.match(pattern, orcid_id):
        raise ValidationError(f"Invalid ORCID format. Expected: 0000-0000-0000-0000, got: {orcid_id}")
    return True

def validate_qubit_count(num_qubits):
    """Validate qubit count is within reasonable range"""
    if not isinstance(num_qubits, int):
        raise ValidationError(f"Qubit count must be an integer, got: {type(num_qubits)}")
    
    if num_qubits < 1:
        raise ValidationError("Qubit count must be at least 1")
    
    if num_qubits > 1000:
        raise ValidationError("Qubit count cannot exceed 1000")
    
    return True

def validate_probability(value, field_name="probability"):
    """Validate probability is between 0 and 1"""
    if value is None:
        return True  # Optional field
    
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number")
    
    if not 0 <= value <= 1:
        raise ValidationError(f"{field_name} must be between 0 and 1, got: {value}")
    
    return True

def validate_status(status, valid_statuses):
    """Validate status is in allowed list"""
    if status not in valid_statuses:
        raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    return True

def validate_framework(framework):
    """Validate quantum framework name"""
    valid_frameworks = ['Qiskit', 'Cirq', 'PennyLane', 'ProjectQ', 'QuTiP', 'Other']
    if framework not in valid_frameworks:
        raise ValidationError(f"Invalid framework. Must be one of: {', '.join(valid_frameworks)}")
    return True

def validate_parameter_type(param_type):
    """Validate parameter type"""
    valid_types = ['numeric', 'string', 'boolean', 'array', 'object']
    if param_type not in valid_types:
        raise ValidationError(f"Invalid parameter type. Must be one of: {', '.join(valid_types)}")
    return True

def validate_date(date_str, field_name="date"):
    """Validate date format (YYYY-MM-DD)"""
    if not date_str:
        return True  # Optional field
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValidationError(f"{field_name} must be in format YYYY-MM-DD, got: {date_str}")
    
    return True

def validate_date_range(start_date, end_date):
    """Validate that end_date is after start_date"""
    if not start_date or not end_date:
        return True
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if end < start:
            raise ValidationError("End date must be after start date")
    except ValueError as e:
        raise ValidationError(f"Invalid date format: {e}")
    
    return True

def validate_circuit_depth(depth):
    """Validate circuit depth"""
    if depth is None:
        return True  # Optional field
    
    if not isinstance(depth, int):
        raise ValidationError(f"Circuit depth must be an integer, got: {type(depth)}")
    
    if depth < 0:
        raise ValidationError("Circuit depth cannot be negative")
    
    if depth > 10000:
        raise ValidationError("Circuit depth seems unreasonably large (max 10000)")
    
    return True

def validate_execution_time(seconds):
    """Validate execution time"""
    if seconds is None:
        return True
    
    try:
        seconds = float(seconds)
    except (TypeError, ValueError):
        raise ValidationError("Execution time must be a number")
    
    if seconds < 0:
        raise ValidationError("Execution time cannot be negative")
    
    if seconds > 86400:  # 24 hours
        raise ValidationError("Execution time seems unreasonably long (max 24 hours)")
    
    return True

def validate_required_fields(data, required_fields):
    """Check that all required fields are present"""
    missing = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")
    
    return True

def sanitize_string(text, max_length=None):
    """Sanitize string input"""
    if not text:
        return text
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

def validate_simulation_id(sim_id):
    """Validate simulation ID format"""
    if not sim_id:
        raise ValidationError("Simulation ID is required")
    
    # Allow alphanumeric, hyphens, underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, sim_id):
        raise ValidationError("Simulation ID can only contain letters, numbers, hyphens, and underscores")
    
    if len(sim_id) > 100:
        raise ValidationError("Simulation ID too long (max 100 characters)")
    
    return True

# Composite validators for common operations
def validate_researcher_data(data, is_update=False):
    """Validate researcher creation/update data"""
    if not is_update:
        validate_required_fields(data, ['first_name', 'last_name', 'email'])
    
    if 'email' in data:
        validate_email(data['email'])
    
    if 'orcid_id' in data and data['orcid_id']:
        validate_orcid(data['orcid_id'])
    
    return True

def validate_project_data(data, is_update=False):
    """Validate project creation/update data"""
    if not is_update:
        validate_required_fields(data, ['title', 'owner_id'])
    
    if 'status' in data:
        valid_statuses = ['active', 'completed', 'archived', 'on-hold']
        validate_status(data['status'], valid_statuses)
    
    if 'start_date' in data:
        validate_date(data['start_date'], 'start_date')
    
    if 'end_date' in data:
        validate_date(data['end_date'], 'end_date')
    
    if 'start_date' in data and 'end_date' in data:
        validate_date_range(data['start_date'], data['end_date'])
    
    return True

def validate_simulation_data(data, is_update=False):
    """Validate simulation creation/update data"""
    if not is_update:
        validate_required_fields(data, ['project_id', 'simulation_id', 'researcher_id', 'framework', 'num_qubits'])
        validate_simulation_id(data['simulation_id'])
        validate_framework(data['framework'])
        validate_qubit_count(data['num_qubits'])
    else:
        if 'num_qubits' in data:
            validate_qubit_count(data['num_qubits'])
        if 'framework' in data:
            validate_framework(data['framework'])
    
    if 'status' in data:
        valid_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
        validate_status(data['status'], valid_statuses)
    
    if 'circuit_depth' in data:
        validate_circuit_depth(data['circuit_depth'])
    
    return True

def validate_result_data(data):
    """Validate simulation result data"""
    if 'execution_time_seconds' in data:
        validate_execution_time(data['execution_time_seconds'])
    
    if 'success_probability' in data:
        validate_probability(data['success_probability'], 'success_probability')
    
    if 'fidelity' in data:
        validate_probability(data['fidelity'], 'fidelity')
    
    if 'error_rate' in data:
        validate_probability(data['error_rate'], 'error_rate')
    
    return True

def validate_metadata_data(data):
    """Validate reproducibility metadata"""
    if 'reproducibility_score' in data:
        validate_probability(data['reproducibility_score'], 'reproducibility_score')
    
    return True

def validate_parameter_data(data):
    """Validate parameter data"""
    validate_required_fields(data, ['parameter_name', 'parameter_value'])
    
    if 'parameter_type' in data:
        validate_parameter_type(data['parameter_type'])
    
    return True