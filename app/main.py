from fastapi import FastAPI, Query, HTTPException
from typing import Optional
from datetime import datetime
from log_parser import load_logs, LOG_FORMAT
from fastapi import Request

app = FastAPI()

# @app.get("/logs")
# def get_logs(
#     request: Request,
#     level: Optional[str] = None,
#     component: Optional[str] = None,
#     start_time: Optional[str] = None,
#     end_time: Optional[str] = None
# ):
#     allowed_params = {"level", "component", "start_time", "end_time", "limit", "offset"}
#     logs = load_logs()  # Reload logs every time this endpoint is called
#     filtered = logs
#     for param in request.query_params.keys():
#         if param not in allowed_params:
#             raise HTTPException(status_code=400, detail=f"Unknown query parameter: {param}")

#     if level:
#         filtered = [log for log in filtered if log.level.upper() == level.upper()]
#     if component:
#         filtered = [log for log in filtered if log.component == component]
#     if start_time:
#         try:
#             start_dt = datetime.strptime(start_time, LOG_FORMAT)
#             filtered = [log for log in filtered if log.timestamp >= start_dt]
#         except ValueError:
#             raise HTTPException(status_code=400, detail="Invalid start_time format.")
#     if end_time:
#         try:
#             end_dt = datetime.strptime(end_time, LOG_FORMAT)
#             filtered = [log for log in filtered if log.timestamp <= end_dt]
#         except ValueError:
#             raise HTTPException(status_code=400, detail="Invalid end_time format.")

#     return [log.to_dict() for log in filtered]


@app.get("/logs")
def get_logs(
    request: Request,
    level: Optional[str] = None,
    component: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),  # max 1000 per request
    offset: int = Query(0, ge=0)
):
    # Optional: Validate unknown query params
    allowed_params = {"level", "component", "start_time", "end_time", "limit", "offset"}
    for param in request.query_params.keys():
        if param not in allowed_params:
            raise HTTPException(status_code=400, detail=f"Unknown query parameter: {param}")

    logs = load_logs()  # reload logs to get latest data

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

    # Pagination: slice the filtered logs
    paginated = filtered[offset: offset + limit]

    return {
        "total_filtered_logs": len(filtered),
        "limit": limit,
        "offset": offset,
        "logs": [log.to_dict() for log in paginated]
    }

@app.get("/logs/stats")
def get_stats():
    logs = load_logs()  # Reload logs
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
    logs = load_logs()  # Reload logs
    for log in logs:
        if log.id == log_id:
            return log.to_dict()
    raise HTTPException(status_code=404, detail="Log entry not found.")
