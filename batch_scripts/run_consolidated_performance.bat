@echo off
echo ==============================================
echo  Consolidated Performance Report Generator
echo ==============================================
echo.

echo 🔬 Generating consolidated performance dashboard...
echo.

cd ..
python generators\consolidated_performance_generator.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Consolidated performance report generated successfully!
    echo.
    echo 📊 Report includes:
    echo    • Multi-board performance comparison
    echo    • Overall success rate analysis
    echo    • Critical performance issues
    echo    • Optimization recommendations
    echo.
    echo 🌐 Check nightly_reports\ folder for the HTML report
) else (
    echo.
    echo ❌ Error generating consolidated report
)

echo.
echo ==============================================
pause