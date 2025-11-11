# QSLRM Advanced Analytics Testing

Write-Host "`n=== ADVANCED ANALYTICS TESTS ===" -ForegroundColor Cyan

# 1. Framework Performance
Write-Host "`n1. Framework Performance Analysis" -ForegroundColor Yellow
$frameworks = Invoke-RestMethod http://localhost:5000/api/analytics/frameworks
Write-Host "Frameworks analyzed: $($frameworks.Count)" -ForegroundColor Green
$frameworks | Format-Table framework, total_simulations, avg_fidelity, avg_execution_time

# 2. Algorithm Performance
Write-Host "`n2. Algorithm Performance Analysis" -ForegroundColor Yellow
$algorithms = Invoke-RestMethod http://localhost:5000/api/analytics/algorithms
Write-Host "Algorithms found: $($algorithms.Count)" -ForegroundColor Green
$algorithms | Format-Table algorithm, total_runs, avg_fidelity, qubit_range

# 3. Researcher Leaderboard
Write-Host "`n3. Researcher Leaderboard (by total simulations)" -ForegroundColor Yellow
$leaderboard = Invoke-RestMethod http://localhost:5000/api/analytics/leaderboard
$leaderboard | Format-Table rank, name, institution, total_simulations, avg_fidelity

Write-Host "`n   Leaderboard (by fidelity)" -ForegroundColor Yellow
$fidelityBoard = Invoke-RestMethod "http://localhost:5000/api/analytics/leaderboard?metric=fidelity&limit=5"
$fidelityBoard | Format-Table rank, name, avg_fidelity, total_simulations

# 4. Project Health Scores
Write-Host "`n4. Project Health Analysis" -ForegroundColor Yellow
for ($i = 1; $i -le 3; $i++) {
    try {
        $health = Invoke-RestMethod "http://localhost:5000/api/analytics/project-health/$i"
        Write-Host "  Project $i ($($health.project_name)): Health Score = $($health.health_score) [$($health.status)]" -ForegroundColor Cyan
    } catch {
        # Skip if project doesn't exist
    }
}

# 5. Trend Analysis
Write-Host "`n5. Trend Analysis (Last 30 days)" -ForegroundColor Yellow
$trends = Invoke-RestMethod "http://localhost:5000/api/analytics/trends?period=30d"
Write-Host "Days with activity: $($trends.total_days)" -ForegroundColor Green
if ($trends.trends.Count -gt 0) {
    Write-Host "Recent activity:" -ForegroundColor Cyan
    $trends.trends[-5..-1] | Format-Table date, simulation_count, avg_fidelity
}

# 6. Qubit Scaling Analysis
Write-Host "`n6. Qubit Scaling Analysis" -ForegroundColor Yellow
$scaling = Invoke-RestMethod http://localhost:5000/api/analytics/qubit-scaling
$scaling | Format-Table qubits, simulations, avg_fidelity, avg_execution_time

# 7. Institution Statistics
Write-Host "`n7. Institution Statistics" -ForegroundColor Yellow
$institutions = Invoke-RestMethod http://localhost:5000/api/analytics/institutions
$institutions | Format-Table institution, researchers, total_simulations, avg_fidelity

# 8. Enhanced Dashboard
Write-Host "`n8. Enhanced Dashboard" -ForegroundColor Yellow
$dashboard = Invoke-RestMethod http://localhost:5000/api/analytics/dashboard/enhanced
Write-Host "Overview:" -ForegroundColor Cyan
$dashboard.overview | Format-List
Write-Host "Status Breakdown:" -ForegroundColor Cyan
$dashboard.status_breakdown | Format-List
Write-Host "Framework Breakdown:" -ForegroundColor Cyan
$dashboard.framework_breakdown | Format-List

# 9. Data Export Tests
Write-Host "`n9. Testing Export Functionality" -ForegroundColor Yellow

# Export simulations CSV
Write-Host "  Exporting simulations to CSV..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "http://localhost:5000/api/export/simulations/csv" -OutFile "simulations_export.csv"
    Write-Host "  ✓ CSV exported successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ CSV export failed" -ForegroundColor Red
}

# Export project report
Write-Host "  Exporting project report..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "http://localhost:5000/api/export/project/1/report" -OutFile "project_1_report.json"
    Write-Host "  ✓ Project report exported" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Project report failed" -ForegroundColor Red
}

# Export researcher portfolio
Write-Host "  Exporting researcher portfolio..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "http://localhost:5000/api/export/researcher/1/portfolio" -OutFile "researcher_1_portfolio.json"
    Write-Host "  ✓ Researcher portfolio exported" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Portfolio export failed" -ForegroundColor Red
}

Write-Host "`n=== ALL ANALYTICS TESTS COMPLETE ===" -ForegroundColor Green
Write-Host "`nExported files:" -ForegroundColor Cyan
Write-Host "  - simulations_export.csv"
Write-Host "  - project_1_report.json"
Write-Host "  - researcher_1_portfolio.json"