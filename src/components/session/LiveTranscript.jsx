import { Link } from "react-router-dom";
import { LIVE_TRANSCRIPT_DUMMY } from "../../constants/constantdummydata";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowUpFromBracket, faComments } from "@fortawesome/free-solid-svg-icons";
import Button from "../common/Button";

export default function LiveTranscript() {
  return (
    <div>
    <div className="w-full rounded-2xl border border-gray-100 bg-white p-4 min-h-[300px] max-h-[500px] overflow-auto">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-base font-bold text-black">
          Live Transcript
        </h2>
        <Link to="/chat" className="cursor-pointer text-gray-500 hover:text-gray-700" aria-label="Open text chat">
          <FontAwesomeIcon icon={faComments} className="text-lg" aria-hidden="true" />
        </Link>
      </div>
      <div className="flex flex-col gap-3">
        {LIVE_TRANSCRIPT_DUMMY.map((msg) => (
          <div
            key={msg.id}
            className="rounded-lg px-4 py-3"
            style={{
              backgroundColor:
                msg.sender === "sakoon_ai" ? "#edf4ff" : "#edfdf3",
            }}
          >
            <div className="mb-1 flex items-start justify-between gap-2">
              <span className="text-sm font-bold text-black">
                {msg.sender === "sakoon_ai" ? "SAKOON AI:" : "YOU:"}
              </span>
              <span className="shrink-0 text-xs text-gray-500">{msg.time}</span>
            </div>
            {msg.content ? (
              <p className="text-sm text-black">{msg.content}</p>
            ) : (
              <p className="text-sm text-gray-400">—</p>
            )}
          </div>
        ))}
      </div>
   
    </div>
       <div className="mt-4 flex gap-2">
            <Button text="End Session" backgroundColor="red" className="w-50" />
            <Button text="Save Session" border className="w-50" />
            <Button
              text="Share"
              border
              className="w-50"
              icon={<FontAwesomeIcon icon={faArrowUpFromBracket} />}
            />
          </div>
          </div>
  );
}
