#!/usr/bin/env python3
"""Generate a minimal Software Bill of Materials (SBOM) from pip freeze."""

import json
import subprocess
from datetime import datetime
from pathlib import Path

def generate() -> int:
    result = subprocess.run(
        [subprocess.sys.executable, "-m", "pip", "freeze"],
        capture_output=True, text=True
    )
    
    packages = []
    for line in result.stdout.splitlines():
        if "==" in line:
            name, version = line.split("==", 1)
            packages.append({
                "name": name,
                "version": version,
                "type": "library",
                "supplier": "PyPI",
            })
    
    sbom = {
        "bomFormat": "CycloneDX-lite",
        "specVersion": "1.4",
        "serialNumber": f"urn:uuid:sof-{datetime.now().strftime('%Y%m%d')}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "tools": [{"name": "sof-sbom", "version": "1.0"}],
        },
        "components": packages,
    }
    
    Path("sbom.json").write_text(json.dumps(sbom, indent=2))
    print(f"✅ sbom.json generated ({len(packages)} packages)")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(generate())
