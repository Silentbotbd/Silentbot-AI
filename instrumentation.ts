import { registerOTel } from "@vercel/otel";

export function register() {
  registerOTel({ serviceName: "ai-chatbot" });
  console.log("\n\x1b[36m%s\x1b[0m", "SILENTBOT AI [ENTERPRISE SERVER]");
  console.log("\x1b[32m%s\x1b[0m", "Status: ONLINE");
  console.log("\x1b[33m%s\x1b[0m", "Singularity UI: Active on Port 3000\n");
}
