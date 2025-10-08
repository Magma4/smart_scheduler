import { useState } from "react";
import SchedulerForm from "../components/SchedulerForm";
import ScheduleResults from "../components/ScheduleResults";
import { bulkImport, createRoom, createTimeslot, createCourse, createStudent, createEnrollment } from "../api/scheduleApi";

export default function Home() {
  const [result, setResult] = useState(null);
  const [bulkJson, setBulkJson] = useState(`{
  "rooms": [{"name": "R1", "capacity": 40}, {"name": "R2", "capacity": 30}],
  "timeslots": [
    {"day": "Mon", "start_time": "09:00:00", "end_time": "11:00:00"},
    {"day": "Mon", "start_time": "12:00:00", "end_time": "14:00:00"}
  ],
  "courses": [
    {"code": "C101", "title": "Algebra", "instructor": "Smith", "students": 25, "preferred_days": ["Mon"]},
    {"code": "C102", "title": "Biology", "instructor": "Doe", "students": 30, "preferred_days": ["Mon"]}
  ],
  "students": [{"identifier": "S1"}],
  "enrollments": [{"student": "S1", "course": "C101"}]
}`);
  return (
    <div className="max-w-5xl mx-auto px-4 pt-6">
      <h1 className="text-2xl font-semibold mb-4">Create a Scheduling Request</h1>
      <SchedulerForm onResult={setResult} />
      <ScheduleResults result={result} />

      <div className="grid md:grid-cols-2 gap-6 mt-10">
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Add Data</h2>
          <div className="border rounded p-3 space-y-2">
            <h3 className="font-medium">Room</h3>
            <RoomForm />
          </div>
          <div className="border rounded p-3 space-y-2">
            <h3 className="font-medium">Timeslot</h3>
            <TimeslotForm />
          </div>
          <div className="border rounded p-3 space-y-2">
            <h3 className="font-medium">Course</h3>
            <CourseForm />
          </div>
          <div className="border rounded p-3 space-y-2">
            <h3 className="font-medium">Student</h3>
            <StudentForm />
          </div>
          <div className="border rounded p-3 space-y-2">
            <h3 className="font-medium">Enrollment</h3>
            <EnrollmentForm />
          </div>
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-2">Bulk Upload (JSON)</h2>
          <p className="text-sm text-gray-600 mb-2">Paste JSON for rooms, timeslots, courses, students, and enrollments, then import.</p>
          <textarea
            className="w-full border rounded p-2 font-mono text-sm"
            rows={10}
            value={bulkJson}
            onChange={(e) => setBulkJson(e.target.value)}
          />
          <div className="mt-2 flex gap-3">
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded"
              onClick={async () => {
                try {
                  const payload = JSON.parse(bulkJson);
                  await bulkImport(payload);
                  alert("Imported successfully. Click Generate Schedule to solve.");
                } catch (e) {
                  alert("Invalid JSON or import failed: " + (e?.message || e));
                }
              }}
            >
              Import JSON
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Input({ label, ...props }) {
  return (
    <label className="block text-sm">
      <span className="block text-gray-700 mb-1">{label}</span>
      <input className="w-full border rounded px-2 py-1" {...props} />
    </label>
  );
}

function RoomForm() {
  const [name, setName] = useState("");
  const [capacity, setCapacity] = useState("");
  return (
    <form
      onSubmit={async (e) => {
        e.preventDefault();
        await createRoom({ name, capacity: Number(capacity) || 0 });
        setName("");
        setCapacity("");
        alert("Room added");
      }}
      className="space-y-2"
    >
      <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} />
      <Input label="Capacity" type="number" value={capacity} onChange={(e) => setCapacity(e.target.value)} />
      <button className="px-3 py-1.5 bg-gray-900 text-white rounded" type="submit">Add Room</button>
    </form>
  );
}

function TimeslotForm() {
  const [day, setDay] = useState("Mon");
  const [start, setStart] = useState("09:00:00");
  const [end, setEnd] = useState("11:00:00");
  return (
    <form
      onSubmit={async (e) => {
        e.preventDefault();
        await createTimeslot({ day, start_time: start, end_time: end });
        alert("Timeslot added");
      }}
      className="space-y-2"
    >
      <Input label="Day" value={day} onChange={(e) => setDay(e.target.value)} />
      <Input label="Start (HH:MM:SS)" value={start} onChange={(e) => setStart(e.target.value)} />
      <Input label="End (HH:MM:SS)" value={end} onChange={(e) => setEnd(e.target.value)} />
      <button className="px-3 py-1.5 bg-gray-900 text-white rounded" type="submit">Add Timeslot</button>
    </form>
  );
}

function CourseForm() {
  const [code, setCode] = useState("");
  const [title, setTitle] = useState("");
  const [instructor, setInstructor] = useState("");
  const [students, setStudents] = useState("");
  const [preferredDays, setPreferredDays] = useState("Mon");
  return (
    <form
      onSubmit={async (e) => {
        e.preventDefault();
        const days = preferredDays.split(",").map((d) => d.trim()).filter(Boolean);
        await createCourse({ code, title, instructor, students: Number(students) || 0, preferred_days: days });
        setCode(""); setTitle(""); setInstructor(""); setStudents("");
        alert("Course added");
      }}
      className="space-y-2"
    >
      <Input label="Code" value={code} onChange={(e) => setCode(e.target.value)} />
      <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
      <Input label="Instructor" value={instructor} onChange={(e) => setInstructor(e.target.value)} />
      <Input label="Students" type="number" value={students} onChange={(e) => setStudents(e.target.value)} />
      <Input label="Preferred Days (comma-separated)" value={preferredDays} onChange={(e) => setPreferredDays(e.target.value)} />
      <button className="px-3 py-1.5 bg-gray-900 text-white rounded" type="submit">Add Course</button>
    </form>
  );
}

function StudentForm() {
  const [identifier, setIdentifier] = useState("");
  return (
    <form
      onSubmit={async (e) => {
        e.preventDefault();
        await createStudent({ identifier });
        setIdentifier("");
        alert("Student added");
      }}
      className="space-y-2"
    >
      <Input label="Identifier" value={identifier} onChange={(e) => setIdentifier(e.target.value)} />
      <button className="px-3 py-1.5 bg-gray-900 text-white rounded" type="submit">Add Student</button>
    </form>
  );
}

function EnrollmentForm() {
  const [student, setStudent] = useState("");
  const [course, setCourse] = useState("");
  return (
    <form
      onSubmit={async (e) => {
        e.preventDefault();
        await createEnrollment({ student, course });
        setStudent(""); setCourse("");
        alert("Enrollment added");
      }}
      className="space-y-2"
    >
      <Input label="Student Identifier" value={student} onChange={(e) => setStudent(e.target.value)} />
      <Input label="Course Code" value={course} onChange={(e) => setCourse(e.target.value)} />
      <button className="px-3 py-1.5 bg-gray-900 text-white rounded" type="submit">Add Enrollment</button>
    </form>
  );
}
