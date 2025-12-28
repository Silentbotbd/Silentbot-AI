diff --git a/app/api/vercel/deploy/route.ts b/app/api/vercel/deploy/route.ts
new file mode 100644
index 0000000000000000000000000000000000000000..3f6a41d6a94a0574e59e64c83064d33a2c02b16d
--- /dev/null
+++ b/app/api/vercel/deploy/route.ts
@@ -0,0 +1,111 @@
+import { NextResponse } from "next/server";
+
+type DeployRequest = {
+  target?: "production" | "preview";
+};
+
+function getRequiredEnv(name: string) {
+  const value = process.env[name];
+  if (!value) {
+    return { error: `Missing required env: ${name}` };
+  }
+  return { value };
+}
+
+async function fetchVercel<T>(url: string) {
+  const { value: token, error } = getRequiredEnv("VERCEL_TOKEN");
+  if (error) {
+    return { error };
+  }
+
+  const response = await fetch(url, {
+    headers: {
+      Authorization: `Bearer ${token}`,
+      "Content-Type": "application/json",
+    },
+  });
+
+  const data = (await response.json()) as T;
+  if (!response.ok) {
+    return {
+      error:
+        (data as { error?: { message?: string } })?.error?.message ??
+        `Vercel API request failed with status ${response.status}`,
+    };
+  }
+
+  return { data };
+}
+
+export async function GET() {
+  const { value: projectId, error } = getRequiredEnv("VERCEL_PROJECT_ID");
+  if (error) {
+    return NextResponse.json({ error }, { status: 400 });
+  }
+
+  const [projectResult, deploymentsResult] = await Promise.all([
+    fetchVercel<{ id: string; name: string }>(
+      `https://api.vercel.com/v9/projects/${projectId}`
+    ),
+    fetchVercel<{ deployments: Array<{ uid: string; url: string }> }>(
+      `https://api.vercel.com/v6/deployments?projectId=${projectId}&limit=1`
+    ),
+  ]);
+
+  if (projectResult.error) {
+    return NextResponse.json({ error: projectResult.error }, { status: 400 });
+  }
+
+  if (deploymentsResult.error) {
+    return NextResponse.json({ error: deploymentsResult.error }, { status: 400 });
+  }
+
+  return NextResponse.json({
+    project: projectResult.data,
+    latestDeployment: deploymentsResult.data?.deployments?.[0] ?? null,
+  });
+}
+
+export async function POST(request: Request) {
+  const { value: deployHookUrl, error } = getRequiredEnv(
+    "VERCEL_DEPLOY_HOOK_URL"
+  );
+
+  if (error) {
+    return NextResponse.json(
+      {
+        error,
+        message:
+          "Set VERCEL_DEPLOY_HOOK_URL to a Vercel Deploy Hook to trigger production builds.",
+      },
+      { status: 400 }
+    );
+  }
+
+  const body = (await request.json().catch(() => ({}))) as DeployRequest;
+  const target = body.target ?? "production";
+  const hook = new URL(deployHookUrl);
+  hook.searchParams.set("target", target);
+
+  const response = await fetch(hook.toString(), {
+    method: "POST",
+  });
+
+  const data = await response.json().catch(() => ({ status: "queued" }));
+
+  if (!response.ok) {
+    return NextResponse.json(
+      {
+        error: `Deploy hook failed with status ${response.status}`,
+        details: data,
+      },
+      { status: 500 }
+    );
+  }
+
+  return NextResponse.json({
+    status: "deployment queued",
+    target,
+    response: data,
+  });
+}
