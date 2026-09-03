# Agent notes: indiana_freeze_enso

Public GitHub. MIT. Question: Does October plus ENSO beat the 1991-2020 median first/last 32 °F date at held-out Indiana GHCND cores?

New tree, not a restamp of last year vs median. Cite `28941fb`. Four cores only. Valparaiso is not in this tree. TMIN ≤ 32 °F. Prior-year October plus Niño 3.4. Same-year October is refused. Last year is a bar, not a Ridge feature.

Live lock `d861556`: No on first fall (9.96 vs 8.75); yes on last spring (7.62 vs 8.21). Do not average that split. Pages stay off. Temp lane, not White River Q.

Do not edit `indiana_freeze_date`, `indiana_djf_snow_tercile`, NWM trees, Calumet maps, `indiana_wx_pages`, or HWM. Do not read `p_sfha`, HAND, or White River 00060.

`ensoforge/` is the GraphForge pin. Six laws: no_hydro, tmin_only, preseason, temporal_split, claim_bans, pages.

Index: Temp lane on https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3 not White River Q.

## Verify

`python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done`
