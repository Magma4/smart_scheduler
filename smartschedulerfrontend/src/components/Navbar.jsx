export default function Navbar() {
  return (
    <nav className="w-full bg-white/70 backdrop-blur border-b border-gray-200">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <a href="/" className="text-lg font-semibold">Smart Scheduler</a>
        <div className="space-x-4 text-sm">
          <a href="/" className="text-gray-700 hover:text-black">Home</a>
          <a href="/about" className="text-gray-700 hover:text-black">About</a>
        </div>
      </div>
    </nav>
  );
}
