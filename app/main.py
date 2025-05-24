from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from log_parser import load_logs, LOG_FORMAT

app = FastAPI()
logs = load_logs()
log_map = {log.id: log for log in logs}  # for quick lookup

@app.get("/logs")
def get_logs(
    level: Optional[str] = None,
    component: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    filtered = logs

    if level:
        filtered = [log for log in filtered if log.level.upper() == level.upper()]
    if component:
        filtered = [log for log in filtered if log.component == component]
    if start_time:
        try:
            start_dt = datetime.strptime(start_time, LOG_FORMAT)
            filtered = [log for log in filtered if log.timestamp >= start_dt]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_time format.")
    if end_time:
        try:
            end_dt = datetime.strptime(end_time, LOG_FORMAT)
            filtered = [log for log in filtered if log.timestamp <= end_dt]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_time format.")

    return [log.to_dict() for log in filtered]

@app.get("/logs/stats")
def get_stats():
    total = len(logs)
    level_counts = {}
    component_counts = {}

    for log in logs:
        level_counts[log.level] = level_counts.get(log.level, 0) + 1
        component_counts[log.component] = component_counts.get(log.component, 0) + 1

    return {
        "total_logs": total,
        "logs_per_level": level_counts,
        "logs_per_component": component_counts
    }

@app.get("/logs/{log_id}")
def get_log_by_id(log_id: str):
    log = log_map.get(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found.")
    return log.to_dict()
