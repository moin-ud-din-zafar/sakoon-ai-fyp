/**
 * Dummy data for Emotional State panel.
 * Valence: 0 = Negative, 100 = Positive.
 * Arousal: 0 = Calm, 100 = Excited.
 */

export const EMOTIONAL_STATE_EMOJI = {
  Neutral: "😊",
  Happy: "😄",
  Sad: "😢",
  Anxious: "😰",
  Calm: "😌",
  Excited: "🤩",
  Stressed: "😣",
  Relaxed: "😎",
};

export  const notes = [
  "Exam anxiety",
  "Focus difficulties",
  "Coping strategies",
  "Relaxation techniques",
];

export const EMOTIONAL_STATE_DUMMY = {
  currentState: "Neutral",
  valence: 45,
  arousal: 35,
  confidence: 70,
};


export const LIVE_TRANSCRIPT_DUMMY = [
  {
    id: "1",
    sender: "sakoon_ai",
    content:
      "Hello! I'm here to support you today. How are you feeling right now?",
    time: "12:30",
  },
  {
    id: "2",
    sender: "you",
    content:
      "I'm feeling quite anxious about my upcoming exams. I can't seem to focus on studying.",
    time: "12:31",
  },
  {
    id: "3",
    sender: "sakoon_ai",
    content: "I understand. Let's take a few deep breaths and focus on your breathing. Inhale through your nose, hold for a count of four, and exhale through your mouth for a count of four. Repeat this five times.",
    time: "12:32",
  },
];
