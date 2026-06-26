# 🛰️ Satellite Ground Station Operations Scheduler

A backend-driven satellite mission planning system that calculates EOS-4 communication windows, schedules mission commands based on available pass duration, and visualizes the complete workflow through an interactive dashboard.

The project uses real TLE data from CelesTrak, performs orbital propagation using Skyfield, stores mission data in PostgreSQL (AWS RDS), and exposes REST APIs through FastAPI which are consumed by a Streamlit frontend.

---

## Features

- Compute upcoming satellite communication passes using real TLE data
- Store pass windows in PostgreSQL (AWS RDS)
- Queue mission commands through a web dashboard
- Automatically schedule commands into available communication windows
- Allocate commands based on priority and pass availability
- Track command and pass execution status in real time
- Interactive Streamlit dashboard for mission monitoring

---

## Tech Stack

- Python
- FastAPI
- Streamlit
- PostgreSQL (AWS RDS)
- SQLModel
- Skyfield
- CelesTrak TLE Data

---

## Project Workflow

```

Latest TLE (CelesTrak)
↓
Skyfield Orbital Propagation
↓
Calculate Future Passes
↓
Store Pass Windows (AWS RDS)
↓
User Creates Command
↓
FastAPI
↓
Scheduler Engine
↓
Updated Command Timeline
↓
Streamlit Dashboard

```

---

## Scheduler Logic

The scheduler uses a **Priority-Based Earliest Pass Allocation** strategy.

### Scheduling Steps

1. Fetch all future satellite passes.
2. Reset previously scheduled commands to allow re-optimization.
3. Retrieve all pending commands.
4. Sort commands by:
   - Higher priority first
   - Earlier creation time
5. For each command:
   - Check the earliest future pass.
   - If sufficient communication time is available, allocate the command.
   - Otherwise, continue checking the next pass.
6. If no suitable pass exists, mark the command as **DEFERRED**.

The scheduler also records:

- Assigned Pass ID
- Scheduled start offset
- Scheduled end offset
- Execution log

---

## Mission Status Synchronization

The scheduler continuously updates mission status based on the current UTC time.

### Pass Status

```

PENDING
↓
ACTIVE
↓
COMPLETED

```

### Command Status

```

PENDING
↓
SCHEDULED
↓
ACTIVE
↓
COMPLETED

```

Command execution time is calculated relative to the assigned pass using the scheduled start and end offsets.

---

## Database Schema

### Pass Window

| Field | Description |
|--------|-------------|
| id | Primary Key |
| satellite_name | Satellite Name |
| start_time | Acquisition of Signal (AOS) |
| end_time | Loss of Signal (LOS) |
| available_duration_secs | Available communication duration |
| max_elevation_deg | Maximum elevation during pass |
| status | Pass status |

### Command

| Field | Description |
|--------|-------------|
| id | Primary Key |
| pass_window_id | Assigned Pass |
| command_type | Mission command |
| priority | Scheduling priority |
| status | Current execution status |
| created_at | Submission timestamp |
| execution_log | Scheduler information |
| scheduled_start_offset_sec | Relative start time |
| scheduled_end_offset_sec | Relative end time |

---

## REST API

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Health Check |
| POST | `/commands` | Queue a new command |
| POST | `/calculate-passes` | Compute future satellite passes |
| POST | `/scheduler/run` | Run scheduler manually |
| GET | `/passes/future` | Retrieve future pass windows |
| GET | `/commands/timeline` | Retrieve scheduled command timeline |

---

## Dashboard

The Streamlit dashboard provides:

- Upcoming satellite passes
- Command creation interface
- Manual orbital pass calculation
- Scheduler execution
- Scheduled command timeline
  
<img width="956" height="440" alt="Image" src="https://github.com/user-attachments/assets/eea3524f-40f2-4abf-948e-7d41c626a9fd" />
---

## Project Structure

```

SAT-COMM
│
├── app
│   ├── create_tables
│   ├── populate_tables
│   ├── database_connection.py
│   └── config.py
│
├── core
│   ├── orbital.py
│   └── scheduler.py
│
├── frontend
│   └── frontend.py
│
├── main.py
└── requirements.txt

```

---

## Future Improvements

- Automatic daily pass calculation
- Background scheduler service
- Multi-satellite support
- Command dependency management
- Real telemetry integration
- Authentication and role-based access

---
