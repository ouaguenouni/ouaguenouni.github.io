import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from datetime import datetime
from slugify import slugify

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_image(img_url, output_dir):
    file_name = os.path.basename(img_url.split("?")[0])
    file_name = sanitize_filename(file_name)
    if "." not in file_name:
        file_name += ".png"
    file_path = os.path.join(output_dir, file_name)
    try:
        r = requests.get(img_url, timeout=10)
        r.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(r.content)
        print(f"Downloaded {file_name}")
        return file_name
    except Exception as e:
        print(f"Failed to download {img_url}: {e}")
        return None

def clean_medium_content(article):
    # Remove only Medium-specific elements
    for unwanted in article.select(
        "header, footer, aside, div[class*='js-postShareWidget'], div[class*='clapButton'], div[class*='pw-post-meta'], div[data-testid='socialStats'], div[data-testid='postActionsBar']"
    ):
        unwanted.decompose()
    return article

def extract_metadata(soup, article):
    # TITLE
    title = None
    h1 = soup.find("h1")
    if h1 and h1.text.strip():
        title = h1.text.strip()
    if not title:
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
    if not title:
        name_title = soup.find("meta", attrs={"name": "title"})
        if name_title and name_title.get("content"):
            title = name_title["content"].strip()
    if not title:
        title = "Untitled"

    # DESCRIPTION: get subtitle/description from h2 after h1
    description = ""
    h1 = soup.find("h1")
    if h1:
        # Look for h2 right after h1 (subtitle)
        h2 = h1.find_next("h2")
        if h2:
            description = h2.get_text(strip=True)
    
    if not description:
        first_p = article.find("p")
        if first_p:
            description = first_p.get_text(strip=True)

    # DATE
    text = soup.get_text(" ")
    date_match = re.search(r"\b([A-Z][a-z]{2,8} \d{1,2}, \d{4})\b", text)
    date = ""
    if date_match:
        try:
            parsed = datetime.strptime(date_match.group(1), "%b %d, %Y")
            date = parsed.strftime("%d/%m/%Y")
        except:
            pass

    return title, description, date

def download_figure_images(article, output_dir):
    for fig in article.find_all("figure"):
        source_tags = fig.find_all("source")
        img_url = None
        if source_tags:
            max_width = 0
            for src in source_tags:
                srcset = src.get("srcset", "")
                if not srcset:
                    continue
                for item in srcset.split(","):
                    parts = item.strip().split(" ")
                    if len(parts) == 2:
                        url, w = parts
                        try:
                            w_val = int(re.sub("[^0-9]", "", w))
                            if w_val > max_width:
                                max_width = w_val
                                img_url = url
                        except:
                            continue
        if not img_url:
            img_tag = fig.find("img")
            if img_tag and img_tag.get("src"):
                img_url = img_tag.get("src")
        if not img_url:
            continue
        local_name = download_image(img_url, output_dir)
        if local_name:
            fig.replace_with(f"\n![{local_name}]({local_name})\n")

def clean_markdown_metadata(markdown_text, title, description):
    """Remove Medium metadata from markdown text"""
    lines = markdown_text.split("\n")
    cleaned_lines = []
    skip_until_content = True
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if skip_until_content:
            # Skip tag links
            if stripped.startswith("[") and ("tagged" in line or "towardsdatascience.com" in line):
                continue
            # Skip separator lines (------ or ======)
            if stripped and all(c in ['-', '='] for c in stripped):
                continue
            # Skip lines containing the title
            if title in line:
                continue
            # Skip lines containing the description
            if description and description in line:
                continue
            # Skip author images and links
            if "[![" in line or ("@" in line and "](/" in line):
                continue
            # Skip metadata like "14 min read", "·", "Listen", "Share"
            if any(keyword in stripped for keyword in ["min read", "Listen", "Share"]) or stripped == "·":
                continue
            # Skip standalone date patterns
            date_regex = r"^[A-Z][a-z]{2} \d{1,2}, \d{4}$"
            if re.match(date_regex, stripped):
                continue
            # Skip horizontal rules at the beginning
            if stripped == "--":
                continue
            # Skip standalone numbers
            if re.match(r"^\d+$", stripped):
                continue
            
            # If we find actual content, stop skipping
            if stripped and not any([
                stripped.startswith("["),
                all(c in ['-', '='] for c in stripped),
                "min read" in stripped,
                stripped in ["·", "--", "Listen", "Share"],
                re.match(r"^\d+$", stripped)
            ]):
                skip_until_content = False
                cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)
    
    return "\n".join(cleaned_lines).strip()

def medium_to_markdown(url):
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    article = soup.find("article")
    if not article:
        raise ValueError("Could not find <article> tag.")
    
    title, description, date = extract_metadata(soup, article)
    
    # Find and download the first/hero image as thumbnail before cleaning
    slug = slugify(title)
    os.makedirs(slug, exist_ok=True)
    
    first_figure = article.find("figure")
    if first_figure:
        source_tags = first_figure.find_all("source")
        img_url = None
        if source_tags:
            max_width = 0
            for src in source_tags:
                srcset = src.get("srcset", "")
                if not srcset:
                    continue
                for item in srcset.split(","):
                    parts = item.strip().split(" ")
                    if len(parts) == 2:
                        url_part, w = parts
                        try:
                            w_val = int(re.sub("[^0-9]", "", w))
                            if w_val > max_width:
                                max_width = w_val
                                img_url = url_part
                        except:
                            continue
        if not img_url:
            img_tag = first_figure.find("img")
            if img_tag and img_tag.get("src"):
                img_url = img_tag.get("src")
        
        # Download as thumbnail
        if img_url:
            try:
                r = requests.get(img_url, timeout=10)
                r.raise_for_status()
                thumbnail_path = os.path.join(slug, "thumbnail.png")
                with open(thumbnail_path, "wb") as f:
                    f.write(r.content)
                print(f"Downloaded thumbnail.png")
            except Exception as e:
                print(f"Failed to download thumbnail: {e}")
        
        # Remove the first figure so it doesn't appear in the markdown
        first_figure.decompose()
    
    article = clean_medium_content(article)

    # CODE BLOCKS
    for pre in article.find_all("pre"):
        code_block = pre.get_text(strip=True)
        lang_tag = ""
        if pre.code and pre.code.has_attr("class"):
            for c in pre.code["class"]:
                if c.startswith("language-"):
                    lang_tag = c.replace("language-", "")
        pre.replace_with(f"\n```{lang_tag}\n{code_block}\n```\n")

    # FIGURE / PICTURE IMAGES
    download_figure_images(article, slug)

    # OTHER IMAGES NOT IN FIGURE
    for img in article.find_all("img"):
        img_url = img.get("src")
        if not img_url:
            continue
        local_name = download_image(img_url, slug)
        if local_name:
            img.replace_with(f"\n![{local_name}]({local_name})\n")

    # CONVERT TO MARKDOWN
    markdown_text = md(str(article))
    markdown_text = re.sub(r"\n{3,}", "\n\n", markdown_text)
    markdown_text = re.sub(r"\n\s*—+\s*\n", "\n\n", markdown_text)
    
    # Clean metadata from markdown
    markdown_text = clean_markdown_metadata(markdown_text, title, description)

    front_matter = f"""---
title: {title}
date: {date}
description: {description}
---
"""

    final_md = front_matter + "\n" + description + "\n\n---\n\n" + markdown_text
    md_path = os.path.join(slug, "article.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(final_md)

    print(f"\n✅ Export complete: {md_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python medium_to_md.py <medium_article_url>")
        sys.exit(1)
    medium_to_markdown(sys.argv[1])