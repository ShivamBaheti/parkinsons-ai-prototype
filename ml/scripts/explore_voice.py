"""Inventory of the ItalianPVS recordings. Writes ml/data/processed/voice_inventory.csv.

Subject folders are named after real people, so they are replaced by anonymous IDs (PD01, EHC01,
YHC01) in the output. The mapping is never written to disk.
"""
import re
from pathlib import Path

import pandas as pd
import soundfile as sf

RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "voice"
OUT = Path(__file__).resolve().parents[1] / "data" / "processed" / "voice_inventory.csv"
GROUPS = {"15_Young_Healthy_Control": ("YHC", "young_hc"), "22_Elderly_Healthy_Control": ("EHC", "elderly_hc"),
          "28_People_with_Parkinson_s_disease": ("PD", "pd")}

rows = []
for top, (prefix, group) in GROUPS.items():
    wavs = sorted((RAW / top).rglob("*.wav"))
    subjects = sorted({w.parent for w in wavs})
    ids = {s: f"{prefix}{i + 1:02d}" for i, s in enumerate(subjects)}
    for w in wavs:
        info = sf.info(str(w))
        m = re.match(r"([A-Za-z]+?)(\d)", w.stem)
        rows.append({"subject": ids[w.parent], "group": group, "task": m.group(1).upper() if m else "?",
                     "rep": m.group(2) if m else "?", "path": str(w.relative_to(RAW)),  # path contains names: dropped below
                     "sr": info.samplerate, "channels": info.channels, "subtype": info.subtype, "duration_s": round(info.duration, 2)})
df = pd.DataFrame(rows)
OUT.parent.mkdir(parents=True, exist_ok=True)
df.drop(columns="path").to_csv(OUT, index=False)  # the version with paths stays in memory only
df.to_pickle("/tmp/voice_inventory_with_paths.pkl")

print("recordings per group:\n", df.group.value_counts().to_string())
print("\nsubjects per group:\n", df.groupby("group").subject.nunique().to_string())
print("\nsample rate / channels / subtype:\n", df.groupby(["sr", "channels", "subtype"]).size().to_string())
print("\ntasks per group:\n", df.pivot_table(index="task", columns="group", values="subject", aggfunc="count", fill_value=0).to_string())
v = df[df.task.isin(["VA", "VE", "VI", "VO", "VU"])]
print("\nvowel duration (s) by group:\n", v.groupby("group").duration_s.describe().round(2).to_string())
print("\nvowel recordings per subject (min/median/max):\n", v.groupby(["group", "subject"]).size().groupby("group").agg(["min", "median", "max"]).to_string())
print("\nsubjects missing any vowel:\n", sorted(set(df.subject) - set(v.subject)))
