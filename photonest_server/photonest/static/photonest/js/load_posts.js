document.addEventListener("DOMContentLoaded", () => {
    const loadBtn = document.getElementById("load-more");
    const container = document.getElementById("post-container");

    if (!loadBtn) return;

    loadBtn.addEventListener("click", () => {
        const nextPage = loadBtn.dataset.nextPage;

        // Filter + Sortierung erhalten
        const queryString = window.location.search.replace("?", "");

        const url = `/gallery/load-more/?${queryString}&page=${nextPage}`;

        loadBtn.disabled = true;
        loadBtn.innerHTML = "<span class='loading loading-spinner'></span> lädt...";

        fetch(url)
            .then(r => r.json())
            .then(data => {
                container.insertAdjacentHTML("beforeend", data.html);

                if (data.has_next) {
                    loadBtn.dataset.nextPage = data.next_page;
                    loadBtn.disabled = false;
                    loadBtn.textContent = "Mehr laden";
                } else {
                    loadBtn.remove();
                }
            });
    });
});
