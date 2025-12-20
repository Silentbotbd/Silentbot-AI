// app/my-page.tsx, or your other component
import { createFeatureFlag } from "../flags";

export default async function Page() {
  const enabled = await createFeatureFlag("my_first_gate")(); //Disabled by default, edit in the Statsig console
  return <div>myFeatureFlag is {enabled ? "on" : "off"}</div>
};
//Note: this is designed for server & middleware - check "Getting Started" for client-side details!
