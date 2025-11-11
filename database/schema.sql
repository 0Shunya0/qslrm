-- =====================================================
-- QSLRM (Quantum Simulation Log & Reproducibility Manager)
-- Database Schema - SQLite
-- =====================================================

-- Enable foreign key constraints (SQLite specific)
PRAGMA foreign_keys = ON;

-- Drop existing tables in reverse dependency order
DROP TABLE IF EXISTS access_log;
DROP TABLE IF EXISTS reproducibility_metadata;
DROP TABLE IF EXISTS simulation_result;
DROP TABLE IF EXISTS quantum_circuit_version;
DROP TABLE IF EXISTS parameter;
DROP TABLE IF EXISTS quantum_simulation;
DROP TABLE IF EXISTS project_researchers;
DROP TABLE IF EXISTS simulation_project;
DROP TABLE IF EXISTS researcher;

-- =====================================================
-- 1. RESEARCHER TABLE
-- =====================================================
CREATE TABLE researcher (
    researcher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    orcid_id TEXT UNIQUE,
    institution TEXT,
    department TEXT,
    role TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (email LIKE '%@%.%')
);

CREATE INDEX idx_researcher_email ON researcher(email);
CREATE INDEX idx_researcher_orcid ON researcher(orcid_id);

-- =====================================================
-- 2. SIMULATION_PROJECT TABLE
-- =====================================================
CREATE TABLE simulation_project (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    field_of_study TEXT,
    owner_id INTEGER NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived', 'on-hold')),
    start_date DATE DEFAULT (DATE('now')),
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES researcher(researcher_id) ON DELETE RESTRICT,
    CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE INDEX idx_project_owner ON simulation_project(owner_id);
CREATE INDEX idx_project_status ON simulation_project(status);

-- =====================================================
-- 3. PROJECT_RESEARCHERS (Junction Table)
-- =====================================================
CREATE TABLE project_researchers (
    project_id INTEGER NOT NULL,
    researcher_id INTEGER NOT NULL,
    role TEXT DEFAULT 'collaborator',
    joined_date DATE DEFAULT (DATE('now')),
    PRIMARY KEY (project_id, researcher_id),
    FOREIGN KEY (project_id) REFERENCES simulation_project(project_id) ON DELETE CASCADE,
    FOREIGN KEY (researcher_id) REFERENCES researcher(researcher_id) ON DELETE CASCADE
);

CREATE INDEX idx_pr_researcher ON project_researchers(researcher_id);
CREATE INDEX idx_pr_project ON project_researchers(project_id);

-- =====================================================
-- 4. QUANTUM_SIMULATION TABLE
-- =====================================================
CREATE TABLE quantum_simulation (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    simulation_id TEXT NOT NULL,
    researcher_id INTEGER NOT NULL,
    framework TEXT NOT NULL CHECK (framework IN ('Qiskit', 'Cirq', 'PennyLane', 'ProjectQ', 'QuTiP', 'Other')),
    num_qubits INTEGER NOT NULL CHECK (num_qubits > 0),
    circuit_depth INTEGER CHECK (circuit_depth >= 0),
    algorithm_type TEXT,
    description TEXT,
    execution_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (project_id, simulation_id),
    FOREIGN KEY (project_id) REFERENCES simulation_project(project_id) ON DELETE CASCADE,
    FOREIGN KEY (researcher_id) REFERENCES researcher(researcher_id) ON DELETE RESTRICT
);

CREATE INDEX idx_simulation_project ON quantum_simulation(project_id);
CREATE INDEX idx_simulation_researcher ON quantum_simulation(researcher_id);
CREATE INDEX idx_simulation_status ON quantum_simulation(status);
CREATE INDEX idx_simulation_date ON quantum_simulation(execution_date);

-- =====================================================
-- 5. PARAMETER TABLE (Weak Entity)
-- =====================================================
CREATE TABLE parameter (
    parameter_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    parameter_name TEXT NOT NULL,
    parameter_value TEXT NOT NULL,
    parameter_unit TEXT,
    parameter_type TEXT DEFAULT 'numeric' CHECK (parameter_type IN ('numeric', 'string', 'boolean', 'array', 'object')),
    UNIQUE (run_id, parameter_name),
    FOREIGN KEY (run_id) REFERENCES quantum_simulation(run_id) ON DELETE CASCADE
);

CREATE INDEX idx_parameter_run ON parameter(run_id);
CREATE INDEX idx_parameter_name ON parameter(parameter_name);

-- =====================================================
-- 6. QUANTUM_CIRCUIT_VERSION TABLE
-- =====================================================
CREATE TABLE quantum_circuit_version (
    circuit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    version TEXT NOT NULL,
    file_path TEXT NOT NULL,
    commit_hash TEXT UNIQUE NOT NULL,
    commit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    description TEXT,
    UNIQUE (run_id, version),
    FOREIGN KEY (run_id) REFERENCES quantum_simulation(run_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES researcher(researcher_id) ON DELETE RESTRICT
);

CREATE INDEX idx_circuit_run ON quantum_circuit_version(run_id);
CREATE INDEX idx_circuit_commit ON quantum_circuit_version(commit_hash);

-- =====================================================
-- 7. SIMULATION_RESULT TABLE (1:1 with QuantumSimulation)
-- =====================================================
CREATE TABLE simulation_result (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER UNIQUE NOT NULL,
    output_data TEXT,  -- JSON stored as TEXT in SQLite
    execution_time_seconds REAL CHECK (execution_time_seconds >= 0),
    success_probability REAL CHECK (success_probability BETWEEN 0 AND 1),
    fidelity REAL CHECK (fidelity BETWEEN 0 AND 1),
    energy_value REAL,
    measurement_counts TEXT,  -- JSON stored as TEXT
    error_rate REAL CHECK (error_rate BETWEEN 0 AND 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES quantum_simulation(run_id) ON DELETE CASCADE
);

CREATE INDEX idx_result_run ON simulation_result(run_id);
CREATE INDEX idx_result_success ON simulation_result(success_probability);

-- =====================================================
-- 8. REPRODUCIBILITY_METADATA TABLE (1:1 with QuantumSimulation)
-- =====================================================
CREATE TABLE reproducibility_metadata (
    metadata_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER UNIQUE NOT NULL,
    random_seed INTEGER,
    hardware_backend TEXT,
    framework_version TEXT,
    software_version TEXT,
    operating_system TEXT,
    python_version TEXT,
    reproducibility_score REAL CHECK (reproducibility_score BETWEEN 0 AND 1),
    verified_by INTEGER,
    verification_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES quantum_simulation(run_id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES researcher(researcher_id) ON DELETE SET NULL
);

CREATE INDEX idx_metadata_run ON reproducibility_metadata(run_id);
CREATE INDEX idx_metadata_score ON reproducibility_metadata(reproducibility_score);

-- =====================================================
-- 9. ACCESS_LOG TABLE
-- =====================================================
CREATE TABLE access_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    researcher_id INTEGER NOT NULL,
    action_type TEXT NOT NULL CHECK (action_type IN ('create', 'read', 'update', 'delete', 'login', 'logout')),
    target_entity TEXT NOT NULL CHECK (target_entity IN ('researcher', 'project', 'simulation', 'result', 'metadata', 'parameter', 'circuit')),
    target_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (researcher_id) REFERENCES researcher(researcher_id) ON DELETE CASCADE
);

CREATE INDEX idx_log_researcher ON access_log(researcher_id);
CREATE INDEX idx_log_timestamp ON access_log(timestamp);
CREATE INDEX idx_log_action ON access_log(action_type);
CREATE INDEX idx_log_entity ON access_log(target_entity);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =====================================================
CREATE TRIGGER update_researcher_updated_at
    AFTER UPDATE ON researcher
    FOR EACH ROW
BEGIN
    UPDATE researcher SET updated_at = CURRENT_TIMESTAMP WHERE researcher_id = NEW.researcher_id;
END;

CREATE TRIGGER update_project_updated_at
    AFTER UPDATE ON simulation_project
    FOR EACH ROW
BEGIN
    UPDATE simulation_project SET updated_at = CURRENT_TIMESTAMP WHERE project_id = NEW.project_id;
END;

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View: Project summary with researcher details
CREATE VIEW vw_project_summary AS
SELECT 
    p.project_id,
    p.title,
    p.field_of_study,
    p.status,
    r.first_name || ' ' || r.last_name AS owner_name,
    r.email AS owner_email,
    COUNT(DISTINCT pr.researcher_id) AS team_size,
    COUNT(DISTINCT qs.run_id) AS simulation_count
FROM simulation_project p
JOIN researcher r ON p.owner_id = r.researcher_id
LEFT JOIN project_researchers pr ON p.project_id = pr.project_id
LEFT JOIN quantum_simulation qs ON p.project_id = qs.project_id
GROUP BY p.project_id, p.title, p.field_of_study, p.status, r.first_name, r.last_name, r.email;

-- View: Simulation details with results
CREATE VIEW vw_simulation_details AS
SELECT 
    qs.run_id,
    qs.simulation_id,
    qs.framework,
    qs.num_qubits,
    qs.algorithm_type,
    qs.status,
    sr.execution_time_seconds,
    sr.success_probability,
    sr.fidelity,
    rm.reproducibility_score,
    rm.hardware_backend,
    p.title AS project_title,
    r.first_name || ' ' || r.last_name AS researcher_name
FROM quantum_simulation qs
LEFT JOIN simulation_result sr ON qs.run_id = sr.run_id
LEFT JOIN reproducibility_metadata rm ON qs.run_id = rm.run_id
JOIN simulation_project p ON qs.project_id = qs.project_id
JOIN researcher r ON qs.researcher_id = r.researcher_id;

-- =====================================================
-- END OF SCHEMA
-- =====================================================