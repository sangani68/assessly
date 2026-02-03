// Real-time avatar uses WebRTC and requires ICE server info from Speech service,
// then AvatarSynthesizer.startAvatarAsync(peerConnection) and speakTextAsync(text). :contentReference[oaicite:1]{index=1}
//
// Sandbox note: this fetches ICE token with your Speech key in the browser.
// For production, proxy via backend.

export const Avatar = (() => {
  let avatarSynth = null;
  let peerConnection = null;

  function ensureSpeechSDK() {
    if (!window.SpeechSDK) throw new Error("SpeechSDK not loaded.");
    return window.SpeechSDK;
  }

  async function fetchIceToken(speechRegion, speechKey) {
    // GET /cognitiveservices/avatar/relay/token/v1 on {region}.tts.speech.microsoft.com :contentReference[oaicite:2]{index=2}
    const url = `https://${speechRegion}.tts.speech.microsoft.com/cognitiveservices/avatar/relay/token/v1`;
    const r = await fetch(url, { method: "GET", headers: { "Ocp-Apim-Subscription-Key": speechKey } });
    if (!r.ok) throw new Error(`ICE token fetch failed: ${r.status}`);
    return await r.json();
  }

  function mountTracks(mountEl) {
    peerConnection.ontrack = (event) => {
      if (event.track.kind === "video") {
        const video = document.createElement("video");
        video.autoplay = true;
        video.playsInline = true;
        video.controls = false;
        video.disablePictureInPicture = true;
        video.muted = true;
        video.style.pointerEvents = "none";
        video.className = "avatarVideo";
        video.srcObject = event.streams[0];
        mountEl.innerHTML = "";
        mountEl.appendChild(video);
        const mask = document.createElement("div");
        mask.className = "avatarMask";
        mask.setAttribute("aria-hidden", "true");
        mountEl.appendChild(mask);
      }
      if (event.track.kind === "audio") {
        const audio = document.createElement("audio");
        audio.autoplay = true;
        audio.muted = false;
        audio.srcObject = event.streams[0];
        mountEl.appendChild(audio);
        // Some browsers block autoplay audio; attempt to play and surface errors.
        audio.play().catch((err) => {
          console.warn("Audio autoplay blocked or failed:", err);
        });
      }
    };

    peerConnection.addTransceiver("video", { direction: "sendrecv" });
    peerConnection.addTransceiver("audio", { direction: "sendrecv" });
  }

  async function init({ speechKey, speechRegion, mountEl, voice="en-US-AvaMultilingualNeural", avatarCharacter="lisa", avatarStyle="casual-sitting" }) {
    const SpeechSDK = ensureSpeechSDK();
    const ice = await fetchIceToken(speechRegion, speechKey);

    const urls = ice.Urls || ice.urls || [];
    const iceUrl = urls.find(u => String(u).startsWith("turn")) || urls[0];
    const username = ice.Username || ice.username;
    const credential = ice.Password || ice.credential || ice.password;

    peerConnection = new RTCPeerConnection({ iceServers: [{ urls: [iceUrl], username, credential }] });
    mountTracks(mountEl);

    const speechConfig = SpeechSDK.SpeechConfig.fromSubscription(speechKey, speechRegion);
    speechConfig.speechSynthesisVoiceName = voice;

    const avatarConfig = new SpeechSDK.AvatarConfig(avatarCharacter, avatarStyle);
    avatarSynth = new SpeechSDK.AvatarSynthesizer(speechConfig, avatarConfig);

    await avatarSynth.startAvatarAsync(peerConnection); // starts avatar + WebRTC stream :contentReference[oaicite:3]{index=3}
    return true;
  }

  async function speak(text) {
    const SpeechSDK = ensureSpeechSDK();
    if (!avatarSynth) throw new Error("Avatar not initialized.");
    const result = await avatarSynth.speakTextAsync(text); // speaks text :contentReference[oaicite:4]{index=4}
    if (result.reason !== SpeechSDK.ResultReason.SynthesizingAudioCompleted) {
      console.warn("Avatar speak result:", result);
    }
  }

  function close() {
    try { avatarSynth?.close(); } catch {}
    try { peerConnection?.close(); } catch {}
    avatarSynth = null;
    peerConnection = null;
  }

  return { init, speak, close };
})();
