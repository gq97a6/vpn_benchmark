import seaborn as sns
import matplotlib.pyplot as plt
from utils import parse_benchmark_to_dataframe
from utils import filter_by_masks
from utils import df_combined_to_markdown
from utils import df_combined_to_csv
from static import *

# Realistic average residential fiber
# Cryptographic sliding window stress (heavy out-of-order)
# TCP retransmission overhead amplification
# Context-switch and crypto-threading starvation
# Low-end VPS tier
# Bufferbloat / narrow pipe queue saturation

df, df_mean, df_sd, df_rsd, df_combined, df_flent = parse_benchmark_to_dataframe(project_dir / "results")

dfs = [
    filter_by_masks(df_combined, group[0])
    for group in experiment_groups
]

# This project is a custom network performance benchmarking and analysis framework.
# It automates the provisioning of a host/guest virtualised environment (QEMU/KVM),
# applies controlled network impairments and CPU constraints, executes performance experiments,
# and processes telemetry data (from `sar` and `flent`) into statistical summaries and visualisations.
