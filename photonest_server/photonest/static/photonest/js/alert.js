const HIDE_DURATION_MS = 60 * 60 * 1000; // 1 Stunde

function hideAlert() {
    const alert = document.getElementById('report-alert');
    if (alert) {
        alert.style.display = 'none';
        const expirationTime = Date.now() + HIDE_DURATION_MS;
        localStorage.setItem('hideReportedAlertUntil', expirationTime.toString());
    }
}

const alert = document.getElementById('report-alert');
const hideUntil = localStorage.getItem('hideReportedAlertUntil');

if (hideUntil && Date.now() < parseInt(hideUntil)) {
    if (alert) alert.style.display = 'none';
} else {
    // Zeit ist abgelaufen oder kein Wert vorhanden → anzeigen und ggf. Speicher zurücksetzen
    localStorage.removeItem('hideReportedAlertUntil');
}
