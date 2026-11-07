import os
import sys
import cv2
import json
import time
import math
import numpy as np
import subprocess
from PIL import Image, ImageDraw, ImageFont

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

WIDTH = 1920
HEIGHT = 1080
FPS = 30

WORKING_DIR = r"e:\Promptwars2026\switchops"
SCENES_DIR = os.path.join(WORKING_DIR, "video_scenes")
AUDIO_MASTER = os.path.join(WORKING_DIR, "processed_audio_seamless", "master_seamless.wav")
AUDIO_META = os.path.join(WORKING_DIR, "processed_audio_seamless", "meta_seamless.json")
OUTPUT_TEMP_VIDEO = os.path.join(WORKING_DIR, "temp_video_seamless.mp4")
OUTPUT_FINAL_VIDEO = os.path.join(WORKING_DIR, "switchops_final_submission_demo.mp4")

with open(AUDIO_META, "r", encoding="utf-8") as f:
    meta = json.load(f)

master_dur = meta["total_duration"]
total_frames = int(round(master_dur * FPS))
print(f"Master seamless duration: {master_dur:.3f}s | Total frames: {total_frames} @ {FPS} FPS")

# Fonts
FONT_BOLD_PATH = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG_PATH = "C:/Windows/Fonts/segoeui.ttf"
FONT_MONO_PATH = "C:/Windows/Fonts/consolab.ttf"

font_caption = ImageFont.truetype(FONT_BOLD_PATH, 34)
font_badge = ImageFont.truetype(FONT_BOLD_PATH, 20)
font_hud_bold = ImageFont.truetype(FONT_BOLD_PATH, 24)
font_mono = ImageFont.truetype(FONT_MONO_PATH, 20)

# Load UI scene screenshots
scenes = {
    "overview": cv2.imread(os.path.join(SCENES_DIR, "scene_1_overview.png")),
    "template": cv2.imread(os.path.join(SCENES_DIR, "scene_2_template_modal.png")),
    "discord": cv2.imread(os.path.join(SCENES_DIR, "scene_3_bridge_discord.png")),
    "triage": cv2.imread(os.path.join(SCENES_DIR, "scene_4_stream_triage.png")),
    "wispr": cv2.imread(os.path.join(SCENES_DIR, "scene_5_wispr_active.png")),
    "decisions": cv2.imread(os.path.join(SCENES_DIR, "scene_6_decisions_tab.png")),
    "scorecard": cv2.imread(os.path.join(SCENES_DIR, "scene_7_wispr_scorecard.png")),
    "tasks": cv2.imread(os.path.join(SCENES_DIR, "scene_8_tasks_tab.png")),
    "protocol": cv2.imread(os.path.join(SCENES_DIR, "scene_9_protocol_tab.png")),
    "rules": cv2.imread(os.path.join(SCENES_DIR, "scene_10_rules_tab.png")),
    "knowledge": cv2.imread(os.path.join(SCENES_DIR, "scene_11_knowledge_tab.png")),
    "showcase": cv2.imread(os.path.join(WORKING_DIR, "switchops_showcase.jpg"))
}

# Ensure all images are 1920x1080
for k in scenes:
    if scenes[k] is not None and (scenes[k].shape[1] != WIDTH or scenes[k].shape[0] != HEIGHT):
        scenes[k] = cv2.resize(scenes[k], (WIDTH, HEIGHT), interpolation=cv2.INTER_LANCZOS4)

# Continuous, naturally synced captions
TIMED_CAPTIONS = [
    # Part 1 (Speech: 0.30s -> 24.15s)
    (0.30, 6.42, "Hey everyone! This is our submission for the Flip the Switch Hackathon in Track 1:"),
    (6.42, 8.14, "Best Business Workflow."),
    (8.14, 13.10, "Solo AI coding agents in terminals are great, but when a critical P0 outage strikes at 3:00 AM..."),
    (13.10, 19.90, "...engineering is collaborative. Fragmented alerts across Datadog, GitHub, and Slack cause chaos."),
    (19.90, 24.15, "We built SwitchOps to bring agents directly into team chat."),
    
    # Part 2 (Speech: 24.65s -> 51.00s)
    (24.65, 32.55, "Using open-source Switch, we transformed Slack channel #incidents-production into a shared room."),
    (32.55, 38.97, "Notice how human teammates Priya, Sam, and Alex share the room with three specialized agents:"),
    (38.97, 44.65, "@SwitchTriager, @InfraOps, and @HotfixCoder."),
    (44.65, 51.00, "They all read from the exact same shared memory, tasks, and decision log."),
    
    # Part 3 (Speech: 51.50s -> 73.45s)
    (51.50, 54.96, "Sam reports checkout API 500 errors."),
    (54.96, 60.90, "Instantly, @SwitchTriager analyzes the logs and flags Postgres connection pool exhaustion."),
    (60.90, 69.44, "Then @InfraOps inspects recent deployments, pinpoints the faulty commit in release v2.14.0..."),
    (69.44, 73.45, "...and prepares our rollback manifest to version v2.13.2."),
    
    # Part 4 (Speech: 73.95s -> 96.90s)
    (73.95, 80.79, "Because Switch strictly enforces Rule-01, agents cannot touch production without human sign-off."),
    (80.79, 87.97, "Priya taps her Wispr Flow key and dictates: 'Approved. Roll back cart-service to version v2.13.2.'"),
    (87.97, 93.95, "Wispr Flow transcribes it 4 times faster than typing, and Switch records the cryptographic..."),
    (93.95, 96.90, "...hash in the immutable Decisions Log."),
    
    # Part 5 (Speech: 97.40s -> 119.85s)
    (97.40, 105.32, "@HotfixCoder executes the rollback, connection pool drops from 100% to 14%, latency..."),
    (105.32, 111.26, "...drops back to 48ms, and the blameless post-mortem is automatically synthesized."),
    (111.26, 116.86, "SwitchOps turns solo agents into your team's most dependable production allies."),
    (116.86, 119.85, "Thank you WeMakeDevs and Switch!")
]

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    curr = []
    for w in words:
        test_line = " ".join(curr + [w])
        bbox = font.getbbox(test_line)
        if (bbox[2] - bbox[0]) <= max_width:
            curr.append(w)
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))
    return lines

def get_active_caption(t):
    for start, end, cap in TIMED_CAPTIONS:
        if start <= t < end:
            return cap
    return ""

def zoom_frame(img, factor=1.0, cx=0.5, cy=0.5):
    if factor <= 1.001:
        return img
    h, w = img.shape[:2]
    crop_w = int(w / factor)
    crop_h = int(h / factor)
    x1 = max(0, min(w - crop_w, int(cx * w - crop_w / 2)))
    y1 = max(0, min(h - crop_h, int(cy * h - crop_h / 2)))
    cropped = img[y1:y1 + crop_h, x1:x1 + crop_w]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

# Visual Scene Timeline with natural continuous transitions (cut at 0.5s pause midpoint)
SCENE_TIMELINE = [
    # CHAPTER 1: INTRO & ARCHITECTURE (0.00s - 24.40s)
    (0.00, 8.14, "overview", 1.00, 1.04, 0.50, 0.40, "SwitchOps: Autonomous Incident War Room & Release Escort", "TRACK 01: $2,000"),
    (8.14, 17.50, "triage", 1.00, 1.05, 0.45, 0.35, "The Problem: Solo Agents in Terminal Isolation During 3:00 AM Outages", "INCIDENT CRISIS"),
    (17.50, 24.40, "overview", 1.00, 1.04, 0.50, 0.50, "Switch Solution: Bringing Coding Agents Directly into Team Chat", "SHARED ROOM"),
    
    # CHAPTER 2: SWITCH ROOMS & TEMPLATE (24.40s - 51.25s)
    (24.40, 32.55, "discord", 1.00, 1.05, 0.50, 0.40, "Switch Room: Shared Workspace Across Slack, Teams, Discord & Telegram", "MULTI-BRIDGE"),
    (32.55, 44.65, "template", 1.00, 1.04, 0.50, 0.50, "Switch Console Template: 3 Specialized Autonomous Agents + 3 Humans", "TEMPLATE YAML"),
    (44.65, 51.25, "overview", 1.02, 1.06, 0.20, 0.45, "Room Shared Memory: Unified Messages, Tasks, Rules & Decision Log", "ROOM PROTOCOL"),
    
    # CHAPTER 3: LIVE INCIDENT TRIAGE (51.25s - 73.70s)
    (51.25, 54.96, "triage", 1.02, 1.06, 0.45, 0.35, "P0 Alert: Checkout API 500 Spike & 4,200ms Latency Degradation", "P0 BLOCKER"),
    (54.96, 60.90, "triage", 1.06, 1.10, 0.48, 0.45, "@SwitchTriager AI: Cart-Service Connection Pool Exhaustion Detected", "CLAUDE CODE"),
    (60.90, 73.70, "overview", 1.03, 1.08, 0.70, 0.40, "@InfraOps Sentry: Correlates Commit a9f24e1 & Prepares Rollback v2.13.2", "ANTIGRAVITY"),
    
    # CHAPTER 4: RULE-01 & WISPR FLOW (73.70s - 97.15s)
    (73.70, 80.79, "rules", 1.00, 1.04, 0.50, 0.40, "Switch Rule-01: Zero Production Mutation Without Human Sign-Off", "RULE-01 ENFORCED"),
    (80.79, 87.97, "wispr", 1.00, 1.05, 0.50, 0.65, "Wispr Flow Voice Dictation: Spoken Rollback Approval (4.2x Faster)", "CODE WITH WISPR"),
    (87.97, 93.95, "scorecard", 1.00, 1.04, 0.50, 0.50, "Wispr Flow Usage Scorecard: 1,842 Words Dictated • 99.4% Accuracy", "$500 SIDE TRACK"),
    (93.95, 97.15, "decisions", 1.00, 1.04, 0.50, 0.40, "Immutable Decision Log (DEC-2026-01): Cryptographic Voice Sign-Off", "AUDIT TRAIL"),
    
    # CHAPTER 5: AUTONOMOUS RESOLUTION (97.15s - 119.85s)
    (97.15, 105.32, "overview", 1.04, 1.08, 0.82, 0.35, "Autonomous Rollback: v2.13.2 Deployed, Latency Restored to 48ms", "HOTFIX CODEX"),
    (105.32, 111.26, "tasks", 1.00, 1.04, 0.50, 0.40, "Room Task Board: All 5/5 Tasks Resolved & Post-Mortem Synthesized", "AUTONOMOUS OPS"),
    (111.26, 116.86, "protocol", 1.00, 1.05, 0.50, 0.50, "Switch Agent Protocol: Live Server-Sent Events (SSE) Inspection", "AGENT PROTOCOL"),
    (116.86, 119.85, "showcase", 1.00, 1.03, 0.50, 0.50, "SwitchOps: Turn Your Solo Agent into a Teammate • WeMakeDevs 2026", "FLIP THE SWITCH"),
    
    # CELEBRATION OUTRO (119.85s - 121.35s)
    (119.85, 121.35, "showcase", 1.03, 1.06, 0.50, 0.50, "WeMakeDevs Flip the Switch Hackathon • Track 1 & Wispr Flow Winner", "SUBMISSION READY")
]

def get_scene_params(t):
    for start, end, key, z_start, z_end, cx, cy, hud_title, hud_badge in SCENE_TIMELINE:
        if start <= t <= end:
            progress = (t - start) / max(0.01, end - start)
            zoom = z_start + (z_end - z_start) * progress
            return key, zoom, cx, cy, hud_title, hud_badge
    return "overview", 1.0, 0.5, 0.5, "SwitchOps War Room", "DEMO"

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(OUTPUT_TEMP_VIDEO, fourcc, FPS, (WIDTH, HEIGHT))

print("Rendering seamless video frames with natural 0.5s transition flow...", flush=True)
t0 = time.time()

for f_idx in range(total_frames):
    t = f_idx / FPS
    
    key, zoom, cx, cy, hud_title, hud_badge = get_scene_params(t)
    base_img = scenes.get(key, scenes["overview"])
    
    frame = zoom_frame(base_img, factor=zoom, cx=cx, cy=cy)
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil, "RGBA")
    
    # -------------------------------------------------------------
    # 1. TOP HUD BANNER
    # -------------------------------------------------------------
    hud_h = 56
    draw.rectangle([(0, 0), (WIDTH, hud_h)], fill=(15, 23, 42, 220))
    draw.line([(0, hud_h), (WIDTH, hud_h)], fill=(226, 232, 240, 60), width=1)
    
    badge_bg = (16, 185, 129, 230) if "TRACK" in hud_badge or "2026" in hud_badge or "READY" in hud_badge else (59, 130, 246, 230)
    if "P0" in hud_badge or "CRISIS" in hud_badge:
        badge_bg = (244, 63, 94, 230)
    elif "WISPR" in hud_badge:
        badge_bg = (139, 92, 246, 230)
        
    draw.rounded_rectangle([(24, 12), (24 + 215, 44)], radius=16, fill=badge_bg)
    draw.text((36, 16), hud_badge, font=font_badge, fill=(255, 255, 255, 255))
    draw.text((256, 15), hud_title, font=font_hud_bold, fill=(255, 255, 255, 255))
    
    time_str = f"{int(t // 60):02d}:{int(t % 60):02d} / {int(master_dur // 60):02d}:{int(master_dur % 60):02d}"
    draw.text((WIDTH - 180, 16), time_str, font=font_mono, fill=(148, 163, 184, 255))
    
    # -------------------------------------------------------------
    # 2. NETFLIX / YOUTUBE STYLE CAPTION (Pure White, Centered, Stroke + Dark Box)
    # -------------------------------------------------------------
    caption = get_active_caption(t)
    if caption:
        cap_lines = wrap_text(caption, font_caption, WIDTH - 280)
        line_height = 42
        
        line_widths = []
        for l in cap_lines:
            bbox = font_caption.getbbox(l)
            line_widths.append(bbox[2] - bbox[0])
            
        max_line_w = max(line_widths) if line_widths else 300
        pill_pad_x = 24
        pill_pad_y = 12
        pill_w = max_line_w + pill_pad_x * 2
        pill_h = len(cap_lines) * line_height + pill_pad_y * 2
        
        pill_x = (WIDTH - pill_w) // 2
        pill_y = HEIGHT - pill_h - 48
        
        # Translucent dark backing box
        draw.rounded_rectangle(
            [(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)],
            radius=12,
            fill=(10, 15, 26, 215),
            outline=(255, 255, 255, 40),
            width=1
        )
        
        # Pure white text with 3px solid black stroke
        for i, l in enumerate(cap_lines):
            l_w = line_widths[i]
            l_x = (WIDTH - l_w) // 2
            l_y = pill_y + pill_pad_y + i * line_height
            
            draw.text(
                (l_x, l_y),
                l,
                font=font_caption,
                fill=(255, 255, 255, 255),
                stroke_width=3,
                stroke_fill=(0, 0, 0, 255)
            )

    frame_final = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    out.write(frame_final)
    
    if (f_idx + 1) % 400 == 0 or (f_idx + 1) == total_frames:
        pct = (f_idx + 1) / total_frames * 100
        print(f"Rendered {f_idx + 1}/{total_frames} frames ({pct:.1f}%) in {time.time() - t0:.1f}s", flush=True)

out.release()
print(f"Raw video rendered in {time.time() - t0:.1f}s!", flush=True)

# Mux audio and video using FFmpeg
print("Muxing video with seamless master audio...", flush=True)
cmd_mux = [
    'ffmpeg', '-y',
    '-i', OUTPUT_TEMP_VIDEO,
    '-i', AUDIO_MASTER,
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '19',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '256k',
    '-shortest',
    OUTPUT_FINAL_VIDEO
]

subprocess.run(cmd_mux, check=True)
print(f"[SUCCESS] FINAL SEAMLESS NATURAL DEMO VIDEO READY: {OUTPUT_FINAL_VIDEO}", flush=True)

if os.path.exists(OUTPUT_TEMP_VIDEO):
    try:
        os.remove(OUTPUT_TEMP_VIDEO)
    except Exception:
        pass
