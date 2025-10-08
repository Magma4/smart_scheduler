import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export const getOptimizedSchedule = async (constraints) => {
  // Backend endpoint implemented in Phase 1B is /api/generate-schedule/
  const res = await axios.post(`${API_BASE_URL}/generate-schedule/`, constraints || {});
  return res.data;
};

// --- Demo data seeding helpers ---
const post = (path, body) => axios.post(`${API_BASE_URL}${path}`, body, { headers: { "Content-Type": "application/json" } });

export const seedDemoData = async () => {
  // Rooms
  await post(`/rooms/`, { name: "R1", capacity: 40 });
  await post(`/rooms/`, { name: "R2", capacity: 30 });

  // Timeslots
  await post(`/timeslots/`, { day: "Mon", start_time: "09:00:00", end_time: "11:00:00" });
  await post(`/timeslots/`, { day: "Mon", start_time: "12:00:00", end_time: "14:00:00" });

  // Courses
  await post(`/courses/`, { code: "C101", title: "Algebra", instructor: "Smith", students: 25, preferred_days: ["Mon"] });
  await post(`/courses/`, { code: "C102", title: "Biology", instructor: "Doe", students: 30, preferred_days: ["Mon"] });
  await post(`/courses/`, { code: "C103", title: "Chemistry", instructor: "Smith", students: 20, preferred_days: ["Mon"] });

  // Students + Enrollments (S1 overlaps C101 & C103)
  await post(`/students/`, { identifier: "S1" });
  await post(`/enrollments/`, { student: "S1", course: "C101" });
  await post(`/enrollments/`, { student: "S1", course: "C103" });
};

export const bulkImport = async (payload) => {
  const res = await axios.post(`${API_BASE_URL}/bulk-import/`, payload, {
    headers: { "Content-Type": "application/json" },
  });
  return res.data;
};

// Entity creation helpers
export const createRoom = (body) => post(`/rooms/`, body);
export const createTimeslot = (body) => post(`/timeslots/`, body);
export const createCourse = (body) => post(`/courses/`, body);
export const createStudent = (body) => post(`/students/`, body);
export const createEnrollment = (body) => post(`/enrollments/`, body);
