"use client";
import { useChat } from "@ai-sdk/react";
import { WorkflowChatTransport } from "@workflow/ai";
import { useMemo } from "react";

import { BookingApproval } from "@/components/booking-approval";

export default function DurableChatPage() {
  // ... (rest of the code until the message mapping) ...

  const { messages, input, handleInputChange, handleSubmit, status } = useChat({
    // ... config ...
  });

  return (
    <div className="flex flex-col w-full max-w-md py-24 mx-auto stretch">
      <h1 className="text-xl font-bold mb-4">Durable Chat (Resumable)</h1>
      <div className="mb-4 text-sm text-gray-500">
        Status: {status} {activeRunId ? `(Last Run: ${activeRunId})` : ""}
      </div>
      
      {messages.map((m) => (
        <div key={m.id} className="whitespace-pre-wrap mb-4">
          <strong>{m.role === "user" ? "User: " : "AI: "}</strong>
          {m.content}
          {m.parts?.map((part, i) => {
             if (part.type === 'tool-invocation') {
               if (part.toolName === 'bookingApproval') {
                 return (
                   <BookingApproval
                     key={i}
                     toolCallId={part.toolCallId}
                     // @ts-ignore - args is inferred as unknown, but we know it matches our tool
                     input={part.args}
                     output={part.result as string}
                   />
                 );
               }
               return <div key={i} className="bg-gray-100 p-2 text-xs mt-1 border rounded">
                 Tool: {part.toolName} ({JSON.stringify(part.args)})
                 { 'result' in part && <div>Result: {JSON.stringify(part.result)}</div>}
               </div>
             }
             return null;
          })}
        </div>
      ))}
      
      {/* ... form ... */}
