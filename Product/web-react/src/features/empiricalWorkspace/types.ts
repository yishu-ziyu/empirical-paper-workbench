export type ClaimStrength =
  | "causal"
  | "qualified_causal"
  | "descriptive"
  | "exploratory"
  | "no_claim";

export type ArtifactStatus =
  | "unknown"
  | "found"
  | "draft"
  | "complete"
  | "blocked"
  | "diagnostic_only"
  | "claim_ready"
  | "stale"
  | "mismatch"
  | "clean"
  | "not_ready"
  | "clean_rerun_required";

export type ArtifactName =
  | "DataContract"
  | "SampleAudit"
  | "MeasurementAudit"
  | "DesignRegister"
  | "MethodGate"
  | "ResultObject"
  | "EvidenceLedger"
  | "ClaimAudit"
  | "ReplicationPackage";

export type EntryType =
  | "idea_only"
  | "data_only"
  | "script_results_only"
  | "draft_only"
  | "mixed_existing_workspace"
  | "rr_package";

export interface NextAction {
  label: string;
  artifactName: ArtifactName;
  gateName: string;
  reason: string;
  actionKind: "open_evidence_panel" | "open_checklist" | "request_human_confirmation";
  destructive: false;
}

export interface GateSummary {
  gateName: string;
  status: ArtifactStatus;
  requiredArtifacts: ArtifactName[];
  hardFlags: string[];
  missingArtifacts: ArtifactName[];
  claimConsequence: string;
  nextAction: NextAction;
  freshness: "fresh" | "stale" | "unknown";
  lastChecked: string | null;
  humanConfirmationRequired: boolean;
}

export interface ArtifactSummary {
  artifactName: ArtifactName;
  status: ArtifactStatus;
  missingFields: string[];
  sourceLocators: string[];
  canSupportClaim: boolean;
  claimConsequence: string;
  staleRisk: boolean;
  evidencePanelId: string;
  domainReason: string;
  nextActionLabel: string;
}

export interface ClaimAuditSummary {
  claimId: string;
  sourceLocator: string;
  originalText: string;
  claimType: "empirical" | "numeric" | "causal" | "policy";
  requestedStrength: ClaimStrength;
  allowedStrength: ClaimStrength;
  blockingReason: string;
  allowedWording: string;
  forbiddenWording: string;
  linkedGate: string;
  linkedResultObjectId: string | null;
  linkedExhibitId: string | null;
}

export interface NumberMismatchSummary {
  mismatchId: string;
  claimId: string;
  resultObjectId: string;
  exhibitLocator: string | null;
  manuscriptValue: string;
  resultValue: string;
  field: "effect" | "se" | "ci" | "p_value" | "n" | "sample" | "cluster" | "unit";
  resolutionPath: string;
}

export interface ReplicationReadinessSummary {
  status: "clean" | "not_ready" | "clean_rerun_required";
  runAllPresent: boolean;
  environmentCaptured: boolean;
  logsPresent: boolean;
  manifestPresent: boolean;
  checksumsPresent: boolean;
  dataAvailabilityStatementPresent: boolean;
  tableFigureScriptMapPresent: boolean;
  cleanRerunStatus: "passed" | "missing" | "failed" | "not_run";
  blockingReason: string;
}

export interface ResultObjectSummary {
  resultObjectId: string;
  estimand: string;
  estimator: string;
  effect: string;
  standardError: string;
  pValue: string;
  n: string;
  sampleId: string;
  clusterLevel: string;
  scriptLocator: string;
  freshness: "fresh" | "stale" | "unknown";
}

export interface EvidenceActivity {
  label: string;
  locator: string;
  status: ArtifactStatus;
}

export interface WorkspaceOverview {
  workspaceId: string;
  projectName: string;
  proofCasePath: string;
  entryType: EntryType;
  researchStateSentence: string;
  dataSummary: string;
  sampleVariableSummary: string;
  discoveredMaterials: string[];
  strongestAllowedClaim: ClaimStrength;
  firstFailingGate: GateSummary;
  artifacts: ArtifactSummary[];
  blockedClaims: ClaimAuditSummary[];
  numberMismatches: NumberMismatchSummary[];
  replicationReadiness: ReplicationReadinessSummary;
  resultObjects: ResultObjectSummary[];
  recentEvidenceActivity: EvidenceActivity[];
  nextAction: NextAction;
}
