import os
import csv

base_dir = "C:/Users/Shivam Patel/.gemini/antigravity/brain/d7a6382f-6722-4f66-a7ae-197ee9225f74/scratch/bulk_export_csv"
out_dir = "C:/Users/Shivam Patel/.gemini/antigravity/brain/d7a6382f-6722-4f66-a7ae-197ee9225f74/scratch/formatted_chats"

os.makedirs(out_dir, exist_ok=True)

html_template_start = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e2e; color: #cdd6f4; margin: 0; padding: 20px; }
    .chat-container { max-width: 800px; margin: 0 auto; background-color: #181825; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .message { margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #313244; }
    .message:last-child { border-bottom: none; }
    .author { font-weight: bold; color: #89b4fa; margin-bottom: 5px; font-size: 1.1em; }
    .content { line-height: 1.5; word-wrap: break-word; margin-bottom: 8px; }
    img.attachment { max-width: 100%; max-height: 400px; border-radius: 8px; margin-top: 10px; display: block; }
    a.attachment-link { display: inline-block; margin-top: 10px; color: #a6e3a1; text-decoration: none; padding: 5px 10px; border: 1px solid #a6e3a1; border-radius: 5px; }
    a.attachment-link:hover { background-color: #a6e3a1; color: #1e1e2e; }
</style>
</head>
<body>
<div class="chat-container">
"""

html_template_end = """
</div>
</body>
</html>
"""

def is_image(filename):
    ext = filename.lower().split('.')[-1]
    return ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']

for filename in os.listdir(base_dir):
    if filename.endswith(".csv"):
        filepath = os.path.join(base_dir, filename)
        channel_name = filename.replace('.csv', '')
        out_filepath = os.path.join(out_dir, f"{channel_name}.html")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            with open(out_filepath, 'w', encoding='utf-8') as out_f:
                out_f.write(html_template_start)
                out_f.write(f"<h2 style='text-align:center; color:#f38ba8;'>{channel_name}</h2><hr style='border:1px solid #313244; margin-bottom:20px;'>\n")
                
                last_author = None
                
                for row in reader:
                    author = row['Author']
                    content = row['Content'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                    attachments = row['Attachments'].split(',') if row['Attachments'] else []
                    
                    if author != last_author:
                        if last_author is not None:
                            out_f.write("</div>\n") # close previous message
                        out_f.write("<div class='message'>\n")
                        out_f.write(f"<div class='author'>{author}</div>\n")
                        last_author = author
                        
                    if content.strip():
                        out_f.write(f"<div class='content'>{content}</div>\n")
                    
                    for att in attachments:
                        att = att.strip()
                        if not att: continue
                        
                        # Convert to forward slashes for URLs
                        att_url = att.replace('\\', '/')
                        # Point to the bulk_export_csv dir since HTML is in formatted_chats
                        rel_path = f"../bulk_export_csv/{att_url}"
                        
                        if is_image(att):
                            out_f.write(f"<img class='attachment' src='{rel_path}' />\n")
                        else:
                            out_f.write(f"<a class='attachment-link' href='{rel_path}' target='_blank'>📎 Download Attachment: {os.path.basename(att)}</a>\n")
                
                if last_author is not None:
                    out_f.write("</div>\n")
                
                out_f.write(html_template_end)
