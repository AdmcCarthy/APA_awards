---
title: Close to home
short_title: "Close to home · APA 2025"
dek: Norway's latest licensing round filled gaps around existing fields. It was taken up by fewer companies, in closer partnerships, and stakes were already changing hands within months.
kicker: NCS · APA 2025 · TFO2025 · granted 20 March 2026
byline: Adam McCarthy
date: 2026-11-07
arc: scqa
register: section
palette: tide
surface: nordic-cool
horizon: true
groups: [Equinor, Aker BP, Vår Energi, Wellesley, DNO, Harbour Energy]
kpis:
  - { metric: n_licences, label: production licences granted }
  - { metric: near_1km, label: within 1 km of a producing field }
  - { metric: n_companies, label: "companies took part, the fewest since the first round in 2003" }
  - { metric: equinor_share, filter: pct, label: of licences include Equinor }
sources:
  sodir:
    name: Sodir FactMaps
    url: https://factmaps.sodir.no
    accessed: 2026-11-06
    note: Licences, licensee history, blocks, fields, the predefined area and the basemap
  ministry:
    name: Ministry of Energy, APA 2025 announcement
    accessed: 2026-01-13
    note: Announced offers; Sodir's licence register is used for all counts
data:
  awards: data/awards.json
  apa_area: data/apa_area.json
  land: data/land.json
  existing: data/licences_existing.json
  quadrants: data/quadrants.json
  sea_lines: data/sea_boundaries.json
  towns: data/towns.json
  summary: data/summary.json
  partners: data/partners.json
---

Every year Norway opens a predefined area of mature acreage, the APA, for licence applications. The
latest round handed out {{ n_licences }} production licences. Read on to see where they are, who won
them, and how close they sit to fields that already produce. Every number here is computed from
Sodir's public data; hover one for its exact value, or see [Basis of analysis](#basis-of-analysis).

::: step {beat=situation kicker="The shelf"}
### {{ n_licences }} new licences among hundreds of old ones

The predefined area is shaded pale. The new licences, coloured by operator, almost vanish among the
existing ones in grey. That is by design: APA exists to keep exploration going around infrastructure
that is already in place. {{ near_25km }} of the {{ n_licences }} lie within {{ 25 | param }} km of a producing
field, and {{ n_strat }} are stratigraphic.

```chart
id: shelf
type: map
frame: area
layers:
  - { data: land, role: land }
  - { data: apa_area, role: area }
  - { data: quadrants, role: grid }
  - { data: existing, role: context, legend: Existing licences }
  - { data: sea_lines, role: lines }
  - data: awards
    role: focus
    colour_by: group
    label: name
    title_prefix: "PL "
    tooltip: [operator, partner_list, area_km2, distance, kind]
    tooltip_labels: { operator: Operator, partner_list: Line-up, area_km2: Area, distance: Nearest field, kind: Type }
  - { data: towns, role: points, label: n }
title: "{{ n_licences }} licences, nearly all next to existing ones"
subtitle: APA 2025 licences by operator, with existing licences and the predefined area
source: sodir
confidence: observed
notes: Hover or tap a licence for its line-up and distance to the nearest field.
```
:::

::: step {beat=situation kicker="North Sea"}
### In the North Sea the licences are slices around existing hubs

{{ ns_n }} of the licences are in the North Sea, and half of them lie within
{{ ns_median_dist | round:1 | km }} of a producing field. {{ ns_strat }} are stratigraphic, granted
only above or below a set depth so they stack onto existing licences, and {{ ns_additional }} add
area to licences that already exist.

```chart
use: shelf
view: { fit: { area_name: North Sea }, pad: 0.15 }
filter: { area_name: North Sea }
title: "North Sea: {{ ns_n }} licences, packed around the hubs"
```
:::

::: step {beat=situation kicker="Norwegian Sea"}
### Tie-backs, and a few long shots

Aker BP, Vår Energi and Harbour took acreage touching Alve, Kristin and Skarv. Further out,
{{ nws_far }} licences lie more than {{ 60 | param }} km from the nearest field: the round's main step-outs.

```chart
use: shelf
view: { fit: { area_name: Norwegian Sea }, pad: 0.12 }
filter: { area_name: Norwegian Sea }
title: "Norwegian Sea: {{ nws_n }} licences, a few far from home"
```
:::

::: step {beat=situation kicker="Barents Sea"}
### Aker BP holds the round's most remote licence on its own

Aker BP's licence 1313 lies {{ remote_km | round:0 | km }} from Snøhvit, the most remote in the round,
and Aker BP holds it with no partners. Only {{ n_solo }} licences in the whole round have a single
owner, and both are Aker BP's.

```chart
use: shelf
view: { fit: { area_name: Barents Sea }, pad: 0.35 }
filter: { area_name: Barents Sea }
title: "Barents Sea: {{ bs_n }} licences, one of them alone"
```
:::

::: step {beat=complication kicker="Who operates"}
### Two companies run half the licences

Equinor operates {{ equinor_operated }} and Aker BP {{ aker_operated }}: together
{{ top2_share | pct }} of the round. Counting partner stakes too, Equinor is in {{ equinor_in }} of the
{{ n_licences }} and Aker BP in {{ aker_in }}.

```chart
use: shelf
filter: { group: [Equinor, Aker BP] }
title: Equinor and Aker BP operate {{ top2_share | pct }} of the new licences
```
:::

::: step {beat=question kicker="The winners"}
### Equinor is almost everywhere

Equinor operates {{ equinor_operated }} licences and is a partner in {{ equinor_partner }} more. The
state, through Petoro, is in {{ petoro_in }}; it manages the state's direct financial interest and
never operates. Further down, strategies differ: Wellesley operates every licence it holds, while
ORLEN takes partner stakes only.

```chart
id: companies
type: bars
data: companies
label: name
value: licences
part: [operated, partner]
parts_labels: [As operator, As partner]
colour_by: group
title: Equinor is in {{ equinor_in }} of {{ n_licences }} licences
subtitle: Licences per company, as operator (solid) and as partner (light)
source: sodir
confidence: observed
```
:::

::: step {beat=answer kicker="Near-field"}
### Each operator's distance from home

{{ near_1km }} of the {{ n_licences }} licences lie within {{ 1 | param }} km of a producing field, and
the median licence is {{ median_dist | round:1 | km }} from one. Harbour is the
purest near-field player: {{ harbour_strat }} of the {{ harbour_operated }} licences it operates are stratigraphic. Aker BP is the opposite: it
takes small extensions next to its hubs, and also operates {{ aker_far50 }} of the {{ n_far50 }}
licences more than {{ 50 | param }} km from any field.

```chart
id: distance
type: dots
data: props
row: operator_group
value: dist_km
label: name
flag: strat
colour_by: operator_group
rows: [Equinor, Aker BP, Vår Energi, Wellesley, DNO, Harbour Energy, Other]
scale: symlog
unit: km
value_label: one dot per licence
flag_label: stratigraphic licence
title: Most licences sit within a few kilometres of a field
subtitle: Distance from each licence to the nearest producing or approved field, km
source: sodir
confidence: derived
notes: Measured edge to edge in ETRS89-LAEA. 0 means the licence touches a field outline; stratigraphic licences can sit directly above or below one.
exception: { rule: linear-scale, reason: "A symmetric-log scale stretches distances under 5 km, where most licences are; ticks are labelled in km" }
```
:::

::: step {beat=answer kicker="Near-field"}
### Harbour and Aker BP sit at opposite ends of the near-field scale

Highlighting the two shows the split: Harbour's dots cluster at zero, Aker BP's run from the hubs out
to the frontier.

```chart
use: distance
highlight: [Harbour Energy, Aker BP]
title: Harbour stays at the hubs; Aker BP spans hubs to frontier
```
:::

::: step {beat=support kicker="From crowd to club"}
### Fewer companies, tighter partnerships

In APA 2013, {{ companies_2013 }} companies won acreage. This year {{ n_companies }} did, the fewest
since the first round in 2003. Mergers explain part of it: Aker BP, Vår Energi and Harbour have each absorbed
several earlier APA players.

```chart
id: club
type: line
data: club
x: year
y: companies
series: series
focus: [Companies]
title: The APA club has shrunk from {{ companies_2013 }} companies to {{ n_companies }}
subtitle: Legal companies winning APA licences, by round
source: sodir
confidence: observed
```
:::

::: step {beat=support kicker="Who partners with whom"}
### In APA 2008 the partnerships formed a wide mesh

Each dot is a company family, sized by the licences it won in the round; a line joins two families
that share at least one licence, thicker for more. In APA 2008, {{ net_2008_groups }} families
shared {{ net_2008_licences }} licences through {{ net_2008_pairs }} distinct partnerships.

```chart
id: network
type: network
data: net_nodes
edges: net_edges
frame: year
node: id
size: n
weight: n
colour_by: group
size_label: licences won
weight_label: licences shared
frame_label: "APA {frame}"
label_top: 8
tooltip: [op]
tooltip_labels: { op: As operator }
frame_default: 2008
title: In 2008, {{ net_2008_groups }} families shared licences in a loose mesh
subtitle: Company families winning APA licences, linked where they share a licence
source: sodir
confidence: derived
notes: Families are grouped by today's owner, so the same dot can be followed from round to round; hover or tap a dot for its partners. Layout is force-directed and positions carry no geographic meaning.
```
:::

::: step {beat=support kicker="Who partners with whom"}
### The mesh was at its widest in APA 2013

By 2013 the mesh had spread to {{ net_2013_groups }} families and {{ net_2013_pairs }}
partnerships across {{ net_2013_licences }} licences. Many of the new dots are small explorers with
one or two partner stakes each.

```chart
use: network
frame: 2013
title: "2013: {{ net_2013_groups }} families and {{ net_2013_pairs }} partnerships"
```
:::

::: step {beat=support kicker="Who partners with whom"}
### By APA 2019 fewer families took part

Because families are grouped by today's owner, mergers alone cannot shrink this picture: a dot
only disappears when its family stops winning acreage. By 2019, {{ net_2019_groups }} families
remained, linked by {{ net_2019_pairs }} partnerships.

```chart
use: network
frame: 2019
title: "2019: down to {{ net_2019_groups }} families"
```
:::

::: step {beat=support kicker="Who partners with whom"}
### In APA 2025 three companies sit at the centre of the partnerships

This year {{ net_2025_groups }} families share {{ net_2025_pairs }} partnerships. Equinor, Aker BP
and Petoro sit at the centre: {{ hub_in }} of the {{ n_licences }} licences include at least one of
the three.

```chart
use: network
frame: 2025
highlight: [Equinor, Aker BP, Petoro]
title: "{{ hub_in }} of {{ n_licences }} licences include Equinor, Aker BP or Petoro"
```
:::

::: step {beat=support kicker="Partnerships that last"}
### The pairs that keep coming back

Equinor and Petoro have shared licences in {{ ep_rounds }} rounds, every one since 2004, and
{{ ep_total }} licences in all. Aker BP and DNO shared only {{ ad_before_2017 }} licences before
2017 but {{ ad_since_2017 }} since. Centrica and DNO, a regular pairing until 2015, have not shared
a licence since.

```chart
id: pairtime
type: heat
data: pairs
x: year
y: pair
value: n
rows: data
value_label: licences shared
title: Equinor and Petoro have shared licences in every round since 2004
subtitle: The {{ n_pairs_shown }} family pairs with the most shared APA licences since 2003, licences shared per round
source: sodir
confidence: derived
notes: Darker means more shared licences in that round. Families as they are today; see the Basis of analysis.
```
:::

::: step {beat=support kicker="Equinor's U-turn"}
### Equinor has regained the share it lost to newcomers

As newcomers poured in, Equinor's share fell to {{ equinor_share_2013 | pct }} in APA 2013. It has
climbed back to {{ equinor_share | pct }}. The state's stake has grown too: Petoro is in
{{ petoro_share | pct }} of this year's licences.

```chart
id: equinor
type: line
data: equinor_share
x: year
y: share
series: series
y_format: pct
focus: [Equinor]
title: Equinor's share fell to {{ equinor_share_2013 | pct }}, then climbed back to {{ equinor_share | pct }}
subtitle: Share of each round's licences that include Equinor (Statoil and Hydro before 2018)
source: sodir
confidence: derived
notes: Company families as they are today; see the Basis of analysis.
```
:::

## What happens to a licence after the award

Of the {{ old_total }} licences from rounds up to 2015, only {{ old_active_share | pct }} are still
active. At that rate, most of this year's {{ n_licences }} will be returned within a decade. A licence is
returned when its work programme does not justify going on, and the acreage is then free for a later round, so
hand-backs are part of how the annual rounds keep exploration moving around existing infrastructure. *Interpreted.*

```chart
id: history
type: stack
data: history
x: year
y: n
series: series
colours: [data-story-1, data-context]
title: Only {{ old_active_share | pct }} of licences from rounds up to 2015 are still active
subtitle: Licences per round, by status in November 2026
source: sodir
confidence: observed
notes: Original licences only. Each round is announced the following January.
```

## Stakes are already changing hands

Partners often farm in, farm out or swap stakes within months of the award. Between June and
October 2026, Sodir registered new ownership for {{ n_changed }} of the {{ n_licences }} licences.

```table
kind: league
data: changes
columns:
  - { field: Licence }
  - { field: Company }
  - { field: Share, unit: "%", format: round1, bar: true }
  - { field: From, label: Effective from }
title: "{{ n_changed }} licences changed hands within eight months"
source: sodir
confidence: observed
```

## All {{ n_licences }} licences

```table
kind: league
data: props
columns:
  - { field: name, label: Licence }
  - { field: operator, label: Operator }
  - { field: area_name, label: Sea }
  - { field: km2, label: Area, unit: km², format: int, bar: true }
  - { field: dist_km, label: To nearest field, unit: km, format: round1 }
  - { field: nearest_field, label: Nearest field }
  - { field: type, label: Depth }
  - { field: status, label: Type }
sort: -km2
highlight: { name: ["1313", "1308"] }
fold: 12
title: Aker BP's two solo long shots are also among the largest licences
source: sodir
confidence: observed
notes: Click a column heading to sort. Highlighted rows are the two single-owner licences.
```

::: appendix
### Methods and caveats

**Data.** All layers come from Sodir FactMaps, retrieved 6 November 2026: licences, licensee
history, blocks, fields, the predefined area and the basemap. Sodir codes APA rounds `TFO<year>`;
this story covers `TFO2025`.

**Counts.** The ministry announced {{ n_offered }} offers on 13 January 2026, but Sodir lists
{{ n_licences }} licences, all granted on 20 March 2026, so counts here can be one lower than in the
press release. Partners and shares are the line-up on the grant date; later changes appear only in
the "changed hands" table.

**Company families.** Long-run partnership charts group companies by today's owner: Equinor includes
Statoil and Hydro; Aker BP includes Det norske, BP Norge and Lundin; Vår Energi includes Eni Norge,
Point Resources, ExxonMobil and Neptune; Harbour includes Wintershall Dea and its predecessors; DNO
includes Faroe Petroleum; ORLEN includes PGNiG and LOTOS. Company counts use legal companies as they
were at award. The grouping follows public merger history and should be checked before formal use.

**Geometry and colour.** Geometry is ED50 (Sodir native), requested as WGS84 and simplified for the
web. Distances are edge to edge in ETRS89-LAEA (EPSG:3035). Operator colours follow SubScout's
identity palette in a fixed order and are not brand colours; operators beyond its slots are grey.

**Rebuilt with SubScout.** This page was rebuilt from the original hand-coded version with the
SubScout framework, as its first real test case. Network layouts are computed at build time with a
force-directed method; each round starts from the previous round's positions, and all rounds share
one scale for dot area, line width and spacing.
:::
