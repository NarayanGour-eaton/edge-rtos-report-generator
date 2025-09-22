@echo off
echo ==============================================
echo  Performance CSV to HTML Report Generator
echo ==============================================
echo.

if "%1"=="" (
    echo Usage: run_performance_report.bat [csv_file_path]
    echo.
    echo Example: run_performance_report.bat nightly_reports\BFT_h743zi_dev\suite_BLR_Test_IoT_SNTP\dynamic_performance_data.csv
    echo.
    echo Searching for CSV files...
    echo.
    
    REM Change to parent directory once
    cd ..
    
    REM Find all CSV files in nightly_reports
    for /r nightly_reports %%i in (dynamic_performance_data.csv) do (
        echo Found: %%i
        python generators\performance_report_generator.py "%%i"
        echo.
    )
) else (
    cd ..
    python generators\performance_report_generator.py "%1"
)

echo.
echo ==============================================
echo Performance reports generated successfully!
echo ==============================================