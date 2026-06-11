import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as pe
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ── DATA ──────────────────────────────────────────────────────────────────────
df = dataset.copy()
df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
df = df.dropna(subset=[c for c in ['avg_temp_c','max_temp_c'] if c in df.columns])

has_avg  = 'avg_temp_c'         in df.columns
has_max  = 'max_temp_c'         in df.columns
has_city = 'city_name'          in df.columns
has_cond = 'dominant_condition' in df.columns

avg_c    = round(df['avg_temp_c'].mean(), 1) if has_avg  else 0
max_c    = round(df['max_temp_c'].max(),  1) if has_max  else 0
n_cities = df['city_name'].nunique()          if has_city else 0
hottest  = (df.groupby('city_name')['max_temp_c'].max().idxmax().title()
            if (has_city and has_max) else 'N/A')
extreme  = int((df['avg_temp_c'] > 35).sum()) if has_avg else 0

# ── PALETTE ───────────────────────────────────────────────────────────────────
BG    = '#0A0E27'
PANEL = '#12172E'
CYAN  = '#00D4FF'
AMBER = '#FF8C42'
RED   = '#FF3366'
TEAL  = '#00FFB2'
GOLD  = '#FFD700'
PURP  = '#B66DFF'
WHITE = '#FFFFFF'
OFFWH = '#C8D0E7'
DIM   = '#4A5480'
GRID  = '#1A1F40'
BORD  = '#1E2448'

plt.rcParams.update({'font.family': 'DejaVu Sans'})

# ── FIGURE: wide 16:9, generous margins so nothing overlaps ──────────────────
fig = plt.figure(figsize=(26, 14.5), facecolor=BG)

# 3 rows: header / kpi / charts — big hspace so they never collide
G = gridspec.GridSpec(
    3, 1, figure=fig,
    height_ratios=[0.10, 0.28, 0.62],
    hspace=0.10,
    left=0.01, right=0.99,
    top=0.98, bottom=0.02
)

# ─────────────────────────────────────────────────────────────────────────────
#  HEADER ROW
# ─────────────────────────────────────────────────────────────────────────────
H = fig.add_subplot(G[0])
H.set_facecolor('#06091A')
H.axis('off')

# Cyan left accent bar
H.add_patch(mpatches.Rectangle(
    (0, 0), 0.003, 1,
    transform=H.transAxes, color=CYAN, zorder=6, linewidth=0))

# Glowing sun
for r, a in [(0.10, 0.07), (0.075, 0.14), (0.050, 0.30)]:
    H.add_patch(plt.Circle(
        (0.022, 0.50), r, color=GOLD,
        alpha=a, transform=H.transAxes, zorder=3))
H.add_patch(plt.Circle(
    (0.022, 0.50), 0.030, color=GOLD,
    transform=H.transAxes, zorder=4))

# Title
H.text(0.045, 0.64,
       'WEATHER INSIGHTS DASHBOARD   |   INDIA',
       color=WHITE, fontsize=20, fontweight='bold',
       transform=H.transAxes, va='center')

# Subtitle
H.text(0.045, 0.18,
       f'Live Data  ·  {n_cities} Cities Tracked  ·  '
       f'Apache Airflow  →  dbt  →  PostgreSQL  →  Power BI',
       color=DIM, fontsize=10, transform=H.transAxes, va='center')

# Right pill badges
for i, (txt, clr) in enumerate([
        ('⬤  City: All', CYAN),
        ('⬤  Live',      TEAL),
        ('⬤  Realtime',  GOLD)]):
    H.text(0.78 + i * 0.075, 0.52, txt,
           color=clr, fontsize=9.5, fontweight='bold',
           transform=H.transAxes, va='center',
           bbox=dict(boxstyle='round,pad=0.4',
                     fc=BORD, ec=clr, lw=1.4, alpha=0.95))

# Bottom hairline
H.axhline(y=0.05, color=CYAN, linewidth=1.5,
          alpha=0.55, xmin=0.0, xmax=0.72)

# ─────────────────────────────────────────────────────────────────────────────
#  KPI CARDS ROW
# ─────────────────────────────────────────────────────────────────────────────
KG = gridspec.GridSpecFromSubplotSpec(
    1, 3, subplot_spec=G[1], wspace=0.014)

def kpi_card(ax, accent):
    ax.set_facecolor(PANEL)
    ax.axis('off')
    # Top accent stripe
    ax.add_patch(mpatches.Rectangle(
        (0, 0.962), 1, 0.038,
        transform=ax.transAxes,
        color=accent, linewidth=0, zorder=5))

def mini_spark(parent, values, color, pos):
    sp = parent.inset_axes(pos)
    sp.set_facecolor(PANEL)
    x = np.arange(len(values))
    sp.plot(x, values, color=color, linewidth=2.5, solid_capstyle='round')
    sp.fill_between(x, values, min(values) * 0.97,
                    alpha=0.22, color=color)
    sp.scatter([0, len(values)-1],
               [values[0], values[-1]],
               color=color, s=50, zorder=5)
    sp.axis('off')

# ── Card 1: Average Temperature
c1 = fig.add_subplot(KG[0])
kpi_card(c1, CYAN)
c1.text(0.06, 0.89, '🌡   AVERAGE TEMPERATURE',
        color=DIM, fontsize=11, fontweight='bold',
        transform=c1.transAxes, va='top')
c1.text(0.06, 0.65, f'{avg_c}°C',
        color=WHITE, fontsize=54, fontweight='bold',
        transform=c1.transAxes, va='top',
        path_effects=[pe.withStroke(linewidth=10, foreground=CYAN+'20')])
c1.text(0.06, 0.28, f'Across all {n_cities} cities',
        color=OFFWH, fontsize=12, transform=c1.transAxes, va='top')
c1.text(0.06, 0.12, f'Peak:  {max_c}°C',
        color=CYAN, fontsize=12, fontweight='bold',
        transform=c1.transAxes, va='top')
if has_city and has_avg:
    mini_spark(c1,
               df.groupby('city_name')['avg_temp_c'].mean().values,
               CYAN, [0.57, 0.10, 0.40, 0.34])

# ── Card 2: Highest Temperature
c2 = fig.add_subplot(KG[1])
kpi_card(c2, AMBER)
c2.text(0.06, 0.89, '🔥   HIGHEST TEMPERATURE',
        color=DIM, fontsize=11, fontweight='bold',
        transform=c2.transAxes, va='top')
c2.text(0.06, 0.65, f'{max_c}°C',
        color=WHITE, fontsize=54, fontweight='bold',
        transform=c2.transAxes, va='top',
        path_effects=[pe.withStroke(linewidth=10, foreground=AMBER+'20')])
c2.text(0.06, 0.28, f'Hottest:  {hottest}',
        color=OFFWH, fontsize=12, transform=c2.transAxes, va='top')
c2.text(0.06, 0.12, 'Max recorded temperature',
        color=AMBER, fontsize=12, fontweight='bold',
        transform=c2.transAxes, va='top')
if has_city and has_max:
    mini_spark(c2,
               df.groupby('city_name')['max_temp_c'].max().values,
               AMBER, [0.57, 0.10, 0.40, 0.34])

# ── Card 3: Alerts
c3 = fig.add_subplot(KG[2])
kpi_card(c3, RED)
c3.text(0.06, 0.89, '⚠   EXTREME WEATHER ALERTS',
        color=DIM, fontsize=11, fontweight='bold',
        transform=c3.transAxes, va='top')
c3.text(0.07, 0.65, str(len(df)),
        color=WHITE, fontsize=54, fontweight='bold',
        transform=c3.transAxes, va='top')
c3.text(0.07, 0.30, 'TOTAL RECORDS',
        color=OFFWH, fontsize=10, transform=c3.transAxes, va='top')
c3.text(0.58, 0.65, str(extreme),
        color=RED, fontsize=54, fontweight='bold',
        transform=c3.transAxes, va='top',
        path_effects=[pe.withStroke(linewidth=10, foreground=RED+'20')])
c3.text(0.58, 0.30, 'HEAT ALERTS',
        color=OFFWH, fontsize=10, transform=c3.transAxes, va='top')
# Alert bar
ab = c3.inset_axes([0.05, 0.04, 0.90, 0.14])
ab.barh([0], [0.50], color='#0094C6', height=1)
ab.barh([0], [0.30], left=[0.50], color=AMBER, height=1)
ab.barh([0], [0.20], left=[0.80], color=RED,   height=1)
for xp, lb in [(0.25,'Heavy Rain'), (0.65,'Heatwave'), (0.90,'Extreme')]:
    ab.text(xp, -2.4, lb, color=OFFWH, fontsize=8, ha='center')
ab.set_xlim(0, 1); ab.set_facecolor(PANEL); ab.axis('off')

# ─────────────────────────────────────────────────────────────────────────────
#  CHARTS ROW
# ─────────────────────────────────────────────────────────────────────────────
CG = gridspec.GridSpecFromSubplotSpec(
    1, 2, subplot_spec=G[2],
    wspace=0.014, width_ratios=[1.65, 1])

# ── LEFT: Grouped Bar Chart ───────────────────────────────────────────────────
ax = fig.add_subplot(CG[0])
ax.set_facecolor(PANEL)
for sp in ax.spines.values(): sp.set_visible(False)

if has_city and has_avg and has_max:
    cs = (df.groupby('city_name')
            .agg(avg=('avg_temp_c', 'mean'),
                 mx=('max_temp_c',  'max'))
            .reset_index()
            .sort_values('mx', ascending=False))

    x = np.arange(len(cs))
    w = 0.34

    # Drop-shadow bars
    ax.bar(x - w/2 + 0.06, cs['mx'],  width=w,
           color='#000000', alpha=0.22, zorder=1)
    ax.bar(x + w/2 + 0.06, cs['avg'], width=w,
           color='#000000', alpha=0.22, zorder=1)

    # Main bars
    bm = ax.bar(x - w/2, cs['mx'],  width=w,
                color=AMBER, alpha=0.93, zorder=3, linewidth=0)
    ba = ax.bar(x + w/2, cs['avg'], width=w,
                color=CYAN,  alpha=0.93, zorder=3, linewidth=0)

    # Value labels (small enough not to overlap)
    for bars, clr in [(bm, AMBER), (ba, CYAN)]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2,
                    h + 0.55, f'{h:.0f}°',
                    color=clr, fontsize=8.5,
                    ha='center', va='bottom', fontweight='bold')

    # Avg trend line
    ax.plot(x + w/2, cs['avg'],
            color=CYAN, linewidth=2.0, linestyle='--',
            alpha=0.50, zorder=5, marker='o', markersize=6,
            markerfacecolor=CYAN,
            markeredgecolor=BG, markeredgewidth=1.8)

    ax.set_xticks(x)
    ax.set_xticklabels([c.title() for c in cs['city_name']],
                        fontsize=11, rotation=22, ha='right', color=OFFWH)

    top_y = cs['mx'].max() + 14
    ax.set_ylim(0, top_y)
    ax.set_yticks(np.arange(0, top_y, 10))
    ax.set_yticklabels(
        [f'{int(v)}°C' for v in np.arange(0, top_y, 10)],
        fontsize=9, color=DIM)

    ax.yaxis.grid(True, color=GRID,
                  linestyle='--', linewidth=0.6, zorder=0)
    ax.tick_params(length=0)
    ax.set_axisbelow(True)

    ax.legend(
        [mpatches.Patch(color=AMBER),
         mpatches.Patch(color=CYAN)],
        ['Max Temp °C', 'Avg Temp °C'],
        loc='upper right', fontsize=10.5,
        facecolor=BG, edgecolor=BORD,
        labelcolor=OFFWH, framealpha=0.95,
        borderpad=0.9)

# Chart title INSIDE axis area (y=0.96 not 1.02 — prevents overlap)
ax.text(0.01, 0.97, 'TEMPERATURE BY CITY  (°C)',
        color=WHITE, fontsize=13, fontweight='bold',
        transform=ax.transAxes, va='top')
ax.text(0.01, 0.90,
        'Max vs Average — sorted by highest recorded temperature',
        color=DIM, fontsize=9, transform=ax.transAxes, va='top')
ax.set_facecolor(PANEL)

# ── RIGHT: Donut Chart ────────────────────────────────────────────────────────
dr = fig.add_subplot(CG[1])
dr.set_facecolor(PANEL)
dr.axis('off')

dr.text(0.05, 0.97, 'WEATHER CONDITIONS BREAKDOWN',
        color=WHITE, fontsize=13, fontweight='bold',
        transform=dr.transAxes, va='top')
dr.text(0.05, 0.91,
        'Dominant weather pattern across all records',
        color=DIM, fontsize=9, transform=dr.transAxes, va='top')

if has_cond:
    cc     = df['dominant_condition'].value_counts()
    total  = cc.sum()
    DCOLS  = [CYAN, GOLD, AMBER, RED, TEAL, PURP, '#FF99C8'][:len(cc)]

    # Outer glow ring
    glow = dr.inset_axes([0.07, 0.22, 0.86, 0.66])
    glow.pie(cc.values,
             colors=[c + '28' for c in DCOLS],
             startangle=90,
             wedgeprops=dict(width=0.64, edgecolor='none'))
    glow.axis('equal')

    # Main donut
    da = dr.inset_axes([0.10, 0.25, 0.80, 0.62])
    da.set_facecolor(PANEL)
    _, _, autotexts = da.pie(
        cc.values, labels=None, autopct='%1.0f%%',
        colors=DCOLS, startangle=90,
        wedgeprops=dict(width=0.46, edgecolor=PANEL, linewidth=3),
        pctdistance=0.73,
        textprops=dict(color=WHITE, fontsize=12, fontweight='bold'))
    for at in autotexts:
        at.set_path_effects(
            [pe.withStroke(linewidth=2, foreground='black')])
    da.axis('equal')

    # Centre label
    da.text(0,  0.12, str(total),
            color=WHITE, fontsize=36, fontweight='bold',
            ha='center', va='center', fontfamily='monospace',
            path_effects=[pe.withStroke(linewidth=4, foreground=BG)])
    da.text(0, -0.20, 'Total Records',
            color=DIM, fontsize=11, ha='center', va='center')

    # Condition tiles (legend) — BELOW donut, fits in remaining 22% height
    la = dr.inset_axes([0.03, 0.01, 0.94, 0.23])
    la.set_facecolor(PANEL)
    la.axis('off')
    nc = 3
    for i, (cond, cnt) in enumerate(cc.items()):
        ci = i % nc
        ri = i // nc
        bx = ci * 0.34 + 0.01
        by = 0.88 - ri * 0.52
        clr = DCOLS[i % len(DCOLS)]
        la.add_patch(mpatches.FancyBboxPatch(
            (bx, by - 0.22), 0.31, 0.40,
            boxstyle='round,pad=0.02',
            facecolor=clr, alpha=0.18, zorder=2,
            linewidth=1.2, edgecolor=clr))
        la.text(bx + 0.155, by + 0.07,
                cond.title(),
                color=WHITE, fontsize=9, ha='center',
                fontweight='bold', zorder=3)
        la.text(bx + 0.155, by - 0.11,
                str(cnt),
                color=clr, fontsize=10, ha='center',
                fontweight='bold', zorder=3)

plt.show()
