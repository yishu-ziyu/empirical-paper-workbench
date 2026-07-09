import type { WorkspaceOverview } from "../types";

const nextAction = {
  label: "Confirm cluster level",
  artifactName: "SampleAudit",
  gateName: "MethodGate",
  reason:
    "Cluster level is needed before the current CGSS association can be treated as claim-ready evidence.",
  actionKind: "open_evidence_panel",
  destructive: false,
} as const;

export const cgssOverview: WorkspaceOverview = {
  workspaceId: "cgss-internet-happiness",
  projectName: "CGSS Internet and Happiness",
  proofCasePath: "/Users/mahaoxuan/Desktop/经济学论文/CGSS_Internet_Happiness/",
  entryType: "mixed_existing_workspace",
  researchStateSentence:
    "Current strongest allowed claim: descriptive. MethodGate is blocked because SampleAudit lacks cluster level and sample construction is not fully auditable.",
  dataSummary:
    "CGSS individual-level survey materials with manuscript draft, variable dictionary, tables, scripts, review report, and replication files discovered.",
  sampleVariableSummary:
    "Internet use and subjective happiness are visible in the workspace, but estimation sample restrictions and cluster level still need audit confirmation.",
  discoveredMaterials: [
    "manuscript draft",
    "variable dictionary",
    "tables",
    "figures",
    "scripts",
    "review report",
    "replication files",
  ],
  strongestAllowedClaim: "descriptive",
  firstFailingGate: {
    gateName: "MethodGate",
    status: "blocked",
    requiredArtifacts: ["SampleAudit", "MeasurementAudit", "DesignRegister", "ResultObject"],
    hardFlags: ["cluster level missing", "sample drop reasons incomplete"],
    missingArtifacts: ["SampleAudit"],
    claimConsequence:
      "Claims can describe association in the current CGSS sample, but cannot say internet use improves happiness.",
    nextAction,
    freshness: "stale",
    lastChecked: "2026-07-09",
    humanConfirmationRequired: true,
  },
  artifacts: [
    {
      artifactName: "DataContract",
      status: "draft",
      missingFields: ["access boundary confirmation", "source card citation"],
      sourceLocators: ["Data/", "docs/variable_dictionary.md"],
      canSupportClaim: false,
      claimConsequence: "Data source is visible, but downstream claims need confirmed access and citation metadata.",
      staleRisk: false,
      evidencePanelId: "artifact-data-contract",
      domainReason:
        "A CGSS claim needs wave, observation unit, population, and access boundary before the sample can be interpreted.",
      nextActionLabel: "Confirm data access boundary",
    },
    {
      artifactName: "SampleAudit",
      status: "blocked",
      missingFields: ["cluster level", "drop reasons", "estimation sample flow"],
      sourceLocators: ["Program/", "Results/"],
      canSupportClaim: false,
      claimConsequence: "Without cluster level and drop reasons, current results cannot become claim-ready evidence.",
      staleRisk: true,
      evidencePanelId: "artifact-sample-audit",
      domainReason:
        "Sample construction changes external validity and standard errors, especially when survey rows are filtered before estimation.",
      nextActionLabel: "Confirm cluster level",
    },
    {
      artifactName: "MeasurementAudit",
      status: "draft",
      missingFields: ["subjective happiness direction", "internet use construction"],
      sourceLocators: ["Data/codebook", "notes/"],
      canSupportClaim: false,
      claimConsequence: "Variable meanings are visible but not yet strong enough for causal or policy wording.",
      staleRisk: false,
      evidencePanelId: "artifact-measurement-audit",
      domainReason:
        "Subjective happiness and internet use must be mapped from survey fields before wording can safely describe direction.",
      nextActionLabel: "Confirm variable direction",
    },
    {
      artifactName: "DesignRegister",
      status: "draft",
      missingFields: ["comparison group", "claim boundary"],
      sourceLocators: ["Manuscripts/", "notes/design.md"],
      canSupportClaim: false,
      claimConsequence: "The design currently supports descriptive association, not causal effect language.",
      staleRisk: false,
      evidencePanelId: "artifact-design-register",
      domainReason:
        "A design register states estimand, comparison group, and identifying assumption before model output becomes interpretable.",
      nextActionLabel: "Lock claim boundary",
    },
    {
      artifactName: "MethodGate",
      status: "blocked",
      missingFields: ["required diagnostics", "hard flag resolution"],
      sourceLocators: ["docs/review_report.md"],
      canSupportClaim: false,
      claimConsequence: "Strongest allowed claim is descriptive until sample and design gaps are resolved.",
      staleRisk: true,
      evidencePanelId: "artifact-method-gate",
      domainReason:
        "MethodGate converts design evidence into the strongest wording the manuscript is allowed to use.",
      nextActionLabel: "Resolve first failing gate",
    },
    {
      artifactName: "ResultObject",
      status: "mismatch",
      missingFields: ["authoritative main_results.json", "SE convention"],
      sourceLocators: ["Results/tables/", "Results/main_results.json"],
      canSupportClaim: false,
      claimConsequence: "A result can be inspected, but a mismatch prevents formal claim binding.",
      staleRisk: true,
      evidencePanelId: "artifact-result-object",
      domainReason:
        "ResultObject is the source of truth for coefficients, standard errors, N, sample id, and script locator.",
      nextActionLabel: "Normalize main_results.json",
    },
    {
      artifactName: "EvidenceLedger",
      status: "draft",
      missingFields: ["Claim C-003 result binding", "robustness status"],
      sourceLocators: ["evidence/claim_register.csv"],
      canSupportClaim: false,
      claimConsequence: "Some manuscript sentences have claim IDs, but unsupported claims cannot enter formal writing.",
      staleRisk: false,
      evidencePanelId: "artifact-evidence-ledger",
      domainReason:
        "Every empirical sentence needs a claim ID connected to result, exhibit, sample, script, robustness, and citation.",
      nextActionLabel: "Bind Claim C-003",
    },
    {
      artifactName: "ClaimAudit",
      status: "blocked",
      missingFields: ["causal overreach resolution"],
      sourceLocators: ["Manuscripts/draft.md"],
      canSupportClaim: false,
      claimConsequence: "Causal wording is blocked until MethodGate allows it.",
      staleRisk: false,
      evidencePanelId: "artifact-claim-audit",
      domainReason:
        "Writing naturally strengthens claims; ClaimAudit downgrades wording that exceeds the evidence chain.",
      nextActionLabel: "Downgrade causal wording",
    },
    {
      artifactName: "ReplicationPackage",
      status: "clean_rerun_required",
      missingFields: ["clean rerun log", "manifest", "checksums"],
      sourceLocators: ["Submissions/", "output/"],
      canSupportClaim: false,
      claimConsequence: "Replication files exist, but the package cannot be presented as rebuildable.",
      staleRisk: true,
      evidencePanelId: "artifact-replication-package",
      domainReason:
        "Replication readiness depends on rebuilding outputs from scripts, not merely having a folder of files.",
      nextActionLabel: "Record clean rerun status",
    },
  ],
  blockedClaims: [
    {
      claimId: "C-003",
      sourceLocator: "Manuscripts/results_section.md#p4",
      originalText: "Internet use improves subjective happiness.",
      claimType: "causal",
      requestedStrength: "causal",
      allowedStrength: "descriptive",
      blockingReason:
        "The current design does not support causal language because MethodGate is blocked by sample and design gaps.",
      allowedWording:
        "Internet use is associated with higher subjective happiness in the current CGSS sample.",
      forbiddenWording: "Internet use improves happiness.",
      linkedGate: "MethodGate",
      linkedResultObjectId: "R-007",
      linkedExhibitId: "Table 2 Column 3",
    },
  ],
  numberMismatches: [
    {
      mismatchId: "M-001",
      claimId: "C-003",
      resultObjectId: "R-007",
      exhibitLocator: "Table 2 Column 3",
      manuscriptValue: "0.083",
      resultValue: "0.071",
      field: "effect",
      resolutionPath:
        "Claim C-003 cites 0.083, but ResultObject R-007 records 0.071. Select the authoritative ResultObject or update the claim before writing.",
    },
  ],
  replicationReadiness: {
    status: "clean_rerun_required",
    runAllPresent: true,
    environmentCaptured: false,
    logsPresent: true,
    manifestPresent: false,
    checksumsPresent: false,
    dataAvailabilityStatementPresent: true,
    tableFigureScriptMapPresent: false,
    cleanRerunStatus: "not_run",
    blockingReason:
      "Replication files exist, but Table 2 and Figure 2 have not been rebuilt from a clean derived-output state.",
  },
  resultObjects: [
    {
      resultObjectId: "R-007",
      estimand: "Descriptive association in CGSS sample",
      estimator: "OLS with controls",
      effect: "0.071",
      standardError: "0.018",
      pValue: "0.004",
      n: "19,404",
      sampleId: "S-CGSS-estimation-v1",
      clusterLevel: "missing",
      scriptLocator: "Program/main_analysis.do",
      freshness: "stale",
    },
  ],
  recentEvidenceActivity: [
    {
      label: "Variable dictionary discovered",
      locator: "docs/variable_dictionary.md",
      status: "found",
    },
    {
      label: "Claim C-003 downgraded",
      locator: "Manuscripts/results_section.md#p4",
      status: "blocked",
    },
    {
      label: "Replication manifest missing",
      locator: "Submissions/replication_package/",
      status: "clean_rerun_required",
    },
  ],
  nextAction,
};
