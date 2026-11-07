import markdown
import re

with open('BLOG_MEDIUM.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# Clean up excessive dividers (---) to eliminate giant gaps in Medium
md_cleaned = re.sub(r'\n---\n', '\n\n', md_content)

# Convert markdown to clean semantic HTML
html_body = markdown.markdown(md_cleaned, extensions=['extra', 'fenced_code'])

full_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Medium Formatted Article - SwitchOps</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #f9fafb;
            margin: 0;
            padding: 30px 15px;
            color: #242424;
        }
        .container {
            max-width: 760px;
            margin: 0 auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        }
        .action-bar {
            position: sticky;
            top: 20px;
            z-index: 100;
            background: #1a8917;
            color: white;
            padding: 18px 24px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 6px 16px rgba(26,137,23,0.3);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 15px;
        }
        .btn-copy {
            background: #ffffff;
            color: #1a8917;
            font-weight: 700;
            font-size: 16px;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
            transition: all 0.2s ease;
            white-space: nowrap;
        }
        .btn-copy:hover {
            background: #f0fdf4;
            transform: translateY(-1px);
        }
        .copy-status {
            font-weight: 600;
            font-size: 15px;
        }
        #article-body {
            line-height: 1.68;
            font-size: 18px;
        }
        #article-body h1 {
            font-size: 36px;
            line-height: 1.2;
            margin: 10px 0 16px 0;
            font-weight: 700;
        }
        #article-body h2 {
            font-size: 26px;
            line-height: 1.3;
            margin: 36px 0 14px 0;
            font-weight: 700;
            color: #111;
        }
        #article-body h3 {
            font-size: 20px;
            line-height: 1.35;
            margin: 24px 0 10px 0;
            font-weight: 600;
            color: #444;
        }
        #article-body p {
            margin: 16px 0;
            color: #242424;
        }
        #article-body strong {
            font-weight: 700;
            color: #111;
        }
        #article-body em {
            font-style: italic;
            color: #555;
        }
        #article-body img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 24px 0 8px 0;
            display: block;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        #article-body blockquote {
            border-left: 3px solid #1a8917;
            padding-left: 18px;
            margin: 20px 0;
            font-style: italic;
            color: #333;
        }
        #article-body pre {
            background: #f6f8fa;
            border: 1px solid #e1e4e8;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 14px;
            line-height: 1.45;
        }
        #article-body code {
            background: #f6f8fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 15px;
        }
        #article-body ul {
            padding-left: 24px;
            margin: 16px 0;
        }
        #article-body li {
            margin-bottom: 8px;
        }
        #article-body a {
            color: #1a8917;
            text-decoration: underline;
        }
    </style>
</head>
<body>

<div class="container">
    <div class="action-bar">
        <div>
            <div style="font-size: 17px; font-weight: 700;">Medium Rich-Formatted Article Ready</div>
            <div style="font-size: 13px; opacity: 0.9; margin-top: 3px;">Zero double stars (**), real headings, embedded table image, and clean spacing.</div>
        </div>
        <button class="btn-copy" id="copyBtn" onclick="copyArticle()">📋 Copy for Medium</button>
    </div>
    <div id="copySuccess" style="display:none; background:#dcfce7; color:#15803d; padding:12px; border-radius:8px; margin-bottom:20px; font-weight:600; text-align:center;">
        ✅ Copied to clipboard! Now open your Medium story, press Ctrl+A and Ctrl+V to paste!
    </div>

    <div id="article-body">
""" + html_body + """
    </div>
</div>

<script>
async function copyArticle() {
    const articleEl = document.getElementById('article-body');
    const htmlContent = articleEl.innerHTML;
    const textContent = articleEl.innerText;
    
    try {
        const htmlBlob = new Blob([htmlContent], { type: 'text/html' });
        const textBlob = new Blob([textContent], { type: 'text/plain' });
        const clipboardItem = new ClipboardItem({
            'text/html': htmlBlob,
            'text/plain': textBlob
        });
        await navigator.clipboard.write([clipboardItem]);
        showSuccess();
    } catch (err) {
        // Fallback for older browsers
        const range = document.createRange();
        range.selectNode(articleEl);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        document.execCommand('copy');
        window.getSelection().removeAllRanges();
        showSuccess();
    }
}

function showSuccess() {
    const status = document.getElementById('copySuccess');
    status.style.display = 'block';
    const btn = document.getElementById('copyBtn');
    btn.innerText = '✅ Copied!';
    setTimeout(() => {
        btn.innerText = '📋 Copy for Medium';
    }, 4000);
}
</script>

</body>
</html>"""

with open('medium_formatted.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print('Updated medium_formatted.html successfully!')
