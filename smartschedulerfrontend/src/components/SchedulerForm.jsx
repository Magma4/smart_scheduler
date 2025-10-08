import { useState } from "react";
import { getOptimizedSchedule, seedDemoData } from "../api/scheduleApi";

export default function SchedulerForm({ onResult }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    preferredDays: ["Mon"],
    notes: "",
  });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      // For now we just forward a minimal constraints object.
      const constraints = { preferred_days: form.preferredDays };
      const res = await getOptimizedSchedule(constraints);
      onResult?.(res);
    } catch (err) {
      setError(err?.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-4 bg-white p-4 rounded-lg border border-gray-200">
      <div>
        <label className="block text-sm font-medium mb-1">Preferred Days</label>
        <select
          multiple
          value={form.preferredDays}
          onChange={(e) =>
            setForm((s) => ({ ...s, preferredDays: Array.from(e.target.selectedOptions).map((o) => o.value) }))
          }
          className="w-full border rounded px-2 py-1"
        >
          {[
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
          ].map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Notes</label>
        <textarea
          value={form.notes}
          onChange={(e) => setForm((s) => ({ ...s, notes: e.target.value }))}
          className="w-full border rounded px-2 py-1"
          rows={3}
        />
      </div>
      {error && <div className="text-red-600 text-sm">{error}</div>}
      <div className="flex items-center gap-3">
        <button
          type="submit"
          className="px-4 py-2 bg-black text-white rounded disabled:opacity-50"
          disabled={loading}
        >
          {loading ? "Generating..." : "Generate Schedule"}
        </button>
        <button
          type="button"
          onClick={async () => {
            setError("");
            setLoading(true);
            try {
              await seedDemoData();
            } catch (err) {
              setError(err?.message || "Seeding failed");
            } finally {
              setLoading(false);
            }
          }}
          className="px-4 py-2 bg-gray-800 text-white rounded disabled:opacity-50"
          disabled={loading}
          title="Add demo rooms, timeslots, courses, and enrollments"
        >
          Seed Demo Data
        </button>
      </div>
    </form>
  );
}
