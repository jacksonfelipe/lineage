"""
Configurações do Jazzmin - Admin Theme
Este arquivo contém todas as configurações relacionadas ao tema Jazzmin do Django Admin.
"""

from django.utils.translation import gettext_lazy as _

# =========================== JAZZMIN CONFIGURATION ===========================

def get_jazzmin_settings(project_title):
    """
    Retorna as configurações do Jazzmin baseadas no título do projeto.
    
    Args:
        project_title (str): Título do projeto
        
    Returns:
        dict: Configurações do Jazzmin
    """
    return {
        # title of the window (Will default to current_admin_site.site_title if absent or None)
        "site_title": project_title,
        # Title on the login screen (19 chars max) (Will default to current_admin_site.site_header if absent or None)
        "site_header": "PDL",
        # Title on the brand (19 chars max) (Will default to current_admin_site.site_header if absent or None)
        "site_brand": "PDL",
        # Logo to use for your site, must be present in static files, used for brand on top left
        "site_logo": "assets/img/ico.jpg",
        # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
        "login_logo": "assets/img/ico.jpg",
        # CSS classes that are applied to the logo above
        "site_logo_classes": "img-circle",
        # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
        "site_icon": "assets/img/ico.jpg",
        # Welcome text on the login screen
        "welcome_sign": "Welcome to PDL Admin",
        # Copyright on the footer
        "copyright": "all rights reserved to PDL System",
        # The model admin to search from the search bar, search bar omitted if excluded
        # "search_model": "auth.User",
        # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
        "user_avatar": True,
        # URL for the login page
        "login_url": "login",
        # URL for the logout page
        "logout_url": "logout",
        # URL for the password change page
        "password_change_url": "password_change",
        # URL for the password reset page
        "password_reset_url": "password_reset",
        # Whether to show the UI customizer on the sidebar
        "show_ui_builder": False,
        ############
        # Top Menu #
        ############
        # Links to put along the top menu
        "topmenu_links": [
            {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
            {"name": "Site", "url": "dashboard"},
        ],
        #############
        # User Menu #
        #############
        # Links to put in the user menu
        "usermenu_links": [
            {"name": _("Meu Perfil"), "url": "profile", "icon": "fas fa-user"},
            {"name": _("Mudar Senha"), "url": "password_change", "icon": "fas fa-key"},
            {"name": _("Segurança"), "url": "administrator:security_settings", "icon": "fas fa-shield-alt"},
            {"name": _("Sair"), "url": "logout", "icon": "fas fa-sign-out-alt"},
        ],
        #############
        # Side Menu #
        #############
        # Whether to display the side menu
        "show_sidebar": True,
        # Whether to aut expand the menu
        "navigation_expanded": True,
        # Custom icons for side menu apps/models
        "icons": {
            # Auth
            "auth": "fas fa-users-cog",
            "auth.user": "fas fa-user",
            "auth.Group": "fas fa-users",
            
            # Administrator
            "administrator.ChatGroup": "fas fa-comments",
            "administrator.Theme": "fas fa-paint-brush",
            "administrator.BackgroundSetting": "fas fa-image",
            "administrator.ThemeVariable": "fas fa-palette",
            
            # Auditor
            "auditor.Auditor": "fas fa-history",
            
            # FAQ
            "faq.FAQ": "fas fa-question-circle",
            "faq.FAQCategory": "fas fa-folder",
            
            # Home
            "home.User": "fas fa-user",
            "home.Profile": "fas fa-id-card",
            "home.State": "fas fa-map-marker-alt",
            "home.City": "fas fa-city",
            "home.DashboardContent": "fas fa-tachometer-alt",
            "home.user": "fas fa-user",
            "home.state": "fas fa-map-marker-alt",
            "home.city": "fas fa-city",
            "home.dashboardcontent": "fas fa-tachometer-alt",
            "home.dashboardcontenttranslation": "fas fa-language",
            "home.sitelogo": "fas fa-image",
            "home.conquista": "fas fa-trophy",
            "home.conquistausuario": "fas fa-medal",
            "home.perfilgamer": "fas fa-gamepad",
            "home.addressuser": "fas fa-map-marker-alt",
            
            # Message
            "message.Friendship": "fas fa-user-friends",
            "message.Chat": "fas fa-comments",
            "message.Message": "fas fa-envelope",
            "message.MessageGroup": "fas fa-envelope-open",
            
            # News
            "news.News": "fas fa-newspaper",
            "news.NewsCategory": "fas fa-folder",
            
            # Notification
            "notification.Notification": "fas fa-bell",
            "notification.PublicNotificationView": "fas fa-eye",
            
            # Solicitation
            "solicitation.Solicitation": "fas fa-clipboard-list",
            "solicitation.SolicitationParticipant": "fas fa-users",
            "solicitation.SolicitationHistory": "fas fa-history",
            
            # Downloads
            "downloads.Download": "fas fa-download",
            "downloads.DownloadCategory": "fas fa-folder",
            "downloads.DownloadLink": "fas fa-download",
            
            # Server
            "server.Server": "fas fa-server",
            "server.ServerStatus": "fas fa-signal",
            "server.ServerConfig": "fas fa-cogs",
            "server.ApiEndpointToggle": "fas fa-toggle-on",
            "server.ActiveAdenaExchangeItem": "fas fa-coins",
            
            # Wallet
            "wallet.Wallet": "fas fa-wallet",
            "wallet.TransacaoWallet": "fas fa-exchange-alt",
            "wallet.CoinConfig": "fas fa-coins",
            
            # Payment
            "payment.PedidoPagamento": "fas fa-money-bill-wave",
            "payment.Pagamento": "fas fa-credit-card",
            "payment.WebhookLog": "fas fa-history",
            
            # Accountancy
            "accountancy.Account": "fas fa-calculator",
            "accountancy.Transaction": "fas fa-file-invoice-dollar",
            
            # Inventory
            "inventory.Inventory": "fas fa-box",
            "inventory.InventoryItem": "fas fa-boxes",
            "inventory.BlockedServerItem": "fas fa-ban",
            "inventory.CustomItem": "fas fa-box-open",
            "inventory.InventoryLog": "fas fa-history",
            
            # Shop
            "shop.ShopItem": "fas fa-box-open",
            "shop.ShopPackage": "fas fa-box",
            "shop.ShopPackageItem": "fas fa-boxes",
            "shop.PromotionCode": "fas fa-tag",
            "shop.Cart": "fas fa-shopping-cart",
            "shop.CartItem": "fas fa-shopping-basket",
            "shop.CartPackage": "fas fa-boxes-stacked",
            "shop.ShopPurchase": "fas fa-receipt",
            
            # Auction
            "auction.Auction": "fas fa-gavel",
            "auction.Bid": "fas fa-hand-holding-usd",
            
            # Games
            "games.Prize": "fas fa-trophy",
            "games.SpinHistory": "fas fa-history",
            "games.Bag": "fas fa-briefcase",
            "games.BagItem": "fas fa-box",
            "games.Item": "fas fa-box-open",
            "games.BoxType": "fas fa-boxes",
            "games.Box": "fas fa-gift",
            "games.BoxItem": "fas fa-boxes-stacked",
            "games.BoxItemHistory": "fas fa-history",
            "games.Recompensa": "fas fa-gift",
            "games.RecompensaRecebida": "fas fa-gift",
            "games.EconomyWeapon": "fas fa-khanda",
            "games.Monster": "fas fa-dragon",
            "games.RewardItem": "fas fa-gift",
            "games.BattlePassSeason": "fas fa-calendar-alt",
            "games.BattlePassLevel": "fas fa-level-up-alt",
            "games.BattlePassReward": "fas fa-medal",
            "games.UserBattlePassProgress": "fas fa-tasks",
            "games.BattlePassItemExchange": "fas fa-exchange-alt",
            
            # Reports
            "reports.Report": "fas fa-chart-bar",
            "reports.ReportType": "fas fa-chart-line",
            
            # Wiki
            "wiki.WikiPage": "fas fa-book",
            "wiki.WikiSection": "fas fa-bookmark",
            "wiki.WikiUpdate": "fas fa-code-branch",
            "wiki.WikiEvent": "fas fa-calendar-alt",
            "wiki.WikiRate": "fas fa-percentage",
            "wiki.WikiFeature": "fas fa-star",
            "wiki.WikiGeneral": "fas fa-info-circle",
            "wiki.WikiRaid": "fas fa-dragon",
            "wiki.WikiAssistance": "fas fa-hands-helping",
            
            # Server
            "server.IndexConfig": "fas fa-cogs",
            "server.IndexConfigTranslation": "fas fa-language",
            "server.ServicePrice": "fas fa-tags",
            "server.Apoiador": "fas fa-star",
            "server.Comissao": "fas fa-percentage",
        },
        # Icons that are used when one is not manually specified
        "default_icon_parents": "fas fa-chevron-circle-right",
        "default_icon_children": "fas fa-circle",
        #############
        # UI Tweaks #
        #############
        # Relative paths to custom CSS/JS files (must be present in static files)
        "custom_css": "custom/admin-custom.css",
        # "custom_js": "custom/admin-custom.js",
        ###############
        # Change view #
        ###############
        # Render out the change view as a single form, or in tabs, current options are
        # - single
        # - horizontal_tabs (default)
        # - vertical_tabs
        # - collapsible
        # - carousel
        "changeform_format": "horizontal_tabs",
        # override change forms on a per modeladmin basis
        "changeform_format_overrides": {
            "auth.user": "collapsible",
            "auth.group": "vertical_tabs",
        },
        # Add a language dropdown into the admin
        "language_chooser": False,
    }


def get_jazzmin_ui_tweaks():
    """
    Retorna as configurações de UI do Jazzmin.
    
    Returns:
        dict: Configurações de UI do Jazzmin
    """
    return {
        "navbar_small_text": False,
        "footer_small_text": False,
        "body_small_text": False,
        "brand_small_text": False,
        "brand_colour": "navbar-primary",
        "accent": "accent-primary",
        "navbar": "navbar-dark",
        "no_navbar_border": False,
        "navbar_fixed": True,
        "layout_boxed": False,
        "footer_fixed": False,
        "sidebar_fixed": True,
        "sidebar": "sidebar-dark-primary",
        "sidebar_nav_small_text": False,
        "sidebar_disable_expand": False,
        "sidebar_nav_child_indent": True,
        "sidebar_nav_compact_style": False,
        "sidebar_nav_legacy_style": False,
        "sidebar_nav_flat_style": False,
        "theme": "default",
        "dark_mode_theme": None,
        "button_classes": {
            "primary": "btn-primary",
            "secondary": "btn-secondary",
            "info": "btn-info",
            "warning": "btn-warning",
            "danger": "btn-danger",
            "success": "btn-success"
        }
    } 
