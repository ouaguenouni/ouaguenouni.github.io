import markdown
import re
from pathlib import Path
import os
import readtime

from PIL import Image, ImageDraw, ImageFont

def generate_og_thumbnail(output_path, title, background_path=None, width=1200, height=630, font_path=None):
    """
    Generate an Open Graph thumbnail using a background image with a dark overlay and title text.
    """
    if background_path and Path(background_path).exists():
        # Open and resize background image
        bg = Image.open(background_path).convert("RGB")
        bg = bg.resize((width, height))
        img = bg
    else:
        # Fallback to solid color background
        img = Image.new('RGB', (width, height), color=(40, 40, 40))

    # Create draw object
    draw = ImageDraw.Draw(img)

    # Add dark overlay
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 150))  # 150 = alpha
    img = Image.alpha_composite(img.convert('RGBA'), overlay)

    # Prepare font
    if font_path is None:
        font_path = "et-book.ttf"  # Replace with your font
    try:
        font_size = 80
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # Wrap text
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

    # Center text vertically
    total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines)
    y_text = (height - total_text_height) // 2

    # Draw text (white)
    draw = ImageDraw.Draw(img)  # recreate draw after alpha_composite
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x_text = (width - text_width) // 2
        draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255))
        y_text += text_height

    img.convert('RGB').save(output_path)
    return output_path



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

    for i, tex in enumerate(block_store):
        article_content = article_content.replace(f"{{{{MATHBLOCK_{i}}}}}", f"$$\n{tex}\n$$")
    for i, tex in enumerate(inline_store):
        article_content = article_content.replace(f"{{{{MATHINLINE_{i}}}}}", f"${tex}$")

    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()

    html_output = template.replace('{{TITLE}}', title)
    html_output = html_output.replace('{{DATE}}', date)
    html_output = html_output.replace('{{CONTENT}}', article_content)

    time_read = readtime.of_text(content)
    html_output = html_output.replace('{{READ_TIME}}', str(time_read))

    link_path = os.path.relpath(output_file, start=Path.cwd()).replace('\\', '/')

    if not thumbnail:
        local_thumb = Path(md_file).parent / 'thumbnail.png'
        if local_thumb.exists():
            thumbnail = os.path.relpath(local_thumb, start=Path.cwd()).replace('\\', '/')

    og_path = Path(md_file).parent / 'og.png'
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

    print(f"✓ Converted {md_file} to {output_file}")
    print(f"  Title: {title}")
    print(f"  Date: {date}")
    print()
    return {
        'title': title,
        'date': date,
        'description': description,
        'link': link_path,
        'thumbnail': thumbnail
    }


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
                articles_info.append(info)
            else:
                print(f"⚠️  No article.md found in {article_subdir}")

    with open(index_template, 'r', encoding='utf-8') as f:
        template = f.read()

    articles_html = ""
    for art in sorted(articles_info, key=lambda x: x['date'], reverse=True):
        thumbnail_html = f'<img src="{art["thumbnail"]}" alt="Article image">' if art["thumbnail"] else ""
        articles_html += f"""
        <article class="article-item">
            <div class="article-content">
                <h3 class="article-title"><a href="{art['link']}">{art['title']}</a></h3>
                <p class="article-description">{art['description']}</p>
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


if __name__ == "__main__":
    generate_all_articles()
