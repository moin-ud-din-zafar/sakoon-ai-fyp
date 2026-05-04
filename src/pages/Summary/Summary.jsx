import FeatureCard from "../../components/common/FeatureCard";
import {
  faMicrophone,
  faGlobe,
  faShield,
  faClock,
  faBrain,
  faUser,
} from "@fortawesome/free-solid-svg-icons";

const FEATURES = [
  {
    id: 1,
    icon: faMicrophone,
    title: "Voice-First Therapy",
    description:
      "Natural conversations with AI therapist using advanced voice recognition.",
  },
  {
    id: 2,
    icon: faGlobe,
    title: "Multilingual Support",
    description:
      "Available in 7 languages including Arabic, Hindi, Spanish, and more.",
  },
  {
    id: 3,
    icon: faShield,
    title: "Privacy & Security",
    description: "End-to-end encrypted sessions with complete confidentiality.",
  },
  {
    id: 4,
    icon: faClock,
    title: "24/7 Availability",
    description: "Access support whenever you need it, day or night.",
  },
  {
    id: 5,
    icon: faBrain,
    title: "Personalized Care",
    description: "AI adapts to your unique needs and therapeutic preferences.",
  },
  {
    id: 6,
    icon: faUser,
    title: "Human Backup",
    description: "Connect with licensed therapists when needed.",
  },
];

export default function Summary() {
  return (
    <div className="min-h-[calc(100vh-64px)] bg-[#f2f4f4] px-6 py-16">
      <div className="mx-auto w-full max-w-6xl text-center">
        <h1 className="text-4xl font-bold text-[#0f1724]">Why Choose Sakoon AI?</h1>
        <p className="mt-4 text-lg text-[#6b7280] ">
          Advanced AI technology meets compassionate care to <br /> provide accessible
          mental health support tailored to your needs.
        </p>

        <div className="mt-10 grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <FeatureCard
              key={f.id}
              icon={f.icon}
              title={f.title}
              description={f.description}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
