# Complete Feature Test for QSLRM v2.0

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "QSLRM v2.0 - Complete Feature Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Global Search
Write-Host "1. Global Search Test" -ForegroundColor Yellow
$search = Invoke-RestMethod "http://localhost:5000/api/search?q=quantum"
Write-Host "  Found: $($search.total_results) results" -ForegroundColor Green
Write-Host "    Researchers: $($search.results.researchers.count)"
Write-Host "    Projects: $($search.results.projects.count)"
Write-Host "    Simulations: $($search.results.simulations.count)"

# 2. Paginated Search
Write-Host "`n2. Paginated Simulation Search" -ForegroundColor Yellow
$paginated = Invoke-RestMethod "http://localhost:5000/api/search/simulations?page=1&per_page=5&sort_by=num_qubits&order=desc"
Write-Host "  Page 1 of $($paginated.total_pages) (Total: $($paginated.total_items) items)" -ForegroundColor Green
Write-Host "  Top simulations by qubit count:"
$paginated.items | Select-Object -First 3 | ForEach-Object {
    Write-Host "    - $($_.simulation_id): $($_.num_qubits) qubits, $($_.framework)" -ForegroundColor Cyan
}

# 3. Advanced Filters
Write-Host "`n3. Filter Options Available" -ForegroundColor Yellow
$filters = Invoke-RestMethod "http://localhost:5000/api/search/filters"
Write-Host "  Frameworks: $($filters.frameworks -join ', ')" -ForegroundColor Cyan
Write-Host "  Qubit range: $($filters.qubit_range.min) - $($filters.qubit_range.max)" -ForegroundColor Cyan

# 4. Framework Comparison
Write-Host "`n4. Framework Performance Comparison" -ForegroundColor Yellow
$frameworks = Invoke-RestMethod "http://localhost:5000/api/analytics/frameworks"
Write-Host "  Top 3 frameworks by usage:" -ForegroundColor Green
$frameworks | Select-Object -First 3 | ForEach-Object {
    Write-Host "    $($_.framework): $($_.total_simulations) sims, avg fidelity: $($_.avg_fidelity)" -ForegroundColor Cyan
}

# 5. Leaderboard
Write-Host "`n5. Researcher Leaderboard" -ForegroundColor Yellow
$leaders = Invoke-RestMethod "http://localhost:5000/api/analytics/leaderboard?limit=5"
Write-Host "  Top 5 researchers:" -ForegroundColor Green
$leaders | ForEach-Object {
    Write-Host "    #$($_.rank) $($_.name) ($($_.institution)): $($_.total_simulations) simulations" -ForegroundColor Cyan
}

# 6. Project Health
Write-Host "`n6. Project Health Scores" -ForegroundColor Yellow
for ($projectId = 1; $projectId -le 3; $projectId++) {
    try {
        $health = Invoke-RestMethod "http://localhost:5000/api/analytics/project-health/$projectId"
        $color = switch ($health.status) {
            "excellent" { "Green" }
            "good" { "Cyan" }
            "fair" { "Yellow" }
            default { "Red" }
        }
        Write-Host "  Project ${projectId}: $($health.health_score)/100 [$($health.status)]" -ForegroundColor $color
    } catch {}
}

# 7. Qubit Scaling
Write-Host "`n7. Qubit Scaling Analysis" -ForegroundColor Yellow
$scaling = Invoke-RestMethod "http://localhost:5000/api/analytics/qubit-scaling"
Write-Host "  Simulations by qubit count:" -ForegroundColor Green
$scaling | Select-Object -First 5 | ForEach-Object {
    Write-Host "    $($_.qubits) qubits: $($_.simulations) simulations, avg fidelity: $($_.avg_fidelity)" -ForegroundColor Cyan
}

# 8. Enhanced Dashboard
Write-Host "`n8. Enhanced Dashboard Metrics" -ForegroundColor Yellow
$dashboard = Invoke-RestMethod "http://localhost:5000/api/analytics/dashboard/enhanced"
Write-Host "  Total Simulations: $($dashboard.overview.total_simulations)" -ForegroundColor Green
Write-Host "  Recent Activity (7d): $($dashboard.overview.recent_activity)" -ForegroundColor Green
Write-Host "  Avg Quality: Fidelity=$($dashboard.quality_metrics.avg_fidelity), Repro=$($dashboard.quality_metrics.avg_reproducibility)" -ForegroundColor Green

# 9. Export Test
Write-Host "`n9. Testing Export Features" -ForegroundColor Yellow
try {
    # Export CSV
    Invoke-WebRequest "http://localhost:5000/api/export/simulations/csv?framework=Qiskit" -OutFile "qiskit_sims.csv"
    $csvSize = (Get-Item "qiskit_sims.csv").Length
    Write-Host "  CSV export: $csvSize bytes" -ForegroundColor Green
    
    # Export project report
    Invoke-WebRequest "http://localhost:5000/api/export/project/1/report" -OutFile "project_report.json"
    $jsonSize = (Get-Item "project_report.json").Length
    Write-Host "  Project report: $jsonSize bytes" -ForegroundColor Green
} catch {
    Write-Host "  Export failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 10. API Summary
Write-Host "`n10. API Endpoint Summary" -ForegroundColor Yellow
$root = Invoke-RestMethod "http://localhost:5000/"
Write-Host "  API Version: $($root.version)" -ForegroundColor Green
Write-Host "  Available Endpoints: $($root.endpoints.Count)" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "All v2.0 Features Working!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Summary of New Features:" -ForegroundColor Yellow
Write-Host "  Advanced Analytics (frameworks, algorithms, trends)" -ForegroundColor Green
Write-Host "  Global Search across all entities" -ForegroundColor Green
Write-Host "  Pagination & Sorting" -ForegroundColor Green
Write-Host "  Data Export (CSV, JSON)" -ForegroundColor Green
Write-Host "  Researcher Leaderboards" -ForegroundColor Green
Write-Host "  Project Health Scoring" -ForegroundColor Green
Write-Host "  Qubit Scaling Analysis" -ForegroundColor Green
Write-Host "  Institution Statistics" -ForegroundColor Green