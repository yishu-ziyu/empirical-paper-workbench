# Hard bars（可测试）

> 上级：[econpaper 论文发动机：数字先于正文](../paper-engine.md)


方向已设且 CSV 含点名列：

1. `identification_diag` 已在，`body_chapters` 仍空。method 为 ols 时：`star_rating is None` 且 `claim_mode=="association"`。这算通过。0 只用于因果诊断全失败。  
2. `estimate.produced_by=="estimate"` 且 `treatment_row` 已在，结果章尚未生成。  
3. `_robustness_ran` 为真之后，才允许写入 `type=="results"`。引言在识别之后即可写。  
4. 结果章 `content` 含 `treatment_row`；mock 另造不同系数表则接地失败。  
5. pytest / `ECONPAPER_LLM=mock` 全 mock；运行时有 MiniMax key 则 MiniMax。  
6. OLS 方法章夹具：≥200 字、含 `$y_i=\\alpha+\\beta D_i+u_i$`、不含 `因果` / `识别策略` / `解决内生性`。`check_structure==[]`；`mock_review` 的 endogeneity=identification=0.7；综合分 ≥ 0.7；`review_chapter` **不**回退 idx。

---
