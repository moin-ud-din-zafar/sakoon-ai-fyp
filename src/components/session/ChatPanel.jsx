import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faComments,
  faCalendar,
  faPaperPlane,
  faShareNodes,
  faFloppyDisk,
  faXmark
} from "@fortawesome/free-solid-svg-icons";
import { LIVE_TRANSCRIPT_DUMMY } from "../../constants/constantdummydata";
import Button from "../common/Button";

export default function ChatPanel() {
  const [inputValue, setInputValue] = useState("");

  const handleSend = () => {
    if (!inputValue.trim()) return;
    setInputValue("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
    <section className="flex min-h-[500px] flex-col rounded-2xl border border-gray-100 bg-white">
      <header className="flex flex-none items-center justify-between border-b border-gray-100 px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-medium text-[#565d6d]">
          <span className="h-2 w-2 rounded-full bg-emerald-500" aria-hidden />
          Session Active
        </div>
        <div className="flex items-center gap-1.5 text-sm text-[#565d6d]">
          <FontAwesomeIcon icon={faCalendar} className="text-gray-600" />
          <span>00:01</span>
        </div>
        <div className="flex items-center gap-1.5 text-sm font-medium text-[#565d6d]">
          <FontAwesomeIcon icon={faComments} className="text-gray-600" />
          Text Chat
        </div>
      </header>

      <div className="min-h-0 flex-1 overflow-auto p-4">
        <div className="flex flex-col gap-3">
          {LIVE_TRANSCRIPT_DUMMY.map((msg) => (
            <div
              key={msg.id}
              className={
                msg.sender === "you"
                  ? "flex justify-end"
                  : "flex justify-start"
              }
            >
              <div
                className="max-w-[85%] rounded-lg px-4 py-3 sm:max-w-[75%]"
                style={{
                  backgroundColor:
                    msg.sender === "sakoon_ai" ? "#edf4ff" : "#edfdf3",
                }}
              >
                <div className="mb-1 flex items-start justify-between gap-2">
                  <span className="text-sm font-bold text-black">
                    {msg.sender === "sakoon_ai" ? "SAKOON AI:" : "YOU:"}
                  </span>
                  <span className="shrink-0 text-xs text-gray-500">
                    {msg.time}
                  </span>
                </div>
                {msg.content ? (
                  <p className="text-sm text-black">{msg.content}</p>
                ) : (
                  <p className="text-sm text-gray-400">—</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex-none border-t border-gray-100 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message here... Press Enter to send"
            className="min-w-0 flex-1 rounded-lg border border-gray-200 px-4 py-2.5 text-sm text-black placeholder:text-gray-400 focus:border-[#32c4c3] focus:outline-none focus:ring-1 focus:ring-[#32c4c3]"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={inputValue.trim().length === 0}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#32c4c3] text-white transition hover:bg-[#27a5a4] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-[#32c4c3]"
            aria-label="Send message"
          >
            <FontAwesomeIcon icon={faPaperPlane} />
          </button>
        </div>
      </div>
    </section>
    <div className="mt-4 flex gap-2">
            <Button text="End Session" backgroundColor="red" className="w-50" icon={<FontAwesomeIcon icon={faXmark} />} />
            <Button text="Save Session" border className="w-50"  icon={<FontAwesomeIcon icon={faFloppyDisk} />} />
            <Button
              text="Share with Clinicians"
              
              className="w-50"
              icon={<FontAwesomeIcon icon={faShareNodes} />}
            />
    </div>
    </>
  );
}
