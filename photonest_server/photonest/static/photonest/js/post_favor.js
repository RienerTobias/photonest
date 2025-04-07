function favorPost(postId, pageprefix) {
    const btn = document.getElementById(`favor-btn-${pageprefix}-${postId}`);
    const btn_modal = document.getElementById(`favor-btn-${pageprefix}-modal_${postId}`);
    const icon = btn.querySelector('i');
    const icon_modal = btn_modal.querySelector('i');

    let url = "";
    if(typeof postId == "number"){
        url = `/posts/${postId}/favor/`;
    }
    else if(typeof postId == "string"){
        url = `/posts/${postId.split("_")[1]}/favor/`;
    }
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ favor: 1 })
    })
    .then(response => response.json())
    .then(data => {
        if (data.favored === 'true') {
            icon.classList.remove('fa-regular');
            icon.classList.add('fa-solid');
            icon_modal.classList.remove('fa-regular');
            icon_modal.classList.add('fa-solid');
            btn.classList.add('favored');
            btn_modal.classList.add('favored');
        } else {
            icon.classList.remove('fa-solid');
            icon.classList.add('fa-regular');
            icon_modal.classList.remove('fa-solid');
            icon_modal.classList.add('fa-regular');
            btn.classList.remove('favored');
            btn_modal.classList.remove('favored');
        }
    })
    .catch(error => console.error('Error:', error));
}