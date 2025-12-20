import { bookingApprovalHook } from "@/workflows/chat/steps/tools";

export async function POST(request: Request) {
  const { toolCallId, approved, comment } = await request.json();
  
  await bookingApprovalHook.resume(toolCallId, { 
    approved,
    comment,
  });
  
  return Response.json({ success: true });
}
