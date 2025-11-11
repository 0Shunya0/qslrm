# QSLRM CRUD Testing Script

Write-Host "`n=== Testing CRUD Operations ===" -ForegroundColor Cyan

# Test CREATE Researcher
Write-Host "`n1. Creating new researcher..." -ForegroundColor Yellow
$newResearcher = @{
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@quantumlab.edu"
    orcid_id = "0000-0009-1234-5678"
    institution = "Oxford"
    department = "Quantum Physics"
    role = "Research Fellow"
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "http://localhost:5000/api/researchers" -Method POST -Body $newResearcher -ContentType "application/json"
$newId = $result.researcher.researcher_id
Write-Host "Created researcher ID: $newId" -ForegroundColor Green

# Test GET One
Write-Host "`n2. Getting researcher details..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:5000/api/researchers/$newId"

# Test UPDATE
Write-Host "`n3. Updating researcher..." -ForegroundColor Yellow
$update = @{
    role = "Senior Research Fellow"
    department = "Advanced Quantum Computing"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/researchers/$newId" -Method PUT -Body $update -ContentType "application/json"

# Test DELETE
Write-Host "`n4. Deleting researcher..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:5000/api/researchers/$newId" -Method DELETE

Write-Host "`n=== CRUD Tests Complete ===" -ForegroundColor Green