# PhotoNest

## Einrichtung der Entwicklungs-Umgebung für Photonest

### Voraussetzungen:
- Python 3.x
- Git

### Schritte zur Installation und Einrichtung:

1. **Projekt klonen**  
   Klone das Repository von GitHub:
   ```bash
   git clone https://github.com/RienerTobias/photonest.git
   cd photonest
   
2. **Virtuelle Umgebung erstellen und aktivieren**  
   Erstelle eine virtuelle Umgebung und aktiviere sie:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux  
   venv\Scripts\activate  # Windows
  
3. **Abhängigkeiten installieren**  
   Installiere alle benötigten Pakete:
   ```bash
   pip install -r requirements.txt
   
4. **Umgebungsvariablen konfigurieren**  
   Erstelle eine .env-Datei im Verzeichnis photonest_server mit folgenden Inhalten::
   ```bash
   ALLOWED_HOSTS=*Wunschdomain/IP-Adresse*
   CSRF_COOKIE_DOMAIN=*Basisdomain/IP-Adresse*  
   DJANGO_SECRET_KEY="django-secret-key"
