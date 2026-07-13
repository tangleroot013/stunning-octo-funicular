#!/usr/bin/env python3
"""Parse log files and aggregate error frequencies with stack trace fingerprinting."""

import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path

ERROR_PATTERNS = [
    re.compile(r"(ERROR|CRITICAL|FATAL).*?:\\s*(.+)", re.IGNORECASE),
    re.compile(r"Traceback \\(most recent call last\\):", re.IGNORECASE),
    re.compile(r"\\w+Error:\\s*(.+)", re.IGNORECASE),
]

def fingerprint(lines: list[str]) -> str:
    # Hash the first 3 lines of a traceback to group similar errors
    text = "\\n".join(lines[:3])
    return hashlib.sha256(text.encode()).hexdigest()[:12]

def analyze() -> None:
    logs = list(Path(".").rglob("*.log")) + list(Path(".").rglob("*.log.*"))
    if not logs:
        print("ℹ️  No .log files found.")
        return
    
    errors = []
    traces = defaultdict(list)
    
    for log in logs:
        current_trace = []
        in_trace = False
        for line in log.read_text(errors="ignore").splitlines():
            if "Traceback" in line:
                in_trace = True
                current_trace = [line]
            elif in_trace:
                if line.strip() and not line.startswith(" "):
                    # End of traceback
                    if current_trace:
                        fp = fingerprint(current_trace)
                        traces[fp].append((log.name, current_trace[0]))
                    in_trace = False
                    current_trace = []
                else:
                    current_trace.append(line)
            
            for pat in ERROR_PATTERNS:
                if m := pat.search(line):
                    errors.append(m.group(0)[:100])
        
        if in_trace and current_trace:
            fp = fingerprint(current_trace)
            traces[fp].append((log.name, current_trace[0]))
    
    print(f"# Log Analysis ({len(logs)} files)\\n")
    if errors:
        print("## Error Frequency")
        for err, count in Counter(errors).most_common(10):
            print(f"- ({count}) {err}")
    
    if traces:
        print(f"\\n## Traceback Groups ({len(traces)} unique)")
        for fp, occurrences in sorted(traces.items(), key=lambda x: -len(x[1]))[:10]:
            print(f"- [{fp}] {len(occurrences)} occurrences (first: {occurrences[0][0]})")

if __name__ == "__main__":
    analyze()
