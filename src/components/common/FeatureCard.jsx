import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

export default function FeatureCard({ icon, title, description }) {
  return (
    <div className="rounded-lg border border-gray-100 bg-white p-6 shadow-sm flex flex-col items-start text-left">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-[#eaf7f6] text-[#32c4c3]">
        <FontAwesomeIcon icon={icon} className="text-xl" aria-hidden />
      </div>

      <div className="w-full">
        <h3 className="text-lg font-semibold text-black">{title}</h3>
        <p className="mt-2 text-sm text-gray-600">{description}</p>
      </div>
    </div>
  );
}
