"""Check upstream-excluded source files before attempting the Android build.
Optionally restore just those paths from a separately checked-out build-input repository.
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
paths = [line.strip().lstrip('/') for line in (ROOT/'.gitignore').read_text().splitlines()
         if line.strip().lstrip('/').startswith('TMessagesProj/')
         and (line.endswith(('.java', '.kt')) or line in ('TMessagesProj/jni/colorado', 'TMessagesProj/jni/security'))]
if len(sys.argv) == 2:
    inputs = Path(sys.argv[1]).resolve()
    for name in paths:
        src, dst = inputs/name, ROOT/name
        if not dst.exists() and src.exists():
            if not src.resolve().is_relative_to(inputs):
                raise SystemExit('Build input escapes its root: '+name)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir(): shutil.copytree(src, dst)
            else: shutil.copy2(src, dst)

required = paths + ['TMessagesProj/jni/security/secure_validator.hpp',
                    'TMessagesProj/jni/security/secure_validator.cpp',
                    'TMessagesProj/jni/security/skCrypter.hpp',
                    'TMessagesProj/jni/colorado/CMakeLists.txt']
missing = [name for name in required if not (ROOT/name).exists()]
if missing:
    print('::error::The upstream public branch excludes source files required for an APK. See docs/session-portability.md.')
    for name in missing: print('Missing source: '+name)
    raise SystemExit(1)
print('Required upstream source files are present.')
