function stopRecording() {
  console.log("stopRecording() called");

  // Stop microphone access
  gumStream.getAudioTracks()[0].stop();

  // Disable the stop button
  stopButton.disabled = true;
  recordButton.disabled = false;

  // Tell the recorder to finish the recording (stop recording + encode the recorded audio)
  recorder.finishRecording();

  __log("Recording stopped");
}

function createDownloadLink(blob, encoding) {
  var url = URL.createObjectURL(blob);
  var au = document.createElement("audio");
  var li = document.createElement("li");

  // Add controls to the <audio> element
  au.controls = true;
  au.src = url;

  // Add the <audio> element to the <li> element
  li.appendChild(au);

  // Add the <li> element to the ordered list
  recordingsList.appendChild(li);

  __log("Recording ready for transcription");

  // Automatically send the audio blob to the server for transcription
  sendBlobForTranscription(blob);
}

function sendBlobForTranscription(blob) {
  const formData = new FormData();
  formData.append("file", blob, "recording.wav");

  fetch("/mic", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.transcript) {
        // Display the transcript on the page
        const transcriptDiv = document.createElement("div");
        transcriptDiv.innerHTML = `
          <h4>Recognized Text:</h4>
          <p style="font-size: 18px; font-weight: bold;">${data.transcript}</p>
        `;
        recordingsList.appendChild(transcriptDiv);
      } else {
        __log("Transcription failed.");
      }
    })
    .catch((err) => {
      console.error("Error during transcription:", err);
    });
}
