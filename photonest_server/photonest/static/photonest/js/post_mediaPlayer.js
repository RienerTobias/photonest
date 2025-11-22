const mediaPlayers = {};

  function initMediaPlayer(postId, pageprefix, mediaFiles) {
      mediaPlayers[postId + pageprefix] = {
          currentIndex: 0,
          mediaFiles: mediaFiles,
          imgElement: document.getElementById(`current-image-${pageprefix}-${postId}`),
          videoElement: document.getElementById(`current-video-${pageprefix}-${postId}`)
      };

      if (Object.keys(mediaFiles).length <= 1){
        document.getElementById(`btn-media-left-${pageprefix}-${postId}`).style.visibility = "hidden";
        document.getElementById(`btn-media-right-${pageprefix}-${postId}`).style.visibility = "hidden";
      }

      if(can_download)document.getElementById(`media-download-${pageprefix}_${postId}`).setAttribute("href", `/media/${mediaFiles[0].id}/download/`);
      document.getElementById(`reportPost${pageprefix}_${postId}_media_number`).value = 1;

    const carouselContainer = document.getElementById(`carousel-container-${pageprefix}-${postId}`);
    if (carouselContainer) {
        carouselContainer.querySelectorAll('.carousel-item').forEach(item => {
            item.addEventListener('click', function() {
                const media = this.querySelector('img');
                
                if (media.src.match(/\.(jpeg|jpg|gif|png|webp)$/) != null) {
                    ShowFullscreenImg(media.getAttribute('data-url'));
                }
                else{
                    console.log("failed fullscreen - url: " + media.src)
                }
            });
        });
    }
  }

  function changeMedia(postId, pageprefix, direction) {
      const player = mediaPlayers[postId + pageprefix];
      if (!player) return;

      player.currentIndex = (player.currentIndex + direction + player.mediaFiles.length) % player.mediaFiles.length;
      
      const currentMedia = player.mediaFiles[player.currentIndex];
      
      if (currentMedia.type === 'photo') {
          player.imgElement.src = currentMedia.url;
          player.imgElement.style.display = 'block';
          player.imgElement.setAttribute('data-url', currentMedia.full_res_url)
          
          player.videoElement.style.display = 'none';
          player.videoElement.pause();
          player.videoElement.currentTime = 0;
      } else {
          player.videoElement.src = currentMedia.url;
          player.videoElement.style.display = 'block';
          player.videoElement.pause();
          player.videoElement.currentTime = 0;

          player.imgElement.style.display = 'none';
      }
      if(can_download)document.getElementById(`media-download-${pageprefix}_${postId}`).setAttribute("href", `/media/${currentMedia.id}/download/`);
      document.getElementById(`reportPost${pageprefix}_${postId}_media_number`).value = player.currentIndex+1;
  }

function ShowFullscreenImg(path){
    const fullscreenimg = document.getElementById('fullscreen_img');
    fullscreenimg.querySelector('img').src = path;
    fullscreenimg.showModal();
}
function CloseFullscreenImg(){
    const fullscreenimg = document.getElementById('fullscreen_img');
    fullscreenimg.querySelector('img').src = "";
    fullscreenimg.close();
}