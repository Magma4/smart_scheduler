"""Domain models for the Smart Scheduler application.

Defines the core entities used by the scheduling system:
- Room: Physical exam room with capacity
- TimeSlot: A day and start/end times of an exam block
- Course: A course with instructor, student count, and preferred exam days
- Exam: An assignment of a course to a room and a timeslot

These models are intentionally minimal and normalized to keep the CSP solver
agnostic of persistence details.
"""

from __future__ import annotations

from django.db import models


class Room(models.Model):
    """A physical room where an exam can be held."""

    name: models.CharField = models.CharField(max_length=50, unique=True)
    capacity: models.PositiveIntegerField = models.PositiveIntegerField()

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.name} (cap {self.capacity})"


class TimeSlot(models.Model):
    """A scheduled block of time on a given day.

    Note: This model does not enforce non-overlapping TimeSlots at the DB level;
    overlap logic is enforced by the CSP and application rules.
    """

    day: models.CharField = models.CharField(max_length=20)
    start_time: models.TimeField = models.TimeField()
    end_time: models.TimeField = models.TimeField()

    class Meta:
        ordering = ["day", "start_time", "end_time"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.day} {self.start_time}-{self.end_time}"


class Course(models.Model):
    """A course that requires an exam scheduling assignment."""

    code: models.CharField = models.CharField(max_length=10, unique=True)
    title: models.CharField = models.CharField(max_length=100)
    instructor: models.CharField = models.CharField(max_length=100)
    students: models.PositiveIntegerField = models.PositiveIntegerField()
    preferred_days: models.JSONField = models.JSONField(default=list)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.code}: {self.title}"


class Exam(models.Model):
    """A scheduled exam assignment for a course in a room at a timeslot."""

    course: models.ForeignKey = models.ForeignKey(Course, on_delete=models.CASCADE)
    room: models.ForeignKey = models.ForeignKey(Room, on_delete=models.CASCADE)
    timeslot: models.ForeignKey = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    fixed_timeslot: models.ForeignKey | None = models.ForeignKey(
        TimeSlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fixed_exams",
    )

    class Meta:
        unique_together = ("room", "timeslot")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Exam({self.course.code} @ {self.room.name} / {self.timeslot})"


class Student(models.Model):
    """A student identified by an external identifier (e.g., student ID)."""

    identifier: models.CharField = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.identifier


class Enrollment(models.Model):
    """Enrollment relation between a student and a course."""

    student: models.ForeignKey = models.ForeignKey(Student, on_delete=models.CASCADE)
    course: models.ForeignKey = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Enrollment({self.student_id} -> {self.course.code})"
