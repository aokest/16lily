# Jazzmin Settings
JAZZMIN_SETTINGS = {
    "site_title": "石榴粒粒系统",
    "site_header": "石榴粒粒",
    "site_brand": "石榴粒粒", 
    "welcome_sign": "欢迎回到石榴粒粒",
    "copyright": "Sixteen Legion",
    "search_model": ["core.Opportunity", "auth.User"],
    
    "topmenu_links": [
        {"name": "首页",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "商机看板", "url": "/admin/core/opportunity/", "permissions": ["core.view_opportunity"]},
        {"name": "大屏战报", "url": "/api/dashboard/screen/", "new_window": True},
    ],
    
    "show_sidebar": True,
    "navigation_expanded": True,
    
    # Custom CSS/JS
    "custom_css": "core/css/custom_admin.css",
    "custom_js": "admin/js/sidebar_grouping.js",

    # RESTORE: Remove hide_models and custom_links to ensure models are visible
    # "hide_models": [],
    # "custom_links": {},

    # Strict Ordering for Grouping
    "order_with_respect_to": [
        # --- 我的工作台 ---
        "core.UserProfile", 
        "core.Announcement", 
        "core.TodoTask", 
        "core.PerformanceTarget",
        "core.WorkReport",
        
        # --- 商机管理 ---
        "core.Opportunity", 
        "core.OpportunityLog", 
        
        # --- 市场活动 ---
        "core.MarketActivity", 
        "core.SocialMediaStats",
        
        # --- 赛事管理 ---
        "core.Competition",
        
        # --- 客户关系 ---
        "core.Customer", 
        "core.Contact",

        # --- 系统配置 (AI & Org) ---
        "core.AIConfiguration",
        "core.PromptTemplate",
        "core.DepartmentModel",
        
        # --- 认证和授权 ---
        "auth.User", 
        "auth.Group"
    ],

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.Opportunity": "fas fa-hand-holding-usd",
        "core.OpportunityLog": "fas fa-history",
        "core.UserProfile": "fas fa-id-card",
        "core.PerformanceTarget": "fas fa-bullseye",
        "core.Competition": "fas fa-trophy",
        "core.MarketActivity": "fas fa-bullhorn",
        "core.Announcement": "fas fa-scroll",
        "core.TodoTask": "fas fa-tasks",
        "core.WorkReport": "fas fa-file-alt",
        "core.SocialMediaStats": "fas fa-chart-line",
        "core.Customer": "fas fa-building",
        "core.Contact": "fas fa-address-book",
        "core.AIConfiguration": "fas fa-robot",
        "core.PromptTemplate": "fas fa-comment-dots",
        "core.DepartmentModel": "fas fa-sitemap",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "danger", # Red-ish
    "accent": "accent-danger", # Red-ish
    "navbar": "navbar-white navbar-light", # Light navbar to contrast with red header
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-danger", # Dark sidebar with red accent
    "sidebar_nav_small_text": False,
    "theme": "default", 
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
