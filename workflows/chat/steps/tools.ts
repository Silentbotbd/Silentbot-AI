import { tool, type LanguageModelV2Prompt } from "ai";
import { z } from "zod";
import { defineHook, getWritable, sleep } from "workflow";

// --- Hooks ---
export const bookingApprovalHook = defineHook({
  schema: z.object({
    approved: z.boolean(),
    comment: z.string().optional(),
  }),
});

// --- Step Implementations ---

export async function searchFlights({ from, to, date }: { from: string; to: string; date: string }) {
  "use step";
  console.log(`[Step] Searching flights from ${from} to ${to} on ${date}`);
  await new Promise(resolve => setTimeout(resolve, 1000));
  return JSON.stringify([
    { id: "FL-101", airline: "SilentAir", price: "$250", departure: "10:00 AM" },
    { id: "FL-202", airline: "BotAir", price: "$180", departure: "06:00 PM" },
  ]);
}

export async function bookFlight({ flightId, passengerName }: { flightId: string; passengerName: string }) {
  "use step";
  console.log(`[Step] Booking flight ${flightId} for ${passengerName}`);
  return JSON.stringify({ status: "confirmed", ticketId: `TKT-${Math.floor(Math.random() * 10000)}` });
}

async function performFetch(url: string) {
  "use step";
  console.log(`[Step] Fetching: ${url}`);
  const response = await fetch(url);
  return response.json();
}

async function getWeatherStep(
  { city }: { city: string },
  { messages }: { messages: LanguageModelV2Prompt }
) { 
  "use step";
  console.log(`[Step] Getting weather for ${city}. History length: ${messages.length}`);
  return `Weather in ${city} is currently 72°F and sunny.`;
}

async function writeToStream(data: any) {
  "use step";
  const writable = getWritable();
  const writer = writable.getWriter();
  await writer.write(data);
  writer.releaseLock();
}

// --- Workflow-level Tool Execution ---

async function executeBookingApproval( 
  { flightNumber, passengerName, price }: { flightNumber: string; passengerName: string; price: number }, 
  { toolCallId }: { toolCallId: string } 
) { 
  const hook = bookingApprovalHook.create({ token: toolCallId }); 
  const { approved, comment } = await hook; 
  if (!approved) {
    return `Booking rejected: ${comment || "No reason provided"}`;
  }
  return `Booking approved for ${passengerName} on flight ${flightNumber}${comment ? ` - Note: ${comment}` : ""}`;
}

async function executeFetchWithDelay({ url }: { url: string }) {
  const result = await performFetch(url);
  console.log("[Workflow] Result fetched, sleeping for 5s...");
  await sleep("5s"); 
  return JSON.stringify(result);
}

// --- Tool Definitions ---

export const flightBookingTools = {
  searchFlights: tool({
    description: "Search for flights between cities on a specific date",
    parameters: z.object({
      from: z.string().describe("Departure city"),
      to: z.string().describe("Destination city"),
      date: z.string().describe("Date of travel YYYY-MM-DD"),
    }),
    execute: searchFlights,
  }),
  bookingApproval: tool({
    description: "Request human approval before booking a flight",
    parameters: z.object({
      flightNumber: z.string().describe("Flight number to book"),
      passengerName: z.string().describe("Name of the passenger"),
      price: z.number().describe("Total price of the booking"),
    }),
    execute: executeBookingApproval,
  }),
  bookFlight: tool({
    description: "Book a specific flight",
    parameters: z.object({
      flightId: z.string().describe("The flight ID to book"),
      passengerName: z.string().describe("Name of the passenger"),
    }),
    execute: bookFlight,
  }),
  getWeather: tool({
    description: "Get the current weather for a city",
    parameters: z.object({
      city: z.string().describe("The city to get weather for"),
    }),
    execute: getWeatherStep,
  }),
  fetchData: tool({
    description: "Fetch data from a URL with a mandatory 5s delay",
    parameters: z.object({
      url: z.string().describe("The URL to fetch"),
    }),
    execute: executeFetchWithDelay,
  }),
};