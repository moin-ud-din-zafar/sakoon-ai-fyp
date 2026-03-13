import { notes } from "../../constants/constantdummydata";

export default function SessionNotesPanel() {
 

  return (
    <section className="flex h-[200px] flex-col gap-3 rounded-2xl border border-gray-100 bg-transparent p-5 overflow-y-auto">
      <h2 className="text-[18px] font-semibold text-gray-800">Session Notes</h2>
      <p className="text-sm font-medium text-black">Key topics discussed:</p>
      <ul
        className="mt-1 list-disc space-y-1 pl-5 text-xs text-black session-notes-list"
        style={{ listStyleColor: "#565d6d" }}
      >
        {notes.map((note) => (
          <li key={note}>{note}</li>
        ))}
      </ul>
    </section>
  );
}

