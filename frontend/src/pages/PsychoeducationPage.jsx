import { useState } from "react";
import { FiClock, FiLayers, FiPlay } from "react-icons/fi";
import AppLayout from "../layouts/AppLayout";
import psychoHeader from "../assets/images/pysho-header.png";
import psychoCard   from "../assets/images/pysho-1.png";

// ── data ───────────────────────────────────────────────────────────────────
const FILTERS = ["All Lessons", "Anxiety", "Breathing", "Mindfulness", "Resilience", "CBT"];

const TAG_COLORS = {
  Anxiety:      "bg-teal-100 text-teal-700",
  Breathing:    "bg-cyan-100 text-cyan-700",
  Mindfulness:  "bg-blue-100 text-blue-700",
  Resilience:   "bg-amber-100 text-amber-700",
  CBT:          "bg-purple-100 text-purple-700",
  Beginner:     "bg-green-100 text-green-700",
  Intermediate: "bg-orange-100 text-orange-700",
  Advanced:     "bg-red-100 text-red-700",
  Relaxation:   "bg-sky-100 text-sky-700",
};

const LESSONS = [
  {
    image: psychoCard,
    link: "https://www.youtube.com/watch?v=ZToicYcHIOU",
    title: "Understanding Anxiety: Your First Step to Healing",
    description:
      "Learn the basics of anxiety, its symptoms, and how it affects your daily life. This foundational lesson will help you recognise triggers and develop coping awareness.",
    tags: ["Anxiety", "Beginner"],
    duration: "15 min",
    exerciseCount: 1,
  },
  {
    image: psychoCard,
    link: "https://www.youtube.com/watch?v=tybOi4hjZFQ",
    title: "Box Breathing: A Simple Technique for Calm",
    description:
      "Master the box breathing technique to quickly reduce anxiety and stress. Practice this 4-4-4-4 breathing pattern to regain control and find inner calm.",
    tags: ["Breathing", "Intermediate", "Relaxation"],
    duration: "10 min",
    exerciseCount: 1,
  },
  {
    image: psychoCard,
    link: "https://www.youtube.com/watch?v=wnHWl0C5pHo",
    title: "Journaling for Emotional Regulation",
    description:
      "Explore how journaling can be a powerful tool for processing emotions, identifying thought patterns, and improving overall mental well-being.",
    tags: ["Mindfulness", "Beginner"],
    duration: "20 min",
    exerciseCount: 2,
  },
  {
    image: psychoCard,
    link: "https://www.youtube.com/watch?v=w6T02g5hnT4",
    title: "Mindfulness Basics: Living in the Present",
    description:
      "An introduction to mindfulness practices that help you stay grounded, reduce stress, and enhance your awareness of the present moment.",
    tags: ["Mindfulness", "Beginner"],
    duration: "25 min",
    exerciseCount: 3,
  },
  {
    image: psychoCard,
    link: "https://www.youtube.com/watch?v=3QIfkeA6HBY",
    title: "Building Resilience: Bouncing Back from Adversity",
    description:
      "Learn strategies to build emotional resilience, adapt to change, and navigate life's challenges with strength and optimism.",
    tags: ["Resilience", "Intermediate"],
    duration: "30 min",
    exerciseCount: 2,
  },
  {
    image: psychoCard,
    link: "https://www.youtube.com/watch?v=0ViaCs0k2jM",
    title: "Cognitive Behavioral Techniques for Daily Life",
    description:
      "Discover practical CBT techniques to challenge negative thoughts, reframe perspectives, and foster healthier emotional responses.",
    tags: ["CBT", "Advanced", "Intermediate"],
    duration: "45 min",
    exerciseCount: 4,
  },
];

// ── sub-components ─────────────────────────────────────────────────────────
function Tag({ label }) {
  const color = TAG_COLORS[label] ?? "bg-gray-100 text-gray-600";
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${color}`}>
      {label}
    </span>
  );
}

function LessonCard({ image, link, title, description, tags, duration, exerciseCount }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden flex flex-col">
      {/* Card image */}
      <img src={image} alt={title} className="w-full h-44 object-cover" />

      {/* Card body */}
      <div className="flex flex-col flex-1 p-4">
        <h3 className="text-sm font-semibold text-gray-800 mb-1 leading-snug line-clamp-2">
          {title}
        </h3>
        <p className="text-xs text-gray-500 leading-relaxed mb-3 line-clamp-3 flex-1">
          {description}
        </p>

        {/* Tags */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          {tags.map((t) => <Tag key={t} label={t} />)}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <div className="flex items-center gap-3 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <FiClock size={12} />
              {duration}
            </span>
            <span className="flex items-center gap-1">
              <FiLayers size={12} />
              {exerciseCount} {exerciseCount === 1 ? "exercise" : "exercises"}
            </span>
          </div>
          <button
            onClick={() => window.open(link, "_blank", "noopener,noreferrer")}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-primary text-primary text-xs font-medium hover:bg-primary hover:text-white transition-colors cursor-pointer"
          >
            <FiPlay size={11} />
            Start
          </button>
        </div>
      </div>
    </div>
  );
}

// ── main page ──────────────────────────────────────────────────────────────
export default function PsychoeducationPage() {
  const [activeFilter, setActiveFilter] = useState("All Lessons");

  const filtered =
    activeFilter === "All Lessons"
      ? LESSONS
      : LESSONS.filter((l) => l.tags.includes(activeFilter));

  return (
    <AppLayout>
      {/* ── Hero ── */}
      <div className="bg-primary-light rounded-2xl overflow-hidden flex flex-col md:flex-row items-center gap-6 p-6 sm:p-8 mb-8">
        {/* Text */}
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 leading-tight mb-3">
            Explore Our Psychoeducation Library
          </h1>
          <p className="text-sm text-gray-600 leading-relaxed mb-5 max-w-sm">
            Access a curated collection of lessons designed to enhance your mental well-being
            through accessible psychoeducation and practical exercises.
          </p>
          <button className="px-5 py-2.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-colors cursor-pointer">
            Start Your Journey
          </button>
        </div>

        {/* Hero image */}
        <div className="shrink-0 w-full md:w-[42%]">
          <img
            src={psychoHeader}
            alt="Psychoeducation"
            className="w-full h-48 md:h-56 object-cover rounded-xl"
          />
        </div>
      </div>

      {/* ── Filter tabs ── */}
      <div className="flex flex-wrap items-center gap-2 mb-6">
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setActiveFilter(f)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors cursor-pointer ${
              activeFilter === f
                ? "bg-primary text-white"
                : "border border-gray-200 text-gray-600 hover:border-primary hover:text-primary bg-white"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* ── Lesson grid ── */}
      {filtered.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((lesson) => (
            <LessonCard key={lesson.title} {...lesson} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 text-gray-400 text-sm">
          No lessons found for this category.
        </div>
      )}
    </AppLayout>
  );
}
