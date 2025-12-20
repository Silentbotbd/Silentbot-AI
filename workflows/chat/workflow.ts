import { DurableAgent } from "@workflow/ai/agent";
import { getWritable } from "workflow";
import { flightBookingTools } from "./steps/tools";
import { gateway } from "@ai-sdk/gateway";
import type { CoreMessage, UIMessageChunk } from "ai";

export async function chatWorkflow(messages: CoreMessage[]) {
  "use workflow";
  const writable = getWritable<UIMessageChunk>();
  
  const agent = new DurableAgent({
    model: gateway("xai/grok-2-vision-1212"),
    system: "You are a helpful flight booking assistant. Use the provided tools to search for flights and book them.",
    tools: flightBookingTools,
  });

  await agent.stream({
    messages,
    writable,
  });
}
