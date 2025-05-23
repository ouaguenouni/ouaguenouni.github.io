import os
import yaml
import json
import re
import markdown
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def fix_relative_links(html_content, base_url):
    """Fix relative links to work with GitHub Pages base URL."""
    # Fix links to assets
    html_content = re.sub(
        r'(href|src)="/(assets/[^"]+)"', 
        f'\\1="{base_url}/\\2"', 
        html_content
    )
    
    # Fix links to other pages
    html_content = re.sub(
        r'href="/([^/"][^"]+\.html)"', 
        f'href="{base_url}/\\1"', 
        html_content
    )
    
    return html_content

def load_config():
    """Load configuration from config.yml."""
    with open("config.yml", "r") as f:
        return yaml.safe_load(f)

def load_plots_metadata():
    """Load metadata about available plots."""
    try:
        with open("_plots/plots_metadata.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Plots metadata not found. Run generate_plots.py first.")
        return {}

def parse_front_matter(content):
    """Extract YAML front matter from markdown content."""
    front_matter_match = re.match(r'^---\s+(.*?)\s+---\s+(.*)$', content, re.DOTALL)
    
    if front_matter_match:
        front_matter_text = front_matter_match.group(1)
        content_text = front_matter_match.group(2)
        front_matter = yaml.safe_load(front_matter_text)
        return front_matter, content_text
    
    return {}, content

def process_plot_tags(content, plots_metadata):
    """Replace plot tags with actual plot HTML."""
    # Pattern to match: {{plot:PLOT_ID}}
    plot_pattern = r'\{\{plot:([\w_-]+)\}\}'
    
    def replace_plot(match):
        plot_id = match.group(1)
        if plot_id in plots_metadata:
            plot_data = plots_metadata[plot_id]
            return f'<div class="plotly-chart">\n<iframe src="{{{{ config.base_url }}}}/assets/plots/{plot_data["filename"]}" width="100%" height="500" frameborder="0"></iframe>\n<p class="caption">{plot_data["description"]}</p>\n</div>'
        else:
            return f'<div class="error">Plot {plot_id} not found</div>'
    
    return re.sub(plot_pattern, replace_plot, content)

def build_site():
    """Build the complete site."""
    # Load configuration
    config = load_config()
    
    # Load plots metadata
    plots_metadata = load_plots_metadata()
    
    # Create output directory
    os.makedirs("_site", exist_ok=True)
    
    # Copy assets
    if os.path.exists("assets"):
        if os.path.exists("_site/assets"):
            shutil.rmtree("_site/assets")
        shutil.copytree("assets", "_site/assets")
    
    # Set up Jinja2 templates
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("base.html")
    
    # Process markdown files
    for md_file in Path("_md").glob("*.md"):
        print(f"Processing {md_file}...")
        
        # Read markdown content
        with open(md_file, "r") as f:
            content = f.read()
        
        # Parse front matter
        front_matter, md_content = parse_front_matter(content)
        
        # Process plot tags
        md_content = process_plot_tags(md_content, plots_metadata)
        
        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
        
        # Render with template
        output = template.render(
            title=front_matter.get("title", "Untitled"),
            content=html_content,
            metadata=front_matter,
            config=config
        )
        
        # Determine output path
        output_filename = md_file.stem + ".html"
        output_path = os.path.join("_site", output_filename)
        
        # Write output
        with open(output_path, "w") as f:
            f.write(output)
        
        print(f"Generated {output_path}")
    
    # Create index.html if it doesn't exist
    if not os.path.exists("_site/index.html"):
        # Get all HTML files in _site except index.html
        html_files = [f for f in Path("_site").glob("*.html") if f.name != "index.html"]
        
        if html_files:
            # Create a simple index
            index_content = "<h1>Index</h1>\n<h2>Posts</h2>\n<ul>\n"
            for html_file in html_files:
                # Get the full path relative to _site
                rel_path = html_file.relative_to("_site")
                name = html_file.stem
                
                # Replace underscores with spaces and capitalize for display
                display_name = name.replace('_', ' ').title()
                
                # Add link to the index
                index_content += f'<li><a href="/{rel_path}">{display_name}</a></li>\n'
            index_content += "</ul>"

            output = template.render(
            title=front_matter.get("title", "Untitled"),
            content=html_content,
            metadata=front_matter,
            config=config
            )
    
            # Fix relative links for GitHub Pages
            if config.get("base_url"):
                output = fix_relative_links(output, config["base_url"])
            
            # Write index.html
            with open("_site/index.html", "w") as f:
                f.write(output)

            # Create .nojekyll file to disable Jekyll processing
            with open("_site/.nojekyll", "w") as f:
                pass
            
            print("Generated _site/index.html")
    
    print("Site build complete!")

if __name__ == "__main__":
    build_site()