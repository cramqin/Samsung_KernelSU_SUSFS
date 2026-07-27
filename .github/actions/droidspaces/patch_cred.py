import sys
import re

path = sys.argv[1] if len(sys.argv) > 1 else "include/linux/cred.h"
try:
    with open(path, "r") as f:
        content = f.read()

    pattern = r"#ifdef\s+CONFIG_USER_NS\s*\n\s*struct\s+user_namespace\s*\*user_ns;[^\n]*\n\s*struct\s+ucounts\s*\*ucounts;[^\n]*\n#endif\s*\n"
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, "", content, flags=re.DOTALL)
        
        kabi_pat = r"(ANDROID_KABI_RESERVE\s*\(\s*1\s*\)\s*;[^\n]*\n\s*ANDROID_KABI_RESERVE\s*\(\s*2\s*\)\s*;)"
        replacement = """#ifdef CONFIG_USER_NS
\tstruct user_namespace *user_ns;
\tstruct ucounts *ucounts;
#else
\tANDROID_KABI_RESERVE(1);
\tANDROID_KABI_RESERVE(2);
#endif"""
        if re.search(kabi_pat, content, re.DOTALL):
            content = re.sub(kabi_pat, replacement, content, flags=re.DOTALL)
        else:
            cred_end_pat = r"(\};\s*\n\s*(?:/\*|__randomize_layout|\n))"
            content = re.sub(cred_end_pat, r"#ifdef CONFIG_USER_NS\n\tstruct user_namespace *user_ns;\n\tstruct ucounts *ucounts;\n#endif\n\1", content, count=1)
        
        with open(path, "w") as f:
            f.write(content)
        print("Successfully patched include/linux/cred.h for USER_NS KABI preservation")
except Exception as e:
    print(f"cred.h patch note: {e}")
