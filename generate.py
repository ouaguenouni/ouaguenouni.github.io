import markdown
import re
from pathlib import Path
import os
import readtime
from datetime import datetime
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from PIL import Image, ImageDraw, ImageFont

def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), '%d/%m/%Y')
    except ValueError:
        print(f"⚠️  Warning: Could not parse date '{date_str}', expected DD/MM/YYYY format")
        return datetime(1900, 1, 1)

def format_date_display(date_str):
    try:
        dt = datetime.strptime(date_str.strip(), '%d/%m/%Y')
        day = dt.day
        month = dt.strftime('%B')
        year = dt.year
        return f'{day} {month} {year}'
    except:
        return date_str

def generate_og_thumbnail(output_path, title, background_path=None, width=1200, height=630, font_path=None):
    if background_path and Path(background_path).exists():
        bg = Image.open(background_path).convert("RGB")
        bg = bg.resize((width, height))
        img = bg
    else:
        img = Image.new('RGB', (width, height), color=(40, 40, 40))

    draw = ImageDraw.Draw(img)

    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 150))
    img = Image.alpha_composite(img.convert('RGBA'), overlay)

    if font_path is None:
        font_path = "et-book.ttf"
    try:
        font_size = 80
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    words = title.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= width - 100:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines)
    y_text = (height - total_text_height) // 2

    draw = ImageDraw.Draw(img)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x_text = (width - text_width) // 2
        draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255))
        y_text += text_height

    img.convert('RGB').save(output_path)
    return output_path

def isolate_html_scripts(html_content):
    def wrap_script(match):
        opening_tag = match.group(1)
        script_content = match.group(2)
        closing_tag = match.group(3)

        if 'src=' in opening_tag:
            return match.group(0)

        if 'type="module"' in opening_tag or "type='module'" in opening_tag:
            return match.group(0)

        wrapped_content = f"\n(function() {{\n{script_content}\n}})();\n"

        return f"{opening_tag}{wrapped_content}{closing_tag}"

    pattern = r'(<script[^>]*>)(.*?)(</script>)'
    isolated_html = re.sub(pattern, wrap_script, html_content, flags=re.DOTALL | re.IGNORECASE)

    return isolated_html

def convert_md_to_html(md_file, output_file=None, template_file='article_template.html'):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    frontmatter_match = re.search(frontmatter_pattern, content, re.DOTALL)

    title = "Untitled Article"
    date = "No date"
    description = ""
    thumbnail = None

    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        content = content[frontmatter_match.end():]

        title_match = re.search(r'title:\s*(.+)', frontmatter)
        if title_match:
            title = title_match.group(1).strip()

        date_match = re.search(r'date:\s*(.+)', frontmatter)
        if date_match:
            date = date_match.group(1).strip()

        description_match = re.search(r'description:\s*(.+)', frontmatter)
        if description_match:
            description = description_match.group(1).strip()

        thumbnail_match = re.search(r'thumbnail:\s*(.+)', frontmatter)
        if thumbnail_match:
            thumbnail = thumbnail_match.group(1).strip()

        is_draft = False
        draft_match = re.search(r'draft:\s*(true|false)', frontmatter, re.IGNORECASE)
        if draft_match:
            is_draft = draft_match.group(1).lower() == 'true'

    html_embed_store = []

    def _stash_html_embed(m):
        file_path = m.group(1).strip()
        idx = len(html_embed_store)

        md_dir = Path(md_file).parent
        full_path = md_dir / file_path

        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            html_content = isolate_html_scripts(html_content)

            wrapped_html = f'<div class="embedded-html" id="embed-{idx}">\n{html_content}\n</div>'
            html_embed_store.append(wrapped_html)
        else:
            print(f"⚠️  Warning: HTML file not found: {full_path}")
            html_embed_store.append(f'<p style="color: red;">Error: HTML file not found: {file_path}</p>')

        return f"\n\n{{{{HTMLEMBED_{idx}}}}}\n\n"

    content = re.sub(r':::html\s+(.+?)\s+:::', _stash_html_embed, content, flags=re.DOTALL)

    block_store = []
    inline_store = []

    def _stash_block(m):
        idx = len(block_store)
        block_store.append(m.group(1))
        return f"\n\n{{{{MATHBLOCK_{idx}}}}}\n\n"

    def _stash_inline(m):
        idx = len(inline_store)
        inline_store.append(m.group(1))
        return f"{{{{MATHINLINE_{idx}}}}}"

    content = re.sub(r'\$\$(.*?)\$\$', _stash_block, content, flags=re.DOTALL)
    content = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', _stash_inline, content, flags=re.DOTALL)

    md = markdown.Markdown(
        extensions=['extra', 'fenced_code', 'codehilite'],
        extension_configs={
            'codehilite': {'guess_lang': False, 'use_pygments': False}
        }
    )
    article_content = md.convert(content)

    for i, html_content in enumerate(html_embed_store):
        article_content = article_content.replace(f"{{{{HTMLEMBED_{i}}}}}", html_content)

    for i, tex in enumerate(block_store):
        article_content = article_content.replace(f"{{{{MATHBLOCK_{i}}}}}", f"$$\n{tex}\n$$")
    for i, tex in enumerate(inline_store):
        article_content = article_content.replace(f"{{{{MATHINLINE_{i}}}}}", f"${tex}$")

    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()

    html_output = template.replace('{{TITLE}}', title)
    html_output = html_output.replace('{{DATE}}', format_date_display(date))
    html_output = html_output.replace('{{CONTENT}}', article_content)

    time_read = readtime.of_text(content)
    html_output = html_output.replace('{{READ_TIME}}', str(time_read))

    link_path = os.path.relpath(output_file, start=Path.cwd()).replace('\\', '/')

    if not thumbnail:
        local_thumb = Path(md_file).parent / 'thumbnail.png'
        if local_thumb.exists():
            thumbnail = os.path.relpath(local_thumb, start=Path.cwd()).replace('\\', '/')

    # og.png is a derived social-preview image. Regenerating it every build
    # rewrites identical-looking bytes and dirties git, so only build it when
    # missing. Delete the file to force a refresh (e.g. after a title change).
    og_path = Path(md_file).parent / 'og.png'
    if not og_path.exists():
        bg_path = thumbnail if thumbnail else None
        generate_og_thumbnail(og_path, title, background_path=bg_path)

    html_output = html_output.replace('{{DESCRIPTION}}', description)

    article_folder = Path(md_file).parent.name
    og_url = f"/articles/{article_folder}/og.png"
    html_output = html_output.replace('{{OG}}', og_url)

    if output_file is None:
        output_file = Path(md_file).parent / 'index.html'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print()
    print(f"✓ Converted {md_file} to {output_file}")
    print(f"  Title: {title}")
    print(f"  Date: {format_date_display(date)}")
    print()
    return {
        'title': title,
        'date': date,
        'description': description,
        'link': link_path,
        'thumbnail': thumbnail,
        'draft': is_draft,
        'read_time': str(time_read)
    }


# ---------------------------------------------------------------------------
# Presentations (reveal.js slide decks compiled from Markdown)
#
# Each talk lives in presentations/<name>/slides.md and is compiled to
# presentations/<name>/index.html. Slides are SEPARATED by lines:
#     ---   new horizontal slide
#     --    new vertical sub-slide (press down-arrow to reach)
# A line of exactly  Note:  starts speaker notes for that slide.
# A leading  <!-- .slide: data-... -->  comment sets section attributes
# (e.g. data-background).
#
# Crucially, math ($...$ and $$...$$) is protected with the SAME stashing
# trick the articles use, so LaTeX survives Markdown conversion intact and
# KaTeX renders it client-side — unlike reveal's built-in Markdown parser,
# which mangles backslashes and underscores.
# ---------------------------------------------------------------------------

def _render_slide_body(content, md_dir):
    """Convert one slide's Markdown to HTML, protecting math and HTML embeds."""
    html_embed_store = []

    def _stash_html_embed(m):
        file_path = m.group(1).strip()
        idx = len(html_embed_store)
        full_path = Path(md_dir) / file_path
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                html_content = isolate_html_scripts(f.read())
            html_embed_store.append(f'<div class="embedded-html" id="embed-{idx}">\n{html_content}\n</div>')
        else:
            print(f"⚠️  Warning: HTML file not found: {full_path}")
            html_embed_store.append(f'<p style="color: red;">Error: HTML file not found: {file_path}</p>')
        return f"\n\n{{{{HTMLEMBED_{idx}}}}}\n\n"

    content = re.sub(r':::html\s+(.+?)\s+:::', _stash_html_embed, content, flags=re.DOTALL)

    block_store, inline_store = [], []

    def _stash_block(m):
        block_store.append(m.group(1))
        return f"\n\n{{{{MATHBLOCK_{len(block_store) - 1}}}}}\n\n"

    def _stash_inline(m):
        inline_store.append(m.group(1))
        return f"{{{{MATHINLINE_{len(inline_store) - 1}}}}}"

    content = re.sub(r'\$\$(.*?)\$\$', _stash_block, content, flags=re.DOTALL)
    content = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', _stash_inline, content, flags=re.DOTALL)

    md = markdown.Markdown(extensions=['extra'])
    html = md.convert(content)

    for i, embed in enumerate(html_embed_store):
        html = html.replace(f"{{{{HTMLEMBED_{i}}}}}", embed)
    for i, tex in enumerate(block_store):
        html = html.replace(f"{{{{MATHBLOCK_{i}}}}}", f"$$\n{tex}\n$$")
    for i, tex in enumerate(inline_store):
        html = html.replace(f"{{{{MATHINLINE_{i}}}}}", f"${tex}$")
    return html


def _render_one_slide(raw, md_dir):
    """Turn one slide's raw Markdown into a <section> (with optional notes/attrs)."""
    attrs = ''
    attr_match = re.search(r'<!--\s*\.slide:\s*(.*?)-->', raw, flags=re.DOTALL)
    if attr_match:
        attrs = ' ' + attr_match.group(1).strip()
        raw = raw.replace(attr_match.group(0), '')

    notes_html = ''
    parts = re.split(r'(?m)^Note:[ \t]*$', raw, maxsplit=1)
    body = parts[0]
    if len(parts) > 1 and parts[1].strip():
        notes_html = '\n<aside class="notes">\n' + _render_slide_body(parts[1].strip(), md_dir) + '\n</aside>'

    body_html = _render_slide_body(body.strip(), md_dir)
    return f"<section{attrs}>\n{body_html}{notes_html}\n</section>"


def convert_slides_to_html(md_file, output_file=None, template_file='presentation_template.html'):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    md_dir = Path(md_file).parent
    title = md_dir.name.replace('-', ' ').replace('_', ' ').title()

    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        content = content[frontmatter_match.end():]
        title_match = re.search(r'title:\s*(.+)', frontmatter)
        if title_match:
            title = title_match.group(1).strip()

    sections = []
    for h_slide in re.split(r'(?m)^---[ \t]*$', content):
        verticals = [v for v in re.split(r'(?m)^--[ \t]*$', h_slide) if v.strip()]
        if not verticals:
            continue
        rendered = [_render_one_slide(v, md_dir) for v in verticals]
        if len(rendered) == 1:
            sections.append(rendered[0])
        else:
            sections.append("<section>\n" + "\n".join(rendered) + "\n</section>")

    slides_html = "\n\n".join(sections)

    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()

    html_output = template.replace('{{TITLE}}', title).replace('{{SLIDES}}', slides_html)

    if output_file is None:
        output_file = md_dir / 'index.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"✓ Built presentation: {output_file}  ({len(sections)} slides) — {title}")
    return {'title': title, 'link': os.path.relpath(output_file, start=Path.cwd()).replace('\\', '/')}


def generate_all_presentations(presentations_dir='presentations', template='presentation_template.html'):
    presentations_path = Path(presentations_dir)
    if not presentations_path.exists():
        return
    for subdir in sorted(presentations_path.iterdir()):
        if not subdir.is_dir() or subdir.name.startswith('_'):
            continue
        slides_md = subdir / 'slides.md'
        if slides_md.exists():
            convert_slides_to_html(slides_md, output_file=subdir / 'index.html', template_file=template)


def generate_all_articles(articles_dir='articles', article_template='article_template.html', index_template='index_template.html', main_index='index.html'):
    articles_path = Path(articles_dir)

    if not articles_path.exists():
        print(f"Directory '{articles_dir}' not found.")
        return

    articles_info = []

    for article_subdir in articles_path.iterdir():
        if article_subdir.is_dir():
            md_file = article_subdir / 'article.md'
            if md_file.exists():
                info = convert_md_to_html(md_file, output_file=article_subdir / 'index.html', template_file=article_template)
                if not info.get('draft', False):
                    articles_info.append(info)
                else:
                    print(f"📝 Skipping draft article: {info['title']}")
            else:
                print(f"⚠️  No article.md found in {article_subdir}")

    with open(index_template, 'r', encoding='utf-8') as f:
        template = f.read()

    articles_html = ""
    for art in sorted(articles_info, key=lambda x: parse_date(x['date']), reverse=True):
        thumbnail_html = f'<img src="{art["thumbnail"]}" alt="Article image">' if art["thumbnail"] else ""
        date_formatted = format_date_display(art['date'])
        
        articles_html += f"""
        <article class="article-item">
            <div class="article-content">
                <h3 class="article-title"><a href="{art['link']}">{art['title']}</a></h3>
                <p class="article-description">{art['description']}</p>
                <p class="article-meta">{date_formatted} · {art['read_time']}</p>
            </div>
            <div class="article-image">
                {thumbnail_html}
            </div>
        </article>
        """

    final_index = template.replace('{{ARTICLES}}', articles_html)

    with open(main_index, 'w', encoding='utf-8') as f:
        f.write(final_index)

    print(f"✓ Generated main index: {main_index}")


class ArticleEventHandler(FileSystemEventHandler):
    def __init__(self, articles_dir='articles', article_template='article_template.html',
                 index_template='index_template.html', main_index='index.html',
                 presentations_dir='presentations', presentation_template='presentation_template.html'):
        self.articles_dir = articles_dir
        self.article_template = article_template
        self.index_template = index_template
        self.main_index = main_index
        self.presentations_dir = presentations_dir
        self.presentation_template = presentation_template
        self.last_regenerate = 0
        self.debounce_seconds = 1

    # Editors save in different ways (in-place write, or write-temp-then-rename),
    # so react to created/modified/moved alike.
    def on_modified(self, event):
        if not event.is_directory:
            self._react(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self._react(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._react(getattr(event, 'dest_path', event.src_path))

    def _react(self, src_path):
        file_path = Path(src_path)
        # Ignore generated output so we don't loop forever.
        if file_path.name == 'index.html' and self.presentations_dir in str(file_path):
            return

        is_article_change = (file_path.name == 'article.md' or
            file_path.name in [self.article_template, self.index_template] or
            (file_path.suffix in ['.html', '.png'] and self.articles_dir in str(file_path)))

        is_presentation_change = (file_path.name == self.presentation_template or
            (file_path.suffix in ['.md', '.svg', '.png', '.html'] and self.presentations_dir in str(file_path)))

        if not (is_article_change or is_presentation_change):
            return

        current_time = time.time()
        if current_time - self.last_regenerate < self.debounce_seconds:
            return

        self.last_regenerate = current_time
        print(f"\n🔄 Change detected in {file_path.name}, regenerating...")
        try:
            if is_article_change:
                generate_all_articles(
                    articles_dir=self.articles_dir,
                    article_template=self.article_template,
                    index_template=self.index_template,
                    main_index=self.main_index
                )
            generate_all_presentations(
                presentations_dir=self.presentations_dir,
                template=self.presentation_template
            )
        except Exception as e:
            print(f"❌ Error during regeneration: {e}")


def watch_and_generate(articles_dir='articles', article_template='article_template.html',
                      index_template='index_template.html', main_index='index.html'):

    print("🚀 Starting site generator with file watching...")
    print(f"📁 Watching: {articles_dir} and presentations\n")
    print("📝 Press Ctrl+C to stop\n")

    generate_all_articles(articles_dir, article_template, index_template, main_index)
    generate_all_presentations()

    event_handler = ArticleEventHandler(articles_dir, article_template, index_template, main_index)
    observer = Observer()

    observer.schedule(event_handler, articles_dir, recursive=True)
    if Path('presentations').exists():
        observer.schedule(event_handler, 'presentations', recursive=True)
    observer.schedule(event_handler, '.', recursive=False)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping file watcher...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--watch':
        watch_and_generate()
    else:
        generate_all_articles()
        generate_all_presentations()