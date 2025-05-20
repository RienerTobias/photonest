document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('input[name="nav-bar"]');
    const contents = {
        'Übersicht': document.getElementById('content-uebersicht'),
        'Home': document.getElementById('content-home'),
        'Gallerie': document.getElementById('content-gallerie'),
        'Dashboard': document.getElementById('content-dashboard'),
        'Profil': document.getElementById('content-profil')
    };

    showContent('Übersicht');

    tabs.forEach(tab => {
        tab.addEventListener('change', (e) => {
            showContent(e.target.value);
        });
    });

    function showContent(selectedTab) {
        Object.values(contents).forEach(content => {
            if (content) content.style.display = 'none';
        });
        
        if (contents[selectedTab]) {
            contents[selectedTab].style.display = 'block';
        }
    }
});