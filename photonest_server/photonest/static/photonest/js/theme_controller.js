// Globale Theme-Steuerung für alle Seiten
document.addEventListener('DOMContentLoaded', function() {
    // Cookie-Funktionen
    function getCookie(name) {
        const cookieName = name + "=";
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookies = decodedCookie.split(';');
        
        for(let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.indexOf(cookieName) === 0) {
                return cookie.substring(cookieName.length, cookie.length);
            }
        }
        return null;
    }

    // Theme setzen
    const savedTheme = getCookie('theme') || 'light'; // Fallback auf light
    document.documentElement.setAttribute('data-theme', savedTheme);
});