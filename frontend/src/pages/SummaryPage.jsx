import AppLayout from "../layouts/AppLayout";
import { FiMic, FiGlobe, FiLock, FiClock, FiSliders, FiUsers } from "react-icons/fi";

const FEATURES = [
  {
    icon: FiMic,
    title: "Voice-First Therapy",
    description:
      "Natural conversations with AI therapist using advanced voice recognition.",
  },
  {
    icon: FiGlobe,
    title: "Multilingual Support",
    description:
      "Available in 7 languages including Arabic, Hindi, Spanish, and more.",
  },
  {
    icon: FiLock,
    title: "Privacy & Security",
    description:
      "End-to-end encrypted sessions with complete confidentiality.",
  },
  {
    icon: FiClock,
    title: "24/7 Availability",
    description:
      "Access support whenever you need it, day or night.",
  },
  {
    icon: FiSliders,
    title: "Personalized Care",
    description:
      "AI adapts to your unique needs and therapeutic preferences.",
  },
  {
    icon: FiUsers,
    title: "Human Backup",
    description:
      "Connect with licensed therapists when needed.",
  },
];

function FeatureCard({ icon: Icon, title, description }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
      <div className="w-10 h-10 rounded-full bg-primary-light flex items-center justify-center mb-4 shrink-0">
        <Icon size={18} className="text-primary" />
      </div>
      <h3 className="text-sm font-semibold text-gray-800 mb-2">{title}</h3>
      <p className="text-sm text-gray-500 leading-relaxed">{description}</p>
    </div>
  );
}

export default function SummaryPage() {
  return (
    <AppLayout>
      {/* Heading */}
      <div className="text-center max-w-2xl mx-auto mb-10 pt-4">
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
          Why Choose Sakoon AI?
        </h1>
        <p className="text-gray-500 leading-relaxed text-sm sm:text-base">
          Advanced AI technology meets compassionate care to provide accessible
          mental health support tailored to your needs.
        </p>
      </div>

      {/* Feature grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {FEATURES.map((feature) => (
          <FeatureCard key={feature.title} {...feature} />
        ))}
      </div>
    </AppLayout>
  );
}
