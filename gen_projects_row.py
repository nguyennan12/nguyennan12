import base64, math

W = 900
OUTER_PAD = 22
GAP = 16

BASE_BG = "#f7fafc"
BASE_BG2 = "#e4eef6"
GRID_LINE = "#1d5f80"
CARD_BG = "#f8fbfe"
TITLE_COLOR = "#1c2b3a"
SUB_COLOR = "#5a7d93"
IMG_BG1 = "#dce9f8"
IMG_BG2 = "#cddef2"

ACCENTS = ["#0b6f96", "#9a5a00", "#6d43c8", "#0b6f96"]  # teal, brown, purple, teal

CHAMFER = 14
THUMB_H = 104
PAD = 12
TITLE_FS = 15
LINK_FS = 10.5
LABEL_FS = 10
CARD_TOP_PAD = 16

def esc(s):
    return s.replace("&", "&amp;")

def load_b64(path, is_pref=False):
    if not path:
        return None
    if is_pref:
        with open(path) as f:
            return f.read()
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')

PER_SLIDE_SECONDS = 3.2  # how long each screenshot stays on screen before crossfading

def get_images(p):
    """Normalize a project's image_path into a list of (path, is_b64_file) tuples."""
    ip = p.get("image_path")
    if not ip:
        return []
    if isinstance(ip, list):
        is_pref = p.get("image_is_b64_file", False)
        return [(path, is_pref) for path in ip]
    return [(ip, p.get("image_is_b64_file", False))]

def slideshow_animate_tag(i, k, total_dur):
    """Build the <animate> opacity tag for image index i out of k in a crossfade loop."""
    if k <= 1:
        return ""
    slot = 1.0 / k
    fade = slot * 0.22
    if i == 0:
        keytimes = [0, max(slot - fade, 0.001), slot, 1]
        values = [1, 1, 0, 0]
    else:
        start = i * slot
        end = (i + 1) * slot
        keytimes = [0, max(start - fade, 0.0001), start, max(end - fade, start + 0.0001), end, 1]
        values = [0, 0, 1, 1, 0, 0]
    kt = ";".join(f"{t:.4f}" for t in keytimes)
    vs = ";".join(str(v) for v in values)
    return f'<animate attributeName="opacity" values="{vs}" keyTimes="{kt}" dur="{total_dur:.2f}s" repeatCount="indefinite"/>'

PROJECTS = [
    {"name": "VitaFlix", "url": "vitaflix.static4j.app",
     "image_path": [
         "/home/claude/projects-blue/vitaflix_b64.txt",
         "/home/claude/projects-blue/vitaflix_b64_2.txt",
         "/home/claude/projects-blue/vitaflix_b64_3.txt",
         "/home/claude/projects-blue/vitaflix_b64_4.txt",
     ],
     "image_is_b64_file": True,
     "status": "LIVE"},
    {"name": "NovaLive", "url": "novalive.online",
     "image_path": [
         "/home/claude/projects-blue/novalive_b64.txt",
         "/home/claude/projects-blue/novalive_b64_2.txt",
         "/home/claude/projects-blue/novalive_b64_3.txt",
         "/home/claude/projects-blue/novalive_b64_4.txt",
     ],
     "image_is_b64_file": True,
     "status": "LIVE"},
    {"name": "HotelBook", "url": "hotel.static4j.app",
     "image_path": [
         "/home/claude/projects-blue/hotelbook_b64_1.txt",
         "/home/claude/projects-blue/hotelbook_b64_2.txt",
         "/home/claude/projects-blue/hotelbook_b64_3.txt",
         "/home/claude/projects-blue/hotelbook_b64_4.txt",
     ],
     "image_is_b64_file": True,
     "status": "LIVE"},
    {"name": "Dự Án #4", "url": "your-project-4.com", "image_path": None, "status": "SOON"},
]

N = len(PROJECTS)
CONTENT_W = W - 2*OUTER_PAD
CARD_W = (CONTENT_W - (N-1)*GAP) / N

LABEL_BLOCK_H = LABEL_FS + 10
TITLE_BLOCK_H = TITLE_FS + 8
LINK_BLOCK_H = LINK_FS + 10

THUMB_GAP = 18   # space between the P0x/status label row and the thumbnail
BOTTOM_PAD = 8   # space below the link line, at the bottom of the card
CARD_H = round(LABEL_BLOCK_H + THUMB_GAP + THUMB_H + PAD + TITLE_BLOCK_H + LINK_BLOCK_H + BOTTOM_PAD)
H = OUTER_PAD*2 + CARD_H + 14

# ---------- pass 1: build all <defs> children up front ----------
defs = []
defs.append(f'<pattern id="gm" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M12 0H0V12" fill="none" stroke="{GRID_LINE}" stroke-opacity="0.08" stroke-width=".7"/></pattern>')
defs.append(f'<pattern id="gM" width="60" height="60" patternUnits="userSpaceOnUse"><rect width="60" height="60" fill="url(#gm)"/><path d="M60 0H0V60" fill="none" stroke="{GRID_LINE}" stroke-opacity="0.16" stroke-width="1"/></pattern>')
defs.append(f'<linearGradient id="bgG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BASE_BG}"/><stop offset="1" stop-color="{BASE_BG2}"/></linearGradient>')
defs.append(f'<clipPath id="plate"><rect x="0" y="0" width="{W}" height="{H}" rx="8"/></clipPath>')

x_cursor = OUTER_PAD
y_top = OUTER_PAD + 6
card_positions = []
for idx, p in enumerate(PROJECTS):
    cx, cy = x_cursor, y_top
    card_positions.append((cx, cy))
    tx, ty, tw, th = cx+PAD, cy+CARD_TOP_PAD+THUMB_GAP, CARD_W-2*PAD, THUMB_H
    defs.append(f'<clipPath id="th{idx}"><rect x="{tx:.1f}" y="{ty:.1f}" width="{tw:.1f}" height="{th}" rx="8"/></clipPath>')
    if not p.get("image_path"):
        defs.append(f'<pattern id="phb{idx}" width="14" height="14" patternTransform="rotate(45)" patternUnits="userSpaceOnUse"><rect width="14" height="14" fill="{IMG_BG1}"/><rect width="7" height="14" fill="{IMG_BG2}"/></pattern>')
    x_cursor += CARD_W + GAP

# ---------- pass 2: build the visible body ----------
body = []
body.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="8" fill="url(#bgG)"/>')
body.append(f'<g clip-path="url(#plate)"><rect x="0" y="0" width="{W}" height="{H}" fill="url(#gM)"/></g>')
body.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="8" fill="none" stroke="#b3cbd9"/>')
body.append(
    f'<g fill="none" stroke="#0b6f96" stroke-opacity=".5" stroke-width="1.4">'
    f'<path d="M13 27V13H27"/>'
    f'<path d="M{W-27} 13H{W-13}V27"/>'
    f'<path d="M{W-13} {H-27}V{H-13}H{W-27}"/>'
    f'<path d="M27 {H-13}H13V{H-27}"/></g>'
)

for idx, p in enumerate(PROJECTS):
    accent = ACCENTS[idx % len(ACCENTS)]
    cx, cy = card_positions[idx]

    pts = f"{cx},{cy} {cx+CARD_W-CHAMFER},{cy} {cx+CARD_W},{cy+CHAMFER} {cx+CARD_W},{cy+CARD_H} {cx},{cy+CARD_H}"
    body.append(f'<polygon points="{pts}" fill="{CARD_BG}" fill-opacity="1" stroke="{accent}" stroke-opacity=".55" stroke-width="1.6" stroke-linejoin="round"/>')
    # defensive solid backing behind the label row
    label_strip_h = LABEL_BLOCK_H + CARD_TOP_PAD + 4
    strip_pts = (
        f"{cx+1},{cy+1} {cx+CARD_W-CHAMFER},{cy+1} {cx+CARD_W-1},{cy+CHAMFER} "
        f"{cx+CARD_W-1},{cy+label_strip_h} {cx+1},{cy+label_strip_h}"
    )
    body.append(f'<polygon points="{strip_pts}" fill="{CARD_BG}" fill-opacity="1"/>')

    # label row
    label_y = cy + CARD_TOP_PAD
    row_cy = label_y + LABEL_FS/2 - 1
    body.append(f'<rect x="{cx+PAD-3.2:.1f}" y="{row_cy-3.2:.1f}" width="6.4" height="6.4" fill="{accent}" transform="rotate(45 {cx+PAD:.1f} {row_cy:.1f})"/>')
    body.append(f'<text x="{cx+PAD+11:.1f}" y="{row_cy+3.6:.1f}" font-size="{LABEL_FS}" letter-spacing="1" font-weight="700" fill="{accent}">P{idx+1:02d}</text>')

    status = p.get("status", "")
    if status:
        st_w = len(status)*6.4 + 30
        st_h = 19
        safe_right_edge = cx + CARD_W - CHAMFER - 6
        st_x = safe_right_edge - st_w
        st_fill = "#e8f8f1" if status == "LIVE" else "#f1f3f6"
        st_border = "#7bc9a4" if status == "LIVE" else "#c3cad6"
        st_text = "#0f6b46" if status == "LIVE" else "#6b7684"
        body.append(f'<rect x="{st_x:.1f}" y="{row_cy-st_h/2:.1f}" width="{st_w:.1f}" height="{st_h}" rx="{st_h/2:.1f}" fill="{st_fill}" stroke="{st_border}" stroke-width="1"/>')
        dotcol = "#1fa971" if status == "LIVE" else "#9aa3b0"
        body.append(f'<circle cx="{st_x+12:.1f}" cy="{row_cy:.1f}" r="2.6" fill="{dotcol}"/>')
        body.append(f'<text x="{st_x+20:.1f}" y="{row_cy+3:.1f}" font-size="8.5" letter-spacing=".6" fill="{st_text}" font-weight="700">{status}</text>')

    # subtle divider under the label row, centered in the gap before the thumbnail
    thumb_top_y = label_y + THUMB_GAP
    divider_y = (row_cy + LABEL_FS/2 + 6 + thumb_top_y) / 2
    body.append(f'<line x1="{cx+PAD:.1f}" y1="{divider_y:.1f}" x2="{cx+CARD_W-PAD:.1f}" y2="{divider_y:.1f}" stroke="{accent}" stroke-opacity=".18" stroke-width="1"/>')

    # thumbnail
    tx, ty, tw, th = cx+PAD, label_y+THUMB_GAP, CARD_W-2*PAD, THUMB_H
    images = get_images(p)
    if images:
        k = len(images)
        total_dur = k * PER_SLIDE_SECONDS
        body.append(f'<g clip-path="url(#th{idx})">')
        for i, (img_path, is_pref) in enumerate(images):
            b64 = load_b64(img_path, is_pref)
            anim = slideshow_animate_tag(i, k, total_dur)
            init_opacity = 1 if i == 0 else 0
            body.append(
                f'<image href="data:image/jpeg;base64,{b64}" x="{tx:.1f}" y="{ty:.1f}" '
                f'width="{tw:.1f}" height="{th}" preserveAspectRatio="xMidYMid slice" '
                f'opacity="{init_opacity}">{anim}</image>'
            )
        body.append('</g>')
    else:
        body.append(f'<g clip-path="url(#th{idx})"><rect x="{tx:.1f}" y="{ty:.1f}" width="{tw:.1f}" height="{th}" fill="url(#phb{idx})"/></g>')
        icx, icy = tx+tw/2, ty+th/2-6
        body.append(f'<rect x="{icx-13:.1f}" y="{icy-10:.1f}" width="26" height="20" rx="3" fill="none" stroke="{accent}" stroke-width="1.6"/>')
        body.append(f'<circle cx="{icx:.1f}" cy="{icy-1:.1f}" r="4" fill="none" stroke="{accent}" stroke-width="1.6"/>')
        body.append(f'<text x="{icx:.1f}" y="{ty+th-8:.1f}" text-anchor="middle" font-size="9.5" fill="{SUB_COLOR}" font-family="Arial,sans-serif">Ảnh preview</text>')

    # title + underline
    title_y = ty + th + PAD + TITLE_FS - 2
    body.append(f'<text x="{tx:.1f}" y="{title_y:.1f}" font-size="{TITLE_FS}" font-weight="700" fill="{TITLE_COLOR}">{esc(p["name"])}</text>')
    body.append(f'<line x1="{tx:.1f}" y1="{title_y+5:.1f}" x2="{tx+26:.1f}" y2="{title_y+5:.1f}" stroke="{accent}" stroke-width="2.4" stroke-linecap="round"/>')

    # link
    link_y = title_y + LINK_FS + 10
    body.append(f'<text x="{tx:.1f}" y="{link_y:.1f}" font-size="{LINK_FS}" fill="{SUB_COLOR}">{esc(p["url"])} \u2197</text>')

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
    f'font-family="\'Courier New\', monospace">\n'
    f'<title>Projects</title>\n'
    f'<defs>\n{chr(10).join(defs)}\n</defs>\n'
    f'{chr(10).join(body)}\n'
    f'</svg>\n'
)

with open('/home/claude/projects-blue/projects-row-v3.svg', 'w', encoding='utf-8') as f:
    f.write(svg)

print("H=", H, "CARD_W=", CARD_W, "CARD_H=", CARD_H)
