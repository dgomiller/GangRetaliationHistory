"""Offline tests for the Chronicle Lua code (tagger + the feed in init.lua), using lupa.
Uses the REAL log (Other/history_log_snapshots, English, 74 lines) and the REAL roster (from the save file), and the
main mod's REAL Spanish/English strings (from its Localization.reds) as test fixtures only.
"""
import collections
import json
import os
import re
import shutil
import tempfile

from lupa import LuaRuntime

MOD = r"H:\OneDrive\Coding\CYBERPUNK MODS\Working\GangRetaliationHistory\bin\x64\plugins\cyber_engine_tweaks\mods\GangRetaliationHistory"
GAME_MODS = r"H:\SteamLibrary\steamapps\common\Cyberpunk 2077\bin\x64\plugins\cyber_engine_tweaks\mods\GangRetaliation"
SAVE = GAME_MODS + r"\data\gang_retaliation.json"
LOCALIZATION = r"H:\SteamLibrary\steamapps\common\Cyberpunk 2077\r6\scripts\GangRetaliation\Localization.reds"
LOG = r"H:\OneDrive\Coding\CYBERPUNK MODS\Other\history_log_snapshots\history_2026-11-11.log"   # legacy v1, English
CAMPAIGN = "333771167"
LABELS = {"Maelstrom": "Maelstrom", "TygerClaws": "Tyger Claws", "Valentinos": "Valentinos", "SixthStreet": "6th Street",
          "Animals": "Animals", "VoodooBoys": "Voodoo Boys", "Wraiths": "Wraiths", "Scavengers": "Scavs", "Barghest": "Barghest"}


def new_lua():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute('package.path = "' + MOD.replace("\\", "/") + '/?.lua;" .. package.path')
    return lua


def check_syntax(lua):
    for name in ("init.lua", os.path.join("modules", "tagger.lua")):
        src = open(os.path.join(MOD, name), encoding="utf-8").read()
        ok, err = lua.eval("function(s) local f, e = load(s); return f ~= nil, e end")(src)
        assert ok, f"SYNTAX ERROR in {name}: {err}"
        print("syntax ok:", name)


def roster_from_save():
    d = json.load(open(SAVE, encoding="utf-8"))
    ns = d["campaigns"][CAMPAIGN]["nemeses"]
    return [{"name": n["name"], "gangKey": n["gang"], "gang": LABELS[n["gang"]], "dead": n.get("status") == "dead"} for n in ns]


def package_strings(class_name):
    """The main mod's own localization strings for one language, as test fixtures."""
    src = open(LOCALIZATION, encoding="utf-8").read()
    start = src.index(f"public class {class_name} extends ModLocalizationPackage")
    nxt = src.find("\npublic class ", start + 10)
    block = src[start: nxt if nxt > 0 else len(src)]
    out = {}
    for m in re.finditer(r'this\.Text\("([^"]+)", "((?:[^"\\]|\\.)*)"\);', block):
        out[m.group(1)] = m.group(2).replace('\\"', '"')
    return out


EN = package_strings("GREnglish")
ES = package_strings("GRSpanish")


def lua_gettext(lua, table):
    """A getText(key) like Codeware's: the language's text, or the key itself when missing."""
    return lua.eval("function(t) return function(key) return t[key] or key end end")(lua.table_from(table))


def lines_of(path):
    return [l.rstrip("\n") for l in open(path, encoding="utf-8")]


def test_tagger(lua):
    tagger = lua.eval('(require("modules/tagger"))')
    roster = lua.table_from([lua.table_from(r) for r in roster_from_save()])
    en_text = lua_gettext(lua, EN)
    matchers = tagger.buildMatchers(None)
    lex = tagger.buildLexicon(None)

    events = []
    for line in lines_of(LOG):
        p = tagger.parseLine(line)
        if p is None or p.campaign != int(CAMPAIGN) or p.kind != "NEWS":
            continue
        events.append(p.text)
    real = [t for t in events if "Chronicle test" not in t]
    print(f"\nreal legacy lines: {len(real)}")
    assert len(real) == 73

    # 1) every real message parses, round-trips through the stored encoding, and renders back EXACTLY in English
    kinds, bad = collections.Counter(), []
    for text in real:
        rec = tagger.parseMessage(text, matchers, lex)
        if rec is None:
            bad.append(("NO MATCH", text))
            continue
        enc = tagger.encode(rec.args)
        again = tagger.render(rec.key, tagger.decode(enc), None)             # no localization at all: English fallback
        again2 = tagger.render(rec.key, tagger.decode(enc), en_text)         # real English package
        if again != text or again2 != text:
            bad.append(("ROUNDTRIP", text, again, again2))
        kinds[rec.kind] += 1
    print("kinds:", dict(kinds))
    assert not bad, bad[:3]
    print("round trip: all 73 messages render back EXACTLY from key + arguments")

    # 2) tags straight from the arguments == tags scanned from the text
    mism = []
    for text in real:
        rec = tagger.parseMessage(text, matchers, lex)
        g1, n1 = tagger.tagArgs(rec.args, roster)
        g2, n2 = tagger.tag(text, roster)
        same = lambda a, b: sorted(x for x in a.split("|") if x) == sorted(x for x in b.split("|") if x)
        if not same(g1, g2) or not same(n1, n2):       # same gangs and nemeses; listing order may differ
            mism.append((text, g1, n1, g2, n2))
    assert not mism, mism[:3]
    print("tagArgs == text-scan tags for all 73")

    # 3) Spanish: every message renders in the real Spanish templates, no placeholder left, same nemeses
    es_text = lua_gettext(lua, ES)
    samples = []
    for text in real:
        rec = tagger.parseMessage(text, matchers, lex)
        es = tagger.render(rec.key, rec.args, es_text)
        assert es and "%s" not in es, (text, es)
        for a in rec.args.values():
            if a.t == "N":
                assert a.name in es, (a.name, es)
        if text != es:
            samples.append((text, es))
    print("Spanish render:", len(samples), "of 73 differ from the English text (frames translated).")
    for en, es in samples[:5]:
        print("   EN:", en, "\n   ES:", es)

    # 4) Spanish text parses back to the same keys/rank codes when the game language is Spanish
    es_matchers = tagger.buildMatchers(es_text)
    es_lex = tagger.buildLexicon(es_text)
    for text in real:
        rec = tagger.parseMessage(text, matchers, lex)
        es = tagger.render(rec.key, rec.args, es_text)
        back = tagger.parseMessage(es, es_matchers, es_lex)
        assert back is not None and back.key == rec.key, (es, back and back.key)
        assert tagger.encode(back.args) == tagger.encode(rec.args), (es, tagger.encode(back.args), tagger.encode(rec.args))
    print("Spanish text -> same key and identical arguments (ranks and traits map back correctly)")

    # collision case: handle "Scrap" as a title word
    g, n = tagger.tag('Rumor: Hollow "Scrap" put Cactus "the Usurper" in their place.', roster)
    assert "|Hollow|Cactus|" == n and "|Scrap|" not in n
    print("handle/title collision ok:", g, n)

    # female boss: Spanish "Jefa" keeps its feminine form through the encoding
    msg = 'Wei Sato "la Fantasma" ha ascendido a Jefa de los Tyger Claws.'
    rec = tagger.parseMessage(msg, es_matchers, es_lex)
    assert rec is not None and rec.args[2].code == "R3F", rec and rec.args[2].code
    assert tagger.render(rec.key, rec.args, es_text) == msg
    print("feminine rank (Jefa -> R3F) round-trips")

    # 6) messages added in Gang Retaliation 1.4.0, built from the main mod's REAL strings (English and Spanish)
    amb = next(t for t in real if t.startswith("Ambush! ") and t.endswith(" found you."))
    label = amb[len("Ambush! "):-len(" found you.")]            # a real nemesis label, e.g.  Name "Title"
    cases = [("GR-MsgRaidBarghest", "RAID", [label]),
             ("GR-MsgBarghestEscape", "RAID", [label]),
             ("GR-MsgStrongholdCleared", "STRONGHOLD", ["Maelstrom"]),
             ("GR-MsgBossWeapon", "WEAPON", ["Kerry's Overture"])]
    for key, kind, fills in cases:
        for lang, templates, tx, mt, lx in (("EN", EN, en_text, matchers, lex), ("ES", ES, es_text, es_matchers, es_lex)):
            msg = templates[key]
            for f in fills:
                msg = msg.replace("%s", f, 1)
            rec = tagger.parseMessage(msg, mt, lx)
            assert rec is not None and rec.key == key and rec.kind == kind, (lang, msg, rec and (rec.key, rec.kind))
            assert tagger.render(rec.key, tagger.decode(tagger.encode(rec.args)), tx) == msg, (lang, msg)
    en_msg = EN["GR-MsgStrongholdCleared"].replace("%s", "Maelstrom")
    g, n = tagger.tagArgs(tagger.parseMessage(en_msg, matchers, lex).args, roster)
    assert "|Maelstrom|" in g, g
    print("1.4.0 messages (Barghest raid / escape, stronghold, boss weapon): parse, round-trip and render in EN and ES")

    # a boss weapon is named after the boss ("<Boss "Title">'s <Weapon>"): the event must be tagged with that
    # nemesis and their gang, in both languages
    boss = next(r for r in roster_from_save() if r["dead"])
    for lang, templ, wfmt, mt, lx, tx in (("EN", EN, "{boss}'s {weapon}", matchers, lex, en_text),
                                          ("ES", ES, "{weapon} de {boss}", es_matchers, es_lex, es_text)):
        weapon = wfmt.replace("{boss}", boss["name"] + ' "the Test"').replace("{weapon}", "Overture")
        msg = templ["GR-MsgBossWeapon"].replace("%s", weapon)
        rec = tagger.parseMessage(msg, mt, lx)
        gangs, names = tagger.tagEvent(rec.key, rec.args, msg, roster)
        assert f"|{boss['name']}|" in names and f"|{boss['gangKey']}|" in gangs, (lang, msg, gangs, names)
    print("boss weapon event is tagged with the boss and their gang (EN and ES)")

    # 7) messages added in Gang Retaliation 1.4.5 (intel): {gang} / {pct} placeholders, real EN and ES strings
    for key, fills in (("GR-IntelGained", {"gang": "Tyger Claws", "pct": "40"}), ("GR-IntelLocated", {"gang": "6th Street"})):
        for lang, templates, tx, mt, lx in (("EN", EN, en_text, matchers, lex), ("ES", ES, es_text, es_matchers, es_lex)):
            msg = templates[key].replace("{gang}", fills["gang"]).replace("{pct}", fills.get("pct", ""))
            rec = tagger.parseMessage(msg, mt, lx)
            assert rec is not None and rec.key == key and rec.kind == "INTEL", (lang, msg, rec and (rec.key, rec.kind))
            assert tagger.render(rec.key, tagger.decode(tagger.encode(rec.args)), tx) == msg, (lang, msg)
            g, n = tagger.tagArgs(rec.args, roster)
            want = "|TygerClaws|" if key == "GR-IntelGained" else "|SixthStreet|"
            assert want in g, (lang, msg, g)
    print("1.4.5 intel messages: parse, round-trip, render and gang tag in EN and ES")


ENV = {}


def make_system(name, campaign, roster_py):
    lua = ENV["lua"]
    pushed = ENV["pushed"]
    if name == "GangRetaliation.GRSystem":
        return lua.eval("""function(cid, texts) return {
            GetCampaignId = function(self) return cid end,
            GetText = function(self, key) return texts()[key] or key end } end""")(campaign, lambda: lua.table_from(ENV["texts"]))
    if name == "GangRetaliation.GRSpawner":
        return lua.eval("function() return { GetGameDay = function(self) return 42.7 end } end")()
    if name == "GangRetaliation.GRMenuData":
        entries = lua.table_from([lua.table_from({"name": r["name"], "gangKey": r["gangKey"], "gang": r["gang"]}) for r in roster_py])
        return lua.eval("function(e) return { GetEntries = function(self) return e end } end")(entries)
    if name == "GangRetaliationHistory.GRChronData":
        def clear(self):
            pushed.clear()

        def add(self, day, kind, text, gangs, names):
            pushed.append((int(day), kind, text, gangs, names))
        return lua.eval("function(clear, add) return { Clear = clear, Add = add } end")(clear, add)
    return None


def test_feed():
    work = tempfile.mkdtemp(prefix="grchron_test_")
    os.makedirs(os.path.join(work, "data"))
    shutil.copy(LOG, os.path.join(work, "data", "history.log"))        # legacy v1 log
    old = os.getcwd()
    os.chdir(work)
    try:
        lua = new_lua()
        ENV["lua"] = lua
        ENV["pushed"] = []
        ENV["texts"] = dict(EN)            # game language: English
        roster_py = roster_from_save()
        events, prints, observed = {}, [], {}
        lua.globals().print = lambda *a: prints.append(" ".join(str(x) for x in a))
        lua.globals().registerForEvent = lambda name, fn: events.__setitem__(name, fn)
        lua.globals().Observe = lambda cls, method, fn: observed.__setitem__((cls, method), fn)
        container = {"campaign": int(CAMPAIGN)}
        game = lua.eval("""function(getsys) return { GetScriptableSystemsContainer = function()
            return { Get = function(self, name) return getsys(name) end } end } end""")(
            lambda name: make_system(name, container["campaign"], roster_py))
        lua.globals().Game = game
        lua.execute(open(os.path.join(MOD, "init.lua"), encoding="utf-8").read())

        events["onInit"]()
        assert ("GangRetaliation.GRDetection", "Notify") in observed
        assert [p for p in prints if "hooked" in p and "v1.2.0" in p], prints

        # ---- first tick: the legacy log is converted, then fed
        before = open("data/history.log", encoding="utf-8").read()
        events["onUpdate"](1.0)
        after = open("data/history.log", encoding="utf-8").read().splitlines()
        assert os.path.exists("data/history.log.v1.bak"), "backup missing"
        assert open("data/history.log.v1.bak", encoding="utf-8").read() == before, "backup is not the original"
        assert not os.path.exists("data/history.log.new") and not os.path.exists("data/history.log.prev")
        v2 = [l for l in after if re.search(r"\| GR-Msg\w+\s+\| ", l)]
        raw = [l for l in after if "| NEWS " in l]
        print(f"\nconversion: {len(v2)} lines now v2, {len(raw)} left raw (unmatched), backup kept")
        assert len(v2) == 73 and len(raw) == 1 and "Chronicle test" in raw[0]
        print("   sample v2 line:", [l for l in v2 if "rose to" in l][0])
        print("   converted:", [p for p in prints if "converted" in p][0][:110])
        pushed = ENV["pushed"]
        assert len(pushed) == 74, len(pushed)
        original = [l.split("| NEWS           | ", 1)[1] for l in before.splitlines()]
        assert [p[2] for p in pushed] == original, "English render of the converted history differs from the original text"
        print("   fed in English: all 74 rendered texts identical to the original recording")

        # the file keeps working on the next run: nothing to convert again, same result
        events["onUpdate"](1.0)

        # ---- the player switches the game to Spanish: the same history re-renders in Spanish
        ENV["texts"] = dict(ES)
        events["onUpdate"](1.0)
        pushed = ENV["pushed"]
        es_texts = [p[2] for p in pushed]
        assert es_texts != original
        changed = sum(1 for a, b in zip(es_texts, original) if a != b)
        print(f"   language switched to Spanish: {changed} of {len(es_texts)} events re-rendered in Spanish (the 74th is the console test message), e.g.:")
        for t in es_texts[:3]:
            print("      ", t)
        assert changed == 73, changed
        assert [p[1] for p in pushed][:5] == ["NEWFACE", "FEUD", "FEUD", "FEUD", "FEUD"], [p[1] for p in pushed][:5]
        assert pushed[0][3] == "|Wraiths|" and pushed[0][4] == "|Cactus|"

        # ---- a NEW event captured while the game is in Spanish is stored neutrally, and shown in English later
        observed[("GangRetaliation.GRDetection", "Notify")](None, 'Wei Ono "el Cicatrizado" ha ascendido a Teniente de los Tyger Claws.')
        events["onUpdate"](1.0)
        newest = ENV["pushed"][-1]
        print("   live Spanish event:", newest[2])
        last_line = open("data/history.log", encoding="utf-8").read().splitlines()[-1]
        print("   stored as:", last_line)
        assert "GR-MsgPromoted" in last_line and "N~Wei Ono~el Cicatrizado~" in last_line and "R~R2" in last_line
        assert newest[1] == "PROMOTED" and newest[3] == "|TygerClaws|" and "|Wei Ono|" in newest[4], newest
        ENV["texts"] = dict(EN)
        events["onUpdate"](1.0)
        eng = ENV["pushed"][-1]
        print("   same event after switching to English:", eng[2])
        assert eng[2] == 'Wei Ono "el Cicatrizado" rose to Lieutenant of the Tyger Claws.'

        # ---- campaign switch still clears
        container["campaign"] = 111
        events["onUpdate"](1.0)
        assert len(ENV["pushed"]) == 0
        print("   campaign switch: feed cleared, ok")
    finally:
        os.chdir(old)


if __name__ == "__main__":
    lua = new_lua()
    check_syntax(lua)
    test_tagger(lua)
    test_feed()
    print("\nALL TESTS PASSED")
