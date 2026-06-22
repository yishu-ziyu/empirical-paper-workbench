import { useCallback, useEffect, useState } from "react";
import { RefreshCcw, ShieldCheck } from "lucide-react";
import { apiUrl } from "../lib/apiBase";

interface ProductControlP0Project {
  id?: string;
  title?: string;
  project_root?: string;
}

interface ProductControlP0TopicBinding {
  expected_topic?: string;
  topic?: string;
}

interface ProductControlP0AgentTask {
  id?: string;
  role?: string;
  task?: string;
  status?: string;
  can_execute?: boolean;
  next_action?: string;
}

interface ProductControlP0EvidenceCheck {
  id?: string;
  label?: string;
  description?: string;
  status?: string;
  need?: string;
}

interface ProductControlP0Report {
  status: string;
  project?: ProductControlP0Project;
  topic_binding?: ProductControlP0TopicBinding;
  summary?: {
    task_count?: number;
    evidence_audit_status?: string;
    portfolio_status?: string;
  };
  agent_tasks?: ProductControlP0AgentTask[];
  evidence_checks?: ProductControlP0EvidenceCheck[];
  formal_boundary?: string;
  portfolio_script_path?: string;
  can_refresh?: boolean;
  next_action?: string;
}

interface ProductControlP1LiteratureReport {
  status: string;
  verified_count?: number;
  candidate_topics?: Array<{ id?: string; query_seed?: string; review_status?: string }>;
  blocking_reasons?: string[];
  product_control_signal?: {
    phase?: string;
    label?: string;
    status?: string;
    next_action?: string;
  };
  can_refresh?: boolean;
  next_action?: string;
}

interface ProductControlP1DataFieldReport {
  status: string;
  candidate_variable_count?: number;
  matched_fields?: Array<{ dataset_column?: string; binding_status?: string }>;
  missing_fields?: Array<{ dataset_column?: string; binding_status?: string }>;
  blocking_reasons?: string[];
  product_control_signal?: {
    phase?: string;
    label?: string;
    status?: string;
    next_action?: string;
  };
  can_refresh?: boolean;
  next_action?: string;
}

interface ProductControlP1MethodReport {
  status: string;
  execution_allowed?: boolean;
  run_id?: string | null;
  method_candidates?: Array<{ method?: string; status?: string }>;
  missing_required_fields?: string[];
  product_control_signal?: {
    phase?: string;
    label?: string;
    status?: string;
    next_action?: string;
  };
  can_refresh?: boolean;
  next_action?: string;
}

interface ProductControlP2ReadinessReport {
  status: string;
  execution_preflight_allowed?: boolean;
  run_id?: string | null;
  field_supplementation?: Array<{ dataset_column?: string; supplement_status?: string }>;
  blocking_reasons?: string[];
  product_control_signal?: {
    phase?: string;
    label?: string;
    status?: string;
    next_action?: string;
  };
  can_refresh?: boolean;
  next_action?: string;
}

interface ProductControlP3DraftPackageReport {
  status: string;
  draft_kind?: string;
  full_draft_ready?: boolean;
  issue_count?: number;
  outputs?: {
    docx?: string;
    markdown?: string;
    issue_list?: string;
    audit_report?: string;
  };
  product_control_signal?: {
    phase?: string;
    label?: string;
    status?: string;
    primary_artifact?: string;
    next_action?: string;
  };
  can_refresh?: boolean;
  next_action?: string;
}

interface ProductControlP4FieldSourceReport {
  status: string;
  candidate_count?: number;
  source_roots?: {
    selected_root?: string | null;
    scanned_file_count?: number;
    stale_source_paths?: string[];
  };
  field_source_candidates?: Array<{
    dataset_column?: string;
    candidate_status?: string;
    candidates?: Array<{ name?: string; label?: string; source_path?: string }>;
  }>;
  product_control_signal?: {
    phase?: string;
    label?: string;
    status?: string;
    next_action?: string;
  };
  can_refresh?: boolean;
  next_action?: string;
}

interface ProductControlP5VariableRolePreflightReport {
  status: string;
  can_write_formal_variable_roles?: boolean;
  draft_variable_roles?: {
    outcome?: { preferred?: string };
    treatment?: {
      preferred?: string;
      construction?: { decision_status?: string; recommended_default?: string };
    };
    controls?: { preferred?: string[] };
  };
  role_bindings?: Array<{
    dataset_column?: string;
    binding_status?: string;
    preferred_candidate?: { name?: string; label?: string; source_path?: string } | null;
  }>;
  product_control_signal?: {
    phase?: string;
    label?: string;
    status?: string;
    next_action?: string;
  };
  can_refresh?: boolean;
  next_action?: string;
}

interface ProductControlP6VariableRoleSignoffReport {
  status: string;
  can_write_editable_draft?: boolean;
  can_write_formal_variable_roles?: boolean;
  required_decisions?: string[];
  recommended_decisions?: Partial<Record<VariableRoleDecisionId, string>>;
  decisions?: Partial<Record<VariableRoleDecisionId, string>>;
  missing_decisions?: string[];
  draft_preview?: {
    outcome?: string;
    treatment?: string;
    parent_education_construction?: string;
    controls?: string[];
    formal_write?: boolean;
  };
  promotion_targets?: Array<{ id?: string; allowed_now?: boolean }>;
  variable_role_set_draft?: {
    id?: string;
    write_boundary?: string;
  };
  product_control_signal?: {
    phase?: string;
    label?: string;
    status?: string;
    next_action?: string;
  };
  can_refresh?: boolean;
  next_action?: string;
}

interface ProductControlP8VariableRoleApprovalReport {
  status: string;
  can_approve_formal_variable_roles?: boolean;
  can_write_formal_variable_roles?: boolean;
  required_confirmations?: string[];
  latest_draft?: {
    id?: string;
    roles?: {
      outcome?: string[];
      treatment?: string[];
      controls?: string[];
    };
  } | null;
  approval?: {
    status?: string;
    reviewer?: string;
    source_draft_id?: string;
  } | null;
  missing_approval_fields?: string[];
  product_control_signal?: {
    phase?: string;
    label?: string;
    status?: string;
    next_action?: string;
  };
  blocking_reasons?: string[];
  next_action?: string;
}

interface ProductControlP9FormalSaveReport {
  status: string;
  can_save_formal_variable_roles?: boolean;
  can_enter_design_spec_preflight?: boolean;
  can_create_run_id?: boolean;
  can_execute_model?: boolean;
  save_confirmation?: string;
  latest_draft?: {
    id?: string;
    roles?: {
      outcome?: string[];
      treatment?: string[];
      controls?: string[];
    };
  } | null;
  approved_roles?: {
    outcome?: string[];
    treatment?: string[];
    controls?: string[];
  };
  source_contract?: {
    dataset_path?: string;
    dataset_name?: string;
    review?: {
      reviewer?: string;
      note?: string;
      confirmation?: string;
    };
  } | null;
  missing_source_metadata_fields?: string[];
  variable_role_set?: {
    version?: number;
    dataset_path?: string;
  };
  product_control_signal?: {
    phase?: string;
    label?: string;
    status?: string;
    next_action?: string;
  };
  blocking_reasons?: string[];
  next_action?: string;
}

interface ProductControlP11SourceMetadataReport {
  status: string;
  save_confirmation?: string;
  can_return_to_p9_formal_save?: boolean;
  can_save_formal_variable_roles?: boolean;
  can_enter_design_spec_preflight?: boolean;
  can_create_run_id?: boolean;
  can_execute_model?: boolean;
  latest_draft?: {
    id?: string;
  } | null;
  required_source_fields?: string[];
  missing_source_metadata_fields?: string[];
  source_contract?: {
    dataset_path?: string;
    dataset_name?: string;
  } | null;
  field_bindings?: Record<string, Record<string, string>>;
  suggested_field_bindings?: Record<string, Record<string, string>>;
  derived_variables?: Record<string, { source_fields?: string[]; construction?: string }>;
  source_contract_review_kit?: {
    status?: string;
    recommended_dataset_path?: string;
    dataset_path_candidates?: string[];
    recommended_parent_education_construction?: string;
    can_save_without_human_review?: boolean;
    can_execute_model?: boolean;
    field_review_items?: Array<{
      field?: string;
      review_status?: string;
      is_missing?: boolean;
      recommended_source?: {
        name?: string;
        label?: string;
        source_path?: string;
        evidence_level?: string;
      } | null;
    }>;
  };
  product_control_signal?: {
    phase?: string;
    label?: string;
    status?: string;
    next_action?: string;
  };
  p9_status_after_update?: string;
}

interface ProductControlP17DataRepairPreflightReport {
  status: string;
  artifact_exists?: boolean;
  missing_fields?: string[];
  source_root?: string | null;
  recommended_parent_education_source?: string | null;
  recommended_parent_education_construction?: string;
  suggested_repaired_dataset_path?: string;
  can_modify_final_dataset?: boolean;
  can_create_run_id?: boolean;
  can_execute_model?: boolean;
  parent_education_candidates?: Array<{
    id?: string;
    status?: string;
    parent_constructable_rows?: number;
    target_rows?: number;
    parent_constructable_rate?: number;
  }>;
  experience_candidate?: {
    status?: string;
    formula?: string;
    candidate_usable_rows?: number;
    target_rows?: number;
    requires_education_years_mapping?: boolean;
    review_note?: string;
  };
  product_control_signal?: {
    phase?: string;
    label?: string;
    status?: string;
    next_action?: string;
  };
  next_action?: string;
}

interface ProductControlP0PanelProps {
  projectId: string;
}

type LoadState = "idle" | "loading" | "ready" | "failed" | "refreshing";
type VariableRoleDecisionId =
  | "confirm_preferred_cfps_wave"
  | "confirm_parent_education_construction"
  | "confirm_hukou_role"
  | "confirm_outcome_and_controls"
  | "approve_before_formal_variable_roles_write";

const P6_SIGNOFF_DECISION_ORDER: VariableRoleDecisionId[] = [
  "confirm_preferred_cfps_wave",
  "confirm_parent_education_construction",
  "confirm_hukou_role",
  "confirm_outcome_and_controls",
  "approve_before_formal_variable_roles_write",
];

const P6_SIGNOFF_DECISION_LABELS: Record<VariableRoleDecisionId, string> = {
  confirm_preferred_cfps_wave: "CFPS 来源",
  confirm_parent_education_construction: "父母教育口径",
  confirm_hukou_role: "hukou 角色",
  confirm_outcome_and_controls: "outcome / controls",
  approve_before_formal_variable_roles_write: "写回边界",
};

const P6_FALLBACK_DECISIONS: Record<VariableRoleDecisionId, string> = {
  confirm_preferred_cfps_wave: "confirmed_current_p4_sources",
  confirm_parent_education_construction: "max(father_education, mother_education)",
  confirm_hukou_role: "control_or_heterogeneity_candidate",
  confirm_outcome_and_controls: "ln_wage_with_age_female_urban_edu_last_experience",
  approve_before_formal_variable_roles_write: "draft_only_no_formal_write",
};

interface P8ApprovalForm {
  reviewer: string;
  note: string;
  confirmation: string;
}

interface P9FormalSaveForm {
  reviewer: string;
  note: string;
  confirmation: string;
}

interface P11SourceFieldFormRow {
  field: string;
  datasetColumn: string;
  sourceField: string;
  sourcePath: string;
  evidenceLevel: string;
  confirmed: boolean;
}

type P11SourceFieldTextKey = "datasetColumn" | "sourceField" | "sourcePath" | "evidenceLevel";
type P11SourceRowReviewStatus = "needs_human_confirmation" | "ready_for_human_confirmation" | "confirmed_source_row";

interface P11SourceMetadataForm {
  reviewer: string;
  note: string;
  confirmation: string;
  datasetPath: string;
  sourceFieldRows: P11SourceFieldFormRow[];
  fieldBindingsJson: string;
  parentEducationConstruction: string;
}

interface P11SourceRowReviewItem {
  field: string;
  status: P11SourceRowReviewStatus;
  missingItems: string[];
  action: string;
}

const P8_APPROVAL_CONFIRMATION = "approve_formal_variable_roles_after_review";
const P8_APPROVAL_DEFAULTS: P8ApprovalForm = {
  reviewer: "",
  note: "",
  confirmation: P8_APPROVAL_CONFIRMATION,
};
const P9_FORMAL_SAVE_CONFIRMATION = "save_formal_variable_roles_from_p8_approved_draft";
const P9_FORMAL_SAVE_DEFAULTS: P9FormalSaveForm = {
  reviewer: "",
  note: "",
  confirmation: P9_FORMAL_SAVE_CONFIRMATION,
};
const P11_SOURCE_METADATA_CONFIRMATION = "save_source_metadata_contract_for_p9_formal_save";
const P11_SOURCE_METADATA_DEFAULTS: P11SourceMetadataForm = {
  reviewer: "",
  note: "",
  confirmation: P11_SOURCE_METADATA_CONFIRMATION,
  datasetPath: "",
  sourceFieldRows: [],
  fieldBindingsJson: "{}",
  parentEducationConstruction: "max(father_education, mother_education)",
};

const NEED_LABELS: Record<string, string> = {
  real_literature_candidates: "真实文献",
  real_data_variable_binding: "数据与变量",
  method_execution_evidence: "方法执行",
};

function statusLabel(status: string): string {
  if (status === "p0_phase_ready_for_review") return "待派工审阅";
  if (status === "p0_phase_report_missing") return "等待刷新阶段包";
  if (status === "blocked_by_topic_binding_audit") return "题目绑定阻断";
  return status || "未读取";
}

function topicLabel(report: ProductControlP0Report | null): string {
  return (
    report?.topic_binding?.expected_topic ||
    report?.topic_binding?.topic ||
    report?.project?.title ||
    "当前研究项目"
  );
}

function evidenceNeedLabel(check: ProductControlP0EvidenceCheck): string {
  const raw = check.id || check.need || check.label || check.description || "";
  return NEED_LABELS[raw] || check.label || check.description || raw || "needs_evidence";
}

function userFieldLabel(field: string): string {
  if (field === "parent_education") return "父母教育信息";
  if (field === "experience") return "工作经验";
  if (field === "ln_wage") return "工资收入";
  if (field === "edu_last") return "本人教育年限";
  if (field === "age") return "年龄";
  if (field === "female") return "性别";
  if (field === "urban") return "城乡信息";
  return field.replace(/_/g, " ");
}

function isNeedsEvidence(check: ProductControlP0EvidenceCheck): boolean {
  const status = String(check.status || "").toLowerCase();
  const serialized = JSON.stringify(check).toLowerCase();
  return status.includes("need") || serialized.includes("needs_evidence");
}

function p6SignoffDecisionDefaults(
  report: ProductControlP6VariableRoleSignoffReport | null,
): Record<VariableRoleDecisionId, string> {
  const source = report?.decisions || report?.recommended_decisions || {};
  return {
    ...P6_FALLBACK_DECISIONS,
    ...Object.fromEntries(
      P6_SIGNOFF_DECISION_ORDER.map((id) => [id, String(source[id] || P6_FALLBACK_DECISIONS[id])]),
    ),
  } as Record<VariableRoleDecisionId, string>;
}

function p11FieldBindingsJson(report: ProductControlP11SourceMetadataReport | null): string {
  const bindings = report?.field_bindings && Object.keys(report.field_bindings).length
    ? report.field_bindings
    : report?.suggested_field_bindings || {};
  return JSON.stringify(bindings, null, 2);
}

function p11DatasetPathDefault(report: ProductControlP11SourceMetadataReport | null): string {
  return (
    report?.source_contract?.dataset_path ||
    report?.source_contract_review_kit?.recommended_dataset_path ||
    report?.source_contract_review_kit?.dataset_path_candidates?.[0] ||
    ""
  );
}

function p11ParentEducationConstructionDefault(report: ProductControlP11SourceMetadataReport | null): string {
  return (
    report?.derived_variables?.parent_education?.construction ||
    report?.source_contract_review_kit?.recommended_parent_education_construction ||
    P11_SOURCE_METADATA_DEFAULTS.parentEducationConstruction
  );
}

function p11SourceFieldRows(report: ProductControlP11SourceMetadataReport | null): P11SourceFieldFormRow[] {
  const bindings = report?.field_bindings && Object.keys(report.field_bindings).length
    ? report.field_bindings
    : report?.suggested_field_bindings || {};
  const sourceContractSaved = report?.status === "source_metadata_contract_ready_for_p9_save";
  const reviewItems = report?.source_contract_review_kit?.field_review_items || [];
  const reviewItemByField = new Map(reviewItems.map((item) => [item.field || "", item]));
  const fields = Array.from(
    new Set([
      ...(report?.required_source_fields || []),
      ...reviewItems.map((item) => item.field || "").filter(Boolean),
      ...Object.keys(bindings),
    ]),
  );
  const datasetPath = p11DatasetPathDefault(report);

  return fields.map((field) => {
    const binding = bindings[field] || {};
    const recommendedSource = reviewItemByField.get(field)?.recommended_source;
    const sourcePath = binding.source_path || recommendedSource?.source_path || datasetPath;
    return {
      field,
      datasetColumn: binding.dataset_column || recommendedSource?.name || field,
      sourceField: binding.source_field || recommendedSource?.name || field,
      sourcePath,
      evidenceLevel: binding.evidence_level || recommendedSource?.evidence_level || (sourcePath ? "local_file" : ""),
      confirmed: sourceContractSaved,
    };
  });
}

function p11FieldBindingsFromRows(
  rows: P11SourceFieldFormRow[],
  fallbackJson: string,
): Record<string, Record<string, string>> {
  if (!rows.length) {
    return JSON.parse(fallbackJson || "{}") as Record<string, Record<string, string>>;
  }
  return Object.fromEntries(
    rows
      .filter((row) => row.field.trim())
      .map((row) => {
        const field = row.field.trim();
        return [
          field,
          {
            dataset_column: row.datasetColumn.trim() || field,
            source_field: row.sourceField.trim() || row.datasetColumn.trim() || field,
            source_path: row.sourcePath.trim(),
            evidence_level: row.evidenceLevel.trim(),
          },
        ];
      }),
  );
}

function p11FieldBindingsJsonFromRows(rows: P11SourceFieldFormRow[]): string {
  return JSON.stringify(p11FieldBindingsFromRows(rows, "{}"), null, 2);
}

function p11SourceContractMissingItems(form: P11SourceMetadataForm): string[] {
  const missing: string[] = [];
  if (!form.datasetPath.trim()) missing.push("dataset_path");
  if (!form.reviewer.trim()) missing.push("reviewer");
  if (!form.note.trim()) missing.push("note");
  if (form.confirmation.trim() !== P11_SOURCE_METADATA_CONFIRMATION) missing.push("confirmation");
  if (!form.parentEducationConstruction.trim()) missing.push("parent_education_construction");
  if (!form.sourceFieldRows.length) missing.push("source_field_rows");

  form.sourceFieldRows.forEach((row) => {
    const field = row.field.trim() || "field";
    if (!row.datasetColumn.trim()) missing.push(`${field}:dataset_column`);
    if (!row.sourceField.trim()) missing.push(`${field}:source_field`);
    if (!row.sourcePath.trim()) missing.push(`${field}:source_path`);
    if (!row.evidenceLevel.trim()) missing.push(`${field}:evidence_level`);
    if (!row.confirmed) missing.push(`${field}:human_confirmation`);
  });

  return missing;
}

function p11SourceRowMissingItems(row: P11SourceFieldFormRow): string[] {
  const missing: string[] = [];
  if (!row.datasetColumn.trim()) missing.push("dataset_column");
  if (!row.sourceField.trim()) missing.push("source_field");
  if (!row.sourcePath.trim()) missing.push("source_path");
  if (!row.evidenceLevel.trim()) missing.push("evidence_level");
  if (!row.confirmed) missing.push("human_confirmation");
  return missing;
}

function p11SourceRowReviewStatus(row: P11SourceFieldFormRow, missingItems: string[]): P11SourceRowReviewStatus {
  if (row.confirmed && missingItems.length === 0) return "confirmed_source_row";
  if (missingItems.length === 1 && missingItems[0] === "human_confirmation") return "ready_for_human_confirmation";
  return "needs_human_confirmation";
}

function p11SourceRowReviewAction(status: P11SourceRowReviewStatus, missingItems: string[]): string {
  if (status === "confirmed_source_row") return "已确认，可进入 source contract 保存前检查";
  if (status === "ready_for_human_confirmation") return "检查字段来源后勾选 human confirmation";
  return `先补齐：${missingItems.join("、") || "source metadata"}`;
}

function buildP11SourceRowReviewItems(rows: P11SourceFieldFormRow[]): P11SourceRowReviewItem[] {
  return rows.map((row) => {
    const missingItems = p11SourceRowMissingItems(row);
    const status = p11SourceRowReviewStatus(row, missingItems);
    return {
      field: row.field || "field",
      status,
      missingItems,
      action: p11SourceRowReviewAction(status, missingItems),
    };
  });
}

async function requestProductControlP0(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p0-phase`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p0_get_failed");
  }
  return (await response.json()) as ProductControlP0Report;
}

async function refreshProductControlP0(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p0-phase`), {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("product_control_p0_post_failed");
  }
  return (await response.json()) as ProductControlP0Report;
}

async function requestProductControlP1Literature(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p1-literature-ledger`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p1_literature_get_failed");
  }
  return (await response.json()) as ProductControlP1LiteratureReport;
}

async function refreshProductControlP1Literature(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p1-literature-ledger`), {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("product_control_p1_literature_post_failed");
  }
  return (await response.json()) as ProductControlP1LiteratureReport;
}

async function requestProductControlP1DataField(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p1-data-field-binding`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p1_data_field_get_failed");
  }
  return (await response.json()) as ProductControlP1DataFieldReport;
}

async function refreshProductControlP1DataField(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p1-data-field-binding`), {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("product_control_p1_data_field_post_failed");
  }
  return (await response.json()) as ProductControlP1DataFieldReport;
}

async function requestProductControlP1Method(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p1-method-execution`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p1_method_get_failed");
  }
  return (await response.json()) as ProductControlP1MethodReport;
}

async function refreshProductControlP1Method(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p1-method-execution`), {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("product_control_p1_method_post_failed");
  }
  return (await response.json()) as ProductControlP1MethodReport;
}

async function requestProductControlP2Readiness(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p2-execution-readiness`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p2_execution_readiness_get_failed");
  }
  return (await response.json()) as ProductControlP2ReadinessReport;
}

async function refreshProductControlP2Readiness(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p2-execution-readiness`), {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("product_control_p2_execution_readiness_post_failed");
  }
  return (await response.json()) as ProductControlP2ReadinessReport;
}

async function requestProductControlP3DraftPackage(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p3-draft-package`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p3_draft_package_get_failed");
  }
  return (await response.json()) as ProductControlP3DraftPackageReport;
}

async function refreshProductControlP3DraftPackage(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p3-draft-package`), {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("product_control_p3_draft_package_post_failed");
  }
  return (await response.json()) as ProductControlP3DraftPackageReport;
}

async function requestProductControlP4FieldSource(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p4-field-source-candidates`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p4_field_source_get_failed");
  }
  return (await response.json()) as ProductControlP4FieldSourceReport;
}

async function refreshProductControlP4FieldSource(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p4-field-source-candidates`), {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("product_control_p4_field_source_post_failed");
  }
  return (await response.json()) as ProductControlP4FieldSourceReport;
}

async function requestProductControlP5VariableRolePreflight(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p5-variable-role-preflight`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p5_variable_role_preflight_get_failed");
  }
  return (await response.json()) as ProductControlP5VariableRolePreflightReport;
}

async function refreshProductControlP5VariableRolePreflight(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p5-variable-role-preflight`), {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("product_control_p5_variable_role_preflight_post_failed");
  }
  return (await response.json()) as ProductControlP5VariableRolePreflightReport;
}

async function requestProductControlP6VariableRoleSignoff(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p6-variable-role-signoff`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p6_variable_role_signoff_get_failed");
  }
  return (await response.json()) as ProductControlP6VariableRoleSignoffReport;
}

async function refreshProductControlP6VariableRoleSignoff(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p6-variable-role-signoff`), {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("product_control_p6_variable_role_signoff_post_failed");
  }
  return (await response.json()) as ProductControlP6VariableRoleSignoffReport;
}

async function promoteProductControlP6VariableRoleSignoff(
  projectId: string,
  decisions: Record<VariableRoleDecisionId, string>,
) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p6-variable-role-signoff/promote`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      promotion_target: "editable_draft",
      allow_formal_write: false,
      decisions,
      note: "P7 页面签收：只生成可编辑草稿，不写正式 VariableRoleSet，不跑模型。",
    }),
  });
  const body = (await response.json()) as ProductControlP6VariableRoleSignoffReport;
  if (!response.ok) {
    throw new Error(body.status || "product_control_p6_variable_role_signoff_promote_failed");
  }
  return body;
}

async function requestProductControlP8VariableRoleApproval(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p8-variable-role-approval`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p8_variable_role_approval_get_failed");
  }
  return (await response.json()) as ProductControlP8VariableRoleApprovalReport;
}

async function approveProductControlP8VariableRoleApproval(projectId: string, form: P8ApprovalForm) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p8-variable-role-approval`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      decision: "approve_formal_variable_roles",
      reviewer: form.reviewer,
      note: form.note,
      confirmation: form.confirmation,
    }),
  });
  const body = (await response.json()) as ProductControlP8VariableRoleApprovalReport;
  if (!response.ok) {
    throw new Error(body.status || "product_control_p8_variable_role_approval_failed");
  }
  return body;
}

async function requestProductControlP9FormalVariableRoles(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p9-variable-role-formal-save`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p9_formal_variable_roles_get_failed");
  }
  return (await response.json()) as ProductControlP9FormalSaveReport;
}

async function saveProductControlP9FormalVariableRoles(
  projectId: string,
  report: ProductControlP9FormalSaveReport,
  form: P9FormalSaveForm,
) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p9-variable-role-formal-save`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      decision: "save_formal_variable_roles",
      reviewer: form.reviewer,
      note: form.note,
      confirmation: form.confirmation,
      source_draft_id: report.latest_draft?.id || "",
      dataset_path: report.source_contract?.dataset_path || "",
      roles: report.approved_roles || report.latest_draft?.roles || {},
    }),
  });
  const body = (await response.json()) as ProductControlP9FormalSaveReport;
  if (!response.ok) {
    const details = [
      body.blocking_reasons?.join(", "),
      body.missing_source_metadata_fields?.join(", "),
    ]
      .filter(Boolean)
      .join("；");
    throw new Error(
      `${body.status || "product_control_p9_formal_variable_roles_save_failed"}${details ? `：${details}` : ""}`,
    );
  }
  return body;
}

async function requestProductControlP11SourceMetadataContract(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p11-source-metadata-contract`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p11_source_metadata_contract_get_failed");
  }
  return (await response.json()) as ProductControlP11SourceMetadataReport;
}

async function saveProductControlP11SourceMetadataContract(
  projectId: string,
  form: P11SourceMetadataForm,
) {
  let field_bindings: Record<string, Record<string, string>>;
  try {
    field_bindings = p11FieldBindingsFromRows(form.sourceFieldRows, form.fieldBindingsJson);
  } catch {
    throw new Error("field_bindings JSON 格式无效");
  }
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p11-source-metadata-contract`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      decision: "save_source_metadata_contract",
      reviewer: form.reviewer,
      note: form.note,
      confirmation: form.confirmation,
      dataset_path: form.datasetPath,
      field_bindings,
      derived_variables: {
        parent_education: {
          source_fields: ["father_education", "mother_education"],
          construction: form.parentEducationConstruction,
        },
      },
    }),
  });
  const body = (await response.json()) as ProductControlP11SourceMetadataReport;
  if (!response.ok) {
    throw new Error(
      `${body.status || "product_control_p11_source_metadata_contract_save_failed"}：${body.missing_source_metadata_fields?.join(", ") || "source metadata incomplete"}`,
    );
  }
  return body;
}

async function requestProductControlP17DataRepairPreflight(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p17-data-repair-preflight`), {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("product_control_p17_data_repair_preflight_get_failed");
  }
  return (await response.json()) as ProductControlP17DataRepairPreflightReport;
}

async function refreshProductControlP17DataRepairPreflight(projectId: string) {
  const response = await fetch(apiUrl(`/api/v1/projects/${projectId}/product-control/p17-data-repair-preflight`), {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("product_control_p17_data_repair_preflight_post_failed");
  }
  return (await response.json()) as ProductControlP17DataRepairPreflightReport;
}

export function ProductControlP0Panel({ projectId }: ProductControlP0PanelProps) {
  const [report, setReport] = useState<ProductControlP0Report | null>(null);
  const [literatureReport, setLiteratureReport] = useState<ProductControlP1LiteratureReport | null>(null);
  const [dataFieldReport, setDataFieldReport] = useState<ProductControlP1DataFieldReport | null>(null);
  const [methodReport, setMethodReport] = useState<ProductControlP1MethodReport | null>(null);
  const [readinessReport, setReadinessReport] = useState<ProductControlP2ReadinessReport | null>(null);
  const [draftPackageReport, setDraftPackageReport] = useState<ProductControlP3DraftPackageReport | null>(null);
  const [fieldSourceReport, setFieldSourceReport] = useState<ProductControlP4FieldSourceReport | null>(null);
  const [variableRolePreflightReport, setVariableRolePreflightReport] =
    useState<ProductControlP5VariableRolePreflightReport | null>(null);
  const [variableRoleSignoffReport, setVariableRoleSignoffReport] =
    useState<ProductControlP6VariableRoleSignoffReport | null>(null);
  const [variableRoleApprovalReport, setVariableRoleApprovalReport] =
    useState<ProductControlP8VariableRoleApprovalReport | null>(null);
  const [formalVariableRoleSaveReport, setFormalVariableRoleSaveReport] =
    useState<ProductControlP9FormalSaveReport | null>(null);
  const [sourceMetadataReport, setSourceMetadataReport] = useState<ProductControlP11SourceMetadataReport | null>(null);
  const [dataRepairPreflightReport, setDataRepairPreflightReport] =
    useState<ProductControlP17DataRepairPreflightReport | null>(null);
  const [state, setState] = useState<LoadState>("idle");
  const [literatureState, setLiteratureState] = useState<LoadState>("idle");
  const [dataFieldState, setDataFieldState] = useState<LoadState>("idle");
  const [methodState, setMethodState] = useState<LoadState>("idle");
  const [readinessState, setReadinessState] = useState<LoadState>("idle");
  const [draftPackageState, setDraftPackageState] = useState<LoadState>("idle");
  const [fieldSourceState, setFieldSourceState] = useState<LoadState>("idle");
  const [variableRolePreflightState, setVariableRolePreflightState] = useState<LoadState>("idle");
  const [variableRoleSignoffState, setVariableRoleSignoffState] = useState<LoadState>("idle");
  const [variableRoleSignoffPromotionState, setVariableRoleSignoffPromotionState] = useState<LoadState>("idle");
  const [variableRoleApprovalState, setVariableRoleApprovalState] = useState<LoadState>("idle");
  const [variableRoleApprovalSubmitState, setVariableRoleApprovalSubmitState] = useState<LoadState>("idle");
  const [formalVariableRoleSaveState, setFormalVariableRoleSaveState] = useState<LoadState>("idle");
  const [formalVariableRoleSaveSubmitState, setFormalVariableRoleSaveSubmitState] = useState<LoadState>("idle");
  const [sourceMetadataState, setSourceMetadataState] = useState<LoadState>("idle");
  const [sourceMetadataSubmitState, setSourceMetadataSubmitState] = useState<LoadState>("idle");
  const [dataRepairPreflightState, setDataRepairPreflightState] = useState<LoadState>("idle");
  const [variableRoleSignoffDecisions, setVariableRoleSignoffDecisions] =
    useState<Record<VariableRoleDecisionId, string>>(P6_FALLBACK_DECISIONS);
  const [variableRoleApprovalForm, setVariableRoleApprovalForm] = useState<P8ApprovalForm>(P8_APPROVAL_DEFAULTS);
  const [formalVariableRoleSaveForm, setFormalVariableRoleSaveForm] =
    useState<P9FormalSaveForm>(P9_FORMAL_SAVE_DEFAULTS);
  const [sourceMetadataForm, setSourceMetadataForm] = useState<P11SourceMetadataForm>(P11_SOURCE_METADATA_DEFAULTS);
  const [error, setError] = useState<string | null>(null);
  const [literatureError, setLiteratureError] = useState<string | null>(null);
  const [dataFieldError, setDataFieldError] = useState<string | null>(null);
  const [methodError, setMethodError] = useState<string | null>(null);
  const [readinessError, setReadinessError] = useState<string | null>(null);
  const [draftPackageError, setDraftPackageError] = useState<string | null>(null);
  const [fieldSourceError, setFieldSourceError] = useState<string | null>(null);
  const [variableRolePreflightError, setVariableRolePreflightError] = useState<string | null>(null);
  const [variableRoleSignoffError, setVariableRoleSignoffError] = useState<string | null>(null);
  const [variableRoleSignoffPromotionMessage, setVariableRoleSignoffPromotionMessage] = useState<string | null>(null);
  const [variableRoleApprovalError, setVariableRoleApprovalError] = useState<string | null>(null);
  const [variableRoleApprovalMessage, setVariableRoleApprovalMessage] = useState<string | null>(null);
  const [formalVariableRoleSaveError, setFormalVariableRoleSaveError] = useState<string | null>(null);
  const [formalVariableRoleSaveMessage, setFormalVariableRoleSaveMessage] = useState<string | null>(null);
  const [sourceMetadataError, setSourceMetadataError] = useState<string | null>(null);
  const [sourceMetadataMessage, setSourceMetadataMessage] = useState<string | null>(null);
  const [dataRepairPreflightError, setDataRepairPreflightError] = useState<string | null>(null);

  const loadProductControlP0 = useCallback(async () => {
    if (!projectId) return;
    setState("loading");
    setError(null);
    try {
      setReport(await requestProductControlP0(projectId));
      setState("ready");
    } catch {
      setError("产品控制状态未读取。请确认当前项目已登记到本地 Product API。");
      setState("failed");
    }
  }, [projectId]);

  const loadProductControlP1Method = useCallback(async () => {
    if (!projectId) return;
    setMethodState("loading");
    setMethodError(null);
    try {
      setMethodReport(await requestProductControlP1Method(projectId));
      setMethodState("ready");
    } catch {
      setMethodError("P1-C 方法执行状态未读取。");
      setMethodState("failed");
    }
  }, [projectId]);

  const handleRefreshProductControlP1Method = useCallback(async () => {
    if (!projectId) return;
    setMethodState("refreshing");
    setMethodError(null);
    try {
      setMethodReport(await refreshProductControlP1Method(projectId));
      setMethodState("ready");
    } catch {
      setMethodError("P1-C 方法执行账本刷新失败。");
      setMethodState("failed");
    }
  }, [projectId]);

  const loadProductControlP2Readiness = useCallback(async () => {
    if (!projectId) return;
    setReadinessState("loading");
    setReadinessError(null);
    try {
      setReadinessReport(await requestProductControlP2Readiness(projectId));
      setReadinessState("ready");
    } catch {
      setReadinessError("P2 执行准入状态未读取。");
      setReadinessState("failed");
    }
  }, [projectId]);

  const handleRefreshProductControlP2Readiness = useCallback(async () => {
    if (!projectId) return;
    setReadinessState("refreshing");
    setReadinessError(null);
    try {
      setReadinessReport(await refreshProductControlP2Readiness(projectId));
      setReadinessState("ready");
    } catch {
      setReadinessError("P2 执行准入账本刷新失败。");
      setReadinessState("failed");
    }
  }, [projectId]);

  const loadProductControlP3DraftPackage = useCallback(async () => {
    if (!projectId) return;
    setDraftPackageState("loading");
    setDraftPackageError(null);
    try {
      setDraftPackageReport(await requestProductControlP3DraftPackage(projectId));
      setDraftPackageState("ready");
    } catch {
      setDraftPackageError("P3 DraftPackage 状态未读取。");
      setDraftPackageState("failed");
    }
  }, [projectId]);

  const handleRefreshProductControlP3DraftPackage = useCallback(async () => {
    if (!projectId) return;
    setDraftPackageState("refreshing");
    setDraftPackageError(null);
    try {
      setDraftPackageReport(await refreshProductControlP3DraftPackage(projectId));
      setDraftPackageState("ready");
    } catch {
      setDraftPackageError("P3 DraftPackage 刷新失败。");
      setDraftPackageState("failed");
    }
  }, [projectId]);

  const loadProductControlP4FieldSource = useCallback(async () => {
    if (!projectId) return;
    setFieldSourceState("loading");
    setFieldSourceError(null);
    try {
      setFieldSourceReport(await requestProductControlP4FieldSource(projectId));
      setFieldSourceState("ready");
    } catch {
      setFieldSourceError("P4 字段来源状态未读取。");
      setFieldSourceState("failed");
    }
  }, [projectId]);

  const handleRefreshProductControlP4FieldSource = useCallback(async () => {
    if (!projectId) return;
    setFieldSourceState("refreshing");
    setFieldSourceError(null);
    try {
      setFieldSourceReport(await refreshProductControlP4FieldSource(projectId));
      setFieldSourceState("ready");
    } catch {
      setFieldSourceError("P4 字段来源候选刷新失败。");
      setFieldSourceState("failed");
    }
  }, [projectId]);

  const loadProductControlP5VariableRolePreflight = useCallback(async () => {
    if (!projectId) return;
    setVariableRolePreflightState("loading");
    setVariableRolePreflightError(null);
    try {
      setVariableRolePreflightReport(await requestProductControlP5VariableRolePreflight(projectId));
      setVariableRolePreflightState("ready");
    } catch {
      setVariableRolePreflightError("P5 VariableRoleSet 草案预检状态未读取。");
      setVariableRolePreflightState("failed");
    }
  }, [projectId]);

  const handleRefreshProductControlP5VariableRolePreflight = useCallback(async () => {
    if (!projectId) return;
    setVariableRolePreflightState("refreshing");
    setVariableRolePreflightError(null);
    try {
      setVariableRolePreflightReport(await refreshProductControlP5VariableRolePreflight(projectId));
      setVariableRolePreflightState("ready");
    } catch {
      setVariableRolePreflightError("P5 VariableRoleSet 草案预检刷新失败。");
      setVariableRolePreflightState("failed");
    }
  }, [projectId]);

  const loadProductControlP6VariableRoleSignoff = useCallback(async () => {
    if (!projectId) return;
    setVariableRoleSignoffState("loading");
    setVariableRoleSignoffError(null);
    try {
      const nextReport = await requestProductControlP6VariableRoleSignoff(projectId);
      setVariableRoleSignoffReport(nextReport);
      setVariableRoleSignoffDecisions(p6SignoffDecisionDefaults(nextReport));
      setVariableRoleSignoffState("ready");
    } catch {
      setVariableRoleSignoffError("P6 人工签收状态未读取。");
      setVariableRoleSignoffState("failed");
    }
  }, [projectId]);

  const handleRefreshProductControlP6VariableRoleSignoff = useCallback(async () => {
    if (!projectId) return;
    setVariableRoleSignoffState("refreshing");
    setVariableRoleSignoffError(null);
    try {
      const nextReport = await refreshProductControlP6VariableRoleSignoff(projectId);
      setVariableRoleSignoffReport(nextReport);
      setVariableRoleSignoffDecisions(p6SignoffDecisionDefaults(nextReport));
      setVariableRoleSignoffPromotionMessage(null);
      setVariableRoleSignoffState("ready");
    } catch {
      setVariableRoleSignoffError("P6 人工签收刷新失败。");
      setVariableRoleSignoffState("failed");
    }
  }, [projectId]);

  const handleP6SignoffDecisionChange = useCallback((id: VariableRoleDecisionId, value: string) => {
    setVariableRoleSignoffDecisions((current) => ({ ...current, [id]: value }));
  }, []);

  const loadProductControlP9FormalVariableRoles = useCallback(async () => {
    if (!projectId) return;
    setFormalVariableRoleSaveState("loading");
    setFormalVariableRoleSaveError(null);
    try {
      setFormalVariableRoleSaveReport(await requestProductControlP9FormalVariableRoles(projectId));
      setFormalVariableRoleSaveState("ready");
    } catch {
      setFormalVariableRoleSaveError("P9 正式变量表保存状态未读取。");
      setFormalVariableRoleSaveState("failed");
    }
  }, [projectId]);

  const loadProductControlP11SourceMetadataContract = useCallback(async () => {
    if (!projectId) return;
    setSourceMetadataState("loading");
    setSourceMetadataError(null);
    try {
      const nextReport = await requestProductControlP11SourceMetadataContract(projectId);
      const sourceFieldRows = p11SourceFieldRows(nextReport);
      setSourceMetadataReport(nextReport);
      setSourceMetadataForm((current) => ({
        ...current,
        reviewer: nextReport.source_contract?.review?.reviewer || current.reviewer,
        note: nextReport.source_contract?.review?.note || current.note,
        confirmation: nextReport.source_contract?.review?.confirmation || current.confirmation,
        datasetPath: p11DatasetPathDefault(nextReport) || current.datasetPath,
        sourceFieldRows,
        fieldBindingsJson: sourceFieldRows.length ? p11FieldBindingsJsonFromRows(sourceFieldRows) : p11FieldBindingsJson(nextReport),
        parentEducationConstruction: p11ParentEducationConstructionDefault(nextReport),
      }));
      setSourceMetadataState("ready");
    } catch {
      setSourceMetadataError("P11 source metadata 状态未读取。");
      setSourceMetadataState("failed");
    }
  }, [projectId]);

  const handlePromoteProductControlP6VariableRoleSignoff = useCallback(async () => {
    if (!projectId) return;
    setVariableRoleSignoffPromotionState("refreshing");
    setVariableRoleSignoffPromotionMessage(null);
    setVariableRoleSignoffError(null);
    try {
      const nextReport = await promoteProductControlP6VariableRoleSignoff(projectId, variableRoleSignoffDecisions);
      setVariableRoleSignoffReport(nextReport);
      setVariableRoleSignoffDecisions(p6SignoffDecisionDefaults(nextReport));
      setVariableRoleSignoffPromotionMessage(
        `已生成可编辑草稿：${nextReport.variable_role_set_draft?.id || "variable_roles_draft"}`,
      );
      setVariableRoleSignoffPromotionState("ready");
      try {
        setVariableRoleApprovalReport(await requestProductControlP8VariableRoleApproval(projectId));
        setVariableRoleApprovalState("ready");
      } catch {
        setVariableRoleApprovalError("P8 状态刷新失败，但 P7 可编辑草稿已生成。");
        setVariableRoleApprovalState("failed");
      }
      await loadProductControlP11SourceMetadataContract();
      await loadProductControlP9FormalVariableRoles();
    } catch {
      setVariableRoleSignoffError("P6 签收提交失败：请补齐五项确认，或刷新签收包后重试。");
      setVariableRoleSignoffPromotionState("failed");
    }
  }, [loadProductControlP11SourceMetadataContract, loadProductControlP9FormalVariableRoles, projectId, variableRoleSignoffDecisions]);

  const loadProductControlP8VariableRoleApproval = useCallback(async () => {
    if (!projectId) return;
    setVariableRoleApprovalState("loading");
    setVariableRoleApprovalError(null);
    try {
      setVariableRoleApprovalReport(await requestProductControlP8VariableRoleApproval(projectId));
      setVariableRoleApprovalState("ready");
    } catch {
      setVariableRoleApprovalError("P8 正式变量角色审批状态未读取。");
      setVariableRoleApprovalState("failed");
    }
  }, [projectId]);

  const handleRefreshProductControlP8VariableRoleApproval = useCallback(async () => {
    if (!projectId) return;
    setVariableRoleApprovalState("refreshing");
    setVariableRoleApprovalError(null);
    try {
      setVariableRoleApprovalReport(await requestProductControlP8VariableRoleApproval(projectId));
      setVariableRoleApprovalState("ready");
    } catch {
      setVariableRoleApprovalError("P8 正式变量角色审批刷新失败。");
      setVariableRoleApprovalState("failed");
    }
  }, [projectId]);

  const handleP8ApprovalFieldChange = useCallback((field: keyof P8ApprovalForm, value: string) => {
    setVariableRoleApprovalForm((current) => ({ ...current, [field]: value }));
  }, []);

  const handleP9FormalSaveFieldChange = useCallback((field: keyof P9FormalSaveForm, value: string) => {
    setFormalVariableRoleSaveForm((current) => ({ ...current, [field]: value }));
  }, []);

  const handleP11SourceMetadataFieldChange = useCallback((field: keyof P11SourceMetadataForm, value: string) => {
    setSourceMetadataForm((current) => ({ ...current, [field]: value }));
  }, []);

  const handleP11SourceFieldRowChange = useCallback(
    (fieldName: string, field: P11SourceFieldTextKey, value: string) => {
      setSourceMetadataForm((current) => {
        const sourceFieldRows = current.sourceFieldRows.map((row) =>
          row.field === fieldName ? { ...row, [field]: value } : row,
        );
        return {
          ...current,
          sourceFieldRows,
          fieldBindingsJson: p11FieldBindingsJsonFromRows(sourceFieldRows),
        };
      });
    },
    [],
  );

  const handleP11SourceFieldRowConfirmChange = useCallback((fieldName: string, confirmed: boolean) => {
    setSourceMetadataForm((current) => ({
      ...current,
      sourceFieldRows: current.sourceFieldRows.map((row) =>
        row.field === fieldName ? { ...row, confirmed } : row,
      ),
    }));
  }, []);

  const handleApproveProductControlP8VariableRoleApproval = useCallback(async () => {
    if (!projectId) return;
    setVariableRoleApprovalSubmitState("refreshing");
    setVariableRoleApprovalMessage(null);
    setVariableRoleApprovalError(null);
    try {
      const nextReport = await approveProductControlP8VariableRoleApproval(projectId, variableRoleApprovalForm);
      setVariableRoleApprovalReport(nextReport);
      setVariableRoleApprovalMessage(
        `已记录 P8 正式变量角色审批：${nextReport.approval?.source_draft_id || nextReport.latest_draft?.id || "latest_draft"}`,
      );
      setVariableRoleApprovalSubmitState("ready");
      await loadProductControlP11SourceMetadataContract();
      await loadProductControlP9FormalVariableRoles();
    } catch {
      setVariableRoleApprovalError("P8 审批提交失败：请确认 reviewer、note 和确认码完整。");
      setVariableRoleApprovalSubmitState("failed");
    }
  }, [loadProductControlP11SourceMetadataContract, loadProductControlP9FormalVariableRoles, projectId, variableRoleApprovalForm]);

  const handleRefreshProductControlP11SourceMetadataContract = useCallback(async () => {
    await loadProductControlP11SourceMetadataContract();
  }, [loadProductControlP11SourceMetadataContract]);

  const handleSaveProductControlP11SourceMetadataContract = useCallback(async () => {
    if (!projectId) return;
    setSourceMetadataSubmitState("refreshing");
    setSourceMetadataMessage(null);
    setSourceMetadataError(null);
    try {
      const nextReport = await saveProductControlP11SourceMetadataContract(projectId, sourceMetadataForm);
      setSourceMetadataReport(nextReport);
      setSourceMetadataMessage(
        `已保存 P11 source contract；P9 状态：${nextReport.p9_status_after_update || "等待刷新"}`,
      );
      setSourceMetadataSubmitState("ready");
      await loadProductControlP9FormalVariableRoles();
    } catch (error) {
      setSourceMetadataError(
        `P11 保存失败：${error instanceof Error ? error.message : "请补齐 dataset path 和字段来源。"}`,
      );
      setSourceMetadataSubmitState("failed");
    }
  }, [loadProductControlP9FormalVariableRoles, projectId, sourceMetadataForm]);

  const loadProductControlP17DataRepairPreflight = useCallback(async () => {
    if (!projectId) return;
    setDataRepairPreflightState("loading");
    setDataRepairPreflightError(null);
    try {
      setDataRepairPreflightReport(await requestProductControlP17DataRepairPreflight(projectId));
      setDataRepairPreflightState("ready");
    } catch {
      setDataRepairPreflightError("P17 数据修复预检状态未读取。");
      setDataRepairPreflightState("failed");
    }
  }, [projectId]);

  const handleRefreshProductControlP17DataRepairPreflight = useCallback(async () => {
    if (!projectId) return;
    setDataRepairPreflightState("refreshing");
    setDataRepairPreflightError(null);
    try {
      setDataRepairPreflightReport(await refreshProductControlP17DataRepairPreflight(projectId));
      setDataRepairPreflightState("ready");
    } catch {
      setDataRepairPreflightError("P17 数据修复预检刷新失败。");
      setDataRepairPreflightState("failed");
    }
  }, [projectId]);

  const handleRefreshProductControlP9FormalVariableRoles = useCallback(async () => {
    if (!projectId) return;
    setFormalVariableRoleSaveState("refreshing");
    setFormalVariableRoleSaveError(null);
    try {
      setFormalVariableRoleSaveReport(await requestProductControlP9FormalVariableRoles(projectId));
      setFormalVariableRoleSaveState("ready");
    } catch {
      setFormalVariableRoleSaveError("P9 正式变量表保存刷新失败。");
      setFormalVariableRoleSaveState("failed");
    }
  }, [projectId]);

  const handleSaveProductControlP9FormalVariableRoles = useCallback(async () => {
    if (!projectId || !formalVariableRoleSaveReport) return;
    setFormalVariableRoleSaveSubmitState("refreshing");
    setFormalVariableRoleSaveMessage(null);
    setFormalVariableRoleSaveError(null);
    try {
      const nextReport = await saveProductControlP9FormalVariableRoles(
        projectId,
        formalVariableRoleSaveReport,
        formalVariableRoleSaveForm,
      );
      setFormalVariableRoleSaveReport(nextReport);
      setFormalVariableRoleSaveMessage(
        `已保存正式变量表：version ${nextReport.variable_role_set?.version ?? "latest"}`,
      );
      setFormalVariableRoleSaveSubmitState("ready");
    } catch (error) {
      setFormalVariableRoleSaveError(
        `P9 保存失败：${error instanceof Error ? error.message : "请确认 P8 已审批、字段来源完整，并填写确认码。"}`,
      );
      setFormalVariableRoleSaveSubmitState("failed");
    }
  }, [formalVariableRoleSaveForm, formalVariableRoleSaveReport, projectId]);

  const handleRefreshProductControlP0 = useCallback(async () => {
    if (!projectId) return;
    setState("refreshing");
    setError(null);
    try {
      setReport(await refreshProductControlP0(projectId));
      setState("ready");
    } catch {
      setError("P0 阶段包刷新失败。后端没有完成项目登记或题目绑定审计。");
      setState("failed");
    }
  }, [projectId]);

  const loadProductControlP1Literature = useCallback(async () => {
    if (!projectId) return;
    setLiteratureState("loading");
    setLiteratureError(null);
    try {
      setLiteratureReport(await requestProductControlP1Literature(projectId));
      setLiteratureState("ready");
    } catch {
      setLiteratureError("P1-A 文献证据状态未读取。");
      setLiteratureState("failed");
    }
  }, [projectId]);

  const handleRefreshProductControlP1Literature = useCallback(async () => {
    if (!projectId) return;
    setLiteratureState("refreshing");
    setLiteratureError(null);
    try {
      setLiteratureReport(await refreshProductControlP1Literature(projectId));
      setLiteratureState("ready");
    } catch {
      setLiteratureError("P1-A 文献证据账本刷新失败。");
      setLiteratureState("failed");
    }
  }, [projectId]);

  const loadProductControlP1DataField = useCallback(async () => {
    if (!projectId) return;
    setDataFieldState("loading");
    setDataFieldError(null);
    try {
      setDataFieldReport(await requestProductControlP1DataField(projectId));
      setDataFieldState("ready");
    } catch {
      setDataFieldError("P1-B 数据字段绑定状态未读取。");
      setDataFieldState("failed");
    }
  }, [projectId]);

  const handleRefreshProductControlP1DataField = useCallback(async () => {
    if (!projectId) return;
    setDataFieldState("refreshing");
    setDataFieldError(null);
    try {
      setDataFieldReport(await refreshProductControlP1DataField(projectId));
      setDataFieldState("ready");
    } catch {
      setDataFieldError("P1-B 数据字段绑定账本刷新失败。");
      setDataFieldState("failed");
    }
  }, [projectId]);

  useEffect(() => {
    void loadProductControlP0();
  }, [loadProductControlP0]);

  useEffect(() => {
    void loadProductControlP1Literature();
  }, [loadProductControlP1Literature]);

  useEffect(() => {
    void loadProductControlP1DataField();
  }, [loadProductControlP1DataField]);

  useEffect(() => {
    void loadProductControlP1Method();
  }, [loadProductControlP1Method]);

  useEffect(() => {
    void loadProductControlP2Readiness();
  }, [loadProductControlP2Readiness]);

  useEffect(() => {
    void loadProductControlP3DraftPackage();
  }, [loadProductControlP3DraftPackage]);

  useEffect(() => {
    void loadProductControlP4FieldSource();
  }, [loadProductControlP4FieldSource]);

  useEffect(() => {
    void loadProductControlP5VariableRolePreflight();
  }, [loadProductControlP5VariableRolePreflight]);

  useEffect(() => {
    void loadProductControlP6VariableRoleSignoff();
  }, [loadProductControlP6VariableRoleSignoff]);

  useEffect(() => {
    void loadProductControlP8VariableRoleApproval();
  }, [loadProductControlP8VariableRoleApproval]);

  useEffect(() => {
    void loadProductControlP11SourceMetadataContract();
  }, [loadProductControlP11SourceMetadataContract]);

  useEffect(() => {
    void loadProductControlP9FormalVariableRoles();
  }, [loadProductControlP9FormalVariableRoles]);

  useEffect(() => {
    void loadProductControlP17DataRepairPreflight();
  }, [loadProductControlP17DataRepairPreflight]);

  const tasks = report?.agent_tasks ?? [];
  const checks = report?.evidence_checks ?? [];
  const needsEvidence = checks.filter(isNeedsEvidence);
  const displayNeeds = needsEvidence.length
    ? needsEvidence
    : [
        { id: "real_literature_candidates", status: "needs_evidence" },
        { id: "real_data_variable_binding", status: "needs_evidence" },
        { id: "method_execution_evidence", status: "needs_evidence" },
      ];
  const p4FatherStatus =
    fieldSourceReport?.field_source_candidates?.find((item) => item.dataset_column === "father_education")?.candidate_status ||
    "father_education:missing";
  const p4MotherStatus =
    fieldSourceReport?.field_source_candidates?.find((item) => item.dataset_column === "mother_education")?.candidate_status ||
    "mother_education:missing";
  const p5ParentEducationStatus =
    variableRolePreflightReport?.draft_variable_roles?.treatment?.construction?.decision_status ||
    "requires_human_confirmation";
  const p5Outcome = variableRolePreflightReport?.draft_variable_roles?.outcome?.preferred || "待确认";
  const p5Controls = variableRolePreflightReport?.draft_variable_roles?.controls?.preferred?.length ?? 0;
  const p6RequiredCount = variableRoleSignoffReport?.required_decisions?.length ?? 5;
  const p6MissingCount = variableRoleSignoffReport?.missing_decisions?.length ?? p6RequiredCount;
  const p6DraftTarget =
    variableRoleSignoffReport?.promotion_targets?.find((target) => target.id === "editable_draft")?.id ||
    "editable_draft";
  const p6CanSubmitSignoff =
    Boolean(projectId) &&
    Boolean(variableRoleSignoffReport?.can_write_editable_draft) &&
    variableRoleSignoffPromotionState !== "refreshing";
  const p8LatestDraftId = variableRoleApprovalReport?.latest_draft?.id || "等待 P7 草稿";
  const p8Outcome = variableRoleApprovalReport?.latest_draft?.roles?.outcome?.join(", ") || "待确认";
  const p8Treatment = variableRoleApprovalReport?.latest_draft?.roles?.treatment?.join(", ") || "待确认";
  const p8CanApprove =
    Boolean(projectId) &&
    Boolean(variableRoleApprovalReport?.can_approve_formal_variable_roles) &&
    variableRoleApprovalSubmitState !== "refreshing" &&
    Boolean(variableRoleApprovalForm.reviewer.trim()) &&
    Boolean(variableRoleApprovalForm.note.trim()) &&
    variableRoleApprovalForm.confirmation.trim() === P8_APPROVAL_CONFIRMATION;
  const p9LatestDraftId = formalVariableRoleSaveReport?.latest_draft?.id || "等待 P8 审批";
  const p9DatasetPath = formalVariableRoleSaveReport?.source_contract?.dataset_path || "dataset_path missing";
  const p9MissingSourceMetadataFields =
    formalVariableRoleSaveReport?.missing_source_metadata_fields?.join(", ") || "none";
  const p11RequiredSourceFields = sourceMetadataReport?.required_source_fields?.join(", ") || "ln_wage, parent_education, age, female, urban, edu_last, experience";
  const p11MissingSourceMetadataFields =
    sourceMetadataReport?.missing_source_metadata_fields?.join(", ") || "none";
  const p11ReviewKit = sourceMetadataReport?.source_contract_review_kit;
  const p11DatasetPathCandidates = p11ReviewKit?.dataset_path_candidates?.slice(0, 4).join("；") || "none";
  const p11FieldReviewItems = p11ReviewKit?.field_review_items?.slice(0, 9) || [];
  const p11SourceRowReviewItems = buildP11SourceRowReviewItems(sourceMetadataForm.sourceFieldRows);
  const confirmedSourceFieldRows = sourceMetadataForm.sourceFieldRows.filter((row) => row.confirmed).length;
  const p11ReadyForConfirmationRows = p11SourceRowReviewItems.filter(
    (item) => item.status === "ready_for_human_confirmation",
  ).length;
  const p11NeedsMetadataRows = p11SourceRowReviewItems.filter(
    (item) => item.status === "needs_human_confirmation",
  ).length;
  const p11ReadinessMissingItems = p11SourceContractMissingItems(sourceMetadataForm);
  const p11SourceContractReady = p11ReadinessMissingItems.length === 0;
  const p11CanSave =
    Boolean(projectId) &&
    sourceMetadataSubmitState !== "refreshing" &&
    p11SourceContractReady;
  const sourceContractSaved =
    sourceMetadataReport?.status === "source_metadata_contract_ready_for_p9_save" &&
    Boolean(sourceMetadataReport?.can_return_to_p9_formal_save);
  const p11SavedDatasetPath =
    sourceMetadataReport?.source_contract?.dataset_path || sourceMetadataForm.datasetPath || "dataset path saved";
  const p9CanSave =
    Boolean(projectId) &&
    Boolean(formalVariableRoleSaveReport?.can_save_formal_variable_roles) &&
    formalVariableRoleSaveSubmitState !== "refreshing" &&
    Boolean(formalVariableRoleSaveForm.reviewer.trim()) &&
    Boolean(formalVariableRoleSaveForm.note.trim()) &&
      formalVariableRoleSaveForm.confirmation.trim() === P9_FORMAL_SAVE_CONFIRMATION;
  const p17MissingFields = dataRepairPreflightReport?.missing_fields?.join(", ") || "parent_education, experience";
  const p17RecommendedSource = dataRepairPreflightReport?.recommended_parent_education_source || "待刷新";
  const p17ParentCandidate = dataRepairPreflightReport?.parent_education_candidates?.find(
    (item) => item.id === dataRepairPreflightReport.recommended_parent_education_source,
  ) || dataRepairPreflightReport?.parent_education_candidates?.[0];
  const p17ExperienceStatus = dataRepairPreflightReport?.experience_candidate?.status || "待刷新";
  const p17Boundary = dataRepairPreflightReport
    ? `No model run；不改正式 CSV；suggested：${dataRepairPreflightReport.suggested_repaired_dataset_path || "Data/Interim/parent_education_wage_repaired.csv"}`
    : "No model run；等待 P17 数据修复预检";
  const currentGateStatus = dataRepairPreflightReport?.status || formalVariableRoleSaveReport?.status || "blocked_missing_dataset_source_metadata";
  const currentGateSummary =
    dataRepairPreflightReport
      ? "P16 已完成阻断交付；当前需要审阅 parent_education 与 experience 的数据修复候选。"
      : currentGateStatus === "formal_variable_roles_saved"
      ? "正式变量表已保存；下一步进入 DesignSpec preflight，仍不能创建 run id。"
      : formalVariableRoleSaveReport?.can_save_formal_variable_roles
        ? "P7 已完成，P8 已审批，P9 source metadata 已满足，可人工保存正式变量表。"
        : "P7 已完成，P8 已审批，P9 等待 source metadata。";
  const currentGateBlockers =
    dataRepairPreflightReport
      ? [
          `缺失字段：${p17MissingFields}`,
          `推荐父母教育来源：${p17RecommendedSource}`,
          "不能创建 run id：P17 只生成修复候选账本",
          "不能跑模型：等待 P18 应用修复门禁",
        ]
      : currentGateStatus === "formal_variable_roles_saved"
      ? [
          "正式变量表已保存：等待 DesignSpec preflight",
          "不能创建 run id：RunPlan 尚未进入审批",
          "不能跑模型：RunPlan 尚未批准",
        ]
      : formalVariableRoleSaveReport?.can_save_formal_variable_roles
        ? [
            "可以保存正式变量表：需要 reviewer、note 和确认码",
            "不能创建 run id：RunPlan 尚未进入审批",
            "不能跑模型：DesignSpec 和 RunPlan 尚未通过",
          ]
        : [
            "不能保存正式变量表：source contract 还不完整",
            "不能创建 run id：RunPlan 尚未进入审批",
            "不能跑模型：正式变量表和 DesignSpec 尚未通过",
          ];

  const userMissingFieldLabels = (
    dataRepairPreflightReport?.missing_fields?.length
      ? dataRepairPreflightReport.missing_fields
      : ["parent_education", "experience"]
  ).map(userFieldLabel);
  const userProgressTitle = dataRepairPreflightReport ? "补齐数据字段后再继续分析" : "补齐数据来源说明后再继续分析";
  const userProgressSummary = dataRepairPreflightReport
    ? `还差 ${userMissingFieldLabels.join("、")}。确认来源和口径后，才能进入正式分析。`
    : "当前还没有读到完整的数据修复状态。先刷新状态；如果仍缺失，再打开技术详情补充数据来源。";
  const userNextSteps = dataRepairPreflightReport
    ? [
        `确认${userMissingFieldLabels[0] || "父母教育信息"}的可用来源`,
        `确认${userMissingFieldLabels[1] || "工作经验"}的计算口径`,
        "生成修复后的分析数据，再进入正式模型步骤",
      ]
    : ["刷新当前状态", "补齐数据来源说明", "确认后再进入正式分析"];
  const userProgressButtonLabel = dataRepairPreflightReport ? "刷新修复建议" : "刷新状态";
  const isUserProgressRefreshing = dataRepairPreflightReport
    ? dataRepairPreflightState === "refreshing"
    : state === "refreshing";

  const dataRepairPreflightSection = (
    <div
      className="product-control-p0-panel__p17 product-control-current-gate-detail"
      data-testid="product-control-p17-data-repair-preflight"
    >
      <div>
        <span>P17 Data Repair Preflight</span>
        <strong>
          {dataRepairPreflightReport?.status ||
            (dataRepairPreflightState === "loading" ? "读取中" : "p17_data_repair_preflight_missing")}
        </strong>
        <p>
          missing：{p17MissingFields}；recommended source：{p17RecommendedSource}
        </p>
        <small>{p17Boundary}</small>
      </div>
      <div className="product-control-p0-panel__p17-grid" aria-label="p17 data repair review summary">
        <div>
          <span>parent_education</span>
          <strong>
            {p17ParentCandidate?.parent_constructable_rows ?? 0}/{p17ParentCandidate?.target_rows ?? 0}
          </strong>
          <small>
            {p17ParentCandidate?.id || "candidate missing"}；rate：
            {p17ParentCandidate?.parent_constructable_rate ?? 0}
          </small>
        </div>
        <div>
          <span>experience</span>
          <strong>{p17ExperienceStatus}</strong>
          <small>{dataRepairPreflightReport?.experience_candidate?.review_note || "等待 education_years 映射确认"}</small>
        </div>
        <div>
          <span>boundary</span>
          <strong>No model run</strong>
          <small>
            can_create_run_id：{dataRepairPreflightReport?.can_create_run_id ? "true" : "false"}；
            can_execute_model：{dataRepairPreflightReport?.can_execute_model ? "true" : "false"}
          </small>
        </div>
      </div>
      <button
        className="btn btn--ghost product-control-p0-panel__refresh"
        type="button"
        onClick={handleRefreshProductControlP17DataRepairPreflight}
        disabled={!projectId || dataRepairPreflightState === "refreshing"}
      >
        <RefreshCcw size={15} aria-hidden="true" />
        <span>{dataRepairPreflightState === "refreshing" ? "刷新中" : "刷新 P17"}</span>
      </button>
      {dataRepairPreflightError ? (
        <p className="product-control-p0-panel__error" role="alert">
          {dataRepairPreflightError}
        </p>
      ) : null}
    </div>
  );

  return (
    <section className="product-control-p0-panel product-control-p0-panel--clean" data-testid="product-control-p0-panel">
      <header className="product-control-p0-panel__header">
        <div>
          <span className="eyebrow">论文工作流</span>
          <h2>当前卡点</h2>
        </div>
        <button
          className="btn btn--ghost product-control-p0-panel__refresh"
          type="button"
          onClick={handleRefreshProductControlP0}
          disabled={!projectId || state === "refreshing"}
        >
          <RefreshCcw size={15} aria-hidden="true" />
          <span>{state === "refreshing" ? "刷新中" : "刷新状态"}</span>
        </button>
      </header>

      <div className="product-control-p0-panel__body" data-testid="product-control-p0-body">
        <section className="research-progress-card" data-testid="research-progress-card">
          <div className="research-progress-card__main">
            <span>研究进度</span>
            <h3>{userProgressTitle}</h3>
            <p>{userProgressSummary}</p>
          </div>
          <div className="research-progress-card__next">
            <strong>下一步</strong>
            <ol>
              {userNextSteps.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ol>
            <button
              className="btn btn--primary"
              type="button"
              onClick={
                dataRepairPreflightReport
                  ? handleRefreshProductControlP17DataRepairPreflight
                  : handleRefreshProductControlP0
              }
              disabled={
                !projectId ||
                isUserProgressRefreshing
              }
            >
              <RefreshCcw size={15} aria-hidden="true" />
              <span>{isUserProgressRefreshing ? "刷新中" : userProgressButtonLabel}</span>
            </button>
          </div>
        </section>

        <details className="product-control-technical-details" data-testid="product-control-technical-details">
          <summary>技术详情</summary>
        <div className="product-control-p0-panel__status">
          <ShieldCheck size={18} aria-hidden="true" />
          <div>
            <strong>{statusLabel(report?.status ?? (state === "loading" ? "loading" : ""))}</strong>
            <p>{topicLabel(report)}</p>
          </div>
        </div>

        {error ? (
          <p className="product-control-p0-panel__error" role="alert">
            {error}
          </p>
        ) : null}

        <section className="product-control-gate-summary" data-testid="product-control-gate-summary">
          <div>
            <span>当前门禁</span>
            <strong>{dataRepairPreflightReport ? "P17 数据修复预检" : "P9 正式变量表保存"}</strong>
            <p>{currentGateStatus}；{currentGateSummary}</p>
          </div>
          <ul>
            {currentGateBlockers.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>

        {dataRepairPreflightSection}

        <details className="product-control-stage-history">
          <summary>
            <span>产品控制 P0-P8 阶段历史</span>
            <strong>P7 已完成；P8 已审批；P9 等待 source metadata</strong>
          </summary>

        <dl className="product-control-p0-panel__metrics">
          <div>
            <dt>Agent tasks</dt>
            <dd>{report?.summary?.task_count ?? tasks.length}</dd>
          </div>
          <div>
            <dt>Evidence Audit</dt>
            <dd>{report?.summary?.evidence_audit_status ?? "needs_evidence"}</dd>
          </div>
          <div>
            <dt>Portfolio</dt>
            <dd>{report?.summary?.portfolio_status ?? report?.portfolio_script_path ?? "待生成"}</dd>
          </div>
        </dl>

        <div className="product-control-p0-panel__needs" data-testid="product-control-p0-needs">
          <span>needs_evidence</span>
          <ul>
            {displayNeeds.map((check) => (
              <li key={check.id || check.label || check.description}>
                <strong>{evidenceNeedLabel(check)}</strong>
                <small>{check.status || "needs_evidence"}</small>
              </li>
            ))}
          </ul>
        </div>

        <div className="product-control-p0-panel__tasks">
          <span>Agent Queue</span>
          <ul>
            {(tasks.length ? tasks : [{ id: "dispatch_review_required", role: "Supervisor", task: "等待 P0 阶段包", next_action: "dispatch_review_required" }]).map(
              (task) => (
                <li key={task.id || task.role || task.task}>
                  <strong>{task.role || task.id || "Agent"}</strong>
                  <p>{task.task || "待派工审阅"}</p>
                  <small>{task.next_action === "dispatch_review_required" ? "待派工审阅" : task.next_action || "dispatch_review_required"}</small>
                </li>
              ),
            )}
          </ul>
        </div>

        <div className="product-control-p0-panel__p1a" data-testid="product-control-p1-literature">
          <div>
            <span>P1-A 文献证据</span>
            <strong>{literatureReport?.status || (literatureState === "loading" ? "读取中" : "p1a_literature_ledger_missing")}</strong>
            <p>
              真实文献候选：{literatureReport?.candidate_topics?.length ?? 0}；verified：
              {literatureReport?.verified_count ?? 0}
            </p>
            <small>
              {literatureReport?.product_control_signal?.status ||
                literatureReport?.next_action ||
                "needs_external_literature_verification"}
            </small>
          </div>
          <button
            className="btn btn--ghost product-control-p0-panel__refresh"
            type="button"
            onClick={handleRefreshProductControlP1Literature}
            disabled={!projectId || literatureState === "refreshing"}
          >
            <RefreshCcw size={15} aria-hidden="true" />
            <span>{literatureState === "refreshing" ? "刷新中" : "刷新 P1-A"}</span>
          </button>
          {literatureError ? (
            <p className="product-control-p0-panel__error" role="alert">
              {literatureError}
            </p>
          ) : null}
        </div>

        <div className="product-control-p0-panel__p1b" data-testid="product-control-p1-data-field">
          <div>
            <span>P1-B 数据字段</span>
            <strong>{dataFieldReport?.status || (dataFieldState === "loading" ? "读取中" : "p1b_data_field_binding_missing")}</strong>
            <p>
              变量字段：{dataFieldReport?.candidate_variable_count ?? 0}；matched：
              {dataFieldReport?.matched_fields?.length ?? 0}；missing：
              {dataFieldReport?.missing_fields?.length ?? 0}
            </p>
            <small>
              {dataFieldReport?.product_control_signal?.status ||
                dataFieldReport?.next_action ||
                "blocked_missing_parent_education_fields"}
            </small>
          </div>
          <button
            className="btn btn--ghost product-control-p0-panel__refresh"
            type="button"
            onClick={handleRefreshProductControlP1DataField}
            disabled={!projectId || dataFieldState === "refreshing"}
          >
            <RefreshCcw size={15} aria-hidden="true" />
            <span>{dataFieldState === "refreshing" ? "刷新中" : "刷新 P1-B"}</span>
          </button>
          {dataFieldError ? (
            <p className="product-control-p0-panel__error" role="alert">
              {dataFieldError}
            </p>
          ) : null}
        </div>

        <div className="product-control-p0-panel__p1c" data-testid="product-control-p1-method">
          <div>
            <span>P1-C 方法执行</span>
            <strong>{methodReport?.status || (methodState === "loading" ? "读取中" : "p1c_method_execution_ledger_missing")}</strong>
            <p>
              run id：{methodReport?.run_id || "未创建"}；methods：
              {methodReport?.method_candidates?.length ?? 0}；missing：
              {methodReport?.missing_required_fields?.length ?? 0}
            </p>
            <small>
              {methodReport?.product_control_signal?.status ||
                methodReport?.next_action ||
                "blocked_missing_required_fields"}
            </small>
          </div>
          <button
            className="btn btn--ghost product-control-p0-panel__refresh"
            type="button"
            onClick={handleRefreshProductControlP1Method}
            disabled={!projectId || methodState === "refreshing"}
          >
            <RefreshCcw size={15} aria-hidden="true" />
            <span>{methodState === "refreshing" ? "刷新中" : "刷新 P1-C"}</span>
          </button>
          {methodError ? (
            <p className="product-control-p0-panel__error" role="alert">
              {methodError}
            </p>
          ) : null}
        </div>

        <div className="product-control-p0-panel__p2" data-testid="product-control-p2-readiness">
          <div>
            <span>P2 执行准入</span>
            <strong>{readinessReport?.status || (readinessState === "loading" ? "读取中" : "p2_execution_readiness_missing")}</strong>
            <p>
              execution_preflight_allowed：
              {readinessReport?.execution_preflight_allowed ? "true" : "false"}；fields：
              {readinessReport?.field_supplementation?.length ?? 0}；run id：
              {readinessReport?.run_id || "未创建"}
            </p>
            <small>
              {readinessReport?.product_control_signal?.status ||
                readinessReport?.next_action ||
                "blocked_missing_parent_education_fields"}
            </small>
          </div>
          <button
            className="btn btn--ghost product-control-p0-panel__refresh"
            type="button"
            onClick={handleRefreshProductControlP2Readiness}
            disabled={!projectId || readinessState === "refreshing"}
          >
            <RefreshCcw size={15} aria-hidden="true" />
            <span>{readinessState === "refreshing" ? "刷新中" : "刷新 P2"}</span>
          </button>
          {readinessError ? (
            <p className="product-control-p0-panel__error" role="alert">
              {readinessError}
            </p>
          ) : null}
        </div>

        <div className="product-control-p0-panel__p3" data-testid="product-control-p3-draft-package">
          <div>
            <span>P3 DraftPackage</span>
            <strong>
              {draftPackageReport?.status || (draftPackageState === "loading" ? "读取中" : "p3_draft_package_missing")}
            </strong>
            <p>
              paper_draft.docx：
              {draftPackageReport?.outputs?.docx || "Submissions/parent_education_wage_paper_draft.docx"}；半成品：
              {draftPackageReport?.full_draft_ready ? "false" : "true"}；issues：
              {draftPackageReport?.issue_count ?? 0}
            </p>
            <small>
              {draftPackageReport?.product_control_signal?.status ||
                draftPackageReport?.next_action ||
                "半成品论文 + 红标问题清单"}
            </small>
          </div>
          <button
            className="btn btn--ghost product-control-p0-panel__refresh"
            type="button"
            onClick={handleRefreshProductControlP3DraftPackage}
            disabled={!projectId || draftPackageState === "refreshing"}
          >
            <RefreshCcw size={15} aria-hidden="true" />
            <span>{draftPackageState === "refreshing" ? "刷新中" : "刷新 P3"}</span>
          </button>
          {draftPackageError ? (
            <p className="product-control-p0-panel__error" role="alert">
              {draftPackageError}
            </p>
          ) : null}
        </div>

        <div className="product-control-p0-panel__p4" data-testid="product-control-p4-field-source">
          <div>
            <span>P4 字段来源</span>
            <strong>
              {fieldSourceReport?.status || (fieldSourceState === "loading" ? "读取中" : "p4_field_source_candidates_missing")}
            </strong>
            <p>
              father_education：{p4FatherStatus}；mother_education：{p4MotherStatus}；候选：
              {fieldSourceReport?.candidate_count ?? 0}
            </p>
            <small>
              {fieldSourceReport?.product_control_signal?.status ||
                fieldSourceReport?.next_action ||
                "扫描 CFPS 元数据，形成字段来源候选"}
            </small>
          </div>
          <button
            className="btn btn--ghost product-control-p0-panel__refresh"
            type="button"
            onClick={handleRefreshProductControlP4FieldSource}
            disabled={!projectId || fieldSourceState === "refreshing"}
          >
            <RefreshCcw size={15} aria-hidden="true" />
            <span>{fieldSourceState === "refreshing" ? "刷新中" : "刷新 P4"}</span>
          </button>
          {fieldSourceError ? (
            <p className="product-control-p0-panel__error" role="alert">
              {fieldSourceError}
            </p>
          ) : null}
        </div>

        <div className="product-control-p0-panel__p5" data-testid="product-control-p5-variable-role-preflight">
          <div>
            <span>P5 VariableRoleSet</span>
            <strong>
              {variableRolePreflightReport?.status ||
                (variableRolePreflightState === "loading" ? "读取中" : "p5_variable_role_preflight_missing")}
            </strong>
            <p>
              parent_education：{p5ParentEducationStatus}；outcome：{p5Outcome}；controls：
              {p5Controls}；formal write：
              {variableRolePreflightReport?.can_write_formal_variable_roles ? "true" : "false"}
            </p>
            <small>
              {variableRolePreflightReport?.product_control_signal?.status ||
                variableRolePreflightReport?.next_action ||
                "requires_human_confirmation"}
            </small>
          </div>
          <button
            className="btn btn--ghost product-control-p0-panel__refresh"
            type="button"
            onClick={handleRefreshProductControlP5VariableRolePreflight}
            disabled={!projectId || variableRolePreflightState === "refreshing"}
          >
            <RefreshCcw size={15} aria-hidden="true" />
            <span>{variableRolePreflightState === "refreshing" ? "刷新中" : "刷新 P5"}</span>
          </button>
          {variableRolePreflightError ? (
            <p className="product-control-p0-panel__error" role="alert">
              {variableRolePreflightError}
            </p>
          ) : null}
        </div>

        <div className="product-control-p0-panel__p6" data-testid="product-control-p6-variable-role-signoff">
          <div>
            <span>P6 签收状态</span>
            <strong>
              {variableRoleSignoffReport?.status ||
                (variableRoleSignoffState === "loading" ? "读取中" : "p6_variable_role_signoff_missing")}
            </strong>
            <p>
              required：{p6RequiredCount}；missing：{p6MissingCount}；target：{p6DraftTarget}；formal write：
              {variableRoleSignoffReport?.can_write_formal_variable_roles ? "true" : "false"}
            </p>
            <small>
              {variableRoleSignoffReport?.product_control_signal?.status ||
                variableRoleSignoffReport?.next_action ||
                "完整签收后才可提升，不跑模型"}
            </small>
          </div>
          <form className="product-control-p0-panel__p6-form" onSubmit={(event) => event.preventDefault()}>
            {P6_SIGNOFF_DECISION_ORDER.map((id) => (
              <label className="product-control-p0-panel__p6-field" key={id}>
                <span>{P6_SIGNOFF_DECISION_LABELS[id]}</span>
                <input
                  aria-label={id}
                  value={variableRoleSignoffDecisions[id]}
                  onChange={(event) => handleP6SignoffDecisionChange(id, event.target.value)}
                  disabled={!variableRoleSignoffReport?.can_write_editable_draft}
                />
              </label>
            ))}
            <button
              className="btn btn--primary product-control-p0-panel__p6-submit"
              type="button"
              onClick={handlePromoteProductControlP6VariableRoleSignoff}
              disabled={!p6CanSubmitSignoff}
            >
              {variableRoleSignoffPromotionState === "refreshing" ? "生成中" : "确认并生成可编辑草稿"}
            </button>
            <small>draft_only_no_formal_write；不写正式 VariableRoleSet；不跑模型</small>
          </form>
          <button
            className="btn btn--ghost product-control-p0-panel__refresh"
            type="button"
            onClick={handleRefreshProductControlP6VariableRoleSignoff}
            disabled={!projectId || variableRoleSignoffState === "refreshing"}
          >
            <RefreshCcw size={15} aria-hidden="true" />
            <span>{variableRoleSignoffState === "refreshing" ? "刷新中" : "刷新 P6"}</span>
          </button>
          {variableRoleSignoffError ? (
            <p className="product-control-p0-panel__error" role="alert">
              {variableRoleSignoffError}
            </p>
          ) : null}
          {variableRoleSignoffPromotionMessage ? (
            <p className="product-control-p0-panel__success" role="status">
              {variableRoleSignoffPromotionMessage}
            </p>
          ) : null}
        </div>

        <div className="product-control-p0-panel__p8" data-testid="product-control-p8-variable-role-approval">
          <div>
            <span>P8 正式变量角色审批</span>
            <strong>
              {variableRoleApprovalReport?.status ||
                (variableRoleApprovalState === "loading" ? "读取中" : "p8_variable_role_approval_missing")}
            </strong>
            <p>
              draft：{p8LatestDraftId}；outcome：{p8Outcome}；treatment：{p8Treatment}；formal write：
              {variableRoleApprovalReport?.can_write_formal_variable_roles ? "true" : "false"}
            </p>
            <small>
              {variableRoleApprovalReport?.product_control_signal?.status ||
                variableRoleApprovalReport?.next_action ||
                "审核 P7 草稿后才允许正式 VariableRoleSet 写入"}
            </small>
          </div>
          <form className="product-control-p0-panel__p8-form" onSubmit={(event) => event.preventDefault()}>
            <label className="product-control-p0-panel__p8-field">
              <span>reviewer</span>
              <input
                aria-label="reviewer"
                value={variableRoleApprovalForm.reviewer}
                onChange={(event) => handleP8ApprovalFieldChange("reviewer", event.target.value)}
                disabled={!variableRoleApprovalReport?.can_approve_formal_variable_roles}
              />
            </label>
            <label className="product-control-p0-panel__p8-field">
              <span>note</span>
              <input
                aria-label="note"
                value={variableRoleApprovalForm.note}
                onChange={(event) => handleP8ApprovalFieldChange("note", event.target.value)}
                disabled={!variableRoleApprovalReport?.can_approve_formal_variable_roles}
              />
            </label>
            <label className="product-control-p0-panel__p8-field">
              <span>confirmation</span>
              <input
                aria-label="confirmation"
                value={variableRoleApprovalForm.confirmation}
                onChange={(event) => handleP8ApprovalFieldChange("confirmation", event.target.value)}
                disabled={!variableRoleApprovalReport?.can_approve_formal_variable_roles}
              />
            </label>
            <button
              className="btn btn--primary product-control-p0-panel__p8-submit"
              type="button"
              onClick={handleApproveProductControlP8VariableRoleApproval}
              disabled={!p8CanApprove}
            >
              {variableRoleApprovalSubmitState === "refreshing" ? "审批中" : "批准正式变量角色保存"}
            </button>
            <small>approve_formal_variable_roles_after_review；不写 RunPlan；不跑模型</small>
          </form>
          <button
            className="btn btn--ghost product-control-p0-panel__refresh"
            type="button"
            onClick={handleRefreshProductControlP8VariableRoleApproval}
            disabled={!projectId || variableRoleApprovalState === "refreshing"}
          >
            <RefreshCcw size={15} aria-hidden="true" />
            <span>{variableRoleApprovalState === "refreshing" ? "刷新中" : "刷新 P8"}</span>
          </button>
          {variableRoleApprovalError ? (
            <p className="product-control-p0-panel__error" role="alert">
              {variableRoleApprovalError}
            </p>
          ) : null}
          {variableRoleApprovalMessage ? (
            <p className="product-control-p0-panel__success" role="status">
              {variableRoleApprovalMessage}
            </p>
          ) : null}
        </div>
        </details>

        <details className="product-control-secondary-workspace product-control-secondary-workspace--p11">
          <summary>
            <span>P11 Source Metadata</span>
            <strong>{sourceMetadataReport?.status || "source contract 复查"}</strong>
          </summary>
          <div
            className="product-control-p0-panel__p11 product-control-current-gate-detail"
            data-testid="product-control-p11-source-metadata-contract"
          >
          <section className="product-control-p0-panel__p11-workspace" aria-label="p11 source contract signoff workspace">
            <header className="product-control-p0-panel__p11-workspace-header">
              <div>
                <span>P11 Source Metadata</span>
                <strong>Source Contract Signoff</strong>
                <p>补齐 source contract 后回到 P9；不写正式 VariableRoleSet；不写 DesignSpec；不写 RunPlan；不跑模型。</p>
              </div>
              <button
                className="btn btn--ghost product-control-p0-panel__refresh"
                type="button"
                onClick={handleRefreshProductControlP11SourceMetadataContract}
                disabled={!projectId || sourceMetadataState === "refreshing"}
              >
                <RefreshCcw size={15} aria-hidden="true" />
                <span>{sourceMetadataState === "refreshing" ? "刷新中" : "刷新 P11"}</span>
              </button>
            </header>

            <div className="product-control-p0-panel__p11-status-strip" aria-label="p11 signoff status strip">
              <div>
                <span>current state</span>
                <strong>
                  {sourceMetadataReport?.status ||
                    (sourceMetadataState === "loading" ? "读取中" : "source_metadata_contract_missing")}
                </strong>
              </div>
              <div>
                <span>fields</span>
                <strong>
                  {confirmedSourceFieldRows}/{sourceMetadataForm.sourceFieldRows.length || p11RequiredSourceFields}
                </strong>
                <small>{p11ReadyForConfirmationRows} ready；{p11NeedsMetadataRows} need metadata</small>
              </div>
              <div>
                <span>missing</span>
                <strong>{p11ReadinessMissingItems.length || p11MissingSourceMetadataFields}</strong>
                <small>{p11ReadinessMissingItems.slice(0, 4).join("；") || "none"}</small>
              </div>
              <div>
                <span>boundary</span>
                <strong>No model run</strong>
                <small>can return to P9：{sourceMetadataReport?.can_return_to_p9_formal_save ? "true" : "false"}</small>
              </div>
            </div>

            {sourceContractSaved ? (
              <section
                className="product-control-p0-panel__p11-saved-next-step"
                aria-label="p11 source contract saved next step"
              >
                <div>
                  <span>P11 已签收</span>
                  <strong>已解锁 P9 正式变量表保存</strong>
                  <p>dataset：{p11SavedDatasetPath}</p>
                </div>
                <ul>
                  <li>下一步：回到 P9 正式保存</li>
                  <li>仍不能进入 P12</li>
                  <li>仍不能创建 run id</li>
                  <li>仍不能运行模型</li>
                </ul>
              </section>
            ) : null}

            <div className="product-control-p0-panel__p11-workspace-grid">
              <aside className="product-control-p0-panel__p11-review-pane" aria-label="p11 source review pane">
                <section
                  className="product-control-p0-panel__p11-review-queue"
                  aria-label="p11 human signoff review queue"
                >
                  <div>
                    <strong>Review queue</strong>
                    <small>Human signoff review queue：先检查字段状态，再逐行勾选 human confirmation。</small>
                  </div>
                  <ol>
                    {p11SourceRowReviewItems.map((item) => (
                      <li
                        className={`product-control-p0-panel__p11-review-queue-item product-control-p0-panel__p11-review-queue-item--${item.status}`}
                        key={item.field}
                      >
                        <div>
                          <strong>{item.field}</strong>
                          <span>{item.status}</span>
                        </div>
                        <small>missing：{item.missingItems.length ? item.missingItems.join("；") : "none"}</small>
                        <small>action：{item.action}</small>
                      </li>
                    ))}
                  </ol>
                </section>

                <details className="product-control-p0-panel__p11-kit" aria-label="source_contract_review_kit">
                  <summary>Source review kit</summary>
                  <div>
                    <strong>Source review kit</strong>
                    <p>
                      recommended dataset path：{p11ReviewKit?.recommended_dataset_path || "待人工确认"}；
                      candidates：{p11DatasetPathCandidates}
                    </p>
                    <small>
                      status：{p11ReviewKit?.status || "source_contract_review_kit_missing"}；field review items：
                      {p11FieldReviewItems.length}
                    </small>
                  </div>
                  <ul>
                    {p11FieldReviewItems.map((item) => (
                      <li key={item.field || item.review_status}>
                        <strong>{item.field || "field"}</strong>
                        <span>{item.review_status || "needs_human_confirmation"}</span>
                        <small>
                          {item.recommended_source?.name || "no candidate"}；{item.recommended_source?.source_path || "needs source"}
                        </small>
                      </li>
                    ))}
                  </ul>
                </details>
              </aside>

              <section className="product-control-p0-panel__p11-form-pane" aria-label="p11 source contract form pane">
                <div className="product-control-p0-panel__p11-form-title">
                  <strong>Source contract form</strong>
                  <small>逐项确认 dataset path、字段来源、evidence level 和人工签收。</small>
                </div>
                <form className="product-control-p0-panel__p11-form" onSubmit={(event) => event.preventDefault()}>
                  <label className="product-control-p0-panel__p11-field">
                    <span>dataset path</span>
                    <input
                      aria-label="p11 dataset path"
                      value={sourceMetadataForm.datasetPath}
                      onChange={(event) => handleP11SourceMetadataFieldChange("datasetPath", event.target.value)}
                      placeholder="Data/Final/analysis_sample.csv"
                    />
                  </label>
                  <label className="product-control-p0-panel__p11-field">
                    <span>reviewer</span>
                    <input
                      aria-label="p11 reviewer"
                      value={sourceMetadataForm.reviewer}
                      onChange={(event) => handleP11SourceMetadataFieldChange("reviewer", event.target.value)}
                    />
                  </label>
                  <label className="product-control-p0-panel__p11-field">
                    <span>note</span>
                    <input
                      aria-label="p11 note"
                      value={sourceMetadataForm.note}
                      onChange={(event) => handleP11SourceMetadataFieldChange("note", event.target.value)}
                    />
                  </label>
                  <label className="product-control-p0-panel__p11-field">
                    <span>confirmation</span>
                    <input
                      aria-label="p11 confirmation"
                      value={sourceMetadataForm.confirmation}
                      onChange={(event) => handleP11SourceMetadataFieldChange("confirmation", event.target.value)}
                    />
                  </label>
                  <section
                    className="product-control-p0-panel__p11-field-editor"
                    aria-label="p11 per-field source confirmation editor p11 row human confirmation p11 readable source row labels"
                  >
                    <div>
                      <strong>Per-field source confirmation</strong>
                      <small>逐字段确认 dataset column、source field、source path 和 evidence level；人工勾选后才允许保存。</small>
                    </div>
                    <div className="product-control-p0-panel__p11-field-editor-header" aria-hidden="true">
                      <span>field</span>
                      <span>dataset column</span>
                      <span>source field</span>
                      <span>source path</span>
                      <span>evidence level</span>
                      <span>reviewed</span>
                    </div>
                    {sourceMetadataForm.sourceFieldRows.map((row) => (
                      <div className="product-control-p0-panel__p11-field-row" key={row.field}>
                        <strong>{row.field}</strong>
                        <label className="product-control-p0-panel__p11-row-field product-control-p0-panel__p11-row-field-label">
                          <span>dataset column</span>
                          <input
                            aria-label={`p11 ${row.field} dataset column`}
                            value={row.datasetColumn}
                            onChange={(event) =>
                              handleP11SourceFieldRowChange(row.field, "datasetColumn", event.target.value)
                            }
                          />
                        </label>
                        <label className="product-control-p0-panel__p11-row-field product-control-p0-panel__p11-row-field-label">
                          <span>source field</span>
                          <input
                            aria-label={`p11 ${row.field} source field`}
                            value={row.sourceField}
                            onChange={(event) =>
                              handleP11SourceFieldRowChange(row.field, "sourceField", event.target.value)
                            }
                          />
                        </label>
                        <label className="product-control-p0-panel__p11-row-field product-control-p0-panel__p11-row-field-label">
                          <span>source path</span>
                          <input
                            aria-label={`p11 ${row.field} source path`}
                            value={row.sourcePath}
                            onChange={(event) => handleP11SourceFieldRowChange(row.field, "sourcePath", event.target.value)}
                          />
                        </label>
                        <label className="product-control-p0-panel__p11-row-field product-control-p0-panel__p11-row-field-label">
                          <span>evidence level</span>
                          <input
                            aria-label={`p11 ${row.field} evidence level`}
                            value={row.evidenceLevel}
                            onChange={(event) =>
                              handleP11SourceFieldRowChange(row.field, "evidenceLevel", event.target.value)
                            }
                          />
                        </label>
                        <label className="product-control-p0-panel__p11-row-confirmation">
                          <input
                            type="checkbox"
                            aria-label={`p11 ${row.field} row human confirmation`}
                            checked={row.confirmed}
                            onChange={(event) =>
                              handleP11SourceFieldRowConfirmChange(row.field, event.target.checked)
                            }
                          />
                        </label>
                      </div>
                    ))}
                  </section>
                  <label className="product-control-p0-panel__p11-field product-control-p0-panel__p11-field--wide">
                    <span>parent_education construction</span>
                    <input
                      aria-label="p11 parent_education construction"
                      value={sourceMetadataForm.parentEducationConstruction}
                      onChange={(event) =>
                        handleP11SourceMetadataFieldChange("parentEducationConstruction", event.target.value)
                      }
                    />
                  </label>
                  <details className="product-control-p0-panel__p11-json-preview">
                    <summary>field_bindings JSON preview</summary>
                    <label className="product-control-p0-panel__p11-field product-control-p0-panel__p11-field--wide">
                      <span>field_bindings JSON preview</span>
                      <textarea
                        aria-label="p11 field_bindings"
                        value={sourceMetadataForm.fieldBindingsJson}
                        onChange={(event) => handleP11SourceMetadataFieldChange("fieldBindingsJson", event.target.value)}
                        rows={6}
                      />
                    </label>
                  </details>
                  <section
                    className="product-control-p0-panel__p11-action-bar"
                    aria-label="p11 action bar p11 source contract readiness check"
                  >
                    <div>
                      <strong>Source contract readiness</strong>
                      <span>
                        {p11SourceContractReady ? "ready_to_save_source_contract" : "needs_source_metadata_review"}
                      </span>
                      <small>
                        confirmed rows：{confirmedSourceFieldRows}/{sourceMetadataForm.sourceFieldRows.length}；
                        missing：{p11ReadinessMissingItems.length ? p11ReadinessMissingItems.slice(0, 12).join("；") : "none"}；
                        No model run
                      </small>
                    </div>
                    <button
                      className="btn btn--primary product-control-p0-panel__p11-submit"
                      type="button"
                      onClick={handleSaveProductControlP11SourceMetadataContract}
                      disabled={!p11CanSave}
                    >
                      {sourceMetadataSubmitState === "refreshing" ? "保存中" : "Save source contract"}
                    </button>
                  </section>
                  <small>save_source_metadata_contract_for_p9_formal_save；只更新 editable draft 的 source_contract</small>
                </form>
              </section>
            </div>

            {sourceMetadataError ? (
              <p className="product-control-p0-panel__error" role="alert">
                {sourceMetadataError}
              </p>
            ) : null}
            {sourceMetadataMessage ? (
              <p className="product-control-p0-panel__success" role="status">
                {sourceMetadataMessage}
              </p>
            ) : null}
          </section>
          </div>
        </details>

        <details className="product-control-secondary-workspace product-control-secondary-workspace--p9">
          <summary>
            <span>P9 正式变量表保存</span>
            <strong>{formalVariableRoleSaveReport?.status || "旧门禁复查"}</strong>
          </summary>
          <div
            className="product-control-p0-panel__p9 product-control-current-gate-detail"
            data-testid="product-control-p9-variable-role-formal-save"
          >
          <div>
            <span>P9 正式变量表保存</span>
            <strong>
              {formalVariableRoleSaveReport?.status ||
                (formalVariableRoleSaveState === "loading" ? "读取中" : "p9_formal_variable_role_save_missing")}
            </strong>
            <p>
              draft：{p9LatestDraftId}；dataset：{p9DatasetPath}；can save：
              {formalVariableRoleSaveReport?.can_save_formal_variable_roles ? "true" : "false"}
            </p>
            <small>
              missing_source_metadata_fields：{p9MissingSourceMetadataFields}
            </small>
          </div>
          <form className="product-control-p0-panel__p9-form" onSubmit={(event) => event.preventDefault()}>
            <label className="product-control-p0-panel__p9-field">
              <span>reviewer</span>
              <input
                aria-label="p9 reviewer"
                value={formalVariableRoleSaveForm.reviewer}
                onChange={(event) => handleP9FormalSaveFieldChange("reviewer", event.target.value)}
                disabled={!formalVariableRoleSaveReport?.can_save_formal_variable_roles}
              />
            </label>
            <label className="product-control-p0-panel__p9-field">
              <span>note</span>
              <input
                aria-label="p9 note"
                value={formalVariableRoleSaveForm.note}
                onChange={(event) => handleP9FormalSaveFieldChange("note", event.target.value)}
                disabled={!formalVariableRoleSaveReport?.can_save_formal_variable_roles}
              />
            </label>
            <label className="product-control-p0-panel__p9-field">
              <span>confirmation</span>
              <input
                aria-label="p9 confirmation"
                value={formalVariableRoleSaveForm.confirmation}
                onChange={(event) => handleP9FormalSaveFieldChange("confirmation", event.target.value)}
                disabled={!formalVariableRoleSaveReport?.can_save_formal_variable_roles}
              />
            </label>
            <button
              className="btn btn--primary product-control-p0-panel__p9-submit"
              type="button"
              onClick={handleSaveProductControlP9FormalVariableRoles}
              disabled={!p9CanSave}
            >
              {formalVariableRoleSaveSubmitState === "refreshing" ? "保存中" : "保存正式变量表"}
            </button>
            <small>save_formal_variable_roles_from_p8_approved_draft；不写 DesignSpec；不写 RunPlan；不跑模型</small>
          </form>
          <button
            className="btn btn--ghost product-control-p0-panel__refresh"
            type="button"
            onClick={handleRefreshProductControlP9FormalVariableRoles}
            disabled={!projectId || formalVariableRoleSaveState === "refreshing"}
          >
            <RefreshCcw size={15} aria-hidden="true" />
            <span>{formalVariableRoleSaveState === "refreshing" ? "刷新中" : "刷新 P9"}</span>
          </button>
          {formalVariableRoleSaveError ? (
            <p className="product-control-p0-panel__error" role="alert">
              {formalVariableRoleSaveError}
            </p>
          ) : null}
          {formalVariableRoleSaveMessage ? (
            <p className="product-control-p0-panel__success" role="status">
              {formalVariableRoleSaveMessage}
            </p>
          ) : null}
          </div>
        </details>

        <p className="product-control-p0-panel__boundary">
          {report?.formal_boundary || "不能进入正式论文；P0 只生成审阅层产物，真实文献、数据与变量、方法执行证据仍需补齐。"}
        </p>
        </details>
      </div>
    </section>
  );
}
