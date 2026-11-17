"""Builds GangRetaliationHistory.archive (the History screen's ink resource).

The screen resource is an empty full-screen canvas whose controller is the redscript class
GangRetaliationHistory.GRChronHistoryController (a built-in DynamicWidgetController holds the
class name as text). All widgets are created in code by that class, so the resource stays tiny.

Requires WolvenKit.CLI (Tools/WolvenKit.Console-10.0.0-beta.1). Run:  python -I build_archive.py
Output: ../archive/pc/mod/GangRetaliationHistory.archive   (never touches the game folder)
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD_ROOT = HERE.parent
CLI = MOD_ROOT.parent.parent / "Tools" / "WolvenKit.Console-10.0.0-beta.1" / "WolvenKit.CLI.exe"
GAME = Path(r"H:\SteamLibrary\steamapps\common\Cyberpunk 2077")

ARCHIVE_NAME = "GangRetaliationHistory"
RESOURCE_DIR = Path("gangretaliationhistory") / "gui"
RESOURCE_NAME = "history.inkwidget"
CONTROLLER = "GangRetaliationHistory.GRChronHistoryController"

STAGE = Path(tempfile.mkdtemp(prefix="grchron_stage_"))   # system temp: OneDrive can lock folders it syncs
OUT_DIR = MOD_ROOT / "archive" / "pc" / "mod"


def cname(value):
    return {"$type": "CName", "$storage": "string", "$value": value}


def vec2(x, y):
    return {"$type": "Vector2", "X": x, "Y": y}


def margin(top=0, left=0, right=0, bottom=0):
    return {"$type": "inkMargin", "bottom": bottom, "left": left, "right": right, "top": top}


def controller(handle):
    return {"HandleId": handle, "Data": {"$type": "DynamicWidgetController", "$className": CONTROLLER}}


def root_canvas(handle_widget, handle_children):
    return {
        "HandleId": handle_widget,
        "Data": {
            "$type": "inkCanvasWidget",
            "affectsLayoutWhenHidden": 0,
            "backendData": None,
            "canSupportFocus": 0,
            "childMargin": margin(),
            "childOrder": "Backward",
            "children": {"HandleId": handle_children, "Data": {"$type": "inkMultiChildren", "children": []}},
            "effects": [],
            "fitToContent": 0,
            "isInteractive": 0,
            "layout": {
                "$type": "inkWidgetLayout",
                "anchor": "TopLeft",
                "anchorPoint": vec2(0, 0),
                "HAlign": "Fill",
                "margin": margin(),
                "padding": margin(),
                "sizeCoefficient": 1,
                "sizeRule": "Fixed",
                "VAlign": "Fill",
            },
            "logicController": None,
            "name": cname("Root"),
            "opacity": 1,
            "parentWidget": None,
            "propertyManager": None,
            "proxyWidget": None,
            "renderTransform": {
                "$type": "inkUITransform",
                "rotation": 0,
                "scale": vec2(1, 1),
                "shear": vec2(0, 0),
                "translation": vec2(0, 0),
            },
            "renderTransformPivot": vec2(0.5, 0.5),
            "secondaryControllers": [],
            "size": vec2(3840, 2160),
            "state": cname("Default"),
            "style": None,
            "tintColor": {"$type": "HDRColor", "Alpha": 1, "Blue": 1, "Green": 1, "Red": 1},
            "userData": [],
            "visible": 1,
        },
    }


def instance(h_controller, h_widget, h_children):
    return {
        "$type": "inkWidgetLibraryItemInstance",
        "gameController": controller(h_controller),
        "rootResolution": "UltraHD_3840_2160",
        "rootWidget": root_canvas(h_widget, h_children),
    }


def build_json():
    item = {
        "$type": "inkWidgetLibraryItem",
        "name": cname("Root"),
        "package": {
            "Flags": 0,
            "Type": "WolvenKit.RED4.Archive.Buffer.CR2WWrapper, WolvenKit.RED4, Version=10.0.0.0, Culture=neutral, PublicKeyToken=null",
            "Data": {"File": {"Version": 195, "BuildVersion": 0,
                              "RootChunk": instance("0", "1", "2"), "EmbeddedFiles": []}},
        },
        "packageData": {
            "BufferId": "0",
            "Flags": 0,
            "Type": "WolvenKit.RED4.Archive.Buffer.RedPackage, WolvenKit.RED4, Version=10.0.0.0, Culture=neutral, PublicKeyToken=null",
            "Data": {"Version": 4, "Sections": 6, "CruidIndex": 0, "CruidDict": {},
                     "Chunks": [instance("3", "4", "5")]},
        },
    }
    return {
        "Header": {"WolvenKitVersion": "10.0.0-beta.1", "WKitJsonVersion": "0.0.9", "GameVersion": 2500,
                   "ExportedDateTime": "2026-11-11T00:00:00.0000000Z", "DataType": "CR2W",
                   "ArchiveFileName": RESOURCE_NAME},
        "Data": {
            "Version": 195,
            "BuildVersion": 0,
            "RootChunk": {
                "$type": "inkWidgetLibraryResource",
                "animationLibraryResRef": {"DepotPath": {"$type": "ResourcePath", "$storage": "uint64", "$value": "0"},
                                           "Flags": "Soft"},
                "cookingPlatform": "PLATFORM_PC",
                "externalDependenciesForInternalItems": [],
                "externalLibraries": [],
                "libraryItems": [item],
                "rootDefinitionIndex": 0,
                "rootResolution": "UltraHD_3840_2160",
                "sequences": [],
                "version": "Default",
            },
            "EmbeddedFiles": [],
        },
    }


def run(*args):
    result = subprocess.run([str(CLI), *map(str, args)], capture_output=True, text=True, errors="replace")
    text = (result.stdout or "") + (result.stderr or "")
    print(f"$ WolvenKit.CLI {' '.join(str(a) for a in args)}\n{text.strip()}\n(exit {result.returncode})")
    return result.returncode, text


def main():
    if not CLI.exists():
        sys.exit(f"console not found: {CLI}")
    pack_root = STAGE / ARCHIVE_NAME
    res_dir = pack_root / RESOURCE_DIR
    res_dir.mkdir(parents=True)
    json_path = res_dir / (RESOURCE_NAME + ".json")
    json_path.write_text(json.dumps(build_json(), indent=1), encoding="utf-8")

    # SAFETY: pass ONLY the file. `convert` has no -gp option; extra arguments are treated as more
    # input paths, and a game folder there makes the tool process (and litter) the whole game folder.
    code, text = run("convert", "deserialize", json_path)
    resource = res_dir / RESOURCE_NAME
    if code != 0 or not resource.exists():
        sys.exit("deserialize failed (see output above)")
    json_path.unlink()                      # only the resource goes into the archive

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    archive = OUT_DIR / (ARCHIVE_NAME + ".archive")
    if archive.exists():
        archive.unlink()                    # never trust a stale file
    # NOTE: `pack` takes folders only; extra arguments would be packed too (no -gp here!)
    code, text = run("pack", pack_root, "-o", OUT_DIR)
    if code != 0 or "Packing failed" in text:
        sys.exit("pack failed (see output above)")
    if not archive.exists():
        sys.exit("pack reported success but produced no archive")
    print(f"OK: {archive}  ({archive.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
