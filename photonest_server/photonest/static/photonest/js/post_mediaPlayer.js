const mediaPlayers = {};

  function initMediaPlayer(postId, mediaFiles) {
      mediaPlayers[postId] = {
          currentIndex: 0,
          mediaFiles: mediaFiles,
          imgElement: document.getElementById(`current-image-${postId}`),
          videoElement: document.getElementById(`current-video-${postId}`)
      };

      if (mediaFiles.length() <= 1){
        document.getElementById(`btn-media-left-${postId}`).classList.add("hidden");
        document.getElementById(`btn-media-right-${postId}`).classList.add("hidden");
      }
  }

  function changeMedia(postId, direction) {
      const player = mediaPlayers[postId];
      if (!player) return;

      // Index aktualisieren mit zirkulärer Navigation
      player.currentIndex = (player.currentIndex + direction + player.mediaFiles.length) % player.mediaFiles.length;
      
      const currentMedia = player.mediaFiles[player.currentIndex];
      
      if (currentMedia.type === 'photo') {
          // Bild anzeigen
          player.imgElement.src = currentMedia.url;
          player.imgElement.style.display = 'block';
          
          // Video verstecken und zurückspulen
          player.videoElement.style.display = 'none';
          player.videoElement.pause();
          player.videoElement.currentTime = 0;
      } else {
          // Video anzeigen
          player.videoElement.src = currentMedia.url;
          player.videoElement.style.display = 'block';
          player.videoElement.pause();
          player.videoElement.currentTime = 0;

          // Bild verstecken
          player.imgElement.style.display = 'none';
      }
  }