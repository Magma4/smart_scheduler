Smart Scheduler — Django Backend
================================

Overview
--------
Smart Scheduler is a Django + DRF backend that generates optimized exam schedules using a Constraint Satisfaction Problem (CSP) solver.

Getting Started
---------------
1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt  # optional; or use pip install with listed libs below
   ```

2. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Run migrations and start the server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

Environment Variables
---------------------
- `DEBUG`: `True` in development
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: Defaults to SQLite; set to Postgres in production
- `ALLOWED_HOSTS`: Comma-separated allowed hosts
- `CORS_ALLOWED_ORIGINS`: Optional comma-separated list of allowed origins



CSP Solver Logic
----------------
Variables are courses; domains are all feasible `(room, timeslot)` pairs that meet room capacity and (optionally) preferred days. The solver enforces:
- No two exams share the same room and timeslot
- No instructor has two exams in the same timeslot
- Room capacity ≥ enrolled students

We use backtracking with MRV (Minimum Remaining Values) heuristic and forward checking to prune the search space.

How scheduling works
--------------------
The solver builds a CSP with one variable per course. Each variable’s domain is the set of `(room, timeslot)` pairs filtered by:
- Room capacity ≥ `course.students`
- `preferred_days` membership, if provided
- Optional `Exam.fixed_timeslot` constraints

During search, the solver:
- Picks the next course using MRV (fewest remaining domain values)
- Checks conflicts for room, instructor, and shared students
- Applies forward checking to prune incompatible values in neighbors


