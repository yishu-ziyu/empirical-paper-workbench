import { useMemo, useState } from "react";
import { useWorkspaceOverview } from "../hooks/useWorkspaceOverview";
import type {
  ArtifactStatus,
  ArtifactSummary,
  ClaimAuditSummary,
  NumberMismatchSummary,
  ReplicationReadinessSummary,
  ResultObjectSummary,
  WorkspaceOverview,
} from "../types";

interface CgssGateDashboardProps {
  workspaceId: string;
}

const STATUS_LABELS: Record<ArtifactStatus, string> = {
  unknown: "unknown",
  found: "found",
  draft: "draft",
  complete: "complete",
  blocked: "blocked",
  diagnostic_only: "diagnostic_only",
  claim_ready: "claim_ready",
  stale: "stale",
  mismatch: "mismatch",
  clean: "clean",
  not_ready: "not_ready",
  clean_rerun_required: "clean_rerun_required",
};

function statusTone(status: ArtifactStatus): string {
  if (status === "blocked" || status === "not_ready" || status === "clean_rerun_required") return "danger";
  if (status === "mismatch" || status === "stale") return "warning";
  if (status === "clean" || status === "complete" || status === "claim_ready") return "clean";
  if (status === "diagnostic_only") return "diagnostic";
  return "draft";
}

function StatusPill({ status }: { status: ArtifactStatus }) {
  return (
    <span className={`epw-status epw-status--${statusTone(status)}`}>
      {STATUS_LABELS[status]}
    </span>
  );
}

function SectionHeader({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div className="epw-section-heading">
      <span>{eyebrow}</span>
      <h3>{title}</h3>
    </div>
  );
}

function GateBanner({ overview }: { overview: WorkspaceOverview }) {
  return (
    <section className="epw-gate-banner" aria-labelledby="epw-gate-title">
      <div className="epw-gate-banner__copy">
        <span className="epw-kicker">CGSS read-only Gate Dashboard</span>
        <h2 id="epw-gate-title">Current strongest allowed claim: {overview.strongestAllowedClaim}</h2>
        <p>{overview.researchStateSentence}</p>
      </div>
      <div className="epw-gate-banner__action">
        <span>One recommended next action</span>
        <button
          className="epw-primary-action"
          type="button"
          data-testid="cgss-primary-cta"
        >
          {overview.nextAction.label}
        </button>
        <p>{overview.nextAction.reason}</p>
      </div>
    </section>
  );
}

function EntryRouting({ overview }: { overview: WorkspaceOverview }) {
  return (
    <section className="epw-card epw-entry-routing">
      <SectionHeader eyebrow="Entry Routing" title="mixed existing workspace" />
      <p>{overview.dataSummary}</p>
      <code>{overview.proofCasePath}</code>
      <div className="epw-chip-list" aria-label="Discovered materials">
        {overview.discoveredMaterials.map((material) => (
          <span className="epw-chip" key={material}>{material}</span>
        ))}
      </div>
    </section>
  );
}

function ArtifactStatusGrid({
  artifacts,
  selectedArtifact,
  onSelectArtifact,
}: {
  artifacts: ArtifactSummary[];
  selectedArtifact: ArtifactSummary;
  onSelectArtifact: (artifact: ArtifactSummary) => void;
}) {
  return (
    <section className="epw-card epw-artifact-grid-card">
      <SectionHeader eyebrow="Artifact Inventory" title="9 artifact cards" />
      <div className="epw-artifact-grid">
        {artifacts.map((artifact) => (
          <button
            aria-label={`${artifact.artifactName} evidence panel`}
            className={
              artifact.artifactName === selectedArtifact.artifactName
                ? "epw-artifact-card epw-artifact-card--active"
                : "epw-artifact-card"
            }
            key={artifact.artifactName}
            onClick={() => onSelectArtifact(artifact)}
            type="button"
          >
            <span className="epw-artifact-card__name">{artifact.artifactName}</span>
            <StatusPill status={artifact.status} />
            <span className="epw-artifact-card__meta">
              {artifact.canSupportClaim ? "can support claim" : "cannot support claim"}
            </span>
            <span className="epw-artifact-card__missing">
              {artifact.missingFields.length ? artifact.missingFields.join(" · ") : "no missing fields"}
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}

function EvidencePanel({ artifact }: { artifact: ArtifactSummary }) {
  return (
    <aside className="epw-card epw-evidence-panel" data-testid="cgss-evidence-panel">
      <SectionHeader eyebrow="Evidence Panel" title={artifact.artifactName} />
      <StatusPill status={artifact.status} />
      <dl>
        <div>
          <dt>source locator</dt>
          <dd>{artifact.sourceLocators.join(" · ")}</dd>
        </div>
        <div>
          <dt>missing fields</dt>
          <dd>{artifact.missingFields.join(" · ") || "none"}</dd>
        </div>
        <div>
          <dt>why this matters</dt>
          <dd>{artifact.domainReason}</dd>
        </div>
        <div>
          <dt>claim consequence</dt>
          <dd>{artifact.claimConsequence}</dd>
        </div>
        <div>
          <dt>exact next action</dt>
          <dd>{artifact.nextActionLabel}</dd>
        </div>
      </dl>
    </aside>
  );
}

function FirstFailingGate({ overview }: { overview: WorkspaceOverview }) {
  return (
    <section className="epw-card epw-first-gate">
      <SectionHeader eyebrow="First failing gate" title={overview.firstFailingGate.gateName} />
      <StatusPill status={overview.firstFailingGate.status} />
      <p>{overview.firstFailingGate.claimConsequence}</p>
      <dl>
        <div>
          <dt>blocking reason</dt>
          <dd>{overview.firstFailingGate.hardFlags.join(" · ")}</dd>
        </div>
        <div>
          <dt>missing artifacts</dt>
          <dd>{overview.firstFailingGate.missingArtifacts.join(" · ")}</dd>
        </div>
        <div>
          <dt>next action</dt>
          <dd>{overview.firstFailingGate.nextAction.label}</dd>
        </div>
      </dl>
    </section>
  );
}

function ClaimBoundaryPanel({ overview }: { overview: WorkspaceOverview }) {
  return (
    <section className="epw-card epw-claim-boundary">
      <SectionHeader eyebrow="Strongest Allowed Claim" title={overview.strongestAllowedClaim} />
      <p>{overview.sampleVariableSummary}</p>
      <div className="epw-claim-scale" aria-label="Claim strength scale">
        {["no_claim", "exploratory", "descriptive", "qualified_causal", "causal"].map((strength) => (
          <span
            className={strength === overview.strongestAllowedClaim ? "epw-claim-scale__item epw-claim-scale__item--active" : "epw-claim-scale__item"}
            key={strength}
          >
            {strength}
          </span>
        ))}
      </div>
    </section>
  );
}

function BlockedClaimsPanel({ claims }: { claims: ClaimAuditSummary[] }) {
  return (
    <section className="epw-card epw-blocked-claims">
      <SectionHeader eyebrow="ClaimAudit Inbox" title="Blocked claims" />
      <div className="epw-list-stack">
        {claims.map((claim) => (
          <article className="epw-claim-row" key={claim.claimId}>
            <div>
              <span className="epw-mono">{claim.claimId}</span>
              <strong>{claim.originalText}</strong>
            </div>
            <p>{claim.blockingReason}</p>
            <dl>
              <div>
                <dt>allowed wording</dt>
                <dd>{claim.allowedWording}</dd>
              </div>
              <div>
                <dt>forbidden wording</dt>
                <dd>{claim.forbiddenWording}</dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
}

function NumberMismatchPanel({ mismatches }: { mismatches: NumberMismatchSummary[] }) {
  return (
    <section className="epw-card epw-number-mismatches">
      <SectionHeader eyebrow="ResultObject" title="Number mismatches" />
      {mismatches.map((mismatch) => (
        <article className="epw-mismatch-callout" key={mismatch.mismatchId}>
          <span className="epw-mono">{mismatch.claimId} · {mismatch.resultObjectId}</span>
          <strong>{mismatch.resolutionPath}</strong>
          <p>
            manuscript value <code>{mismatch.manuscriptValue}</code> conflicts with result value <code>{mismatch.resultValue}</code>
            {mismatch.exhibitLocator ? ` in ${mismatch.exhibitLocator}` : ""}.
          </p>
        </article>
      ))}
    </section>
  );
}

function ResultObjectTable({ results }: { results: ResultObjectSummary[] }) {
  return (
    <section className="epw-card epw-result-object">
      <SectionHeader eyebrow="ResultObject Viewer" title="Result facts" />
      <div className="epw-result-table" role="table" aria-label="ResultObject facts">
        <div className="epw-result-table__row epw-result-table__row--head" role="row">
          <span role="columnheader">result_id</span>
          <span role="columnheader">effect</span>
          <span role="columnheader">SE</span>
          <span role="columnheader">N</span>
          <span role="columnheader">cluster</span>
        </div>
        {results.map((result) => (
          <div className="epw-result-table__row" key={result.resultObjectId} role="row">
            <span role="cell">{result.resultObjectId}</span>
            <span role="cell">{result.effect}</span>
            <span role="cell">{result.standardError}</span>
            <span role="cell">{result.n}</span>
            <span role="cell">{result.clusterLevel}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function ReplicationReadinessPanel({ replication }: { replication: ReplicationReadinessSummary }) {
  const checks = [
    ["run_all", replication.runAllPresent],
    ["environment", replication.environmentCaptured],
    ["logs", replication.logsPresent],
    ["manifest", replication.manifestPresent],
    ["checksums", replication.checksumsPresent],
    ["DAS", replication.dataAvailabilityStatementPresent],
    ["table map", replication.tableFigureScriptMapPresent],
  ] as const;
  return (
    <section className="epw-card epw-replication">
      <SectionHeader eyebrow="Replication readiness" title={replication.status} />
      <p>{replication.blockingReason}</p>
      <div className="epw-chip-list" aria-label="Replication readiness checks">
        {checks.map(([label, present]) => (
          <span className={present ? "epw-chip epw-chip--ok" : "epw-chip epw-chip--missing"} key={label}>
            {label}: {present ? "found" : "missing"}
          </span>
        ))}
      </div>
    </section>
  );
}

function RecentEvidenceActivity({ overview }: { overview: WorkspaceOverview }) {
  return (
    <section className="epw-card epw-recent-activity">
      <SectionHeader eyebrow="EvidenceLedger" title="Recent evidence activity" />
      <div className="epw-list-stack">
        {overview.recentEvidenceActivity.map((activity) => (
          <div className="epw-activity-row" key={`${activity.label}-${activity.locator}`}>
            <StatusPill status={activity.status} />
            <span>{activity.label}</span>
            <code>{activity.locator}</code>
          </div>
        ))}
      </div>
    </section>
  );
}

export function CgssGateDashboard({ workspaceId }: CgssGateDashboardProps) {
  const overview = useWorkspaceOverview(workspaceId);
  const defaultArtifact = useMemo(
    () => overview.artifacts.find((artifact) => artifact.artifactName === "SampleAudit") ?? overview.artifacts[0],
    [overview.artifacts],
  );
  const [selectedArtifactName, setSelectedArtifactName] = useState(defaultArtifact.artifactName);
  const selectedArtifact =
    overview.artifacts.find((artifact) => artifact.artifactName === selectedArtifactName) ?? defaultArtifact;

  return (
    <section className="epw-dashboard" data-testid="cgss-gate-dashboard" aria-label="CGSS read-only Gate Dashboard">
      <GateBanner overview={overview} />
      <div className="epw-dashboard__top-grid">
        <EntryRouting overview={overview} />
        <FirstFailingGate overview={overview} />
        <ClaimBoundaryPanel overview={overview} />
      </div>
      <div className="epw-dashboard__main-grid">
        <div className="epw-dashboard__left">
          <ArtifactStatusGrid
            artifacts={overview.artifacts}
            selectedArtifact={selectedArtifact}
            onSelectArtifact={(artifact) => setSelectedArtifactName(artifact.artifactName)}
          />
          <EvidencePanel artifact={selectedArtifact} />
        </div>
        <div className="epw-dashboard__right">
          <BlockedClaimsPanel claims={overview.blockedClaims} />
          <NumberMismatchPanel mismatches={overview.numberMismatches} />
          <ResultObjectTable results={overview.resultObjects} />
        </div>
      </div>
      <div className="epw-dashboard__bottom-grid">
        <ReplicationReadinessPanel replication={overview.replicationReadiness} />
        <RecentEvidenceActivity overview={overview} />
      </div>
    </section>
  );
}
