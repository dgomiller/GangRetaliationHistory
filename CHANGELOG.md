# Changelog

## 1.2.0

- The History screen now has the **same view switcher as Gang Retaliation's Nemeses screen** (TAB, GANGS | TERRITORY | ARSENAL) with **HISTORY** added at the end and highlighted, so it reads as one more page of that screen. Clicking GANGS, TERRITORY or ARSENAL opens the Nemeses screen on that page (uses `GRMenuData.RequestView`).
- Pressing **TAB** on the History screen wraps back around to GANGS, completing the cycle. The title now matches the Nemeses screen's title in size and position.
- Gang Retaliation 1.4.5's **intel gathering** is recorded: each intel gain ("<gang> intel: N %") and "<gang> stronghold located" appears in the history with a new `INTEL` tag, tagged with the gang, in English and Spanish.
- **The separate "Nemesis History" button under Character is gone.** History is now reached from the Nemeses screen's switcher (**requires the Gang Retaliation version that adds the HISTORY entry and `GRMenuData.RequestView`**; menu name `gangretaliationhistory_history_menu`).

## 1.1.1

- The History screen now shows the **current in-game day** ("Current Day: N", "Día actual: N" in Spanish) in large cyan text at the top right, above the alive / fallen count, so the day labels on the timeline have a reference point.

## 1.1.0

Support for Gang Retaliation 1.4.0.

- New events are recorded, tagged and translated: **Barghest raids** and a nemesis shooting their way out of one
  (tag `RAID`), a gang's **stronghold falling** (new tag `STRONGHOLD`, tagged with the gang) and **taking a
  Boss's weapon** (new tag `WEAPON`, tagged with the boss and their gang).
- English and Spanish labels for the new tags.
- Tested with Gang Retaliation 1.4.0.

## 1.0.0

First release.

- **Nemesis History screen** under Character in the hub menu (below Nemeses): a **Full History** tab plus one tab per gang.
  Member cards (alive first by rank, then the fallen), a sideways-scrolling card list, and a scrolling
  oldest-to-newest timeline with day labels and colored event tags. `A` / `D` switch tabs.
- **history.log** keeps every on-screen Gang Retaliation message in a language-neutral form (message type plus
  its parts, with the text as shown beside it), with the campaign and in-game day. History re-renders in the
  language you play in; nemesis titles are shown as recorded. Older logs are converted automatically (the original
  is kept as `history.log.v1.bak`).
- Events are classified (death, raid, ambush, promotion, power vacuum, ...) and tagged with the gangs and
  nemeses they involve.
- Full English and Spanish text, using the same localization mechanism as Gang Retaliation.
- Tested with Gang Retaliation 1.3.4 on Cyberpunk 2077 2.5.
