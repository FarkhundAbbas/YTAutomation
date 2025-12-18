from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from backend.models import Article, db
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple HTML Template embedded for single-file portability as requested "Minimal/No placeholders"
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SaaS Approval Dashboard</title>
    <style>
        body { font-family: sans-serif; padding: 20px; background: #f0f2f5; }
        .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .actions { margin-top: 10px; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; color: white; margin-right: 10px; }
        .btn-approve { background: #4caf50; }
        .btn-reject { background: #f44336; }
        .btn-add { background: #2196F3; }
        video { max-width: 300px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>SaaS Dashboard</h1>
    
    <!-- Add Channel Section -->
    <div class="card">
        <h2>Add New Channel</h2>
        <form action="/add_channel" method="post">
            <div class="form-group">
                <label>Platform</label>
                <select name="platform">
                    <option value="youtube">YouTube</option>
                    <option value="tiktok">TikTok</option>
                    <option value="facebook">Facebook</option>
                </select>
            </div>
            <div class="form-group">
                <label>Channel Name / Handle</label>
                <input type="text" name="channel_name" required placeholder="@mychannel">
            </div>
            <div class="form-group">
                <label>API Key / Token (Optional for Demo)</label>
                <input type="text" name="api_key" placeholder="Enter credentials...">
            </div>
            <button class="btn btn-add" type="submit">Add Channel</button>
        </form>
    </div>

    <h1>Pending Approvals</h1>
    {% if not articles %}
        <p>No pending articles.</p>
    {% endif %}
    
    {% for article in articles %}
    <div class="card">
        <h3>{{ article.title }}</h3>
        <p><strong>Source:</strong> {{ article.source }} | <strong>Trend Score:</strong> {{ article.trend_score }}</p>
        <p>{{ article.content[:200] }}...</p>
        
        {% if article.video_path %}
            <video controls>
                <source src="/video/{{ article.id }}" type="video/mp4">
                Your browser does not support video.
            </video>
        {% else %}
            <p><em>Video generation pending or failed...</em></p>
        {% endif %}
        
        <div class="actions">
            <form action="/approve/{{ article.id }}" method="post" style="display:inline;">
                <button class="btn btn-approve" type="submit">Approve</button>
            </form>
            <form action="/reject/{{ article.id }}" method="post" style="display:inline;">
                <button class="btn btn-reject" type="submit">Reject</button>
            </form>
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""

@app.before_request
def before_request():
    db.connect()

@app.after_request
def after_request(response):
    db.close()
    return response

@app.route('/')
def index():
    # Show articles that have a video but are not yet approved/published
    articles = Article.select().where(
        (Article.approval_status == 'pending')
        # & (Article.video_path.is_null(False)) # Commented out for demo to show even if video failed/mocked
    )
    return render_template_string(HTML_TEMPLATE, articles=articles)

@app.route('/add_channel', methods=['POST'])
def add_channel():
    platform = request.form.get('platform')
    name = request.form.get('channel_name')
    key = request.form.get('api_key')
    
    # Save to config or database
    # For this demo, we'll append to a yaml file or just log it
    import yaml
    try:
        config_path = os.path.join(os.getcwd(), 'config', 'platforms.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f) or {}
                
            # Naive append for demo
            if 'custom_channels' not in data:
                data['custom_channels'] = []
                
            data['custom_channels'].append({
                'platform': platform,
                'name': name,
                'key': key[:5] + "***" if key else "N/A"
            })
            
            with open(config_path, 'w') as f:
                yaml.dump(data, f)
                
        logger.info(f"Added channel: {platform} - {name}")
    except Exception as e:
        logger.error(f"Failed to add channel: {e}")
        
    return redirect(url_for('index'))

@app.route('/approve/<int:article_id>', methods=['POST'])
def approve(article_id):
    try:
        art = Article.get_by_id(article_id)
        art.approval_status = 'approved'
        art.save()
        logger.info(f"Approved Article {article_id}")
        # Here we would trigger the upload task via Celery
        # from backend.worker import upload_task
        # upload_task.delay(article_id)
    except Exception as e:
        logger.error(f"Error approving: {e}")
    return redirect(url_for('index'))

@app.route('/reject/<int:article_id>', methods=['POST'])
def reject(article_id):
    try:
        art = Article.get_by_id(article_id)
        art.approval_status = 'rejected'
        art.save()
        logger.info(f"Rejected Article {article_id}")
    except Exception as e:
        logger.error(f"Error rejecting: {e}")
    return redirect(url_for('index'))

@app.route('/video/<int:article_id>')
def serve_video(article_id):
    from flask import send_file
    try:
        art = Article.get_by_id(article_id)
        if art.video_path and os.path.exists(art.video_path):
            return send_file(art.video_path)
    except:
        pass
    return "Video not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
