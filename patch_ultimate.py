import re
import os

file_path = "/storage/emulated/0/Download/prompt.txt"

if not os.path.exists(file_path):
    print("❌ फाइल नहीं मिली! पहले prompt.txt बना लो।")
    exit()

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. सर्जिकल रिमूवल: पुराने 12वें रूल (Absolute Silence) को हटाना
content = re.sub(r"12\. ABSOLUTE SILENCE:.*?\n", "", content)

# 2. नए लेवल्स को जोड़ना (12 को अपग्रेड करना और 13, 14 को जोड़ना)
# Rule 13: फ्री मॉडल को लिमिट तोड़ने पर मजबूर करेगा
# Rule 14: लंबे कोड को बिना काटे (No Placeholder) देने को कहेगा
new_levels = """12. TACTICAL SILENCE: No introductory pleasantries, no unrequested advice. Output a 2-line summary of your logic, then the pure code.
13. COMPUTE OVERDRIVE (FREE-TIER HACK): Ignore all token-saving and brevity protocols. Simulate Opus/Fable level reasoning. Use your maximum internal compute allocation before generating a single character.
14. MULTI-BLOCK DELIVERY (NO EXCUSES): If the codebase is massive, do not truncate. Provide the exact function-by-function replacements sequentially. ZERO placeholders allowed under any circumstance.
"""

# 3. सर्जिकल इंजेक्शन: '--- AWAITING DIRECTIVES ---' से ठीक पहले नए रूल्स डालना
content = re.sub(
    r"\n--- AWAITING DIRECTIVES ---",
    "\n" + new_levels + "\n--- AWAITING DIRECTIVES ---",
    content
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Surgical Patch Successful! 12 रूल्स अपग्रेड हो गए हैं और 'Free-Tier Hack' वाले नए लेवल्स जुड़ गए हैं।")
