from utils import parse_benchmark_to_dataframe
from utils import filter_by_masks
from utils import df_combined_to_markdown
from utils import df_combined_to_csv
from static import *

df, df_mean, df_sd, df_rsd, df_combined, df_flent = parse_benchmark_to_dataframe(project_dir / "results")

output_dir = project_dir / "outputs"
output_dir.mkdir(parents=True, exist_ok=True)

for mask, sort_cols, filename in experiment_groups:
    sdf = filter_by_masks(df_combined, mask).sort_values(by=sort_cols, ascending=False)

    csv_data = df_combined_to_csv(sdf)
    md_data = df_combined_to_markdown(sdf, sd_thresholds=thresholds, rsd_threshold=0.15)

    (output_dir / f"{filename}.csv").write_text(csv_data, encoding="utf-8")
    (output_dir / f"{filename}.md").write_text(md_data, encoding="utf-8")

# Dump combined views
combined_csv = df_combined_to_csv(df_combined)
combined_md = df_combined_to_markdown(df_combined.sort_values(by=key_cols, ascending=False), sd_thresholds=thresholds, rsd_threshold=0.15)
(output_dir / "combined.csv").write_text(combined_csv, encoding="utf-8")
(output_dir / "combined.md").write_text(combined_md, encoding="utf-8")

# Dump raw views
raw_md = df.round(2).sort_values(by=key_cols, ascending=False).to_markdown()
(output_dir / "raw.md").write_text(raw_md, encoding="utf-8")