#!/usr/bin/env python3
import sys
import os
import re

def patch_cred_h(common_dir):
    cred_h_path = os.path.join(common_dir, "include/linux/cred.h")
    if not os.path.exists(cred_h_path):
        print(f"[USER_NS KABI] Warning: {cred_h_path} not found.")
        return

    with open(cred_h_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern for un-padded CONFIG_USER_NS block in struct cred
    unpadded_pattern = r"#ifdef\s+CONFIG_USER_NS\s*\n\s*struct\s+user_namespace\s*\*user_ns;[^\n]*\n\s*struct\s+ucounts\s*\*ucounts;[^\n]*\n#endif\s*\n"

    # Pattern for ANDROID_KABI_RESERVE(1) & (2)
    kabi_pattern = r"(ANDROID_KABI_RESERVE\s*\(\s*1\s*\)\s*;[^\n]*\n\s*ANDROID_KABI_RESERVE\s*\(\s*2\s*\)\s*;)"

    replacement = """#ifdef CONFIG_USER_NS
\tstruct user_namespace *user_ns;
\tstruct ucounts *ucounts;
#else
\tANDROID_KABI_RESERVE(1);
\tANDROID_KABI_RESERVE(2);
#endif"""

    modified = False

    # 1. Remove the un-padded block so fields are not shifted or duplicated
    if re.search(unpadded_pattern, content):
        content = re.sub(unpadded_pattern, "", content)
        modified = True
        print("[USER_NS KABI] Removed un-padded CONFIG_USER_NS block from struct cred.")

    # 2. Replace KABI reserves with conditional user_ns / ucounts
    if re.search(kabi_pattern, content):
        content = re.sub(kabi_pattern, replacement, content)
        modified = True
        print("[USER_NS KABI] Successfully replaced ANDROID_KABI_RESERVE(1/2) with user_ns/ucounts.")
    else:
        print("[USER_NS KABI] Note: ANDROID_KABI_RESERVE(1/2) pattern not found, checking alternative replacement.")

    if modified:
        with open(cred_h_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[USER_NS KABI] Saved updated include/linux/cred.h.")
    else:
        print("[USER_NS KABI] No changes needed for include/linux/cred.h.")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    patch_cred_h(target_dir)
