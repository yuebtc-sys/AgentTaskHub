# AGENT_TASKS.md

## Current Goal: AgentTaskHub Platform Development

Develop a robust Agent platform that allows Agents to freely post and claim tasks, with a 1% platform fee directed to your wallet (0x305656CfE21736330CD32A793817166AfaFff0CB).

## Rules for Autonomous Advancement:

This Agent operates under a strict "Forced Auto-Advance Mode" (不可退出 - Cannot Exit).

1.  **No Human Intervention for Auto-Fixable Issues:** The Agent will not stop or request human intervention for any issue deemed automatically fixable.
2.  **Automatic Issue Resolution:** All ModuleNotFoundError (e.g., web3, sqlalchemy, fastapi), pip dependency issues, `edit`/`read` tool failures (by switching strategies), and command execution failures (by changing execution methods) must be handled automatically.
3.  **Strict Stop Condition:** The Agent will only stop and request human intervention if:
    *   An issue persists after two consecutive automatic repair attempts.
    *   The failure is explicitly due to non-automatable causes (e.g., system permissions, network errors, missing credentials).
4.  **Execution Cycle (within a single session):** The Agent must continuously advance through the following loop until the sole stop condition is met:
    *   Select the current "next task."
    *   Execute the task (write code / install dependencies / launch service).
    *   Perform minimal verification (e.g., `pytest`, import checks, startup checks).
    *   Record progress in `progress.md` (done / next / blockers).
    *   Immediately proceed to the next execution round (no waiting for user input).

## Current Project Status:

*   AgentTaskHub project structure initialized.
*   All Python files (`database.py`, `models.py`, `crud.py`, `blockchain.py`, `main.py`, `scripts/init_db.py`) have been written.
*   Database `sql_app.db` has been successfully initialized.
*   Python dependencies installed.
*   `.env` file created.
*   Uvicorn server process `delta-lagoon` has been stopped.

## Next Steps:

The Agent will now proceed with setting up continuous integration/delivery for self-advancement using GitHub Actions, as outlined in the "Forced Auto-Advance Mode" directives.
