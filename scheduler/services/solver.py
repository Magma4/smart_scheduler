"""Constraint Satisfaction Problem solver for exam scheduling.

Implements CSP scheduling using backtracking search with MRV and forward
checking. This file demonstrates constraint propagation and early failure
detection.

Variables: courses (one exam per course)
Domains: feasible (room, timeslot) pairs filtered by room capacity, course
preferred_days, and any fixed timeslot constraints.

Hard constraints:
- No two exams share the same room and timeslot
- No instructor teaches overlapping exams
- No student has overlapping exams
- Room capacity ≥ enrolled students

Returns a result dict:
{
  "CSPStatus": "success" | "failure",
  "assignments": { code: {"room": str, "timeslot": str} }
}
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple
import logging

from django.db.models import QuerySet

from ..models import Course, Room, TimeSlot, Exam, Enrollment

logger = logging.getLogger(__name__)


Assignment = Dict[str, Tuple[str, int]]  # course_code -> (room_name, timeslot_id)
Domain = Dict[str, List[Tuple[str, int]]]


@dataclass(frozen=True)
class ProblemContext:
    courses: List[Course]
    rooms: List[Room]
    timeslots: List[TimeSlot]
    course_to_students: Dict[str, Set[str]]


def _initial_domain(ctx: ProblemContext) -> Domain:
    domain: Domain = {}
    for course in ctx.courses:
        candidates: List[Tuple[str, int]] = []
        # Check for fixed timeslot constraint from existing Exam rows
        fixed_qs = Exam.objects.filter(course=course, fixed_timeslot__isnull=False).values_list(
            "fixed_timeslot_id", flat=True
        )
        fixed_ts_ids = set(fixed_qs)

        for room in ctx.rooms:
            if room.capacity < course.students:
                continue
            for ts in ctx.timeslots:
                if course.preferred_days and ts.day not in course.preferred_days:
                    continue
                if fixed_ts_ids and ts.id not in fixed_ts_ids:
                    continue
                candidates.append((room.name, ts.id))
        domain[course.code] = candidates
    return domain


def _select_unassigned_var_mrv(assignment: Assignment, domain: Domain) -> Optional[str]:
    unassigned = [(code, len(vals)) for code, vals in domain.items() if code not in assignment]
    if not unassigned:
        return None
    unassigned.sort(key=lambda x: x[1])
    return unassigned[0][0]


def _is_consistent(
    var: str,
    value: Tuple[str, int],
    assignment: Assignment,
    courses_by_code: Dict[str, Course],
) -> bool:
    room_name, timeslot_id = value
    course = courses_by_code[var]

    # Instructor conflicts: same instructor cannot have two exams in the same timeslot
    for other_code, (other_room, other_ts) in assignment.items():
        if other_ts == timeslot_id:
            other_course = courses_by_code[other_code]
            if other_course.instructor == course.instructor:
                return False
            # Student overlap: any common student cannot be in two exams at once
            students_a = ctx_course_to_students.get(course.code, set())
            students_b = ctx_course_to_students.get(other_course.code, set())
            if students_a and students_b and (students_a & students_b):
                return False
        # Room conflict at the same timeslot
        if other_ts == timeslot_id and other_room == room_name:
            return False
    return True


def _forward_check(
    var: str,
    value: Tuple[str, int],
    domain: Domain,
    assignment: Assignment,
    courses_by_code: Dict[str, Course],
) -> Optional[Domain]:
    room_name, timeslot_id = value
    new_domain: Domain = {k: list(v) for k, v in domain.items()}

    for other_var, values in list(new_domain.items()):
        if other_var in assignment or other_var == var:
            continue
        filtered: List[Tuple[str, int]] = []
        for candidate in values:
            cand_room, cand_ts = candidate
            if cand_ts == timeslot_id and cand_room == room_name:
                continue  # room already used at this timeslot
            # instructor conflict check
            if cand_ts == timeslot_id:
                if courses_by_code[other_var].instructor == courses_by_code[var].instructor:
                    continue
                # student overlap check
                students_a = ctx_course_to_students.get(other_var, set())
                students_b = ctx_course_to_students.get(var, set())
                if students_a and students_b and (students_a & students_b):
                    continue
            filtered.append(candidate)
        if not filtered:
            return None
        new_domain[other_var] = filtered
    return new_domain


def _backtrack(
    assignment: Assignment,
    domain: Domain,
    courses_by_code: Dict[str, Course],
) -> Optional[Assignment]:
    if len(assignment) == len(domain):
        return assignment

    var = _select_unassigned_var_mrv(assignment, domain)
    if var is None:
        return assignment

    for value in domain[var]:
        if not _is_consistent(var, value, assignment, courses_by_code):
            continue
        new_assignment = dict(assignment)
        new_assignment[var] = value

        new_domain = _forward_check(var, value, domain, new_assignment, courses_by_code)
        if new_domain is None:
            continue

        result = _backtrack(new_assignment, new_domain, courses_by_code)
        if result is not None:
            return result
    return None


def _timeslot_label(ts: TimeSlot) -> str:
    return f"{ts.day} {ts.start_time.strftime('%H:%M')}–{ts.end_time.strftime('%H:%M')}"


def schedule_all_exams() -> Dict[str, object]:
    """Run the CSP solver and return the structured result with status and assignments."""
    try:
        courses: List[Course] = list(Course.objects.all())
        rooms: List[Room] = list(Room.objects.all())
        timeslots: List[TimeSlot] = list(TimeSlot.objects.all())
        # Build course -> student identifiers map
        course_to_students: Dict[str, Set[str]] = {}
        enrollments = Enrollment.objects.select_related("course", "student").all()
        for enr in enrollments:
            course_to_students.setdefault(enr.course.code, set()).add(enr.student.identifier)

        ctx = ProblemContext(courses=courses, rooms=rooms, timeslots=timeslots, course_to_students=course_to_students)

        courses_by_code: Dict[str, Course] = {c.code: c for c in courses}
        global ctx_course_to_students
        ctx_course_to_students = course_to_students  # used in consistency checks
        domain = _initial_domain(ctx)

        logger.info("Starting CSP solver: %d courses, %d rooms, %d timeslots", len(courses), len(rooms), len(timeslots))
        assignment = _backtrack({}, domain, courses_by_code)
        if assignment is None:
            logger.warning("No feasible schedule found with given constraints")
            return {"CSPStatus": "failure", "assignments": {}}

        # Build labeled response
        ts_by_id: Dict[int, TimeSlot] = {ts.id: ts for ts in timeslots}
        result_assignments: Dict[str, Dict[str, str]] = {}
        for code, (room, ts_id) in assignment.items():
            label = _timeslot_label(ts_by_id[ts_id])
            result_assignments[code] = {"room": room, "timeslot": label}
        logger.info("CSP solver finished successfully with %d assignments", len(result_assignments))
        return {"CSPStatus": "success", "assignments": result_assignments}
    except Exception:
        # Log and re-raise for API layer to handle
        logger.exception("CSP solver failed")
        raise
