const mediaPlayers = {};

  function initMediaPlayer(postId, mediaFiles) {
      mediaPlayers[postId] = {
          currentIndex: 0,
          mediaFiles: mediaFiles,
          imgElement: document.getElementById(`current-image-${postId}`),
          videoElement: document.getElementById(`current-video-${postId}`)
      };

      if (Object.keys(mediaFiles).length <= 1){
        document.getElementById(`btn-media-left-${postId}`).classList.add("invisible");
        document.getElementById(`btn-media-right-${postId}`).classList.add("invisible");
      }

      document.getElementById(`media-download_${postId}`).setAttribute("href", `media/${mediaFiles[0].id}/download/`);
  }

  function changeMedia(postId, direction) {
      const player = mediaPlayers[postId];
      if (!player) return;

      player.currentIndex = (player.currentIndex + direction + player.mediaFiles.length) % player.mediaFiles.length;
      
      const currentMedia = player.mediaFiles[player.currentIndex];
      
      if (currentMedia.type === 'photo') {
          player.imgElement.src = currentMedia.url;
          player.imgElement.style.display = 'block';
          
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
      document.getElementById(`media-download_${postId}`).setAttribute("href", `media/${currentIndex}/download/`);
  }