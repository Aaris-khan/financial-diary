import sys
import re
import os

def main():
    target_file = 'index.html'
    if not os.path.exists(target_file):
        print(f"Error: {target_file} not found.")
        sys.exit(1)

    with open(target_file, 'r', encoding='utf-8') as f:
        code = f.read()

    if "PHANTOM PEN DRIVE BOOTLOADER" in code:
        print("✅ Logic is already present. Skipping injection.")
        return

    # 1. THE PHANTOM BOOTLOADER & LONG-PRESS ENGINE
    engine_code = """
// ========================== PHANTOM PEN DRIVE BOOTLOADER & ENGINE ==========================
window.__PHANTOM_ACTIVE = false;
function initPhantomBootloader() {
    const params = new URLSearchParams(window.location.search);
    const pType = params.get('phantom');
    const pName = params.get('pname');
    const pData = params.get('data');

    if (pType && pName && pData) {
        window.__PHANTOM_ACTIVE = true;
        try {
            const decodedStr = decodeURIComponent(atob(pData));
            const parsedData = JSON.parse(decodedStr);

            document.addEventListener('DOMContentLoaded', () => {
                // 1. App Boot Bypassing
                const loginScreen = document.getElementById('login-screen');
                const mainApp = document.getElementById('main-app');
                if(loginScreen) loginScreen.style.display = 'none';
                if(mainApp) mainApp.classList.remove('hidden');

                // 2. CSS Nuclear Lockdown
                const style = document.createElement('style');
                style.innerHTML = `
                    button[onclick*="save"], button[onclick*="delete"], button[onclick*="Modal"],
                    .action-btn, .btn-ios-add, .milk-detail-delete-core-btn,
                    .credit-delete-btn-core, .credit-add-btn-core, .credit-profile-delete-btn-core,
                    .salary-profile-delete-btn-core, .salary-delete-btn-core,
                    .business-delete-btn-core, #expense-add-btn-core { display: none !important; pointer-events: none !important; }
                    .bottom-nav { display: none !important; }
                    .header-sticky button i.fa-chevron-left { display: none !important; }
                    .screen { padding-bottom: 24px !important; }
                    .phantom-badge { display: inline-block; background: rgba(155, 114, 203, 0.2); color: #9b72cb; padding: 4px 10px; border-radius: 12px; font-size: 10px; font-weight: 800; border: 1px solid rgba(155, 114, 203, 0.4); margin-left: 8px; vertical-align: middle; text-shadow: none !important; }
                `;
                document.head.appendChild(style);

                // 3. Backend Mutators Neutered
                window.aarishFirebaseLaterV48 = async () => false;
                window.flushFirebaseWriteOutboxV87 = async () => false;
                window.aarishFirebaseBatchLaterV87 = async () => { return {queued: false}; };

                // 4. Inject Payload into RAM
                if (pType === 'milk') {
                    window.milkDB = {};
                    window.milkDB[pName] = parsedData;
                    window.activeMilkCustomer = pName;
                    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
                    document.getElementById('milk-detail-screen').classList.add('active');
                    const titleEl = document.getElementById('milk-detail-title');
                    if(titleEl) titleEl.innerHTML = `${pName} <span class="phantom-badge">LIVE SNAPSHOT</span>`;
                    if(typeof renderMilkRecords === 'function') renderMilkRecords();
                } else if (pType === 'udhar') {
                    window.udharDB = parsedData;
                    window.activeUdharPerson = pName;
                    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
                    document.getElementById('udhar-detail-screen').classList.add('active');
                    const titleEl = document.getElementById('udhar-detail-title');
                    if(titleEl) titleEl.innerHTML = `${pName} <span class="phantom-badge">LIVE SNAPSHOT</span>`;
                    if(typeof renderUdharRecords === 'function') renderUdharRecords();
                }
                
                if(typeof hideLoader === 'function') hideLoader();
                setTimeout(() => { if(typeof showToast === 'function') showToast("Offline Snapshot: View Only"); }, 800);
            });
            return true;
        } catch (e) {
            alert("Corrupted Snapshot Link!");
        }
    }
    return false;
}
initPhantomBootloader();

window.__aarishLongPressTimer = null;
window.__aarishIsLongPressActive = false;

window.aarishStartCardHold = function(type, name) {
    window.__aarishIsLongPressActive = false;
    if (window.__aarishLongPressTimer) clearTimeout(window.__aarishLongPressTimer);
    window.__aarishLongPressTimer = setTimeout(() => {
        window.__aarishIsLongPressActive = true;
        try { if (navigator.vibrate) navigator.vibrate([80, 50, 80]); } catch(e) {}
        aarishGeneratePenDriveSnapshotLink(type, name);
    }, 1500); 
};

window.aarishCancelCardHold = function() {
    if (window.__aarishLongPressTimer) {
        clearTimeout(window.__aarishLongPressTimer);
        window.__aarishLongPressTimer = null;
    }
};

window.aarishGeneratePenDriveSnapshotLink = function(type, name) {
    let dataToShare = null;
    if (type === 'milk') {
        if (!milkDB[name] || !milkDB[name].records || milkDB[name].records.length === 0) {
            return showToast("No records found to generate snapshot!");
        }
        dataToShare = milkDB[name];
    } else if (type === 'udhar') {
        const records = (typeof creditEntriesCoreV1 === 'function' ? creditEntriesCoreV1() : udharDB).filter(u => String(u.name || '').trim() === String(name || '').trim());
        if (records.length === 0) {
            return showToast("No credit records found to generate snapshot!");
        }
        dataToShare = records;
    }

    try {
        const minified = JSON.stringify(dataToShare);
        const encoded = btoa(encodeURIComponent(minified));
        const link = window.location.origin + window.location.pathname + "?phantom=" + encodeURIComponent(type) + "&pname=" + encodeURIComponent(name) + "&data=" + encoded;
        
        const msg = `*Aarish Dairy Pro - Offline Snapshot*\\nHere is your live ${type} ledger for *${name}*. Tap the secure link to view records instantly (No login required):\\n\\n${link}`;
        window.open(`https://wa.me/?text=${encodeURIComponent(msg)}`, '_blank');
        showToast("Snapshot Link Generated!");
    } catch(e) {
        showToast("Data too large for snapshot link. Use PDF export.");
    }
};
// ===========================================================================================
"""
    # INJECT BOOTLOADER ENGINE
    code = code.replace("function initFirebase() {", engine_code + "\nfunction initFirebase() {")
    
    # BYPASS FIREBASE IF PHANTOM IS ACTIVE
    code = code.replace("function initFirebase() {", "function initFirebase() {\n    if (window.__PHANTOM_ACTIVE) return;")
    code = code.replace("async function loadUserData() {", "async function loadUserData() {\n    if (window.__PHANTOM_ACTIVE) return;")

    # MILK CARD EXACT STRING REPLACE
    old_milk = 'onclick="haptic(); openMilkDetail(${argName})"'
    new_milk = 'ontouchstart="aarishStartCardHold(\'milk\', ${argName})" ontouchend="aarishCancelCardHold()" ontouchmove="aarishCancelCardHold()" onmousedown="aarishStartCardHold(\'milk\', ${argName})" onmouseup="aarishCancelCardHold()" onmouseleave="aarishCancelCardHold()" onclick="if(window.__aarishIsLongPressActive){ window.__aarishIsLongPressActive=false; return; } haptic(); openMilkDetail(${argName})"'
    code = code.replace(old_milk, new_milk)

    # UDHAR CARD REGEX CAPTURE REPLACE
    udhar_regex = r'(onclick="([^"]*openUdharDetail\(([^)]+)\)[^"]*)")'
    def udhar_replacer(match):
        inner_click = match.group(2)
        arg = match.group(3)
        return f'ontouchstart="aarishStartCardHold(\'udhar\', {arg})" ontouchend="aarishCancelCardHold()" ontouchmove="aarishCancelCardHold()" onmousedown="aarishStartCardHold(\'udhar\', {arg})" onmouseup="aarishCancelCardHold()" onmouseleave="aarishCancelCardHold()" onclick="if(window.__aarishIsLongPressActive){{ window.__aarishIsLongPressActive=false; return; }} {inner_click}"'
    code = re.sub(udhar_regex, udhar_replacer, code)

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(code)

    print("✅ FINAL SUCCESS: Absolute God-Tier 'Stateless Phantom Protocol' applied successfully!")

if __name__ == '__main__':
    main()
