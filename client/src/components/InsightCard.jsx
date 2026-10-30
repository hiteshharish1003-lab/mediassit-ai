import React from "react";
import { AlertTriangle, Info } from "lucide-react";

export default function InsightCard({ title, detail, type }) {
  const isWarning = type === "warning" || type === "risk";

  return (
    <div
      className={`p-5 rounded-xl shadow-md border ${
        isWarning ? "bg-red-50 border-red-300" : "bg-blue-50 border-blue-300"
      }`}
    >
      <div className="flex items-center gap-3">
        {isWarning ? (
          <AlertTriangle className="text-red-600" size={24} />
        ) : (
          <Info className="text-blue-600" size={24} />
        )}
        <h3
          className={`text-lg font-semibold ${
            isWarning ? "text-red-700" : "text-blue-700"
          }`}
        >
          {title}
        </h3>
      </div>
      <p className="mt-2 text-gray-700">{detail}</p>
    </div>
  );
}
