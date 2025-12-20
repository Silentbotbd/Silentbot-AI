"use client";
import { useState } from "react";

interface BookingApprovalProps {
  toolCallId: string;
  input: {
    flightNumber: string;
    passengerName: string;
    price: number;
  };
  output?: string;
}

export function BookingApproval({ toolCallId, input, output }: BookingApprovalProps) {
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (output) {
    return (
      <div className="border rounded-lg p-4 bg-gray-50">
        <p className="text-sm text-gray-700">{output}</p>
      </div>
    );
  }

  const handleSubmit = async (approved: boolean) => {
    setIsSubmitting(true);
    try {
      await fetch("/api/approve-booking", { 
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify({ toolCallId, approved, comment }), 
      }); 
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="border rounded-lg p-4 space-y-4 bg-white shadow-sm">
      <div className="space-y-2">
        <p className="font-medium">Approve this booking?</p>
        <div className="text-sm text-gray-600">
          <div>Flight: {input.flightNumber}</div>
          <div>Passenger: {input.passengerName}</div>
          <div>Price: ${input.price}</div>
        </div>
      </div>
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Add a comment (optional)..."
        className="w-full border rounded p-2 text-sm"
        rows={2}
      />
      <div className="flex gap-2">
        <button
          onClick={() => handleSubmit(true)}
          disabled={isSubmitting}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
        >
          {isSubmitting ? "Submitting..." : "Approve"}
        </button>
        <button
          onClick={() => handleSubmit(false)}
          disabled={isSubmitting}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
        >
          {isSubmitting ? "Submitting..." : "Reject"}
        </button>
      </div>
    </div>
  );
}
