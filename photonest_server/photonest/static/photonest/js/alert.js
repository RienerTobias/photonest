const HIDE_DURATION_MS = 60 * 60 * 1000; // 1 Stunde
const ALERT_DURATION = 5 * 1000; //5 Sekunden

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
    localStorage.removeItem('hideReportedAlertUntil');
}

function AddTimedAlert(type, message, icon="triangle-exclamation"){
    const TYPES = "alert-success alert-warning alert-error";

    const alert = document.createElement("div");
    alert.innerHTML = `<div role="alert" class="alert alert-${type} m-1"><i class="fa-regular fa-${icon} text-lg"></i><span>${message}</span></div>`;

    document.getElementById("alert-container").appendChild(alert); 

    setTimeout(() => {
        alert.remove();
    }, ALERT_DURATION);
}