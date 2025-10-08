"""REST API endpoints for the Smart Scheduler service.

Exposes CRUD endpoints for `Room`, `TimeSlot`, and `Course` via DRF viewsets
and provides a `generate-schedule` endpoint that runs the CSP solver to produce
an optimized exam schedule.
"""

from __future__ import annotations

from typing import Any, Dict

import logging
from django.urls import path, include
from rest_framework import routers, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Room, TimeSlot, Course, Exam, Student, Enrollment
from .serializers import (
    RoomSerializer,
    TimeSlotSerializer,
    CourseSerializer,
    ExamSerializer,
    StudentSerializer,
    EnrollmentSerializer,
)
from .services.solver import schedule_all_exams

logger = logging.getLogger(__name__)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer


router = routers.DefaultRouter()
router.register(r"rooms", RoomViewSet)
router.register(r"timeslots", TimeSlotViewSet)
router.register(r"courses", CourseViewSet)
router.register(r"exams", ExamViewSet)
router.register(r"students", StudentViewSet)
router.register(r"enrollments", EnrollmentViewSet)


class GenerateScheduleAPIView(APIView):
    """POST /api/generate-schedule/ — runs the CSP solver and returns JSON."""

    def post(self, request: Request) -> Response:  # type: ignore[override]
        try:
            result = schedule_all_exams()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error generating schedule")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def health_check(_request: Request) -> Response:
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


urlpatterns = [
    path("", include(router.urls)),
    path("generate-schedule/", GenerateScheduleAPIView.as_view(), name="generate-schedule"),
    path("health/", health_check, name="health-check"),
]


@api_view(["POST"])
def bulk_import(request: Request) -> Response:
    """Create core data in bulk from a single JSON payload.

    Expected JSON shape (all keys optional):
    {
      "rooms": [{"name": "R1", "capacity": 40}, ...],
      "timeslots": [{"day": "Mon", "start_time": "09:00:00", "end_time": "11:00:00"}, ...],
      "courses": [{"code": "C101", "title": "Algebra", "instructor": "Smith", "students": 25, "preferred_days": ["Mon"]}, ...],
      "students": [{"identifier": "S1"}, ...],
      "enrollments": [{"student": "S1", "course": "C101"}, ...]
    }

    The endpoint is idempotent-ish: it uses get_or_create by natural keys to avoid
    duplicates on repeated imports.
    """
    data: Dict[str, Any] = request.data if isinstance(request.data, dict) else {}
    created = {"rooms": 0, "timeslots": 0, "courses": 0, "students": 0, "enrollments": 0}
    try:
        # Rooms
        for r in data.get("rooms", []) or []:
            obj, was_created = Room.objects.get_or_create(name=r.get("name"), defaults={"capacity": r.get("capacity", 0)})
            if not was_created and "capacity" in r:
                obj.capacity = r["capacity"]
                obj.save(update_fields=["capacity"])
            created["rooms"] += 1 if was_created else 0

        # Timeslots
        for t in data.get("timeslots", []) or []:
            obj, was_created = TimeSlot.objects.get_or_create(
                day=t.get("day"), start_time=t.get("start_time"), end_time=t.get("end_time")
            )
            created["timeslots"] += 1 if was_created else 0

        # Courses
        for c in data.get("courses", []) or []:
            obj, was_created = Course.objects.get_or_create(
                code=c.get("code"),
                defaults={
                    "title": c.get("title", ""),
                    "instructor": c.get("instructor", ""),
                    "students": c.get("students", 0),
                    "preferred_days": c.get("preferred_days", []),
                },
            )
            if not was_created:
                # Update basic fields if provided
                updates = []
                for fld in ("title", "instructor", "students", "preferred_days"):
                    if fld in c:
                        setattr(obj, fld, c[fld])
                        updates.append(fld)
                if updates:
                    obj.save(update_fields=updates)
            created["courses"] += 1 if was_created else 0

        # Students
        for s in data.get("students", []) or []:
            _, was_created = Student.objects.get_or_create(identifier=s.get("identifier"))
            created["students"] += 1 if was_created else 0

        # Enrollments
        for e in data.get("enrollments", []) or []:
            try:
                student = Student.objects.get(identifier=e.get("student"))
                course = Course.objects.get(code=e.get("course"))
                _, was_created = Enrollment.objects.get_or_create(student=student, course=course)
                created["enrollments"] += 1 if was_created else 0
            except (Student.DoesNotExist, Course.DoesNotExist):
                logger.warning("Skipping enrollment; missing student/course: %s", e)
                continue

        return Response({"status": "ok", "created": created}, status=status.HTTP_200_OK)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Bulk import failed")
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
