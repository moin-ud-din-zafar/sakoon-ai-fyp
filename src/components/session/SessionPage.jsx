import VideoSessionPanel from "./VideoSessionPanel";
import LiveTranscript from "./LiveTranscript";
import EmotionStatePanel from "./EmotionStatePanel";
import SessionNotesPanel from "./SessionNotesPanel";

export default function SessionPage() {
  return (
    <main className="min-h-[calc(100vh-64px)] overflow-x-hidden bg-white px-3 py-4 sm:px-4 sm:py-5 md:px-6 md:py-8 lg:px-8">
      <div className="m-auto flex w-full max-w-7xl flex-col gap-4 sm:gap-5">
        <section className="m-auto grid w-full max-w-7xl grid-cols-1 gap-4 p-2 sm:gap-6 sm:p-4 lg:grid-cols-[minmax(0,2.7fr)_minmax(0,1fr)] lg:p-6 lg:gap-6">
          <div className="min-w-0 flex flex-col gap-4">
            <VideoSessionPanel />
            <LiveTranscript />
          </div>

          <div className="min-w-0 flex flex-col gap-4 lg:mt-[50px]">
            <EmotionStatePanel />
            <SessionNotesPanel />
          </div>
        </section>
      </div>
    </main>
  );
}

