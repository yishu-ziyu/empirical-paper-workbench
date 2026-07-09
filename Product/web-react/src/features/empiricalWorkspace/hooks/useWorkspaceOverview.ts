import { cgssOverview } from "../fixtures/cgssOverview";
import type { WorkspaceOverview } from "../types";

export function useWorkspaceOverview(workspaceId: string): WorkspaceOverview {
  if (workspaceId !== cgssOverview.workspaceId) {
    return cgssOverview;
  }
  return cgssOverview;
}
