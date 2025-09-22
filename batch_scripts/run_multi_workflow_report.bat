@echo off
echo ===================================================
echo ETN Multi-Workflow Regression Report Publisher
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
    echo Warning: config.json not found in config folder
    echo Please update it with your run IDs and run this script again
    echo.
    exit /b 1
)

echo Starting Multi-Workflow Report Generation...
echo.
echo NOTE: You will be prompted for GitHub token if not already configured
echo You can also:
echo   - Set GITHUB_TOKEN environment variable
echo   - Add github_token to config.json
echo   - Use --github-token command line argument
echo.

:: Run the multi-workflow publisher in interactive mode
python publishers\multi_publisher.py --interactive

echo.
echo ===================================================
echo Report generation completed!
echo Check the nightly_reports folder for output files
echo ===================================================