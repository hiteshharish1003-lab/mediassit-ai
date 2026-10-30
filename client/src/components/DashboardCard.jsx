import React from "react";
import { Users, Stethoscope, HeartPulse, Pill } from "lucide-react";

export default function DashboardCard({ title, value, icon }) {
  const Icon =
    icon === "patient"
      ? Users
      : icon === "doctor"
      ? Stethoscope
      : icon === "vitals"
      ? HeartPulse
      : Pill;

  return (
    <div className="bg-white shadow-md hover:shadow-lg transition-all rounded-xl p-6 border border-gray-100 flex flex-col justify-center items-center text-center">
      <Icon className="text-indigo-600 mb-3" size={32} />
      <h3 className="text-xl font-semibold text-gray-800">{title}</h3>
      <p className="text-3xl font-bold text-indigo-700 mt-1">{value}</p>
    </div>
  );
}
