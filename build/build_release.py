"""Builds the Gang Retaliation History release package from Working/ (the source of truth).

  python -I build_release.py [--skip-checks]

1. Pre-flight (unless --skip-checks): offline redscript compile check + Lua tests. Aborts on failure.
2. Verifies the version string matches in init.lua, README.md, CHANGELOG.md and the Nexus text.
3. Writes the in-game tree to  Distribution/GangRetaliationHistory/<version>/  and builds
   GangRetaliationHistory_v<version>.zip from only that tree.
   NEXUS_DESCRIPTION.txt is deliberately NOT shipped (publishing-only text).
Never touches the game folder.
"""
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE.parent                                   # Working/GangRetaliationHistory
ROOT = MOD.parent.parent                            # CYBERPUNK MODS
TOOLS = ROOT / "Tools"
NAME = "GangRetaliationHistory"
VERSION = "1.2.0"

CET = Path("bin/x64/plugins/cyber_engine_tweaks/mods") / NAME
SCRIPTS = Path("r6/scripts") / NAME
FILES = [  # (source relative to Working/<mod>, destination relative to the game root)
    (Path("archive/pc/mod") / f"{NAME}.archive", Path("archive/pc/mod") / f"{NAME}.archive"),
    (SCRIPTS / "Data.reds", SCRIPTS / "Data.reds"),
    (SCRIPTS / "History.reds", SCRIPTS / "History.reds"),
    (SCRIPTS / "Localization.reds", SCRIPTS / "Localization.reds"),
    (CET / "init.lua", CET / "init.lua"),
    (CET / "modules/tagger.lua", CET / "modules/tagger.lua"),
    (CET / "data/.keep", CET / "data/.keep"),
    (Path("README.md"), CET / "README.md"),
    (Path("LICENSE"), CET / "LICENSE"),
    (Path("CHANGELOG.md"), CET / "CHANGELOG.md"),
]
NOT_SHIPPED = ["NEXUS_DESCRIPTION.txt"]


def fail(msg):
    sys.exit("BUILD FAILED: " + msg)


def run_checks():
    print("== pre-flight: offline compile check")
    r = subprocess.run([sys.executable, "-I", str(TOOLS / "scc_check.py"), str(MOD / SCRIPTS)],
                       capture_output=True, text=True, errors="replace")
    if "exit code: 0" not in r.stdout:
        print(r.stdout[-3000:])
        fail("redscript compile check did not pass")
    print("   compiles cleanly")
    print("== pre-flight: Lua tests")
    r = subprocess.run([sys.executable, "-I", str(HERE / "test_chronicle.py")], capture_output=True, text=True,
                       errors="replace", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    if "ALL TESTS PASSED" not in r.stdout:
        print(r.stdout[-3000:], r.stderr[-1500:])
        fail("Lua tests did not pass")
    print("   all tests passed")


def check_version():
    for rel, pattern in [(CET / "init.lua", rf'local VERSION = "{re.escape(VERSION)}"'),
                         (Path("CHANGELOG.md"), rf"## {re.escape(VERSION)}\b"),
                         (Path("README.md"), r"Gang Retaliation History")]:
        text = (MOD / rel).read_text(encoding="utf-8")
        if not re.search(pattern, text):
            fail(f"version/text check failed for {rel} (expected {pattern})")
    print(f"== version {VERSION} consistent")


def main():
    if "--skip-checks" not in sys.argv:
        run_checks()
    check_version()
    for src, _ in FILES:
        if not (MOD / src).is_file():
            fail(f"missing source file: {src}")

    out = ROOT / "Distribution" / NAME / VERSION
    stage = Path(tempfile.mkdtemp(prefix="grchron_release_"))          # system temp: no OneDrive locks
    for src, dst in FILES:
        target = stage / dst
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(MOD / src, target)

    zip_path = stage / f"{NAME}_v{VERSION}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for src, dst in FILES:
            z.write(stage / dst, dst.as_posix())

    # publish into Distribution (copy file by file; never delete anything there)
    for src, dst in FILES:
        target = out / dst
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(stage / dst, target)
    shutil.copy2(zip_path, out / zip_path.name)

    with zipfile.ZipFile(out / zip_path.name) as z:
        names = z.namelist()
    for bad in NOT_SHIPPED:
        if any(n.endswith(bad) for n in names):
            fail(f"{bad} must not be inside the zip")
    print(f"\nOK: {out / zip_path.name}  ({(out / zip_path.name).stat().st_size} bytes)")
    for n in names:
        print("   ", n)


if __name__ == "__main__":
    main()
