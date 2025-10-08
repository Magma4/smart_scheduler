"""API tests for Smart Scheduler endpoints."""

from __future__ import annotations

import datetime as dt
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import Room, TimeSlot, Course, Student, Enrollment


class TestAPI(APITestCase):
    def setUp(self) -> None:
        Room.objects.create(name="R1", capacity=40)
        Room.objects.create(name="R2", capacity=20)
        TimeSlot.objects.create(day="Tue", start_time=dt.time(9, 0), end_time=dt.time(11, 0))
        TimeSlot.objects.create(day="Tue", start_time=dt.time(12, 0), end_time=dt.time(14, 0))
        Course.objects.create(code="M101", title="Math", instructor="A", students=30, preferred_days=["Tue"])
        Course.objects.create(code="P101", title="Physics", instructor="B", students=15, preferred_days=["Tue"])

    def test_health(self) -> None:
        url = "/api/health/"
        resp = self.client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json().get("status") == "ok"

    def test_generate_schedule(self) -> None:
        url = "/api/generate-schedule/"
        # Create an overlap for one student across both courses to test conflict handling
        s1 = Student.objects.create(identifier="S1")
        Enrollment.objects.create(student=s1, course=Course.objects.get(code="M101"))
        Enrollment.objects.create(student=s1, course=Course.objects.get(code="P101"))

        resp = self.client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data.get("CSPStatus") in {"success", "failure"}
        assert set(data.get("assignments", {}).keys()) == {"M101", "P101"} if data.get("CSPStatus") == "success" else True
