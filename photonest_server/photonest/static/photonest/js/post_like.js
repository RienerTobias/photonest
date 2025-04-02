function likePost(postId) {
    const btn = document.getElementById(`like-btn-${postId}`);
    const countElement = document.getElementById(`like-count-${postId}`);
    const icon = btn.querySelector('i');
    const counter = btn.querySelector('span')
    
    fetch(`/posts/${postId}/like/`, {
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
            btn.classList.add('liked');
        } else {
            icon.classList.remove('fa-solid');
            icon.classList.add('fa-regular');
            btn.classList.remove('liked');
        }
        counter.innerText = data.like_count;
    })
    .catch(error => console.error('Error:', error));
}