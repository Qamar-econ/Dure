#!/bin/bash
cd "$(dirname "$0")"
THREADS=2 python3 brief.py 3b > run3.log 2>&1
FINDINGS=findings_heldout.json TAG=_heldout THREADS=2 python3 brief.py 3b > run3h.log 2>&1
echo done > both.done
