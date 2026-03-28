#!/usr/bin/env python3
"""Generates static HTML from JSON configs."""

import glob
import json
import os
import shutil

from PIL import Image, ImageDraw, ImageFont

CONFIG_DIR = "config"
OUTPUT_DIR = "html"


WATERMARK_TEXT = "© emanueleagle.net"


def watermark_image(src_path, dst_path):
    img = Image.open(src_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = max(14, img.width // 40)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    margin = 10
    x = img.width - text_w - margin - 60
    y = img.height - text_h - margin - 20

    # Shadow for readability
    draw.text((x + 1, y + 1), WATERMARK_TEXT, font=font, fill=(0, 0, 0, 180))
    draw.text((x, y), WATERMARK_TEXT, font=font, fill=(255, 255, 255, 200))

    watermarked = Image.alpha_composite(img, overlay).convert("RGB")
    watermarked.save(dst_path, quality=90)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def site_config():
    return load_json(os.path.join(CONFIG_DIR, "site.json"))


def render_nav(site, current_title, prefix=""):
    parts = []
    for item in site["nav"]:
        label = item["label"]
        href = item["href"]
        if label == current_title:
            parts.append(f"[<b>{label}</b>]")
        else:
            parts.append(f'[<a href="{prefix}{href}">{label}</a>]')
    return "\n&nbsp; ".join(parts)


def render_header(site, prefix=""):
    return f"""<!-- LOGO / HEADER -->
<tr>
<td colspan="2">
<table border="2" cellpadding="0" cellspacing="0" bordercolor="#000000"><tr>
<td bgcolor="#000000"><font face="Times New Roman, Times, serif" size="5" color="#FFFFFF"><b>&nbsp;Emanuel&nbsp;</b></font></td>
<td bgcolor="#FFFFFF"><font face="Times New Roman, Times, serif" size="5"><b>&nbsp;Eagle&nbsp;</b></font></td>
</tr></table>
</td>
</tr>"""


def render_footer(site):
    return f"""<!-- FOOTER -->
<tr>
<td colspan="2">
<hr size="1" noshade>
<font face="Times New Roman, Times, serif" size="2">
{site["footer"]}
</font>
<br><br>
</td>
</tr>"""


def wrap_page(title, site, body, prefix=""):
    nav = render_nav(site, title, prefix)
    header = render_header(site, prefix)
    footer = render_footer(site)
    return f"""<!DOCTYPE html>
<html>
<head>
<title>{title} - {site["name"]}</title>
<meta charset="utf-8">
</head>
<body bgcolor="#E8E8E8" text="#000000" link="#0000FF" vlink="#800080" alink="#FF0000">

<table border="0" cellpadding="10" cellspacing="0" width="100%">

{header}

<!-- NAVIGATION -->
<tr>
<td colspan="2">
<font face="Times New Roman, Times, serif" size="3">
{nav}
</font>
<hr size="1" noshade>
</td>
</tr>

{body}

{footer}

</table>

</body>
</html>
"""


def render_two_column(page):
    left_parts = []
    for i, blurb in enumerate(page["left_blurbs"]):
        left_parts.append(f"<i>{blurb}</i>")
        if i < len(page["left_blurbs"]) - 1:
            left_parts.append("<br><br><br><br>")
    left = "\n\n".join(left_parts)

    right_parts = []
    for paragraph in page["right_content"]:
        right_parts.append(paragraph)
    right = "\n<br><br>\n\n".join(right_parts)

    return f"""<!-- MAIN TWO-COLUMN CONTENT -->
<tr valign="top">

<td width="25%">
<br>
<font face="Times New Roman, Times, serif" size="3">
{left}
</font>
</td>

<td width="75%">
<br>
<font face="Times New Roman, Times, serif" size="3">
{right}
</font>
</td>

</tr>"""


def render_list(page):
    status_colors = {
        "Complete": "#006600",
        "In Progress": "#CC6600",
    }

    tags_html = ""
    for tag in page.get("tags", []):
        tags_html += f'<option value="{tag}">{tag}</option>'

    rows = ""
    for item in page["items"]:
        link_html = f'<a href="{item["link"]}">View</a>' if item.get("link") else ""
        status = item.get("status", "")
        color = status_colors.get(status, "#000000")
        status_html = f'<font color="{color}"><b>{status}</b></font>' if status else ""
        tags = ",".join(item.get("tags", []))
        rows += f"""<tr class="project-row" data-tags="{tags}">
<td><font face="Times New Roman" size="3"><b>{item["name"]}</b></font></td>
<td><font face="Times New Roman" size="3">{item["description"]}</font></td>
<td align="center"><font face="Times New Roman" size="3">{status_html}</font></td>
<td align="center"><font face="Times New Roman" size="3">{link_html}</font></td>
</tr>
"""

    tags_filter = ""
    if page.get("tags"):
        tags_filter = f"""<label for="project-tags">Filter by tag:</label>
<select id="project-tags" name="project-tags">
{tags_html}
</select>"""

    return f"""<tr>
<td colspan="2">
<br>
<font face="Times New Roman, Times, serif" size="3">
{page["intro"]}
{tags_filter}
</font>
<br><br>
<table border="1" cellpadding="5" cellspacing="0" bordercolor="#808080" width="100%">
<tr bgcolor="#FFFFCC">
<td><font face="Arial" size="2"><b>Project</b></font></td>
<td><font face="Arial" size="2"><b>Description</b></font></td>
<td><font face="Arial" size="2"><b>Status</b></font></td>
<td><font face="Arial" size="2"><b>Link</b></font></td>
</tr>
{rows}</table>
</td>
</tr>
<script>
document.getElementById('project-tags').addEventListener('change', function() {{
  var selected = this.value;
  document.querySelectorAll('.project-row').forEach(function(el) {{
    if (selected === 'All') {{
      el.style.display = '';
    }} else {{
      var tags = el.getAttribute('data-tags').split(',');
      el.style.display = tags.indexOf(selected) !== -1 ? '' : 'none';
    }}
  }});
}});
</script>"""


def render_blog_index(page):
    posts_dir = page["posts_dir"]
    posts = []
    for path in sorted(glob.glob(os.path.join(posts_dir, "*.json")), reverse=True):
        post = load_json(path)
        slug = os.path.splitext(os.path.basename(path))[0]
        posts.append((slug, post))

    tags_html = ""
    for tag in page.get("tags", []):
        tags_html += f'<option value="{tag}">{tag}</option>'

    post_links = ""
    for slug, post in posts:
        description = post.get("description", "")
        desc_html = f"""<br><font size="2">{description}</font>""" if description else ""
        tags = ",".join(post.get("tags", []))
        post_links += f"""<div class="post-item" data-tags="{tags}"><b><a href="blog/{slug}.html">{post["title"]}</a></b> <font size="2" color="#666666">({post["date"]})</font>{desc_html}<br><br>
</div>
"""

    tags_filter = ""
    if page.get("tags"):
        tags_filter = f"""<label for="blog-tags">Filter by tag:</label>
<select id="blog-tags" name="blog-tags">
{tags_html}
</select>"""

    return f"""<tr>
<td colspan="2">
<br>
<font face="Times New Roman, Times, serif" size="3">
{page["intro"]}
{tags_filter}
</font>
<br><br>
<hr size="1" noshade>
{post_links}
</td>
</tr>
<script>
document.getElementById('blog-tags').addEventListener('change', function() {{
  var selected = this.value;
  document.querySelectorAll('.post-item').forEach(function(el) {{
    if (selected === 'All') {{
      el.style.display = '';
    }} else {{
      var tags = el.getAttribute('data-tags').split(',');
      el.style.display = tags.indexOf(selected) !== -1 ? '' : 'none';
    }}
  }});
}});
</script>"""


def render_gallery(page):
    photos_html = ""
    tags_html = ""
    for i in range(len(page["tags"])):
        tag = page["tags"][i]
        tags_html += f"<option value={tag}>{tag}</option>"
    for photo in sorted(page["photos"], key=lambda p: p["title"]):
        tags = ",".join(photo.get("tags", []))
        photos_html += f"""<div class="photo-item" data-tags="{tags}">
<table border="1" cellpadding="4" cellspacing="0" bordercolor="#808080">
<tr><td><img src="{photo["src"]}" alt="{photo["title"]}" width="400"></td></tr>
<tr><td bgcolor="#FFFFCC"><font face="Times New Roman" size="2">
<b>{photo["title"]}</b><br>
{photo["caption"]}
<br><font size="1" color="#666666">{photo["date"]}</font>
</font></td></tr>
</table>
<br>
</div>
"""

    return f"""<tr>
<td colspan="2">
<br>
<font face="Times New Roman, Times, serif" size="3">
{page["intro"]}
<label for="tags">Filter images with this:</label>
<select id="tags" name="tags">
{tags_html}
</select>
</font>
<br><br>
{photos_html}
</td>
</tr>
<script>
document.getElementById('tags').addEventListener('change', function() {{
  var selected = this.value;
  document.querySelectorAll('.photo-item').forEach(function(el) {{
    if (selected === 'All') {{
      el.style.display = '';
    }} else {{
      var tags = el.getAttribute('data-tags').split(',');
      el.style.display = tags.indexOf(selected) !== -1 ? '' : 'none';
    }}
  }});
}});
</script>"""


def render_blog_post(slug, post, site):
    paragraphs = "\n<br><br>\n\n".join(post["content"])

    body = f"""<tr>
<td colspan="2">
<br>
<font face="Times New Roman, Times, serif" size="4"><b>{post["title"]}</b></font>
<br>
<font face="Times New Roman, Times, serif" size="2" color="#666666">{post["date"]}</font>
<br><br>
<font face="Times New Roman, Times, serif" size="3">
{paragraphs}
</font>
<br><br>
<a href="../blog.html">&lt;&lt; Back to all posts</a>
</td>
</tr>"""

    return wrap_page(post["title"], site, body, prefix="../")


def build():
    site = site_config()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "blog"), exist_ok=True)

    # Copy and watermark images
    src_images = os.path.join(CONFIG_DIR, "pages", "images")
    dst_images = os.path.join(OUTPUT_DIR, "images")
    if os.path.isdir(src_images):
        if os.path.exists(dst_images):
            shutil.rmtree(dst_images)
        os.makedirs(dst_images)
        for fname in os.listdir(src_images):
            src = os.path.join(src_images, fname)
            dst = os.path.join(dst_images, fname)
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                watermark_image(src, dst)
                print(f"Watermarked {fname}")
            else:
                shutil.copy2(src, dst)

    # Build pages
    for path in glob.glob(os.path.join(CONFIG_DIR, "pages", "*.json")):
        page = load_json(path)
        layout = page["layout"]
        slug = os.path.splitext(os.path.basename(path))[0]

        if layout == "two-column":
            body = render_two_column(page)
        elif layout == "list":
            body = render_list(page)
        elif layout == "blog":
            body = render_blog_index(page)
        elif layout == "gallery":
            body = render_gallery(page)
        else:
            print(f"Unknown layout: {layout}")
            continue

        html = wrap_page(page["title"], site, body)
        out_path = os.path.join(OUTPUT_DIR, f"{slug}.html")
        with open(out_path, "w") as f:
            f.write(html)
        print(f"Built {out_path}")

    # Build blog posts
    for path in sorted(glob.glob(os.path.join(CONFIG_DIR, "blog", "*.json"))):
        post = load_json(path)
        slug = os.path.splitext(os.path.basename(path))[0]
        html = render_blog_post(slug, post, site)
        out_path = os.path.join(OUTPUT_DIR, "blog", f"{slug}.html")
        with open(out_path, "w") as f:
            f.write(html)
        print(f"Built {out_path}")


if __name__ == "__main__":
    build()
