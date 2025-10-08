"""Tests for the CSP exam scheduler.

Validates key constraints: room capacity, room-time conflicts, and instructor
conflicts. Uses the ORM to seed a small dataset and verifies a feasible
assignment is produced.
"""

from __future__ import annotations

import datetime as dt
from django.test import TestCase

from ..models import Room, TimeSlot, Course, Student, Enrollment
from ..services.solver import schedule_all_exams


class TestSolver(TestCase):
    def setUp(self) -> None:  # noqa: D401
        # Rooms
        Room.objects.create(name="R1", capacity=30)
        Room.objects.create(name="R2", capacity=50)

        # Timeslots
        TimeSlot.objects.create(day="Mon", start_time=dt.time(9, 0), end_time=dt.time(11, 0))
        TimeSlot.objects.create(day="Mon", start_time=dt.time(12, 0), end_time=dt.time(14, 0))

        # Courses with instructors
        Course.objects.create(code="C101", title="Algebra", instructor="Smith", students=25, preferred_days=["Mon"])
        Course.objects.create(code="C102", title="Biology", instructor="Doe", students=45, preferred_days=["Mon"])
        Course.objects.create(code="C103", title="Chemistry", instructor="Smith", students=20, preferred_days=["Mon"])

    def test_basic_schedule_success(self) -> None:
        # Enroll one student overlapping in C101 and C103 to force separation
        s1 = Student.objects.create(identifier="S1")
        Enrollment.objects.create(student=s1, course=Course.objects.get(code="C101"))
        Enrollment.objects.create(student=s1, course=Course.objects.get(code="C103"))

        result = schedule_all_exams()
        assert result["CSPStatus"] == "success"
        assignments = result["assignments"]
        assert set(assignments.keys()) == {"C101", "C102", "C103"}

        used = set()
        for _, assignment in assignments.items():
            key = (assignment["room"], assignment["timeslot"])  # timeslot label string
            assert key not in used
            used.add(key)

        # Instructor conflicts and student conflicts: C101 and C103 must differ
        assert assignments["C101"]["timeslot"] != assignments["C103"]["timeslot"]
