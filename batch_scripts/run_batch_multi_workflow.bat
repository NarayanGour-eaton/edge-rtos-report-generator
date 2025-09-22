@echo off
echo ===================================================
echo ETN Multi-Workflow Regression Report Publisher
echo (Batch Mode - Using existing config.json)
echo ===================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    exit /b 1
)

:: Check if workflow configuration exists
if not exist "config\config.json" (
    echo Error: config.json not found in config folder
    echo Please create the configuration file with your run IDs
    echo Use run_multi_workflow_report.bat for interactive mode
    echo.
    exit /b 1
)

echo Running Multi-Workflow Report Generation...
echo Using configuration from config\config.json
echo.

:: Run the multi-workflow publisher in batch mode
python publishers\multi_publisher.py

echo.
echo ===================================================
echo Report generation completed!
echo Check the nightly_reports folder for output files
echo ===================================================