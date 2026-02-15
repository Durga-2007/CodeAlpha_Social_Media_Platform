
import os

base_content = """{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CreativeHub — Share your Masterpiece</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Playfair+Display:ital,wght@0,700;0,900;1,700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="{% static 'social/style.css' %}">
</head>
<body>
    <nav class="navbar">
        <div class="container nav-content">
            <a href="{% url 'feed' %}" class="logo">CreativeHub</a>

            {% if user.is_authenticated %}
                <form action="{% url 'feed' %}" method="get" class="search-form">
                    <input type="text" name="q" placeholder="Search poems, creators..." value="{{ query|default:'' }}">
                    <button type="submit"><i class="fas fa-search"></i></button>
                </form>
            {% endif %}

            <div class="nav-links">
                {% if user.is_authenticated %}
                    <a href="{% url 'feed' %}"><i class="fas fa-home"></i> <span>Feed</span></a>
                    <a href="{% url 'notifications' %}" class="nav-icon" title="Notifications">
                        <i class="fas fa-bell"></i>{% if unread_notifications %}<span class="badge">{{ unread_notifications }}</span>{% endif %}
                    </a>
                    <a href="{% url 'profile' user.username %}"><i class="fas fa-user-circle"></i> <span>Profile</span></a>
                    <a href="{% url 'settings' %}"><i class="fas fa-cog"></i> <span>Settings</span></a>
                    <form action="{% url 'logout' %}" method="post" style="display:inline;">
                        {% csrf_token %}
                        <button type="submit" class="logout-btn">
                            <i class="fas fa-sign-out-alt"></i> <span>Logout</span>
                        </button>
                    </form>
                {% else %}
                    <a href="{% url 'login' %}"><i class="fas fa-sign-in-alt"></i> Login</a>
                    <a href="{% url 'register' %}"><i class="fas fa-user-plus"></i> Register</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <main class="container">
        {% if messages %}
            {% for message in messages %}
                <div class="card" style="padding:15px 25px; border-left:5px solid var(--secondary); background:rgba(240, 42, 162, 0.05); color:var(--secondary); font-weight:700; margin-bottom:20px; text-align:center;">
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>

    <footer style="text-align:center; padding:40px 0; color:var(--text-light); font-weight:700; opacity:0.8;">
        <p>&copy; 2026 CreativeHub. Share the Magic.</p>
    </footer>

    <script src="{% static 'social/voice.js' %}"></script>
</body>
</html>"""

feed_content = """{% extends 'social/base.html' %}

{% block content %}
<!-- Premium Hero Section -->
<div class="hero-section fade-in">
    <h1>Welcome to the Creative Hub</h1>
    <p>A sanctuary for poets, storytellers, and visual artists to share their masterpieces.</p>
</div>

<div class="main-layout fade-in">
    <div class="feed-column">
        <div class="card post-form">
            <h3><i class="fas fa-pen-nib"></i> Share your Masterpiece</h3>
            <form method="post" enctype="multipart/form-data">
                {% csrf_token %}
                {{ form.content }}
                <div style="margin-bottom:20px; background:rgba(99, 102, 241, 0.05); padding:20px; border-radius:15px; border:2px dashed var(--primary-light);">
                    <label style="display:block; font-size:1rem; font-weight:800; color:var(--primary); margin-bottom:10px;">
                        <i class="fas fa-cloud-upload-alt"></i> Add an image of your art (Optional)
                    </label>
                    {{ form.image }}
                </div>
                <div style="display:flex; gap:15px; align-items:center;">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-paper-plane"></i> Post Creation
                    </button>
                    <button type="button" id="voice-btn" class="btn mic-btn" title="Speak to create post">
                        <i class="fas fa-microphone"></i> Speak
                    </button>
                    <span id="voice-status" style="font-size:0.9rem; color:var(--secondary); font-weight:800;"></span>
                </div>
            </form>
        </div>

        {% if query %}
            <h2 style="font-family:var(--text-serif); margin-bottom:25px; color:var(--primary); font-size:2rem;">
                <i class="fas fa-search"></i> Results for "{{ query }}"
            </h2>
        {% endif %}

        <div class="feed">
            {% for post in posts %}
                <div class="card post fade-in">
                    <div class="post-header">
                        <div style="display:flex; align-items:center; gap:15px;">
                            <img src="{{ post.user.profile.profile_pic.url }}" class="avatar" style="border-radius:15px; border:3px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.1);">
                            <div>
                                <a href="{% url 'profile' post.user.username %}" class="username" style="font-size:1.2rem; background:linear-gradient(to right, var(--primary), var(--secondary)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">@{{ post.user.username }}</a>
                                <span class="timestamp"><i class="far fa-clock"></i> {{ post.timestamp|timesince }} ago</span>
                            </div>
                        </div>
                        {% if post.user == user %}
                            <div class="post-menu">
                                <a href="{% url 'edit_post' post.id %}" class="action-link" title="Edit Creation"><i class="fas fa-edit"></i></a>
                                <a href="{% url 'delete_post' post.id %}" class="action-link" style="color:#ef4444;" title="Remove"><i class="fas fa-trash-alt"></i></a>
                            </div>
                        {% endif %}
                    </div>
                    
                    {% if post.image %}
                        <img src="{{ post.image.url }}" alt="Art piece" class="post-image" style="border-radius:25px; box-shadow:0 20px 40px rgba(0,0,0,0.15);">
                    {% endif %}

                    <div class="post-content" style="font-size:1.2rem; color:var(--text-main); margin:15px 0;">
                        {{ post.content|linebreaks }}
                    </div>
                    
                    <div class="post-actions" style="border-top:1px solid rgba(0,0,0,0.05); padding-top:15px;">
                        <a href="{% url 'like_post' post.id %}" class="action-link {% if post.is_liked %}liked{% else %}not-liked{% endif %}" style="font-size:1.1rem;">
                            {% if post.is_liked %}<i class="fas fa-heart"></i>{% else %}<i class="far fa-heart"></i>{% endif %}
                            Liked by {{ post.likes.count }}
                        </a>
                        <span class="action-link" style="font-size:1.1rem;"><i class="fas fa-comment-alt"></i> {{ post.comments.count }} Appreciations</span>
                    </div>

                    <div class="comments-section" style="background:rgba(99, 102, 241, 0.03); border-radius:20px; padding:20px; margin-top:20px;">
                        {% for comment in post.comments.all %}
                            <div class="comment" style="padding:10px 0; border-bottom:1px solid rgba(0,0,0,0.03);">
                                <strong style="color:var(--secondary);">@{{ comment.user.username }}</strong>: {{ comment.content }}
                            </div>
                        {% endfor %}
                        
                        <form action="{% url 'add_comment' post.id %}" method="post" class="comment-form" style="margin-top:15px; display:flex; gap:10px;">
                            {% csrf_token %}
                            <input type="text" name="content" placeholder="Leave a word of appreciation..." class="comment-input" required 
                                   style="width:100%; padding:15px; border-radius:15px; border:2px solid var(--border); outline:none; background:white;">
                            <button type="submit" class="btn btn-primary" style="padding: 10px 20px; border-radius:15px;">
                                <i class="fas fa-reply"></i>
                            </button>
                        </form>
                    </div>
                </div>
            {% empty %}
                <div class="card" style="text-align:center; padding:80px 20px; border:2px dashed var(--border);">
                    <i class="fas fa-paint-brush" style="font-size:4rem; color:var(--primary-light); margin-bottom:20px; display:block; opacity:0.5;"></i>
                    <p style="color:var(--text-light); font-size:1.3rem; font-weight:700;">The Hub is waiting for your magic. Share your first creation!</p>
                </div>
            {% endfor %}
        </div>
    </div>

    <!-- Discovery Sidebar -->
    <div class="sidebar-column">
        <div class="card sidebar-card" style="position:sticky; top:100px; border-top:5px solid var(--secondary);">
            <h4 style="font-family:var(--text-serif); margin-bottom:25px; font-size:1.5rem;"><i class="fas fa-fire-alt" style="color:var(--accent);"></i> Suggested Artists</h4>
            {% for creator in suggested_creators %}
                <div class="creator-item" style="padding:15px; border-bottom:1px solid rgba(0,0,0,0.03);">
                    <img src="{{ creator.profile.profile_pic.url }}" class="avatar-small" style="width:45px; height:45px; border-radius:12px;">
                    <div class="creator-info">
                        <a href="{% url 'profile' creator.username %}" class="username-small">@{{ creator.username }}</a>
                        <p style="font-size:0.8rem; font-weight:700; color:var(--text-light);">{{ creator.post_count }} Masterpieces</p>
                    </div>
                    <form action="{% url 'follow_user' creator.username %}" method="post" style="margin-left:auto;">
                        {% csrf_token %}
                        <button type="submit" class="follow-mini-btn" style="background:linear-gradient(to right, var(--primary), var(--secondary));"><i class="fas fa-plus"></i></button>
                    </form>
                </div>
            {% empty %}
                <p style="font-size:1rem; color:var(--text-light); text-align:center; padding:20px 0; font-weight:700;">You've connected with all creators! 🌟</p>
            {% endfor %}
            <div style="margin-top:40px;">
                <h4 style="font-family:var(--text-serif); margin-bottom:20px; font-size:1.5rem;"><i class="fas fa-star" style="color:var(--accent);"></i> Trending</h4>
                <div class="tags" style="gap:15px;">
                    <span class="tag" style="background:var(--primary); color:white; border:none; padding:10px 20px;">#Poetry</span>
                    <span class="tag" style="background:var(--secondary); color:white; border:none; padding:10px 20px;">#VisualArt</span>
                    <span class="tag" style="background:var(--accent); color:white; border:none; padding:10px 20px;">#Stories</span>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""

with open("social/templates/social/base.html", "w", encoding="utf-8") as f:
    f.write(base_content)

with open("social/templates/social/feed.html", "w", encoding="utf-8") as f:
    f.write(feed_content)

print("Files written successfully.")
