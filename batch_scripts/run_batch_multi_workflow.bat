@echo off
echo ===================================================
echo ETN Multi-Workflow Regression Report Publisher
echo (Batch Mode - Using existing workflow_runs.json)
echo ===================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

:: Check if workflow configuration exists
if not exist "..\samples\workflow_runs.json" (
    echo Error: workflow_runs.json not found in samples folder
    echo Please create the configuration file with your run IDs
    echo Use run_multi_workflow_report.bat for interactive mode
    echo.
    pause
    exit /b 1
)

echo Running Multi-Workflow Report Generation...
echo Using configuration from samples\workflow_runs.json
echo.

:: Change to parent directory to run Python scripts
cd ..

:: Run the multi-workflow publisher in batch mode
python publishers\multi_publisher.py

echo.
echo ===================================================
echo Report generation completed!
echo Check the nightly_reports folder for output files
echo ===================================================
pause