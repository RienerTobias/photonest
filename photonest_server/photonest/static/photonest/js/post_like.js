function likePost(postId) {
    const btn = document.getElementById(`like-btn-${postId}`);
    const btn_modal = document.getElementById(`like-btn-modal_${postId}`);
    const icon = btn.querySelector('i');
    const icon_modal = btn_modal.querySelector('i');
    const counter = btn.querySelector('span');
    const counter_modal = btn_modal.querySelector('span');
    
    let url = "";
    if(typeof postId == "number"){
        url = `/posts/${postId}/like/`;
    }
    else if(typeof postId == "string"){
        url = `/posts/${postId.split("_")[1]}/like/`;
    }
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ like: 1 })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'liked') {
            icon.classList.remove('fa-regular');
            icon.classList.add('fa-solid');
            icon_modal.classList.remove('fa-regular');
            icon_modal.classList.add('fa-solid');
            btn.classList.add('liked');
            btn_modal.classList.add('liked');
        } else {
            icon.classList.remove('fa-solid');
            icon.classList.add('fa-regular');
            icon_modal.classList.remove('fa-solid');
            icon_modal.classList.add('fa-regular');
            btn.classList.remove('liked');
            btn_modal.classList.remove('liked');
        }
        counter.innerText = data.like_count;
        counter_modal.innerText = data.like_count;
    })
    .catch(error => console.error('Error:', error));
}