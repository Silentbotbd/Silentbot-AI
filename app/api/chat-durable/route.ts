import { convertToCoreMessages, createUIMessageStreamResponse } from "ai";
import { start } from "workflow/api";
import { chatWorkflow } from "@/workflows/chat/workflow";

export async function POST(req: Request) {
  const { messages } = await req.json();
  const modelMessages = convertToCoreMessages(messages);
  
  const run = await start(chatWorkflow, [modelMessages]);
  
  return createUIMessageStreamResponse({
    stream: run.readable,
    headers: {
      "x-workflow-run-id": run.runId,
    },
  });
}
