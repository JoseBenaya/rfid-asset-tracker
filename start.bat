@echo off
echo Starting RFID Asset Tracker...
echo.

:: Create and activate virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install backend dependencies if needed
if not exist venv\Lib\site-packages\fastapi (
    echo Installing backend dependencies...
    pip install -r requirements.txt
)

:: Start backend server in a separate window
start cmd /k "title RFID Tracker Backend && venv\Scripts\activate && python api\main.py"

:: Navigate to frontend directory
cd frontend

:: Install frontend dependencies if needed
if not exist node_modules (
    echo Installing frontend dependencies...
    npm install
)

:: Start frontend development server
echo Starting frontend development server...
npm run dev

:: Return to root directory
cd .. 