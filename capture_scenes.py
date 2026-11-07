import os
import time
from playwright.sync_api import sync_playwright

OUT_DIR = r"e:\Promptwars2026\switchops\video_scenes"
os.makedirs(OUT_DIR, exist_ok=True)

with sync_playwright() as p:
    try:
        browser = p.chromium.launch(channel="chrome", headless=True)
    except Exception:
        browser = p.chromium.launch(channel="msedge", headless=True)

    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    page.goto("http://localhost:8089/index.html")
    page.wait_for_selector("#app")
    time.sleep(1)

    # 1. Base Dashboard
    page.screenshot(path=os.path.join(OUT_DIR, "scene_1_overview.png"))
    print("Captured scene 1: Overview")

    # 2. Template Modal Open
    page.click("#btnViewTemplate")
    time.sleep(0.5)
    page.screenshot(path=os.path.join(OUT_DIR, "scene_2_template_modal.png"))
    page.click("#btnCloseTemplate")
    time.sleep(0.3)
    print("Captured scene 2: Template Modal")

    # 3. Discord Bridge Active
    page.click("#bridgeDiscord")
    time.sleep(0.5)
    page.screenshot(path=os.path.join(OUT_DIR, "scene_3_bridge_discord.png"))
    page.click("#bridgeSlack")
    time.sleep(0.3)
    print("Captured scene 3: Discord Bridge")

    # 4. Stream with Incident & Agent Triage
    page.screenshot(path=os.path.join(OUT_DIR, "scene_4_stream_triage.png"))
    print("Captured scene 4: Stream Triage")

    # 5. Wispr Voice Active (Trigger voice recording visually)
    page.evaluate("document.getElementById('btnVoiceMic').classList.add('recording'); document.getElementById('micBtnText').textContent = 'Listening (Wispr Voice)...';")
    time.sleep(0.3)
    page.screenshot(path=os.path.join(OUT_DIR, "scene_5_wispr_active.png"))
    page.evaluate("document.getElementById('btnVoiceMic').classList.remove('recording'); document.getElementById('micBtnText').textContent = 'Wispr Voice';")
    time.sleep(0.3)
    print("Captured scene 5: Wispr Voice Active")

    # 6. Decisions Log Tab
    page.click("#tabDecisions")
    time.sleep(0.5)
    page.screenshot(path=os.path.join(OUT_DIR, "scene_6_decisions_tab.png"))
    print("Captured scene 6: Decisions Log")

    # 7. Wispr Scorecard Modal
    page.click("#btnWisprScorecard")
    time.sleep(0.5)
    page.screenshot(path=os.path.join(OUT_DIR, "scene_7_wispr_scorecard.png"))
    page.click("#btnCloseWispr")
    time.sleep(0.3)
    print("Captured scene 7: Wispr Scorecard")

    # 8. Tasks Tab
    page.click("#tabTasks")
    time.sleep(0.5)
    page.screenshot(path=os.path.join(OUT_DIR, "scene_8_tasks_tab.png"))
    print("Captured scene 8: Tasks Tab")

    # 9. Protocol SSE Inspector Tab
    page.click("#tabProtocol")
    time.sleep(0.5)
    page.screenshot(path=os.path.join(OUT_DIR, "scene_9_protocol_tab.png"))
    print("Captured scene 9: Protocol Tab")

    # 10. Rules Tab
    page.click("#tabRules")
    time.sleep(0.5)
    page.screenshot(path=os.path.join(OUT_DIR, "scene_10_rules_tab.png"))
    print("Captured scene 10: Rules Tab")

    # 11. Knowledge Runbooks Tab
    page.click("#tabKnowledge")
    time.sleep(0.5)
    page.screenshot(path=os.path.join(OUT_DIR, "scene_11_knowledge_tab.png"))
    print("Captured scene 11: Knowledge Tab")

    browser.close()
    print("All 11 UI scenes captured in pristine 1920x1080!")
