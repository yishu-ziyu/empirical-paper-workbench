# Covariance label observation (not changed)

The actual container Card run `c96fd037-efc9-4ac6-a249-95769cbce028` completed all 12 specifications. Its region OLS reports coefficient `0.07469325559311328`, SE `0.003498345658478739` and metadata `covariance=HC1`, consistent with the historical workbench SE.

The separate package smoke explicitly calls `statspai.feols(..., vcov='HC1')` and produces coefficient `0.07469325559311328`, SE `0.003646247706203475`. `agent/nodes/estimate.py::_fit` supplies only `data` when cluster is absent; it does not pass the HC1 argument. The installed StatsPAI signature defaults `vcov=None`.

These are different estimator call arguments. Do not attribute the SE discrepancy to platform floating point, treat the direct package smoke as historical reproduction, or infer all covariance labels are validated. The existing execution/label consistency question remains separate from this deployment and issue #34; no research-engine behavior or result label was changed here.
