@echo off
REM — back-end modules —
start "API"             cmd /k "cd /d "%~dp0" && python app.py"
start "ContactEval"     cmd /k "cd /d "%~dp0" && python contact_evaluator.py"
start "DataProvider"    cmd /k "cd /d "%~dp0" && python data_provider.py"
start "EntryPlanner"    cmd /k "cd /d "%~dp0" && python entry_planner.py"
start "ExitPlanner"     cmd /k "cd /d "%~dp0" && python exit_planner.py"
start "PatternDisc"     cmd /k "cd /d "%~dp0" && python pattern_discovery.py"
start "PortfolioTrack"  cmd /k "cd /d "%~dp0" && python portfolio_tracker.py"
start "StrategyEngine"  cmd /k "cd /d "%~dp0" && python strategy_engine.py"
start "UpgradeMonitor"  cmd /k "cd /d "%~dp0" && python upgrade_monitor.py"

REM — give back-ends a moment —
timeout /t 3 /nobreak >nul

REM — launch your Electron build from dist folder —
start "" "C:\QMMX_Pro_Phase1\frontend\dist\QMMX Pro Setup 1.0.0.exe"

exit
