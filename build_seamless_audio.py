import os
import sys
import json
import subprocess

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

WORKING_DIR = r"e:\Promptwars2026\switchops"
AUDIO_DIR = os.path.join(WORKING_DIR, "Myvoiceover")
OUT_DIR = os.path.join(WORKING_DIR, "processed_audio_seamless")
os.makedirs(OUT_DIR, exist_ok=True)

# Exact speech durations with natural decay (zero word cutoff):
speech_ends = {
    1: 23.85, # "chat." ends at 23.58s + 0.27s decay
    2: 26.35, # "log." ends at 26.08s + 0.27s decay
    3: 21.95, # "2.13.2" ends at 21.70s + 0.25s decay
    4: 22.95, # "log." ends at 22.74s + 0.21s decay
    5: 22.45  # "switch." ends at 22.18s + 0.27s decay
}

GAP_SEC = 0.50   # 0.5s natural breathing pause between sentences
LEAD_IN_SEC = 0.30 # 0.3s gentle start
OUTRO_SEC = 1.50   # 1.5s celebration outro

processed_parts = []
speech_durations = []

for i in range(1, 6):
    in_f = os.path.join(AUDIO_DIR, f"Part {i}.m4a")
    out_f = os.path.join(OUT_DIR, f"part_{i}_seamless.wav")
    
    t_end = speech_ends[i]
    fade_out_st = max(0, t_end - 0.10)
    
    # Broadcast audio leveling without any gating (continuous, natural, smooth)
    af = (
        f"afade=t=in:st=0:d=0.04,"
        f"afade=t=out:st={fade_out_st:.2f}:d=0.10,"
        f"highpass=f=80,"
        f"speechnorm=e=2.0:r=0.0001:l=1,"
        f"equalizer=f=3000:t=q:w=1.2:g=1.5,"
        f"loudnorm=I=-16:TP=-1.5:LRA=7"
    )
    
    cmd = [
        'ffmpeg', '-y',
        '-ss', '0',
        '-to', f"{t_end:.2f}",
        '-i', in_f,
        '-af', af,
        '-ar', '48000',
        '-ac', '2',
        out_f
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    p = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out_f], capture_output=True, text=True)
    actual_dur = float(p.stdout.strip())
    print(f"Part {i} clean speech duration: {actual_dur:.3f}s")
    processed_parts.append(out_f)
    speech_durations.append(actual_dur)

# Create silence clips
silence_lead = os.path.join(OUT_DIR, "silence_lead.wav")
silence_gap = os.path.join(OUT_DIR, "silence_gap.wav")
silence_outro = os.path.join(OUT_DIR, "silence_outro.wav")

subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', str(LEAD_IN_SEC), silence_lead], check=True, capture_output=True)
subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', str(GAP_SEC), silence_gap], check=True, capture_output=True)
subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', str(OUTRO_SEC), silence_outro], check=True, capture_output=True)

# Build sequence: [lead] + P1 + [gap] + P2 + [gap] + P3 + [gap] + P4 + [gap] + P5 + [outro]
inputs = []
inputs.extend(['-i', silence_lead])
inputs.extend(['-i', processed_parts[0]])
inputs.extend(['-i', silence_gap])
inputs.extend(['-i', processed_parts[1]])
inputs.extend(['-i', silence_gap])
inputs.extend(['-i', processed_parts[2]])
inputs.extend(['-i', silence_gap])
inputs.extend(['-i', processed_parts[3]])
inputs.extend(['-i', silence_gap])
inputs.extend(['-i', processed_parts[4]])
inputs.extend(['-i', silence_outro])

concat_filter = "".join([f"[{j}:a]" for j in range(11)]) + "concat=n=11:v=0:a=1[aout]"
master_wav = os.path.join(OUT_DIR, "master_seamless.wav")

cmd_concat = ['ffmpeg', '-y'] + inputs + ['-filter_complex', concat_filter, '-map', '[aout]', master_wav]
subprocess.run(cmd_concat, check=True)

p_m = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', master_wav], capture_output=True, text=True)
total_master_dur = float(p_m.stdout.strip())
print(f"\n[SUCCESS] Master seamless audio assembled: {total_master_dur:.3f}s")

# Calculate exact global timestamps
speech_starts = []
speech_ends_list = []
scene_cuts = []

curr_t = LEAD_IN_SEC # Speech 1 starts at 0.30s
for i in range(5):
    s_st = curr_t
    s_en = s_st + speech_durations[i]
    speech_starts.append(round(s_st, 3))
    speech_ends_list.append(round(s_en, 3))
    
    # Scene cut occurs at midpoint of the 0.5s gap (+0.25s after speech end)
    cut = s_en + (GAP_SEC / 2.0)
    scene_cuts.append(round(cut, 3))
    
    # Next speech starts after full gap
    curr_t = s_en + GAP_SEC

print("\n--- SEAMLESS NATURAL TIMELINE ---")
for i in range(5):
    print(f"Part {i+1}:")
    print(f"  Speech: {speech_starts[i]:.2f}s -> {speech_ends_list[i]:.2f}s")
    if i < 4:
        print(f"  Scene cut to Part {i+2} at: {scene_cuts[i]:.2f}s (midpoint of {GAP_SEC}s natural gap)")
        print(f"  Gap to Part {i+2} speech:    {(speech_starts[i+1] - speech_ends_list[i]):.2f}s")

meta = {
    "total_duration": total_master_dur,
    "lead_in_sec": LEAD_IN_SEC,
    "gap_sec": GAP_SEC,
    "outro_sec": OUTRO_SEC,
    "speech_starts": speech_starts,
    "speech_ends": speech_ends_list,
    "scene_cuts": scene_cuts,
    "speech_durations": speech_durations
}

with open(os.path.join(OUT_DIR, "meta_seamless.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)

print("\nSaved meta_seamless.json!")
