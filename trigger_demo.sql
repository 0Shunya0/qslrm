-- =====================================================
-- QSLRM TRIGGER DEMONSTRATION SCRIPT
-- Run this in DB Browser for SQLite
-- =====================================================

.mode column
.headers on
.width 15 20 35 25

-- =====================================================
-- DEMO 1: Researcher Timestamp Trigger
-- =====================================================
SELECT '';
SELECT '========================================' as '';
SELECT '  DEMO 1: RESEARCHER TIMESTAMP TRIGGER' as '';
SELECT '========================================' as '';
SELECT '';

-- Show the trigger
SELECT 'Trigger Code:' as '';
SELECT sql FROM sqlite_master 
WHERE type = 'trigger' AND name = 'update_researcher_timestamp';

SELECT '';
SELECT '--- BEFORE UPDATE ---' as status;
SELECT researcher_id, first_name, email, updated_at 
FROM researcher WHERE researcher_id = 1;

SELECT '';
SELECT 'Executing UPDATE...' as action;

-- This will fire the trigger!
UPDATE researcher 
SET email = 'alice.trigger-demo@quantumlab.edu' 
WHERE researcher_id = 1;

SELECT '';
SELECT '--- AFTER UPDATE (Timestamp Auto-Updated!) ---' as status;
SELECT researcher_id, first_name, email, updated_at 
FROM researcher WHERE researcher_id = 1;

-- =====================================================
-- DEMO 2: Project Timestamp Trigger
-- =====================================================
SELECT '';
SELECT '';
SELECT '========================================' as '';
SELECT '  DEMO 2: PROJECT TIMESTAMP TRIGGER' as '';
SELECT '========================================' as '';
SELECT '';

SELECT '--- BEFORE UPDATE ---' as status;
SELECT project_id, title, status, updated_at 
FROM simulation_project WHERE project_id = 1;

SELECT '';
SELECT 'Executing UPDATE...' as action;

-- This will fire the trigger!
UPDATE simulation_project 
SET status = 'active' 
WHERE project_id = 1;

SELECT '';
SELECT '--- AFTER UPDATE (Timestamp Auto-Updated!) ---' as status;
SELECT project_id, title, status, updated_at 
FROM simulation_project WHERE project_id = 1;

-- =====================================================
-- DEMO 3: Simulation Creation Trigger
-- =====================================================
SELECT '';
SELECT '';
SELECT '========================================' as '';
SELECT '  DEMO 3: SIMULATION CREATION TRIGGER' as '';
SELECT '========================================' as '';
SELECT '';

SELECT '--- BEFORE: Count of simulations ---' as status;
SELECT COUNT(*) as simulation_count FROM quantum_simulation;

SELECT '';
SELECT 'Creating new simulation...' as action;

-- Insert new simulation (triggers will fire)
INSERT INTO quantum_simulation (
    project_id, simulation_id, researcher_id, 
    framework, num_qubits, algorithm_type, status
) VALUES (
    1, 'DEMO_TRIGGER_001', 1, 
    'Qiskit', 8, 'VQE', 'completed'
);

SELECT '';
SELECT '--- AFTER: New simulation created ---' as status;
SELECT COUNT(*) as simulation_count FROM quantum_simulation;

SELECT '';
SELECT 'Latest simulation:' as '';
SELECT simulation_id, framework, num_qubits, status, created_at 
FROM quantum_simulation 
ORDER BY run_id DESC LIMIT 1;

-- =====================================================
-- DEMO 4: Access Log Trigger (if exists)
-- =====================================================
SELECT '';
SELECT '';
SELECT '========================================' as '';
SELECT '  DEMO 4: ACCESS LOG CHECK' as '';
SELECT '========================================' as '';
SELECT '';

SELECT '--- Recent Access Logs ---' as status;
SELECT researcher_id, action_type, target_entity, timestamp 
FROM access_log 
ORDER BY timestamp DESC LIMIT 5;

-- =====================================================
-- DEMO 5: Show All Active Triggers
-- =====================================================
SELECT '';
SELECT '';
SELECT '========================================' as '';
SELECT '  ALL ACTIVE TRIGGERS IN DATABASE' as '';
SELECT '========================================' as '';
SELECT '';

SELECT 
    name as trigger_name,
    tbl_name as table_name,
    CASE 
        WHEN sql LIKE '%BEFORE%' THEN 'BEFORE'
        WHEN sql LIKE '%AFTER%' THEN 'AFTER'
        ELSE 'UNKNOWN'
    END as timing,
    CASE 
        WHEN sql LIKE '%INSERT%' THEN 'INSERT'
        WHEN sql LIKE '%UPDATE%' THEN 'UPDATE'
        WHEN sql LIKE '%DELETE%' THEN 'DELETE'
        ELSE 'MULTIPLE'
    END as event_type
FROM sqlite_master 
WHERE type = 'trigger'
ORDER BY tbl_name, name;

SELECT '';
SELECT 'Total Triggers: ' || COUNT(*) as summary
FROM sqlite_master WHERE type = 'trigger';

SELECT '';
SELECT '========================================' as '';
SELECT '  DEMO COMPLETE!' as '';
SELECT '========================================' as '';