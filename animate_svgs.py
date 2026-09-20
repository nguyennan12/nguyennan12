#!/usr/bin/env python3
"""
Sinh ra profile-banner.svg và profile-stats.svg CÓ HIỆU ỨNG cho GitHub README.

Vì sao không dùng JavaScript?
  GitHub chặn <script> trong README, và SVG nhúng qua <img> cũng không chạy JS.
  Nên hiệu ứng được viết bằng CSS animation + SMIL (<animate>) đặt ngay trong SVG
  -> GitHub vẫn chạy được bình thường.

Cách dùng:
  python animate_svgs.py                      # dùng số trong CONFIG (offline)
  STATS_TOKEN=ghp_xxx python animate_svgs.py --user nguyennan12
                                              # lấy số THẬT từ GitHub API rồi sinh SVG
  python animate_svgs.py --out dist           # ghi ra thư mục khác

Nếu có --user thì cần token trong biến môi trường STATS_TOKEN (hoặc GITHUB_TOKEN).
Chữ / màu / nút timeline: sửa phần CONFIG bên dưới.
"""
import argparse
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# ───────────────────────────── CONFIG ─────────────────────────────
NAME = "Du Nguyen An"
FOLLOWERS = 1
ROLE = "Software Engineer"
SKILLS = "BACKEND ENGINEERING &#183; SYSTEM DESIGN &#183; DEVOPS"
TAGLINE = "LEARNING &#183; BUILDING &#183; GROWING"
NODES = [(270, "CODE"), (620, "BUILD"), (990, "SHIP"), (1340, "RUN")]

# (nhãn, giá trị, màu thanh gạch chân, chú thích dưới số | None)
STATS = [
    ("TOTAL CONTRIBUTIONS", 678, "#b8860b", "JAN 1 2026 - PRESENT"),
    ("CURRENT STREAK",      8,   "#2f6690", "SEP 9 - SEP 16 2026"),
    ("LONGEST STREAK",      63,  "#6b46c1", "MAR 16 - MAY 17 2026"),
    ("PUBLIC REPOS",        17,  "#3a8a5c", None),
]
TOTAL_FROM_YEAR = 2025   # tổng contributions tính từ 1/1 năm này tới nay (None = chỉ năm hiện tại)
MAX_SECONDS = 1.8     # số lớn nhất chạy tối đa bấy nhiêu giây
SECONDS_PER_UNIT = 0.04  # số nhỏ thì chạy ngắn hơn (mỗi đơn vị ~0.04s), tối thiểu 0.6s
FPS = 60              # tốc độ đổi số tối đa (khung/giây)


def count_seconds(value):
    return min(MAX_SECONDS, max(0.6, value * SECONDS_PER_UNIT))
# ──────────────────────────────────────────────────────────────────

CSS = """
@keyframes rise  {from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes fade  {from{opacity:0}to{opacity:1}}
@keyframes growx {from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes growy {from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop   {from{opacity:0;transform:scale(0)}to{opacity:1;transform:scale(1)}}
@keyframes draw  {from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes pulse {0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(1.9)}}
.a{transform-box:fill-box;transform-origin:center;animation-fill-mode:both;
   animation-duration:var(--t,.9s);animation-delay:var(--d,0s);
   animation-timing-function:cubic-bezier(.33,1,.68,1)}
.rise{animation-name:rise}.fade{animation-name:fade}.pop{animation-name:pop}
.growx{animation-name:growx}.growy{animation-name:growy}
.corner{stroke-dasharray:1;animation-name:draw}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2s ease-in-out infinite}
"""

BG = """
  <rect width="{w}" height="{h}" rx="18" fill="#fafcfe"/>
  <rect width="{w}" height="{h}" rx="18" fill="url(#{grid})"/>
  <rect x="4" y="4" width="{w4}" height="{h4}" rx="16" fill="none" stroke="#c9d6e3" stroke-width="2"/>
"""


def corners(paths):
    out = ['<g stroke="#33475b" stroke-width="3" fill="none" stroke-linecap="round">']
    for i, d in enumerate(paths):
        out.append(f'  <path class="a corner" pathLength="1" style="--d:{0.1 * i:.1f}s;--t:1s" d="{d}"/>')
    out.append("</g>")
    return "\n  ".join(out)


def svg_open(w, h, grid, drift=False):
    anim = ('<animateTransform attributeName="patternTransform" type="translate" '
            'from="0 0" to="40 40" dur="12s" repeatCount="indefinite"/>') if drift else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="\'Courier New\', monospace">\n'
            f'  <style>{CSS}</style>\n'
            f'  <defs>\n'
            f'    <pattern id="{grid}" width="40" height="40" patternUnits="userSpaceOnUse">'
            f'<path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e3ebf2" stroke-width="1"/>{anim}</pattern>\n'
            f'  </defs>\n')


# ─────────────────────────── BANNER ───────────────────────────
def banner(followers=FOLLOWERS):
    w, h = 1600, 560
    s = svg_open(w, h, "grid", drift=True)
    s += BG.format(w=w, h=h, w4=w - 8, h4=h - 8, grid="grid")
    s += "  " + corners(["M 40 70 L 40 40 L 70 40", "M 1530 40 L 1560 40 L 1560 70",
                         "M 40 490 L 40 520 L 70 520", "M 1530 520 L 1560 520 L 1560 490"]) + "\n"

    s += f'''
  <text class="a rise" style="--d:.3s" x="800" y="110" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-weight="800" font-size="52" fill="#16232f">{NAME}</text>

  <g class="a rise" style="--d:.6s">
    <rect x="660" y="138" width="280" height="42" rx="10" fill="#f2f6fa" stroke="#cfd8e3" stroke-width="1.5"/>
    <circle class="pulse" cx="695" cy="159" r="4.5" fill="#b8860b"/>
    <text x="810" y="165" text-anchor="middle" font-size="14" font-weight="600" letter-spacing="0.5" fill="#33475b">GITHUB&#160;&#183;&#160;{followers} FOLLOWER{"S" if followers != 1 else ""}</text>
  </g>

  <rect class="a growx" style="--d:.95s;--t:.7s;transform-origin:100% 50%" x="740" y="198" width="60" height="4" fill="#2f6690"/>
  <rect class="a growx" style="--d:.95s;--t:.7s;transform-origin:0% 50%"   x="800" y="198" width="60" height="4" fill="#b8860b"/>

  <text class="a rise" style="--d:1s" x="800" y="247" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="30" fill="#33475b">{ROLE}</text>
  <text class="a rise" style="--d:1.15s" x="800" y="282" text-anchor="middle" font-size="18" letter-spacing="1.5" fill="#7c93a8">{SKILLS}</text>

  <line class="a growx" style="--d:1.3s;--t:1.3s;transform-origin:0% 50%" x1="200" y1="360" x2="1400" y2="360" stroke="#c9d6e3" stroke-width="2"/>
'''
    # các nút timeline: hiện ra đúng lúc đường kẻ "chạy tới"
    s += '  <g font-size="17" letter-spacing="2" fill="#33475b" text-anchor="middle">\n'
    for i, (x, label) in enumerate(NODES):
        d = 1.3 + 1.3 * (x - 200) / 1200
        s += f'    <circle class="a pop" style="--d:{d:.2f}s;--t:.5s" cx="{x}" cy="360" r="9" fill="#fafcfe" stroke="#33475b" stroke-width="2.5"/>\n'
        if i == 0:
            s += f'    <circle class="a pop" style="--d:{d + .1:.2f}s;--t:.5s" cx="{x}" cy="360" r="3" fill="#33475b"/>\n'
            s += f'    <circle class="a pop" style="--d:{d + .2:.2f}s;--t:.5s" cx="{x + 35}" cy="360" r="4" fill="#b8860b"/>\n'
        s += f'    <text class="a rise" style="--d:{d + .1:.2f}s;--t:.6s" x="{x}" y="392">{label}</text>\n'
    s += '  </g>\n'

    # hạt sáng chạy dọc timeline (lặp vô hạn)
    x0, x1 = NODES[0][0], NODES[-1][0]
    s += f'''
  <circle cx="{x0}" cy="360" r="5" fill="#2f6690" opacity="0">
    <animate attributeName="cx" values="{x0};{x1};{x1}" keyTimes="0;.7;1" dur="4.5s" begin="3s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0;.9;.9;0;0" keyTimes="0;.05;.65;.72;1" dur="4.5s" begin="3s" repeatCount="indefinite"/>
  </circle>

  <text class="a fade" style="--d:2.8s;--t:1s" x="800" y="440" text-anchor="middle" font-size="18" letter-spacing="2" fill="#7c93a8">{TAGLINE}</text>
</svg>
'''
    return s


# ─────────────────────────── STATS ───────────────────────────
def odometer(uid, cx, y, value, delay, tail=0.3, size=52, W=30, L=72):
    """Số đếm nhanh 1 -> value kiểu đồng hồ cơ: mỗi chữ số là 1 cột 0-9 trượt lên, dùng SMIL (không cần JS)."""
    n = len(str(value))
    dur = count_seconds(value)
    total = delay + dur + tail
    # đếm tuyến tính 1 -> value; số nhỏ hiện từng số một, số lớn nhảy theo FPS
    start = min(1, value)
    frames = max(1, min(value - start, round(dur * FPS)))
    vals = [round(start + (value - start) * i / frames) for i in range(frames + 1)]
    times = [0.0] + [(delay + dur * i / frames) / total for i in range(1, frames + 1)]
    x0 = cx - n * W / 2

    cols = []
    for k in range(n):
        place = 10 ** (n - 1 - k)
        # ô số 10 = ô trống -> ẩn số 0 ở đầu khi đang đếm
        idx = lambda v: 10 if (place > 1 and v < place) else (v // place) % 10
        seq = [idx(v) for v in vals]
        kt, kv, prev = [], [], None
        for t, i in zip(times, seq):                       # bỏ khung trùng để file gọn
            if i != prev:
                kt.append(f"{t:.4f}")
                kv.append(f"0 {-i * L}")
                prev = i
        cells = "".join(f'<text y="{y + j * L}">{j}</text>' for j in range(10))
        cols.append(
            f'<g transform="translate({x0 + (k + .5) * W:.1f} 0)">'
            f'<g transform="translate(0 {-seq[-1] * L})">'
            f'<animateTransform attributeName="transform" type="translate" calcMode="discrete" '
            f'dur="{total:.3f}s" begin="0s" fill="freeze" keyTimes="{";".join(kt)}" values="{";".join(kv)}"/>'
            f'{cells}</g></g>')
    return (f'<clipPath id="c{uid}"><rect x="{x0 - 4}" y="{y - 46}" width="{n * W + 8}" height="60"/></clipPath>\n'
            f'  <g clip-path="url(#c{uid})" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" '
            f'font-weight="800" font-size="{size}" fill="#16232f">\n    ' + "\n    ".join(cols) + "\n  </g>")


def stats(items=STATS):
    w, h = 1600, 260
    s = svg_open(w, h, "grid3")
    s += BG.format(w=w, h=h, w4=w - 8, h4=h - 8, grid="grid3")
    s += "  " + corners(["M 40 70 L 40 30 L 70 30", "M 1530 30 L 1560 30 L 1560 70",
                         "M 40 190 L 40 230 L 70 230", "M 1530 230 L 1560 230 L 1560 190"]) + "\n\n"

    for i, x in enumerate((400, 800, 1200)):
        s += (f'  <line class="a growy" style="--d:{.2 + .1 * i:.1f}s;--t:.8s;transform-origin:50% 0%" '
              f'x1="{x}" y1="45" x2="{x}" y2="215" stroke="#e3ebf2" stroke-width="1.5"/>\n')

    for i, (label, value, color, caption) in enumerate(items):
        cx = 200 + 400 * i
        d = .3 + .15 * i
        s += f'''
  <!-- {label} -->
  <text class="a rise" style="--d:{d:.2f}s" x="{cx}" y="80" text-anchor="middle" font-size="15" letter-spacing="2" fill="#7c93a8">{label}</text>
  {odometer(i, cx, 150, value, d + .15)}
  <rect class="a growx" style="--d:{d + .15:.2f}s;--t:{count_seconds(value):.2f}s;animation-timing-function:linear" x="{cx - 50}" y="164" width="100" height="4" rx="2" fill="{color}"/>
'''
        if caption:
            lines = caption if isinstance(caption, (list, tuple)) else [caption]
            y0 = 200 if len(lines) == 1 else 194
            for j, line in enumerate(lines):
                s += (f'  <text class="a fade" style="--d:{d + .15 + count_seconds(value) + .15 * j:.2f}s;--t:.8s" '
                      f'x="{cx}" y="{y0 + 16 * j}" text-anchor="middle" font-size="12" fill="#9aacba">{line}</text>\n')
    return s + "</svg>\n"


# ─────────────────────── LẤY SỐ THẬT TỪ GITHUB ───────────────────────
REPO_LISTS = ("commitContributionsByRepository", "pullRequestContributionsByRepository",
              "pullRequestReviewContributionsByRepository", "issueContributionsByRepository")
BY_REPO = "repository { nameWithOwner owner { login } } contributions(first: 1) { totalCount }"
QUERY = """
query($login: String!, $from: DateTime!, $jan1: DateTime!) {
  user(login: $login) {
    followers { totalCount }
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    contributionsCollection(from: $from) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
    ytd: contributionsCollection(from: $jan1) {
      commitContributionsByRepository(maxRepositories: 100) { %(r)s }
      pullRequestContributionsByRepository(maxRepositories: 100) { %(r)s }
      pullRequestReviewContributionsByRepository(maxRepositories: 100) { %(r)s }
      issueContributionsByRepository(maxRepositories: 100) { %(r)s }
    }
  }
}
""" % {"r": BY_REPO}


def gh_graphql(login, token, past_years=()):
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=364)                             # API cho tối đa 1 năm
    by_repo = "".join(f" {k}(maxRepositories: 100) {{ {BY_REPO} }}" for k in REPO_LISTS)
    extra = "".join(
        f'\n    y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") '
        f'{{ contributionCalendar {{ totalContributions }}{by_repo} }}' for y in past_years)
    query = QUERY.replace("    followers { totalCount }", "    followers { totalCount }" + extra)
    body = json.dumps({"query": query, "variables": {
        "login": login, "from": since.strftime("%Y-%m-%dT00:00:00Z"),
        "jan1": f"{now.year}-01-01T00:00:00Z"}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats-svg"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors") or not data.get("data", {}).get("user"):
        raise RuntimeError(f"GitHub API lỗi: {data.get('errors') or 'không tìm thấy user'}")
    return data["data"]["user"]


def fmt(d):                                    # date -> "SEP 9"
    return f"{d.strftime('%b').upper()} {d.day}"


def span(a, b):                                # "MAR 16 - MAY 17 2026"
    return f"{fmt(a)} - {fmt(b)} {b.year}"


def compute_stats(days, followers, repos, others=(0, 0), past_total=0, from_year=None):
    """days: [(date, count)] theo thứ tự thời gian, ngày cuối = hôm nay."""
    today = days[-1][0]
    jan1 = date(today.year, 1, 1)
    total = past_total + sum(c for d, c in days if d >= jan1)

    # streak dài nhất
    best, best_rng, run_start, run = 0, None, None, 0
    for d, c in days:
        if c > 0:
            run_start = run_start or d
            run += 1
            if run > best:
                best, best_rng = run, (run_start, d)
        else:
            run_start, run = None, 0

    # streak hiện tại (hôm nay chưa commit thì vẫn tính từ hôm qua)
    i = len(days) - 1
    if days[i][1] == 0:
        i -= 1
    cur_end = days[i][0] if i >= 0 else None
    cur = 0
    while i >= 0 and days[i][1] > 0:
        cur, i = cur + 1, i - 1
    cur_rng = (days[i + 1][0], cur_end) if cur else None

    n_contrib, n_repos = others
    total_cap = f"JAN 1 {from_year or today.year} - PRESENT"
    if n_contrib:                                # dòng phụ: đóng góp cho repo của người khác
        total_cap = [total_cap, f"{n_contrib} IN {n_repos} OTHER REPO{'S' if n_repos != 1 else ''}"]
    items = [
        ("TOTAL CONTRIBUTIONS", total, "#b8860b", total_cap),
        ("CURRENT STREAK", cur, "#2f6690", span(*cur_rng) if cur else "NO ACTIVE STREAK"),
        ("LONGEST STREAK", best, "#6b46c1", span(*best_rng) if best else "-"),
        ("PUBLIC REPOS", repos, "#3a8a5c", None),
    ]
    return items, followers


def others_contrib(collections, login):
    """Cộng commit + PR + review + issue trong repo KHÔNG thuộc về `login` (gồm cả repo của tổ chức),
    gộp qua nhiều năm."""
    per_repo = {}
    for coll in collections:
        for key, group in coll.items():
            if not key.endswith("ByRepository"):
                continue
            for e in group:
                r = e["repository"]
                if r["owner"]["login"].lower() != login.lower():
                    per_repo[r["nameWithOwner"]] = per_repo.get(r["nameWithOwner"], 0) + e["contributions"]["totalCount"]
    per_repo = {k: v for k, v in per_repo.items() if v > 0}
    return sum(per_repo.values()), len(per_repo)


def fetch_stats(login, token):
    this_year = datetime.now(timezone.utc).year
    past_years = list(range(TOTAL_FROM_YEAR, this_year)) if TOTAL_FROM_YEAR else []
    u = gh_graphql(login, token, past_years)
    past_total = sum(u[f"y{y}"]["contributionCalendar"]["totalContributions"] for y in past_years)
    days = [(date.fromisoformat(d["date"]), d["contributionCount"])
            for w in u["contributionsCollection"]["contributionCalendar"]["weeks"]
            for d in w["contributionDays"]]
    days.sort()
    return compute_stats(days, u["followers"]["totalCount"], u["repositories"]["totalCount"],
                         others_contrib([u["ytd"]] + [u[f"y{y}"] for y in past_years], login),
                         past_total, TOTAL_FROM_YEAR if past_years else None)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".", help="thư mục ghi file (mặc định: thư mục hiện tại)")
    ap.add_argument("--user", help="GitHub username -> lấy số thật qua API (cần token)")
    args = ap.parse_args()

    items, followers = STATS, FOLLOWERS
    if args.user:
        token = os.environ.get("STATS_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("Thiếu token: đặt biến môi trường STATS_TOKEN (hoặc GITHUB_TOKEN)")
        items, followers = fetch_stats(args.user, token)
        print("Số liệu:", [(i[0], i[1]) for i in items], "| followers:", followers)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "profile-banner.svg").write_text(banner(followers), encoding="utf-8")
    (out / "profile-stats.svg").write_text(stats(items), encoding="utf-8")
    print(f"Đã tạo profile-banner.svg và profile-stats.svg trong {out.resolve()}")
