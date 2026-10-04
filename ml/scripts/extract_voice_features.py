"""Extract sustained-vowel features for every VA/VE/VI/VO/VU recording.

Run explore_voice.py first (it writes the path list used here). Output has anonymous subject IDs only.
"""
import sys
from pathlib import Path

import pandas as pd
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.features.voice_features import FEATURE_NAMES, extract_features  # noqa: E402

RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "voice"
OUT = Path(__file__).resolve().parents[1] / "data" / "processed" / "voice_features.csv"

inv = pd.read_pickle("/tmp/voice_inventory_with_paths.pkl")
inv = inv[inv.task.isin(["VA", "VE", "VI", "VO", "VU"])]
rows, failed = [], []
for r in inv.itertuples():
    sig, sr = sf.read(str(RAW / r.path))
    try:
        rows.append({"subject": r.subject, "group": r.group, "task": r.task, "rep": r.rep,
                     "sr_orig": sr, "duration_s": r.duration_s, **extract_features(sig, sr)})
    except ValueError as e:
        failed.append((r.subject, r.task, r.rep, str(e)))
df = pd.DataFrame(rows)
df.to_csv(OUT, index=False)
print(f"extracted {len(df)} of {len(inv)} recordings; failed {len(failed)}")
for f in failed[:20]:
    print("  failed:", f)
print(df.groupby(["group", "task"]).size().unstack().to_string())
print(df.groupby("group")[FEATURE_NAMES].median().round(4).T.to_string())
