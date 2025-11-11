-- SQLite Sample Data for QSLRM
PRAGMA foreign_keys = ON;

-- Clear existing data
DELETE FROM access_log;
DELETE FROM reproducibility_metadata;
DELETE FROM simulation_result;
DELETE FROM quantum_circuit_version;
DELETE FROM parameter;
DELETE FROM quantum_simulation;
DELETE FROM project_researchers;
DELETE FROM simulation_project;
DELETE FROM researcher;
-- DELETE FROM sqlite_sequence; -- Only needed to reset AUTOINCREMENT counters, often omitted for simple data clearing.

-- Insert Researchers
INSERT INTO researcher (first_name, last_name, email, orcid_id, institution, department, role) VALUES
('Alice', 'Johnson', 'alice.johnson@quantumlab.edu', '0000-0001-2345-6789', 'MIT', 'Physics', 'Principal Investigator'),
('Bob', 'Smith', 'bob.smith@quantumlab.edu', '0000-0002-3456-7890', 'Stanford', 'Computer Science', 'Senior Researcher'),
('Carol', 'Williams', 'carol.williams@quantumlab.edu', '0000-0003-4567-8901', 'Caltech', 'Applied Physics', 'Postdoctoral Fellow'),
('David', 'Brown', 'david.brown@quantumlab.edu', '0000-0004-5678-9012', 'UC Berkeley', 'Electrical Engineering', 'PhD Student'),
('Emma', 'Davis', 'emma.davis@quantumlab.edu', '0000-0005-6789-0123', 'Harvard', 'Chemistry', 'Research Scientist'),
('Frank', 'Miller', 'frank.miller@quantumlab.edu', '0000-0006-7890-1234', 'Princeton', 'Mathematics', 'Assistant Professor'),
('Grace', 'Wilson', 'grace.wilson@quantumlab.edu', '0000-0007-8901-2345', 'Yale', 'Physics', 'Graduate Student'),
('Henry', 'Moore', 'henry.moore@quantumlab.edu', '0000-0008-9012-3456', 'Columbia', 'Computer Science', 'Research Assistant');

-- Insert Projects
INSERT INTO simulation_project (title, description, field_of_study, owner_id, status, start_date, end_date) VALUES
('Quantum Error Correction Study', 'Investigating surface codes and logical qubit performance', 'Quantum Error Correction', 1, 'active', '2024-01-15', NULL),
('VQE for Molecular Systems', 'Variational Quantum Eigensolver applications', 'Quantum Chemistry', 2, 'active', '2024-02-01', NULL),
('QAOA Optimization Research', 'QAOA for combinatorial problems', 'Quantum Algorithms', 3, 'completed', '2023-09-01', '2024-08-31'),
('Quantum Machine Learning', 'Quantum neural networks and kernel methods', 'Quantum ML', 1, 'active', '2024-03-10', NULL),
('Grover Search Benchmarks', 'Performance analysis of Grover algorithm', 'Quantum Algorithms', 4, 'on-hold', '2024-04-15', NULL),
('Quantum Cryptography Protocols', 'QKD and post-quantum cryptography', 'Quantum Cryptography', 5, 'active', '2024-05-01', NULL);

-- Insert Project Researchers
INSERT INTO project_researchers (project_id, researcher_id, role, joined_date) VALUES
(1, 1, 'lead', '2024-01-15'), (1, 4, 'developer', '2024-01-20'), (1, 7, 'analyst', '2024-02-01'),
(2, 2, 'lead', '2024-02-01'), (2, 5, 'co-lead', '2024-02-01'), (2, 8, 'developer', '2024-02-15'),
(3, 3, 'lead', '2023-09-01'), (3, 6, 'consultant', '2023-10-01'),
(4, 1, 'lead', '2024-03-10'), (4, 3, 'collaborator', '2024-03-15'), (4, 7, 'developer', '2024-03-20'),
(5, 4, 'lead', '2024-04-15'), (5, 2, 'advisor', '2024-04-20'),
(6, 5, 'lead', '2024-05-01'), (6, 6, 'collaborator', '2024-05-05');

-- Insert Simulations (The implicit rowid for these 16 insertions will be 1 through 16)
INSERT INTO quantum_simulation (project_id, simulation_id, researcher_id, framework, num_qubits, circuit_depth, algorithm_type, description, status, execution_date) VALUES
(1, 'QEC-001', 1, 'Qiskit', 9, 12, 'Surface Code', 'Initial implementation', 'completed', '2024-01-20 10:30:00'), -- rowid 1
(1, 'QEC-002', 4, 'Qiskit', 17, 18, 'Surface Code', 'Distance 5 code', 'completed', '2024-02-05 14:15:00'), -- rowid 2
(1, 'QEC-003', 7, 'Qiskit', 25, 24, 'Surface Code', 'Large scale', 'completed', '2024-03-10 09:00:00'), -- rowid 3
(2, 'VQE-001', 2, 'PennyLane', 4, 8, 'VQE', 'H2 molecule', 'completed', '2024-02-10 11:00:00'), -- rowid 4
(2, 'VQE-002', 5, 'PennyLane', 6, 12, 'VQE', 'LiH molecule', 'completed', '2024-03-15 13:30:00'), -- rowid 5
(2, 'VQE-003', 8, 'PennyLane', 8, 16, 'VQE', 'H2O molecule', 'running', '2024-09-25 10:00:00'), -- rowid 6 (no result/metadata)
(3, 'QAOA-001', 3, 'Cirq', 12, 10, 'QAOA', 'MaxCut problem', 'completed', '2023-11-15 16:45:00'), -- rowid 7
(3, 'QAOA-002', 6, 'Cirq', 16, 14, 'QAOA', 'Graph partitioning', 'completed', '2024-01-20 12:00:00'), -- rowid 8
(3, 'QAOA-003', 3, 'Cirq', 20, 18, 'QAOA', 'Portfolio optimization', 'completed', '2024-06-30 15:30:00'), -- rowid 9
(4, 'QML-001', 1, 'Qiskit', 8, 10, 'QNN', 'Binary classification', 'completed', '2024-04-01 14:00:00'), -- rowid 10
(4, 'QML-002', 3, 'PennyLane', 10, 12, 'Quantum Kernel', 'SVM with quantum kernel', 'completed', '2024-05-15 11:30:00'), -- rowid 11
(4, 'QML-003', 7, 'Qiskit', 12, 15, 'QNN', 'Multi-class classification', 'failed', '2024-07-20 09:45:00'), -- rowid 12 (no result/metadata)
(5, 'GROVER-001', 4, 'Qiskit', 10, 8, 'Grover', 'Database search', 'completed', '2024-05-10 10:15:00'), -- rowid 13
(5, 'GROVER-002', 2, 'Cirq', 12, 10, 'Grover', 'Amplitude amplification', 'completed', '2024-06-05 13:00:00'), -- rowid 14
(6, 'QKD-001', 5, 'QuTiP', 8, 6, 'BB84', 'BB84 protocol', 'completed', '2024-06-15 12:30:00'), -- rowid 15
(6, 'QKD-002', 6, 'QuTiP', 10, 8, 'E91', 'Entanglement-based QKD', 'completed', '2024-08-01 14:45:00'); -- rowid 16

-- Insert Parameters
INSERT INTO parameter (run_id, parameter_name, parameter_value, parameter_unit, parameter_type) VALUES
(1, 'code_distance', '3', 'qubits', 'numeric'), (1, 'num_cycles', '10', 'rounds', 'numeric'),
(4, 'optimizer', 'COBYLA', NULL, 'string'), (4, 'bond_length', '0.735', 'angstrom', 'numeric'),
(7, 'num_layers', '5', 'layers', 'numeric'), (7, 'optimizer', 'SPSA', NULL, 'string'),
(10, 'learning_rate', '0.01', 'unitless', 'numeric'), (10, 'batch_size', '32', 'samples', 'numeric'),
(13, 'database_size', '1024', 'entries', 'numeric'), (13, 'num_iterations', '25', 'iterations', 'numeric');

-- Insert Circuit Versions
INSERT INTO quantum_circuit_version (run_id, version, file_path, commit_hash, created_by, description) VALUES
(1, 'v1.0', '/circuits/qec001_v1.qasm', 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0', 1, 'Initial'),
(1, 'v1.1', '/circuits/qec001_v1_1.qasm', 'b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1', 1, 'Optimized'),
(4, 'v1.0', '/circuits/vqe001_v1.qasm', 'c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2', 2, 'H2 ansatz'),
(7, 'v1.0', '/circuits/qaoa001_v1.qasm', 'd4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3', 3, 'MaxCut'),
(10, 'v1.0', '/circuits/qml001_v1.qasm', 'e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4', 1, 'QNN v1');

-- Insert Results
INSERT INTO simulation_result (run_id, output_data, execution_time_seconds, success_probability, fidelity, error_rate) VALUES
(1, '{"logical_errors": 0}', 45.23, 0.9850, 0.9920, 0.0150),
(2, '{"logical_errors": 1}', 128.67, 0.9650, 0.9780, 0.0350),
(3, '{"logical_errors": 2}', 287.45, 0.9400, 0.9550, 0.0600),
(4, '{"eigenvalue": -1.1372}', 234.12, 0.8900, 0.9450, 0.0110),
(5, '{"eigenvalue": -7.8823}', 456.78, 0.8650, 0.9280, 0.0135),
(7, '{"max_cut_value": 18}', 189.34, 0.7800, 0.8920, 0.0220),
(8, '{"cut_value": 24}', 267.89, 0.8100, 0.9050, 0.0190),
(9, '{"portfolio_return": 0.145}', 345.67, 0.7950, 0.8890, 0.0205),
(10, '{"accuracy": 0.87}', 123.45, 0.8700, 0.9100, 0.0130),
(11, '{"accuracy": 0.91}', 198.76, 0.9100, 0.9350, 0.0090),
(13, '{"found_element": true}', 67.89, 0.9600, 0.9750, 0.0040),
(14, '{"found_element": true}', 89.12, 0.9450, 0.9680, 0.0055),
(15, '{"key_generated": true}', 156.34, 0.9750, 0.9850, 0.0025),
(16, '{"key_generated": true}', 203.45, 0.9690, 0.9820, 0.0031);

-- Insert Metadata
INSERT INTO reproducibility_metadata (run_id, random_seed, hardware_backend, framework_version, reproducibility_score, verified_by, verification_date) VALUES
(1, 42, 'ibmq_qasm_simulator', 'Qiskit 0.45.0', 0.9800, 4, '2024-01-25 15:30:00'),
(2, 123, 'ibmq_qasm_simulator', 'Qiskit 0.45.0', 0.9650, 7, '2024-02-10 11:20:00'),
(3, 456, 'ibmq_qasm_simulator', 'Qiskit 0.45.0', 0.9450, 1, '2024-03-15 14:45:00'),
(4, 789, 'default.qubit', 'PennyLane 0.33.0', 0.9900, 5, '2024-02-15 10:00:00'),
(5, 321, 'default.qubit', 'PennyLane 0.33.0', 0.9750, 8, '2024-03-20 13:15:00'),
(7, 654, 'cirq_simulator', 'Cirq 1.3.0', 0.9550, 6, '2023-11-20 09:30:00'),
(8, 987, 'cirq_simulator', 'Cirq 1.3.0', 0.9600, 3, '2024-01-25 16:00:00'),
(9, 147, 'cirq_simulator', 'Cirq 1.3.0', 0.9400, 3, '2024-07-05 12:30:00'),
(10, 258, 'aer_simulator', 'Qiskit 0.45.0', 0.8900, 3, '2024-04-05 15:45:00'),
(11, 369, 'default.qubit', 'PennyLane 0.33.0', 0.9200, 7, '2024-05-20 10:30:00'),
(13, 741, 'aer_simulator', 'Qiskit 0.45.0', 0.9850, 2, '2024-05-15 14:00:00'),
(14, 852, 'cirq_simulator', 'Cirq 1.3.0', 0.9800, 4, '2024-06-10 11:45:00'),
(15, 963, 'qutip_simulator', 'QuTiP 4.7.1', 0.9700, 6, '2024-06-20 13:30:00'),
(16, 159, 'qutip_simulator', 'QuTiP 4.7.1', 0.9650, 5, '2024-08-05 15:15:00');

-- Insert Access Logs
INSERT INTO access_log (researcher_id, action_type, target_entity, target_id, timestamp, ip_address) VALUES
(1, 'login', 'researcher', 1, '2024-01-15 08:00:00', '192.168.1.10'),
(1, 'create', 'project', 1, '2024-01-15 09:30:00', '192.168.1.10'),
(1, 'create', 'simulation', 1, '2024-01-20 10:30:00', '192.168.1.10'),
(2, 'login', 'researcher', 2, '2024-02-01 08:30:00', '192.168.1.11'),
(2, 'create', 'project', 2, '2024-02-01 10:00:00', '192.168.1.11'),
(3, 'login', 'researcher', 3, '2024-01-15 09:00:00', '192.168.1.12'),
(4, 'create', 'simulation', 2, '2024-02-05 14:15:00', '192.168.1.14'),
(5, 'create', 'simulation', 5, '2024-03-15 13:30:00', '192.168.1.15');