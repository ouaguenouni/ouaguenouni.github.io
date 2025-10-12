import markdown
import re
from pathlib import Path
import os
import readtime

def convert_md_to_html(md_file, output_file=None, template_file='article_template.html'):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
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

    # Handle math blocks and inline math
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

    # Restore math
    for i, tex in enumerate(block_store):
        article_content = article_content.replace(f"{{{{MATHBLOCK_{i}}}}}", f"$$\n{tex}\n$$")
    for i, tex in enumerate(inline_store):
        article_content = article_content.replace(f"{{{{MATHINLINE_{i}}}}}", f"${tex}$")

    # Load template
    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()

    html_output = template.replace('{{TITLE}}', title)
    html_output = html_output.replace('{{DATE}}', date)
    html_output = html_output.replace('{{CONTENT}}', article_content)

    time_read = readtime.of_text(content)
    html_output = html_output.replace('{{READ_TIME}}', str(time_read))

    if output_file is None:
        output_file = Path(md_file).parent / 'index.html'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"✓ Converted {md_file} to {output_file}")
    print(f"  Title: {title}")
    print(f"  Date: {date}")

    # Compute link relative to main index.html
    link_path = os.path.relpath(output_file, start=Path.cwd()).replace('\\', '/')

    # Handle local thumbnail.png if frontmatter not provided
    if not thumbnail:
        local_thumb = Path(md_file).parent / 'thumbnail.png'
        if local_thumb.exists():
            thumbnail = os.path.relpath(local_thumb, start=Path.cwd()).replace('\\', '/')

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

    # Generate each article page
    for article_subdir in articles_path.iterdir():
        if article_subdir.is_dir():
            md_file = article_subdir / 'article.md'
            if md_file.exists():
                info = convert_md_to_html(md_file, output_file=article_subdir / 'index.html', template_file=article_template)
                articles_info.append(info)
            else:
                print(f"⚠️  No article.md found in {article_subdir}")

    # Generate main index.html
    with open(index_template, 'r', encoding='utf-8') as f:
        template = f.read()

    # Generate the articles section
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
