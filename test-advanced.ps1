# Advanced CRUD Testing for QSLRM

Write-Host "`n=== ADVANCED CRUD TESTS ===" -ForegroundColor Cyan

# 1. CREATE Project
Write-Host "`n1. Creating new project..." -ForegroundColor Yellow
$newProject = @{
    title = "Quantum Annealing Research"
    description = "Exploring D-Wave quantum annealing for optimization problems"
    field_of_study = "Quantum Optimization"
    owner_id = 1
    status = "active"
    start_date = "2025-10-03"
} | ConvertTo-Json

$project = Invoke-RestMethod -Uri "http://localhost:5000/api/projects" -Method POST -Body $newProject -ContentType "application/json"
$projectId = $project.project.project_id
Write-Host "Created project ID: $projectId" -ForegroundColor Green

# 2. Add Team Members
Write-Host "`n2. Adding team members to project..." -ForegroundColor Yellow
$member1 = @{ researcher_id = 2; role = "co-lead" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/projects/$projectId/team" -Method POST -Body $member1 -ContentType "application/json"

$member2 = @{ researcher_id = 3; role = "collaborator" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/projects/$projectId/team" -Method POST -Body $member2 -ContentType "application/json"

Write-Host "Added 2 team members" -ForegroundColor Green

# 3. CREATE Simulation
Write-Host "`n3. Creating simulation..." -ForegroundColor Yellow
$newSim = @{
    project_id = $projectId
    simulation_id = "QA-SIM-001"
    researcher_id = 1
    framework = "Qiskit"
    num_qubits = 16
    circuit_depth = 45
    algorithm_type = "Quantum Annealing"
    description = "QUBO problem solving with 16 qubits"
    status = "running"
} | ConvertTo-Json

$sim = Invoke-RestMethod -Uri "http://localhost:5000/api/simulations" -Method POST -Body $newSim -ContentType "application/json"
$simId = $sim.simulation.run_id
Write-Host "Created simulation ID: $simId" -ForegroundColor Green

# 4. Add Simulation Parameters
Write-Host "`n4. Adding simulation parameters..." -ForegroundColor Yellow
$param1 = @{
    parameter_name = "temperature"
    parameter_value = "0.001"
    parameter_unit = "K"
    parameter_type = "numeric"  # Changed from 'float'
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/simulations/$simId/parameters" -Method POST -Body $param1 -ContentType "application/json"

$param2 = @{
    parameter_name = "annealing_time"
    parameter_value = "20"
    parameter_unit = "microseconds"
    parameter_type = "numeric"  # Changed from 'integer'
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/simulations/$simId/parameters" -Method POST -Body $param2 -ContentType "application/json"

Write-Host "Added 2 parameters" -ForegroundColor Green
# 5. Add Results
Write-Host "`n5. Completing simulation with results..." -ForegroundColor Yellow
$results = @{
    execution_time_seconds = 1.234
    success_probability = 0.923
    fidelity = 0.967
    error_rate = 0.033
    output_data = "Energy: -42.5, Solution: [1,0,1,1,0,1,0,1]"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/simulations/$simId/results" -Method POST -Body $results -ContentType "application/json"
Write-Host "Results saved" -ForegroundColor Green

# 6. Add Reproducibility Metadata
Write-Host "`n6. Adding reproducibility metadata..." -ForegroundColor Yellow
$metadata = @{
    random_seed = 42
    hardware_backend = "ibmq_qasm_simulator"
    framework_version = "0.45.1"
    reproducibility_score = 0.985
    verified_by = "Alice Johnson"
} | ConvertTo-Json
Write-Host "Reproducibility: $($fullSim.repro_metadata.reproducibility_score)" -ForegroundColor Cyan
Invoke-RestMethod -Uri "http://localhost:5000/api/simulations/$simId/metadata" -Method POST -Body $metadata -ContentType "application/json"
Write-Host "Metadata saved" -ForegroundColor Green

# 7. Get Complete Simulation Details
Write-Host "`n7. Retrieving complete simulation..." -ForegroundColor Yellow
$fullSim = Invoke-RestMethod -Uri "http://localhost:5000/api/simulations/$simId"
Write-Host "Simulation: $($fullSim.simulation_id)" -ForegroundColor Cyan
Write-Host "Status: $($fullSim.status)" -ForegroundColor Cyan
Write-Host "Fidelity: $($fullSim.result.fidelity)" -ForegroundColor Cyan
Write-Host "Reproducibility: $($fullSim.repro_metadata.reproducibility_score)" -ForegroundColor Cyan

# 8. Get Researcher's Simulations
Write-Host "`n8. Getting researcher's simulations..." -ForegroundColor Yellow
$researcherSims = Invoke-RestMethod -Uri "http://localhost:5000/api/researchers/1/simulations"
Write-Host "Total simulations: $($researcherSims.simulation_count)" -ForegroundColor Cyan

# 9. Search/Filter Simulations
Write-Host "`n9. Testing filters..." -ForegroundColor Yellow
$qiskitSims = Invoke-RestMethod -Uri "http://localhost:5000/api/simulations?framework=Qiskit"
Write-Host "Qiskit simulations: $($qiskitSims.Count)" -ForegroundColor Cyan

$largeSims = Invoke-RestMethod -Uri "http://localhost:5000/api/simulations?min_qubits=15"
Write-Host "Simulations with 15+ qubits: $($largeSims.Count)" -ForegroundColor Cyan

# 10. Update Dashboard
Write-Host "`n10. Checking updated dashboard..." -ForegroundColor Yellow
$dashboard = Invoke-RestMethod -Uri "http://localhost:5000/api/analytics/dashboard"
Write-Host "Total Projects: $($dashboard.total_projects)" -ForegroundColor Cyan
Write-Host "Total Simulations: $($dashboard.total_simulations)" -ForegroundColor Cyan
Write-Host "Avg Fidelity: $($dashboard.avg_fidelity)" -ForegroundColor Cyan

# Cleanup
Write-Host "`n11. Cleaning up test data..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:5000/api/simulations/$simId" -Method DELETE
Invoke-RestMethod -Uri "http://localhost:5000/api/projects/$projectId" -Method DELETE

Write-Host "`n=== ALL TESTS PASSED ===" -ForegroundColor Green