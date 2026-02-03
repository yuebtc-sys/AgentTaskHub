@echo off
echo ========================================
echo Checking GitHub Actions Workflow Status
echo ========================================
echo.
echo Current time:
date /t & time /t
echo.
echo Pulling latest changes from GitHub...
cd C:\Users\yueyo\clawd\AgentTaskHub
git pull origin master
echo.
echo ========================================
echo Recent GitHub Actions Bot Commits:
echo ========================================
git log --author="github-actions[bot]" --oneline -5
echo.
echo ========================================
echo Latest progress.md updates:
echo =================================-------
type progress.md | findstr /C:"GitHub Actions Run"
echo.
echo ========================================
echo If you see new commits above, workflow is running!
echo ========================================
pause
