export default function ScheduleResults({ result }) {
  if (!result) return null;
  const { CSPStatus, assignments } = result;
  return (
    <div className="mt-6">
      <div className="mb-2 text-sm text-gray-600">Status: <span className="font-medium">{CSPStatus}</span></div>
      {CSPStatus === "success" && assignments && (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm border border-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left border-b">Course</th>
                <th className="px-3 py-2 text-left border-b">Room</th>
                <th className="px-3 py-2 text-left border-b">Timeslot</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(assignments).map(([code, a]) => (
                <tr key={code} className="odd:bg-white even:bg-gray-50">
                  <td className="px-3 py-2 border-b font-medium">{code}</td>
                  <td className="px-3 py-2 border-b">{a.room}</td>
                  <td className="px-3 py-2 border-b">{a.timeslot}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {CSPStatus === "failure" && (
        <div className="text-red-600">No feasible schedule found. Try adjusting constraints.</div>
      )}
    </div>
  );
}
