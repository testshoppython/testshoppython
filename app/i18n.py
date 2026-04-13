"""
Internationalization (i18n) Module für OWRE
Konfigurierbare Messages für mehrere Sprachen
"""
from typing import Dict, Optional

# Supported languages
LANGUAGES = {
    "de": "Deutsch",
    "en": "English",
    "fr": "Français",
    "es": "Español",
    "it": "Italiano",
}

# Translation strings
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "de": {
        # Navigation
        "nav_home": "Startseite",
        "nav_shop": "Shop",
        "nav_cart": "Warenkorb",
        "nav_orders": "Bestellungen",
        "nav_account": "Mein Konto",
        "nav_admin": "Admin",
        "nav_login": "Anmelden",
        "nav_logout": "Abmelden",
        "nav_register": "Registrieren",
        
        # General
        "brand_name": "OWRE",
        "brand_tagline": "Premium Aufbewahrungslösungen für dein Zuhause",
        "currency": "€",
        "language": "Sprache",
        
        # Products
        "products": "Produkte",
        "featured": "Empfohlene Produkte",
        "product_name": "Produktname",
        "product_description": "Beschreibung",
        "product_price": "Preis",
        "product_stock": "Lagerbestand",
        "product_category": "Kategorie",
        "product_image": "Produktbild",
        "add_to_cart": "In den Warenkorb",
        "remove_from_cart": "Aus Warenkorb entfernen",
        "no_products": "Keine Produkte gefunden",
        "product_added": "Produkt hinzugefügt",
        "product_removed": "Produkt entfernt",
        
        # Cart
        "cart": "Warenkorb",
        "cart_empty": "Warenkorb ist leer",
        "cart_total": "Summe",
        "cart_subtotal": "Zwischensumme",
        "cart_tax": "MwSt.",
        "cart_shipping": "Versand",
        "continue_shopping": "Weiter einkaufen",
        "proceed_checkout": "Zur Kasse",
        "quantity": "Menge",
        "subtotal": "Zwischensumme",
        
        # Orders
        "orders": "Bestellungen",
        "order_number": "Bestellnummer",
        "order_date": "Bestelldatum",
        "order_status": "Status",
        "order_total": "Gesamtbetrag",
        "status_pending": "Ausstehend",
        "status_paid": "Bezahlt",
        "status_shipped": "Versendet",
        "status_delivered": "Zugestellt",
        "status_cancelled": "Storniert",
        "place_order": "Bestellung aufgeben",
        
        # Users
        "users": "Benutzer",
        "username": "Benutzername",
        "email": "E-Mail",
        "password": "Passwort",
        "confirm_password": "Passwort wiederholen",
        "firstname": "Vorname",
        "lastname": "Nachname",
        "phone": "Telefon",
        "address": "Adresse",
        "city": "Stadt",
        "postal_code": "Postleitzahl",
        "country": "Land",
        "login": "Anmelden",
        "register": "Registrieren",
        "logout": "Abmelden",
        "profile": "Profil",
        "my_account": "Mein Konto",
        
        # Admin
        "admin": "Admin",
        "add_product": "Produkt hinzufügen",
        "edit_product": "Produkt bearbeiten",
        "delete_product": "Produkt löschen",
        "manage_products": "Produkte verwalten",
        "manage_categories": "Kategorien verwalten",
        "manage_users": "Benutzer verwalten",
        "manage_orders": "Bestellungen verwalten",
        "statistics": "Statistiken",
        "total_revenue": "Gesamtumsatz",
        "total_orders": "Gesamtbestellungen",
        "total_users": "Gesamtbenutzer",
        "total_products": "Gesamtprodukte",
        
        # Messages
        "success": "Erfolgreich",
        "error": "Fehler",
        "warning": "Warnung",
        "info": "Information",
        "confirm": "Bestätigen",
        "cancel": "Abbrechen",
        "save": "Speichern",
        "delete": "Löschen",
        "edit": "Bearbeiten",
        "close": "Schließen",
        "back": "Zurück",
        "next": "Weiter",
        "previous": "Zurück",
        "search": "Suchen",
        "filter": "Filtern",
        "sort": "Sortieren",
        "loading": "Lädt",
        
        # Legal
        "legal": "Rechtliches",
        "imprint": "Impressum",
        "privacy": "Datenschutz",
        "terms": "Geschäftsbedingungen",
        "shipping": "Versandinformationen",
        "about": "Über uns",
        "contact": "Kontakt",
        "all_rights_reserved": "Alle Rechte vorbehalten",
    },
    "en": {
        # Navigation
        "nav_home": "Home",
        "nav_shop": "Shop",
        "nav_cart": "Cart",
        "nav_orders": "Orders",
        "nav_account": "My Account",
        "nav_admin": "Admin",
        "nav_login": "Login",
        "nav_logout": "Logout",
        "nav_register": "Register",
        
        # General
        "brand_name": "OWRE",
        "brand_tagline": "Premium Storage Solutions for your Home",
        "currency": "$",
        "language": "Language",
        
        # Products
        "products": "Products",
        "featured": "Featured Products",
        "product_name": "Product Name",
        "product_description": "Description",
        "product_price": "Price",
        "product_stock": "Stock",
        "product_category": "Category",
        "product_image": "Product Image",
        "add_to_cart": "Add to Cart",
        "remove_from_cart": "Remove from Cart",
        "no_products": "No products found",
        "product_added": "Product added",
        "product_removed": "Product removed",
        
        # Cart
        "cart": "Cart",
        "cart_empty": "Your cart is empty",
        "cart_total": "Total",
        "cart_subtotal": "Subtotal",
        "cart_tax": "Tax",
        "cart_shipping": "Shipping",
        "continue_shopping": "Continue Shopping",
        "proceed_checkout": "Proceed to Checkout",
        "quantity": "Quantity",
        "subtotal": "Subtotal",
        
        # Orders
        "orders": "Orders",
        "order_number": "Order Number",
        "order_date": "Order Date",
        "order_status": "Status",
        "order_total": "Total",
        "status_pending": "Pending",
        "status_paid": "Paid",
        "status_shipped": "Shipped",
        "status_delivered": "Delivered",
        "status_cancelled": "Cancelled",
        "place_order": "Place Order",
        
        # Users
        "users": "Users",
        "username": "Username",
        "email": "Email",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "firstname": "First Name",
        "lastname": "Last Name",
        "phone": "Phone",
        "address": "Address",
        "city": "City",
        "postal_code": "Postal Code",
        "country": "Country",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "profile": "Profile",
        "my_account": "My Account",
        
        # Admin
        "admin": "Admin",
        "add_product": "Add Product",
        "edit_product": "Edit Product",
        "delete_product": "Delete Product",
        "manage_products": "Manage Products",
        "manage_categories": "Manage Categories",
        "manage_users": "Manage Users",
        "manage_orders": "Manage Orders",
        "statistics": "Statistics",
        "total_revenue": "Total Revenue",
        "total_orders": "Total Orders",
        "total_users": "Total Users",
        "total_products": "Total Products",
        
        # Messages
        "success": "Success",
        "error": "Error",
        "warning": "Warning",
        "info": "Information",
        "confirm": "Confirm",
        "cancel": "Cancel",
        "save": "Save",
        "delete": "Delete",
        "edit": "Edit",
        "close": "Close",
        "back": "Back",
        "next": "Next",
        "previous": "Previous",
        "search": "Search",
        "filter": "Filter",
        "sort": "Sort",
        "loading": "Loading",
        
        # Legal
        "legal": "Legal",
        "imprint": "Imprint",
        "privacy": "Privacy",
        "terms": "Terms",
        "shipping": "Shipping Information",
        "about": "About",
        "contact": "Contact",
        "all_rights_reserved": "All rights reserved",
    },
}

class I18n:
    """Translation helper class"""
    
    def __init__(self, default_language: str = "de"):
        self.current_language = default_language
        self.default_language = default_language
    
    def set_language(self, language: str):
        """Set the current language"""
        if language in TRANSLATIONS:
            self.current_language = language
        else:
            self.current_language = self.default_language
    
    def translate(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """Translate a key to the current language"""
        lang = language or self.current_language
        
        if lang not in TRANSLATIONS:
            lang = self.default_language
        
        translation = TRANSLATIONS[lang].get(key, key)
        
        # Support for string formatting
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return translation
    
    def t(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """Shortcut for translate"""
        return self.translate(key, language, **kwargs)

# Global i18n instance
i18n = I18n()

def get_i18n() -> I18n:
    """Get the global i18n instance"""
    return i18n
