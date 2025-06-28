<#
.SYNOPSIS
   Runs Broadway scraper with automatic AWS authentication
#>

# Step 1: Authenticate
Write-Host "Starting AWS Authentication..." -ForegroundColor Cyan
$authCommand = python .\data_collection\aws_auth.py
Invoke-Expression $authCommand

# Step 2: Run Scraper
Write-Host "Starting Scraper..." -ForegroundColor Cyan
python .\data_collection\scraper.py

# Step 3: Verify
if ($LASTEXITCODE -eq 0) {
    Write-Host "Scraping completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Scraping failed with exit code $LASTEXITCODE" -ForegroundColor Red
}