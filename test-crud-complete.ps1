# QSLRM v2.0 - Complete CRUD Testing Script
# Final fixed version with all PowerShell quirks resolved

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QSLRM v2.0 - CRUD Operations Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:5000/api"
$testPassed = 0
$testFailed = 0

# Initialize variables
$newResearcherId = $null
$newProjectId = $null
$newSimId = $null

# TEST 1: CREATE Researcher
Write-Host "1. Creating new researcher..." -ForegroundColor Yellow
$newResearcher = @{
    first_name = "Jane"
    last_name = "Smith"
    email = "jane.smith@quantumlab.edu"
    orcid_id = "0000-0009-9999-9999"
    institution = "MIT"
    department = "Quantum Computing"
    role = "Postdoctoral Researcher"
} | ConvertTo-Json

try {
    $createResult = Invoke-RestMethod -Uri "$baseUrl/researchers" -Method POST -Body $newResearcher -ContentType "application/json"
    $newResearcherId = $createResult.researcher.researcher_id
    Write-Host "   ✓ Created researcher ID: $newResearcherId" -ForegroundColor Green
    $testPassed++
} catch {
    Write-Host "   ✗ Create failed: $($_.Exception.Message)" -ForegroundColor Red
    $testFailed++
    Write-Host ""
    Write-Host "Cannot continue without researcher. Exiting..." -ForegroundColor Red
    exit 1
}

# TEST 2: GET One Researcher
Write-Host ""
Write-Host "2. Getting researcher details..." -ForegroundColor Yellow
try {
    $researcher = Invoke-RestMethod -Uri "$baseUrl/researchers/$newResearcherId"
    Write-Host "   ✓ Retrieved: $($researcher.full_name)" -ForegroundColor Green
    Write-Host "     Institution: $($researcher.institution)" -ForegroundColor Gray
    Write-Host "     Total Simulations: $($researcher.statistics.total_simulations)" -ForegroundColor Gray
    $testPassed++
} catch {
    Write-Host "   ✗ Get failed: $($_.Exception.Message)" -ForegroundColor Red
    $testFailed++
}

# TEST 3: UPDATE Researcher
Write-Host ""
Write-Host "3. Updating researcher role..." -ForegroundColor Yellow
$update = @{
    role = "Senior Researcher"
    department = "Advanced Quantum Systems"
} | ConvertTo-Json

try {
    $updateResult = Invoke-RestMethod -Uri "$baseUrl/researchers/$newResearcherId" -Method PUT -Body $update -ContentType "application/json"
    Write-Host "   ✓ Updated role to: $($updateResult.researcher.role)" -ForegroundColor Green
    $testPassed++
} catch {
    Write-Host "   ✗ Update failed: $($_.Exception.Message)" -ForegroundColor Red
    $testFailed++
}

# TEST 4: CREATE Project
Write-Host ""
Write-Host "4. Creating new project..." -ForegroundColor Yellow
$newProject = @{
    title = "Quantum Entanglement Studies"
    description = "Research on entanglement properties"
    field_of_study = "Quantum Information Theory"
    owner_id = $newResearcherId
    status = "active"
    start_date = "2025-10-01"
} | ConvertTo-Json

try {
    $projectResult = Invoke-RestMethod -Uri "$baseUrl/projects" -Method POST -Body $newProject -ContentType "application/json"
    $newProjectId = $projectResult.project.project_id
    Write-Host "   ✓ Created project ID: $newProjectId" -ForegroundColor Green
    $testPassed++
} catch {
    Write-Host "   ✗ Project creation failed: $($_.Exception.Message)" -ForegroundColor Red
    $testFailed++
}

# TEST 5: Add Team Member
if ($newProjectId) {
    Write-Host ""
    Write-Host "5. Adding team member to project..." -ForegroundColor Yellow
    $teamMember = @{
        researcher_id = 1
        role = "collaborator"
    } | ConvertTo-Json

    try {
        $teamResult = Invoke-RestMethod -Uri "$baseUrl/projects/$newProjectId/team" -Method POST -Body $teamMember -ContentType "application/json"
        Write-Host "   ✓ Added: $($teamResult.member.researcher_name)" -ForegroundColor Green
        $testPassed++
    } catch {
        Write-Host "   ✗ Team member add failed: $($_.Exception.Message)" -ForegroundColor Red
        $testFailed++
    }
} else {
    Write-Host ""
    Write-Host "5. ⊘ Skipping team member test (no project ID)" -ForegroundColor Yellow
}

# TEST 6: CREATE Simulation
Write-Host ""
Write-Host "6. Creating simulation..." -ForegroundColor Yellow
if ($newProjectId) {
    $newSim = @{
        project_id = $newProjectId
        simulation_id = "ENT-001"
        researcher_id = $newResearcherId
        framework = "Qiskit"
        num_qubits = 8
        circuit_depth = 12
        algorithm_type = "Entanglement"
        description = "Bell state preparation"
        status = "completed"
    } | ConvertTo-Json

    try {
        $simResult = Invoke-RestMethod -Uri "$baseUrl/simulations" -Method POST -Body $newSim -ContentType "application/json"
        $newSimId = $simResult.simulation.run_id
        Write-Host "   ✓ Created simulation ID: $newSimId" -ForegroundColor Green
        $testPassed++
    } catch {
        Write-Host "   ✗ Simulation creation failed: $($_.Exception.Message)" -ForegroundColor Red
        $testFailed++
    }
} else {
    Write-Host "   ⊘ Skipping simulation test (no project ID)" -ForegroundColor Yellow
}

# TEST 7: Add Results
if ($newSimId) {
    Write-Host ""
    Write-Host "7. Adding simulation results..." -ForegroundColor Yellow
    $results = @{
        execution_time_seconds = 45.2
        success_probability = 0.985
        fidelity = 0.978
        error_rate = 0.022
        output_data = "Bell state fidelity measured"
    } | ConvertTo-Json

    try {
        $resultData = Invoke-RestMethod -Uri "$baseUrl/simulations/$newSimId/results" -Method POST -Body $results -ContentType "application/json"
        Write-Host "   ✓ Results saved - Fidelity: $($resultData.result.fidelity)" -ForegroundColor Green
        $testPassed++
    } catch {
        Write-Host "   ✗ Results failed: $($_.Exception.Message)" -ForegroundColor Red
        $testFailed++
    }
} else {
    Write-Host ""
    Write-Host "7. ⊘ Skipping results test (no simulation ID)" -ForegroundColor Yellow
}

# TEST 8: Add Metadata
if ($newSimId) {
    Write-Host ""
    Write-Host "8. Adding reproducibility metadata..." -ForegroundColor Yellow
    $metadata = @{
        random_seed = 42
        hardware_backend = "ibmq_simulator"
        framework_version = "0.45.0"
        reproducibility_score = 0.96
        verified_by = $newResearcherId
    } | ConvertTo-Json

    try {
        $metaData = Invoke-RestMethod -Uri "$baseUrl/simulations/$newSimId/metadata" -Method POST -Body $metadata -ContentType "application/json"
        Write-Host "   ✓ Metadata saved - Repro score: $($metaData.metadata.reproducibility_score)" -ForegroundColor Green
        $testPassed++
    } catch {
        Write-Host "   ✗ Metadata failed: $($_.Exception.Message)" -ForegroundColor Red
        $testFailed++
    }
} else {
    Write-Host ""
    Write-Host "8. ⊘ Skipping metadata test (no simulation ID)" -ForegroundColor Yellow
}

# TEST 9: Add Parameters
if ($newSimId) {
    Write-Host ""
    Write-Host "9. Adding simulation parameters..." -ForegroundColor Yellow
    $param1 = @{
        parameter_name = "theta"
        parameter_value = "0.785"
        parameter_unit = "radians"
        parameter_type = "float"
    } | ConvertTo-Json

    try {
        $paramResult = Invoke-RestMethod -Uri "$baseUrl/simulations/$newSimId/parameters" -Method POST -Body $param1 -ContentType "application/json"
        Write-Host "   ✓ Parameter theta added" -ForegroundColor Green
        $testPassed++
    } catch {
        Write-Host "   ✗ Parameter failed: $($_.Exception.Message)" -ForegroundColor Red
        $testFailed++
    }
} else {
    Write-Host ""
    Write-Host "9. ⊘ Skipping parameters test (no simulation ID)" -ForegroundColor Yellow
}

# TEST 10: Filter Simulations - Using SINGLE QUOTES to avoid ampersand parsing
Write-Host ""
Write-Host "10. Testing simulation filters..." -ForegroundColor Yellow
try {
    # Build query string in single quotes to prevent PowerShell ampersand parsing
    $queryString = 'framework=Qiskit&min_qubits=8'
    $filterUrl = "$baseUrl/simulations?$queryString"

    $filtered = Invoke-RestMethod -Uri $filterUrl
    $count = if ($filtered -is [Array]) { $filtered.Count } else { 1 }
    Write-Host "   ✓ Found $count Qiskit simulation(s) with 8+ qubits" -ForegroundColor Green
    $testPassed++
} catch {
    Write-Host "   ✗ Filter failed: $($_.Exception.Message)" -ForegroundColor Red
    $testFailed++
}

# TEST 11: Get Researcher's Projects
Write-Host ""
Write-Host "11. Getting researcher's projects..." -ForegroundColor Yellow
try {
    $projects = Invoke-RestMethod -Uri "$baseUrl/researchers/$newResearcherId/projects"
    $ownedCount = if ($projects.owned_projects) { $projects.owned_projects.Count } else { 0 }
    $participatedCount = if ($projects.participated_projects) { $projects.participated_projects.Count } else { 0 }
    Write-Host "   ✓ Owned: $ownedCount, Participated: $participatedCount" -ForegroundColor Green
    $testPassed++
} catch {
    Write-Host "   ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    $testFailed++
}

# CLEANUP
Write-Host ""
Write-Host "12. Cleanup - Deleting test data..." -ForegroundColor Yellow
$cleanupSuccess = $true

if ($newSimId) {
    try {
        Invoke-RestMethod -Uri "$baseUrl/simulations/$newSimId" -Method DELETE | Out-Null
        Write-Host "   ✓ Deleted simulation $newSimId" -ForegroundColor Gray
    } catch {
        Write-Host "   ⚠ Could not delete simulation: $($_.Exception.Message)" -ForegroundColor Yellow
        $cleanupSuccess = $false
    }
}

if ($newProjectId) {
    try {
        Invoke-RestMethod -Uri "$baseUrl/projects/$newProjectId" -Method DELETE | Out-Null
        Write-Host "   ✓ Deleted project $newProjectId" -ForegroundColor Gray
    } catch {
        Write-Host "   ⚠ Could not delete project: $($_.Exception.Message)" -ForegroundColor Yellow
        $cleanupSuccess = $false
    }
}

if ($newResearcherId) {
    try {
        Invoke-RestMethod -Uri "$baseUrl/researchers/$newResearcherId" -Method DELETE | Out-Null
        Write-Host "   ✓ Deleted researcher $newResearcherId" -ForegroundColor Gray
    } catch {
        Write-Host "   ⚠ Could not delete researcher: $($_.Exception.Message)" -ForegroundColor Yellow
        $cleanupSuccess = $false
    }
}

if ($cleanupSuccess) {
    Write-Host ""
    Write-Host "   ✓ All test data cleaned up successfully" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "   ⚠ Some cleanup operations failed (may be due to cascade deletes)" -ForegroundColor Yellow
}

# SUMMARY
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CRUD Testing Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tests Passed: " -NoNewline
Write-Host "$testPassed" -ForegroundColor Green
Write-Host "Tests Failed: " -NoNewline
Write-Host "$testFailed" -ForegroundColor $(if ($testFailed -eq 0) { "Green" } else { "Red" })

if (($testPassed + $testFailed) -gt 0) {
    Write-Host "Success Rate: " -NoNewline
    $successRate = [math]::Round(($testPassed / ($testPassed + $testFailed)) * 100, 1)
    Write-Host "$successRate%" -ForegroundColor $(if ($successRate -eq 100) { "Green" } elseif ($successRate -ge 75) { "Yellow" } else { "Red" })
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Exit with appropriate code
exit $(if ($testFailed -eq 0) { 0 } else { 1 })
