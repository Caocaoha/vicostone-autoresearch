# Vicostone Sentiment Monitor — AutoResearch

**GPU:** NVIDIA T4 16GB (Google Colab Free)  
**Metric:** composite_sentiment_score (higher = better)  
**Inspired by:** [karpathy/autoresearch](https://github.com/karpathy/autoresearch)

---

## Mục Tiêu

Tối ưu hóa Vicostone Sentiment Monitor bằng cách thử nghiệm các parameters và đánh giá kết quả tự động mỗi ngày.

---

## Cấu Trúc

```
vicostone-autoresearch/
├── vicostone_monitor.py      # Main module
├── experiment.py              # Experiment loop
├── parameters.py              # Parameter definitions
├── metrics.py                # Composite score calculation
├── requirements.txt          # Dependencies
└── memory/
    └── vicostone-sentiment/
        ├── daily/            # Daily data
        ├── charts/           # Generated charts
        └── experiment_log.tsv  # Experiment tracking
```

---

## Quick Start (Google Colab)

```python
# Clone repo
!git clone https://github.com/Caocaoha/vicostone-autoresearch.git
%cd vicostone-autoresearch

# Setup API key
import os
os.environ['PERPLEXITY_API_KEY'] = 'YOUR-KEY-HERE'

# Run baseline
from vicostone_monitor import VicostoneExperiment
exp = VicostoneExperiment()
baseline = exp.run_baseline()
print(f"Baseline: {baseline}")

# Run autonomous loop
exp.autonomous_loop(days=7)
```

---

## Parameters Để Tune

| Parameter | Default | Range | Priority |
|-----------|---------|-------|----------|
| perplexity_queries | 15 | 10-20 | 🔴 Cao |
| forums_to_check | 6 | 4-10 | 🟡 Trung |
| min_review_length | 20 | 10-50 | 🟡 Trung |

---

## Composite Score Formula

```
composite_score = (
    avg_sentiment * 0.4 +
    sqrt(sources) / sqrt(30) * 0.3 +
    (1 - std/4) * 0.3
)
```

---

## Experiment Log

Lưu tại: `memory/vicostone-sentiment/experiment_log.tsv`

| Cột | Mô tả |
|-----|---------|
| date | Ngày experiment |
| param_changed | Parameter thay đổi |
| old_value → new_value | Giá trị trước/sau |
| composite_score | Kết quả |
| status | improved/neutral/reverted |

---

## Tài Liệu Tham Khảo

- [Karpathy AutoResearch](https://github.com/karpathy/autoresearch)
- [Karpathy NanoChat](https://github.com/karpathy/nanochat)
- [Google Colab](https://colab.research.google.com)
