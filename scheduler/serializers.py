"""Serializers for Smart Scheduler domain models.

Provide clear, typed DRF serializers for Room, TimeSlot, Course, and Exam.
"""

from __future__ import annotations

from rest_framework import serializers
from .models import Room, TimeSlot, Course, Exam, Student, Enrollment


class RoomSerializer(serializers.ModelSerializer[Room]):
    class Meta:
        model = Room
        fields = ["id", "name", "capacity"]


class TimeSlotSerializer(serializers.ModelSerializer[TimeSlot]):
    class Meta:
        model = TimeSlot
        fields = ["id", "day", "start_time", "end_time"]


class CourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["id", "code", "title", "instructor", "students", "preferred_days"]


class ExamSerializer(serializers.ModelSerializer[Exam]):
    course = serializers.SlugRelatedField(slug_field="code", queryset=Course.objects.all())
    room = serializers.SlugRelatedField(slug_field="name", queryset=Room.objects.all())
    timeslot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all())
    fixed_timeslot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Exam
        fields = ["id", "course", "room", "timeslot", "fixed_timeslot"]


class StudentSerializer(serializers.ModelSerializer[Student]):
    class Meta:
        model = Student
        fields = ["id", "identifier"]


class EnrollmentSerializer(serializers.ModelSerializer[Enrollment]):
    student = serializers.SlugRelatedField(slug_field="identifier", queryset=Student.objects.all())
    course = serializers.SlugRelatedField(slug_field="code", queryset=Course.objects.all())

    class Meta:
        model = Enrollment
        fields = ["id", "student", "course"]
