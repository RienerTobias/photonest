document.addEventListener('DOMContentLoaded', function() {
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

    const savedTheme = getCookie('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
});