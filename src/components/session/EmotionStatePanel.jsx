import {
  EMOTIONAL_STATE_DUMMY,
  EMOTIONAL_STATE_EMOJI,
} from "../../constants/constantdummydata";

export default function EmotionStatePanel() {
  const { currentState, valence, arousal, confidence } = EMOTIONAL_STATE_DUMMY;
  const emoji = EMOTIONAL_STATE_EMOJI[currentState] ?? EMOTIONAL_STATE_EMOJI.Neutral;

  return (
    <section className="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-transparent p-5">
      <header className="flex items-center justify-between gap-3">
        <h2 className="text-[18px] font-bold text-black">Emotional State</h2>
        <span className="text-lg" aria-hidden="true">
          {emoji}
        </span>
      </header>

      <div className="flex flex-col items-center gap-4">
        <span className="rounded-[5px] bg-[#4a90e2] px-4 py-1.5 text-xs font-medium text-white">
          {currentState}
        </span>

        <div className="w-full space-y-4">
          <div>
            <div className="flex justify-between text-xs font-medium text-black">
              <span className="text-[#565d6d] font-semibold text-sm">Negative</span>
              <span className="text-[#565d6d] font-semibold text-sm">Positive</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={valence}
              readOnly
              className="emotional-range h-2 w-full cursor-default appearance-none rounded-full [&::-webkit-slider-thumb]:h-6 [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-[#5c7aea] [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:shadow-sm [&::-moz-range-thumb]:h-6 [&::-moz-range-thumb]:w-6 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:border-2 [&::-moz-range-thumb]:border-[#5c7aea] [&::-moz-range-thumb]:bg-white"
              style={{
                background: `linear-gradient(to right, #5c7aea ${valence}%, #ccd6f8 ${valence}%)`,
              }}
            />
          </div>

          <div >
            <div className="flex justify-between text-xs font-medium text-black">
              <span className="text-[#565d6d] font-semibold text-sm">Calm</span>
              <span className="text-[#565d6d] font-semibold text-sm">Excited</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={arousal}
              readOnly
              className="emotional-range h-2 w-full cursor-default appearance-none rounded-full [&::-webkit-slider-thumb]:h-6 [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-[#5c7aea] [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:shadow-sm [&::-moz-range-thumb]:h-6 [&::-moz-range-thumb]:w-6 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:border-2 [&::-moz-range-thumb]:border-[#5c7aea] [&::-moz-range-thumb]:bg-white"
              style={{
                background: `linear-gradient(to right, #5c7aea ${arousal}%, #ccd6f8 ${arousal}%)`,
              }}
            />
          </div>

          <p className="font-semibold text-[#565d6d]">
            Confidence: <span className="font-semibold text-[#565d6d]">{confidence}%</span>
          </p>
        </div>
      </div>
    </section>
  );
}
