import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

run_data = pd.read_csv("rundata.csv")
playlist = pd.read_csv("playlist.csv")

# prepare
run_data["secs"] = run_data["Duration"].cumsum()
run_data["spm"] = round(run_data["Cadence"] * 2, 0)

# song start at/bpm change at sec
playlist["duration_seconds"] = playlist["duration"].apply(
    lambda x: sum(int(t) * 60 ** i for i, t in enumerate(reversed(x.split(":"))))
)
playlist["start_seconds"] = playlist["duration_seconds"].cumsum() - playlist["duration_seconds"]

def get_bpm_at_time(secs, play_data):
    # Finde das Lied, dessen Startzeit und Dauer den aktuellen Zeitpunkt abdecken
    for _, row in play_data.iterrows():
        # find song at point in time
        if row["start_seconds"] <= secs < row["start_seconds"] + row["duration_seconds"]:
            return row["bpm"]
    return np.nan  # not found (actually unnecessary)

run_data["bpm"] = run_data["secs"].apply(lambda x: get_bpm_at_time(x, playlist))

# store data (optional)
# data = run_data[["secs", "spm", "bpm", "Pace"]]
# data.to_csv("run_data.csv")

# plot data
fig, ax1 = plt.subplots(figsize=(15, 8))

# primary y axis: spm, bpm
ax1.plot(run_data["secs"], run_data["spm"], label="Steps per Minute (spm)", color="red", alpha=0.7)
ax1.plot(run_data["secs"], run_data["bpm"], label="Beats per Minute (bpm)", color="blue", alpha=0.7)
ax1.set_xlabel("Time (seconds)")
ax1.set_ylabel("Steps per Minute (spm) / Beats per Minute (bpm)")
ax1.set_ybound(100,290)
ax1.legend(loc="lower left")

# secondary y axis: pace (seconds)
ax2 = ax1.twinx()
ax2.plot(run_data["secs"], run_data["Pace"], label="Pace (s/km)", color="green", alpha=0.5)
ax2.set_ylabel("Pace (s/km)")
ax2.set_ybound(200,400)
ax2.legend(loc="lower right")
ax2.invert_yaxis() # the lower the faster

# vertical lines and labels at the times at which the songs begin
for _, row in playlist.iterrows():
    ax1.axvline(x=row["start_seconds"], color="black", linestyle="--", alpha=0.25)
    ax1.text(row["start_seconds"], ax1.get_ylim()[1] * 0.975, row["title"], rotation=90, verticalalignment="top")

ax1.grid(alpha=0.3)
plt.title("spm vs. bpm vs. pace")
plt.tight_layout()
plt.show()