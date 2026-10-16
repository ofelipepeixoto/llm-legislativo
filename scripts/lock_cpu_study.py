#!/usr/bin/env python3
"""Regenerate the CPU study lock. Explicit developer action; no model or training."""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
TORCH_URL='https://download-r2.pytorch.org/whl/cpu/torch-2.14.1%2Bcpu-cp312-cp312-manylinux_2_28_x86_64.whl'
TORCH_SHA='5a6363570c753812540a05eb82380e329469cbe668643e88111414c12627711f'

if __name__=='__main__':
    subprocess.run(['uv','pip','compile','configs/python/study.in','--python-version','3.12',
                    '--generate-hashes','--emit-index-url','--output-file','requirements-cpu.lock'],cwd=ROOT,check=True)
    path=ROOT/'requirements-cpu.lock'
    path.write_text('# Generated CPU profile: Linux x86_64 / Python 3.12.\n'+path.read_text()+
                    '\n# Exact official CPU wheel; no global fallback index.\n'+
                    f'torch @ {TORCH_URL} \\\n    --hash=sha256:{TORCH_SHA}\n')
