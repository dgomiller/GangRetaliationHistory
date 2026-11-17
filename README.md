# Gang Retaliation History

A companion mod for [**Gang Retaliation**](https://www.nexusmods.com/cyberpunk2077/mods/36235). It adds a
**Nemesis History** screen, opened from the **HISTORY** entry at the end of the view switcher on Gang Retaliation's Nemeses screen (GANGS | TERRITORY | ARSENAL | HISTORY), so you can look back at everything that has
happened to your Nemeses and their gangs: who escaped, who was promoted, who died, which gangs went to war.

It does **not** modify Gang Retaliation. It reads the messages the mod already shows you and keeps them
in order, so the history only covers what happens **after you install it**.

## What you get

- **Nemesis History**, the HISTORY page of the Nemeses screen.
  - **Full History** tab: an *All History* card and one card per gang. Pick one to see every event, or just
    that gang's events (each row shows which gang it belongs to).
  - One tab per gang, with an *All Gang History* card followed by its members: alive first by rank, then the
    fallen. Pick a member to see only their events.
  - A timeline from oldest to newest with a day label for each day, opening at the newest event. Event tags:
    `DEATH`, `RAID`, `ARRESTED`, `RELEASED`, `AMBUSH`, `BACKUP`, `ESCAPED`, `PROMOTED`, `NEW FACE`, `FEUD`,
    `POWER VACUUM`, `RETURNED`, `TRAIT`, `WAR`, `TERRITORY`, `STRONGHOLD`, `WEAPON`, `INTEL`.
  - Mouse wheel scrolls the timeline and the card list. `A` / `D` switch tabs, `Esc` goes back.
- **history.log**: a plain text record of every message, kept in a **language-neutral** form (the message type
  plus its parts, with the text as shown beside it). The screen re-renders the whole history in whatever language
  the game uses now, so switching English <-> Spanish changes every sentence, old ones included.
- **English and Spanish**, following your game language, using the same localization setup as Gang Retaliation.

## Requirements

- **Gang Retaliation 1.4.5 or newer** (older versions: use History 1.1.1) and everything it requires: Cyber Engine Tweaks, RED4ext, redscript,
  Codeware, ArchiveXL, TweakXL and Mod Settings. See its mod page for the current versions.
- Cyberpunk 2077 2.5.

## Installation

**Automatic:** install with Vortex Mod Manager.

**Manual:** extract the download into your Cyberpunk 2077 folder. It adds:

- `archive\pc\mod\GangRetaliationHistory.archive`
- `r6\scripts\GangRetaliationHistory\` (three `.reds` files)
- `bin\x64\plugins\cyber_engine_tweaks\mods\GangRetaliationHistory\`

Load a save and give it a few seconds. In the CET console you should see
`[GangRetaliationHistory] hooked GangRetaliation.GRDetection:Notify` and, once a save is loaded,
`History screen fed: N events, ...`.

## Uninstallation

Delete the three paths above (or remove the mod in Vortex). Your `history.log` lives only in the
`GangRetaliationHistory\data` folder, so copy it first if you want to keep it. Gang Retaliation itself is
not affected.

## How it works

The CET part watches the method Gang Retaliation uses to show each message and matches it against the mod's own
message templates. That turns it into a message type plus typed parts (nemesis, gang, rank, trait, ...), which is
what gets saved. Each event is also tagged with the gangs and Nemeses it names, using the live Nemesis roster.
Before the events go to the screen, each one is rendered in the active language with the mod's own text. They are
handed to a small script system that the History screen reads. The screen's resource is a tiny archive;
everything on it is drawn by script.

If you already have a `history.log` from an earlier build, it is converted automatically the first time a save
loads; the original is kept once as `history.log.v1.bak`.

## Known limitations

- History starts when you install the mod. Earlier events are not recovered.
- Only messages Gang Retaliation actually shows are recorded. The newest 600 events per campaign are kept
  on the screen.
- The screen shows what the mod had recorded when you opened it; reopen it to see new events.
- **Nemesis titles** ("the Usurper" / "el Usurpador") live inside Gang Retaliation's own data, which this mod cannot
  read, so they are shown as they were recorded. Everything else in a sentence follows the game language.
- It depends on a few public parts of Gang Retaliation (its message method, campaign ID and Nemesis roster
  data). **If a Gang Retaliation update changes them, this mod may stop working or fail to compile** until it
  is updated. If you get a redscript compilation error after updating Gang Retaliation, remove this mod's
  `r6\scripts\GangRetaliationHistory` folder until a new version is out.

## Credits

- **NovaAntonsito**, for [Gang Retaliation](https://www.nexusmods.com/cyberpunk2077/mods/36235). This mod
  builds on it and would not exist without it.
- psiberx, for Codeware (localization) and TweakXL; jac3km4 and the redscript team; the Cyber Engine Tweaks
  and RED4ext teams; the WolvenKit team and the REDmodding wiki.
- The **Ping** mod by theCyanideX was a reference for how the game's scroll widgets fit together. The code in this
  mod is separately written and contains none of Ping's files.
- Built by RedFalcon with AI assistance (Claude).

## License

All rights reserved, with terms kept in line with Gang Retaliation's own permissions: no reuploading, and
modification, reuse and porting only with permission. See `LICENSE`.
