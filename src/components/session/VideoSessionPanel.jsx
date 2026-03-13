import { useState, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faMicrophone,
  faMicrophoneSlash,
  faVolumeHigh,
  faVolumeXmark,
  faClock,
} from "@fortawesome/free-solid-svg-icons";
import dummyAvatar from "../../assets/Dummy Avatar.png";

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function VideoSessionPanel() {
  const [isMicOn, setIsMicOn] = useState(false);
  const [isSpeakerOn, setIsSpeakerOn] = useState(true);
  const [currentTime, setCurrentTime] = useState(() => formatTime(new Date()));

  useEffect(() => {
    const id = setInterval(() => setCurrentTime(formatTime(new Date())), 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <section className="flex flex-col items-center gap-2 lg:gap-2">
      <header className="flex w-full items-center justify-between px-4 py-3 text-[13px] text-gray-500">
        <div className="flex items-center gap-2">
          <span
            className="h-2 w-2 rounded-full border-2 border-emerald-500 bg-white"
            aria-hidden="true"
          />
          <span>Session Active</span>
          <span className="ml-2 flex items-center gap-1.5">
            <FontAwesomeIcon icon={faClock} className="text-xs" aria-hidden="true" />
            <span>{currentTime}</span>
          </span>
        </div>

        <span className="text-gray-500">
          Voice Session with AI Therapist
        </span>
      </header>

      <div className="relative w-full overflow-hidden rounded-2xl border border-[#e3e4f2] bg-gradient-to-br from-[#f9fbff] via-white to-[#f4f0ff] shadow-[0_18px_40px_rgba(15,23,42,0.08)]">
        <img
          src={dummyAvatar}
          alt="AI Therapist"
          className="h-[260px] w-full object-cover md:h-[400px]"
        />

        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/25 via-transparent to-black/10" />

        <div className="pointer-events-none absolute inset-x-0 bottom-5 flex justify-center">
          <div className="pointer-events-auto flex items-center gap-5 rounded-full bg-black/35 px-6 py-3 backdrop-blur-sm">
            <button
              type="button"
              onClick={() => setIsMicOn((prev) => !prev)}
              className={`flex h-8 w-8 items-center justify-center rounded-full text-white transition hover:bg-white/10 ${
                isMicOn ? "opacity-100" : "opacity-80"
              }`}
              aria-label={isMicOn ? "Mute microphone" : "Unmute microphone"}
            >
              <FontAwesomeIcon icon={isMicOn ? faMicrophone : faMicrophoneSlash} />
            </button>

            <button
              type="button"
              onClick={() => setIsSpeakerOn((prev) => !prev)}
              className={`flex h-8 w-8 items-center justify-center rounded-full text-white transition hover:bg-white/10 ${
                isSpeakerOn ? "opacity-100" : "opacity-80"
              }`}
              aria-label={isSpeakerOn ? "Mute speaker" : "Unmute speaker"}
            >
              <FontAwesomeIcon icon={isSpeakerOn ? faVolumeHigh : faVolumeXmark} />
            </button>
          </div>
        </div>
      </div>

      <button
        type="button"
        className="flex flex-col items-center gap-2 text-xs font-medium text-gray-500"
      >
        <span className="flex h-14 w-14 items-center justify-center rounded-full bg-[#1a73e8] text-white shadow-md transition hover:bg-[#1559b5]">
          <FontAwesomeIcon icon={faMicrophone} className="text-xl" />
        </span>
        <span>Tap to speak</span>
      </button>
    </section>
  );
}

