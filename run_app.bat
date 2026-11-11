@echo off
echo ========================================================
echo   AutoReels Enterprise v2.0 (Master Build Specification)
echo   Local Dev Stack: MySQL + FastAPI + Next.js
echo ========================================================
echo.

:: Ensure Python virtual environment / dependencies
echo [1/3] Verifying Backend & Health Probes...
cd backend
python -c "import app.database; print('Database engine ready:', app.database.check_db_connection())"
cd ..

echo [2/3] Starting FastAPI Backend on http://localhost:8000 ...
start "AutoReels API (FastAPI)" cmd /k "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Next.js Frontend on http://localhost:3000 ...
start "AutoReels Web (Next.js 16)" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo   AutoReels Enterprise Stack Running:
echo   - Web UI: http://localhost:3000
echo   - API Root: http://localhost:8000
echo   - Health Liveness: http://localhost:8000/health/live
echo   - Health Readiness: http://localhost:8000/health/ready
echo   - Swagger Docs: http://localhost:8000/docs
echo ========================================================
echo.
pause
