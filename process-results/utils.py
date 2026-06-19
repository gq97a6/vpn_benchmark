import json
import gzip
import pandas as pd
from pathlib import Path
from static import *
import csv
import io

# def parse_iperf(exp_dir):
#     iperf_data = json.loads((exp_dir / "iperf.json").read_text())
#     return int(iperf_data["end"]["sum_received"]["bits_per_second"] / 1_000_000)

def parse_sar(exp_dir):
    sar_df = pd.read_csv(exp_dir / "cpu.csv", sep=None, engine="python")
    return (100.0 - pd.to_numeric(sar_df["%idle"], errors="coerce")).mean()

def parse_flent(exp_dir):
    # Fetch raw json
    with gzip.open(next(exp_dir.glob("*.flent.gz")), "rt") as f:
        flent_raw = json.load(f)

    # Get results section
    results = flent_raw.get("results", {})
    
    # Get filtered data series
    ping_series = pd.Series([v for v in results.get("Ping (ms) avg", []) if v is not None])
    down_series = pd.Series([v for v in results.get("TCP download sum", []) if v is not None])
    up_series = pd.Series([v for v in results.get("TCP upload sum", []) if v is not None])

    # Extract mean values
    ping = flent_raw.get("metadata", {}).get("SERIES_META", {}).get("Ping (ms) avg", {}).get("MEAN_VALUE", 0)
    down = flent_raw.get("metadata", {}).get("SERIES_META", {}).get("TCP download sum", {}).get("MEAN_VALUE", 0)
    up = flent_raw.get("metadata", {}).get("SERIES_META", {}).get("TCP upload sum", {}).get("MEAN_VALUE", 0)

    return down_series, up_series, ping_series, down, up, ping

def process_experiment(exp_dir: Path, exp_meta: dict) -> tuple[dict, dict]:
    header = {
        "vpn": exp_meta.get("vpn"),
        "bandwidth": exp_meta.get("bandwidth"),
        "delay": exp_meta.get("delay"),
        "jitter": exp_meta.get("jitter"),
        "loss": exp_meta.get("loss"),
        "cpu_freq": exp_meta.get("cpu_freq"),
        "core_count": exp_meta.get("core_count", 0),
    }

    down_series, up_series, ping_series, down, up, ping = parse_flent(exp_dir)

    row = {
        **header,
        "cpu": parse_sar(exp_dir),
        "ping": ping,
        "down": down,
        "up": up,
    }

    row_flent = {
        **header,
        "ping": ping_series,
        "down": down_series,
        "up": up_series,
    }

    return row, row_flent


def parse_benchmark_to_dataframe(results_dir: Path):
    # Get experiment metadata
    with (results_dir / "metadata.json").open("r") as f:
        meta_list = json.load(f)

    # Parse results
    rows, rows_flent = [], []
    for idx, meta in enumerate(meta_list):
        row, flent_row = process_experiment(results_dir / str(idx), meta)
        rows.append(row)
        rows_flent.append(flent_row)

    # Create dataframes
    df = pd.DataFrame(rows)
    df_flent = pd.DataFrame(rows_flent)

    # Clean strings to numbers
    for adf in df, df_flent:
        adf["bandwidth"] = adf["bandwidth"].astype(str).str.replace("mbit", "", regex=False).astype(int)
        adf["delay"] = adf["delay"].astype(str).str.replace("ms", "", regex=False).astype(int)
        adf["jitter"] = adf["jitter"].astype(str).str.replace("ms", "", regex=False).astype(int)
        adf["loss"] = adf["loss"].astype(str).str.replace("%", "", regex=False).astype(float)
        adf["cpu_freq"] = adf["cpu_freq"].astype(str).str.replace("GHz", "", regex=False).astype(float)

    # Enchance
    df["efficiency"] = (df["down"] + df["up"]) / df["cpu"]

    # Group reruns of same experiment
    grouped = df.groupby(key_cols)

    # Aggregate reruns
    df_mean = grouped.mean()
    df_sd = grouped.std()
    df_rsd = (df_sd / df_mean).round(4)
    df_combined = (
        df_mean.join(df_sd, lsuffix="_mean", rsuffix="_sd")
        .join(df_rsd.add_suffix("_rsd"))
        .reset_index()
    )

    return (
        df,
        df_mean.reset_index(),
        df_sd.reset_index(),
        df_rsd.reset_index(),
        df_combined,
        df_flent
    )

def df_combined_to_markdown(
    df_combined: pd.DataFrame,
    group_cols: list[str] = key_cols,
    units: dict[str, str] = {},
    precision: int = 1,
    sd_thresholds: dict[str, float] = {},
    rsd_threshold: float = 0.15,
) -> str:
    metrics = [c[:-5] for c in df_combined.columns if c.endswith("_mean")]

    headers = list(group_cols)
    for m in metrics:
        headers += [m, "", ""]

    lines = ["| " + " | ".join(headers) + " |",
             "| " + " | ".join("---" for _ in headers) + " |"]

    for _, r in df_combined.iterrows():
        cells = [str(r[g]) for g in group_cols]
        for m in metrics:
            mean, sd, rsd = r.get(f"{m}_mean"), r.get(f"{m}_sd"), r.get(f"{m}_rsd")
            unit = units.get(m, "")
            if pd.isna(mean):
                cells += ["—", "", ""]
                continue

            mean_s = f"{mean:.{precision}f}{unit}"
            #sd_s = "—" if pd.isna(sd) else f"± {sd:.{precision}f}"
            sd_s = "—" if pd.isna(sd) else f"{sd:.{precision}f}"
            rsd_s = "—" if pd.isna(rsd) else f"{rsd * 100:.0f}%"

            sd_bad = (m in sd_thresholds and not pd.isna(sd) and sd > sd_thresholds[m])
            rsd_bad = not pd.isna(rsd) and rsd > rsd_threshold

            if sd_bad and rsd_bad:
                mean_s = f"🔴 {mean_s}"
            else:
                mean_s = f"🟢 {mean_s}"

            cells += [mean_s, sd_s, rsd_s]
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)

def df_combined_to_csv(
    df_combined: pd.DataFrame,
    group_cols: list[str] = key_cols,
    units: dict[str, str] = {},
    precision: int = 1
) -> str:
    metrics = [c[:-5] for c in df_combined.columns if c.endswith("_mean")]

    headers = list(group_cols)
    for m in metrics:
        headers += [f"{m}_mean", f"{m}_sd", f"{m}_rsd"]

    output = io.StringIO()
    # Delimiter set to semicolon
    writer = csv.writer(output, delimiter=";", lineterminator="\n")
    writer.writerow(headers)

    for _, r in df_combined.iterrows():
        cells = [str(r[g]) for g in group_cols]
        for m in metrics:
            mean, sd, rsd = (
                r.get(f"{m}_mean"),
                r.get(f"{m}_sd"),
                r.get(f"{m}_rsd"),
            )

            if pd.isna(mean):
                cells += ["—", "", ""]
                continue

            mean_s = f"{mean:.{precision}f}{units.get(m, '')}"
            sd_s = "—" if pd.isna(sd) else f"{sd:.{precision}f}"
            rsd_s = "—" if pd.isna(rsd) else f"{rsd * 100:.0f}%"

            cells += [mean_s, sd_s, rsd_s]

        writer.writerow(cells)

    return output.getvalue()

def filter_by_mask(df, mask):
    return df[
        (df['bandwidth'] == mask[0]) &
        (df['delay'] == mask[1]) &
        (df['jitter'] == mask[2]) &
        (df['loss'] == mask[3]) &
        (df['cpu_freq'] == mask[4]) &
        (df['core_count'] == mask[5])
    ]