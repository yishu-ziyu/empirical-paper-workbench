# Dataset Motherlode Index Review

- 题目：工业机器人对劳动力市场匹配效率的影响
- 状态：needs_human_dataset_index_review
- 数据源：primary_local_dataset_motherlode
- 路径：/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库
- 边界：read_only / local_only / user_provided_public_dataset_pool
- 正式层写回：否

## 候选数据绑定
- 外部源数据 | score=46 | years=1911, 1914, 1993, 2000, 2001, 2002, 2006, 2007, 2011, 2012, 2013, 2014, 2015, 2016, 2018, 2019, 2020, 2022, 2023, 2024, 2026 | reasons=ifr, robot, 工业机器人, 机器人, cfps, clds, 劳动, 劳动力, 匹配, 就业, 工资
- A005CLDS中国劳动力动态调查数据 | score=12 | years=1911, 2011, 2012, 2014, 2015, 2016, 2018, 2019 | reasons=clds, 劳动, 劳动力
- A001CFPS中国家庭追踪调查 | score=4 | years=2010, 2011, 2012, 2014, 2015, 2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | reasons=cfps
- A004CGSS中国综合社会调查 | score=4 | years=2012, 2013, 2015, 2017, 2018, 2021, 2023 | reasons=cfps
- A019-中国流动人口动态监测CMDS数据2011-2018年 | score=4 | years=2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018 | reasons=cmds

## 数据族概览
- A001CFPS中国家庭追踪调查: 64 files, 4260828917 bytes, .dta, .md, .pdf, .sav, .xlsx, years=2010, 2011, 2012, 2014, 2015, 2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024
- A004CGSS中国综合社会调查: 40 files, 468844884 bytes, .dta, .md, .pdf, .rar, .sav, .txt, .xls, .xlsx, years=2012, 2013, 2015, 2017, 2018, 2021, 2023
- A005CLDS中国劳动力动态调查数据: 112 files, 3253689596 bytes, .do, .doc, .docx, .dta, .md, .pdf, .sav, .txt, years=1911, 2011, 2012, 2014, 2015, 2016, 2018, 2019
- A019-中国流动人口动态监测CMDS数据2011-2018年: 59 files, 3538291965 bytes, .csv, .dta, .pdf, .sav, .txt, .xls, .xlsx, years=2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018
- 外部源数据: 147 files, 3040555463 bytes, .csv, .do, .doc, .docx, .dta, .md, .pdf, .rar, .sav, .txt, .xlsx, .zip, years=1911, 1914, 1993, 2000, 2001, 2002, 2006, 2007, 2011, 2012, 2013, 2014, 2015, 2016, 2018, 2019, 2020, 2022, 2023, 2024, 2026

## 边界确认
- 修改原始数据：False
- 修改正式论文：False
- 修改正式 bibliography：False
- 修改 run plan：False

## 下一步
- 人工审阅候选数据绑定。
- 对入选数据族运行字段级 profiling。
- 生成项目级 DatasetBinding proposal，仍不写正式层。
