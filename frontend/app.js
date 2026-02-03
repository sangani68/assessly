import { Avatar } from "./speech-avatar.js";

let sessionId = null;

const elChat = document.getElementById("chat");
const elUserText = document.getElementById("userText");
let backendBaseUrl = "http://localhost:8000";
const elScores = document.getElementById("scores");
const elReport = document.getElementById("report");

const DOMAIN_LABELS = {
  A: "AI fundamentals",
  B: "Use case framing",
  C: "Data safety",
  D: "Responsible AI",
  E: "Prompting",
  F: "Validation",
  G: "Governance",
};

const LEVEL_LABELS = {
  0: "Unaware / misconceptions",
  1: "Aware / basic",
  2: "Practicing with checks",
  3: "Proficient / sets standards",
};

const elAvatarMount = document.getElementById("avatarMount");

function addMsg(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  elChat.appendChild(div);
  elChat.scrollTop = elChat.scrollHeight;
}

function renderScores(scores) {
  if (!elScores) return;
  const entries = Object.entries(DOMAIN_LABELS).map(([k, label]) => {
    const v = (scores || {})[k];
    const level = v === undefined ? "—" : `${v} · ${LEVEL_LABELS[v] || "Unknown"}`;
    return `<div class="scoreRow"><div class="scoreKey">${k}</div><div class="scoreLabel">${label}</div><div class="scoreValue">${level}</div></div>`;
  });
  elScores.innerHTML = entries.join("");
}

async function api(path, body) {
  const url = `${backendBaseUrl.replace(/\/$/, "")}${path}`;
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {})
  });
  if (!r.ok) throw new Error(`API error ${r.status}: ${await r.text()}`);
  return await r.json();
}

async function verifyAccess(password) {
  const r = await fetch(`${backendBaseUrl.replace(/\/$/, "")}/auth/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password })
  });
  if (!r.ok) return false;
  const data = await r.json();
  return !!data.ok;
}

function showApp() {
  const landing = document.getElementById("landing");
  const app = document.getElementById("app");
  if (landing) {
    landing.classList.add("is-hidden");
    landing.style.display = "none";
  }
  if (app) {
    app.classList.remove("is-hidden");
    app.style.display = "block";
  }
}

function toggleAccessControls() {
  const consent = document.getElementById("consentCheck");
  const pwd = document.getElementById("accessPassword");
  const enterBtn = document.getElementById("enterBtn");
  const enabled = !!consent?.checked;
  if (pwd) pwd.disabled = !enabled;
  if (enterBtn) enterBtn.disabled = !enabled;
}

async function handleEnter() {
  const consent = document.getElementById("consentCheck");
  const pwd = document.getElementById("accessPassword");
  const err = document.getElementById("landingError");
  err.textContent = "";
  if (!consent?.checked) {
    err.textContent = "Please accept the guidelines to proceed.";
    return;
  }
  if (!pwd?.value?.trim()) {
    err.textContent = "Enter the access password.";
    return;
  }
  const ok = await verifyAccess(pwd.value.trim());
  if (!ok) {
    err.textContent = "Invalid password.";
    return;
  }
  showApp();
}

async function startSession() {
  await initAvatar();
  const res = await api("/session/start", {});
  sessionId = res.session_id;
  addMsg("assistant", res.assistant_text);
  try { await Avatar.speak(res.assistant_text); } catch {}
}

async function sendText(text) {
  if (!sessionId) return addMsg("assistant", "Start a session first.");
  addMsg("user", text);

  const res = await api(`/session/${sessionId}/chat`, { user_text: text });
  addMsg("assistant", res.assistant_text);

  renderScores(res.scores || {});
  if (res.report) elReport.textContent = JSON.stringify(res.report, null, 2);

  try { await Avatar.speak(res.assistant_text); } catch {}
}

async function initAvatar() {
  if (!window.__speechKey || !window.__speechRegion) {
    await loadConfig();
  }
  if (!window.__speechKey || !window.__speechRegion) {
    return addMsg("assistant", "Speech config missing. Check backend /config env.");
  }
  const loader = document.getElementById("avatarLoader");
  if (loader) loader.style.display = "flex";
  await Avatar.init({ speechKey: window.__speechKey, speechRegion: window.__speechRegion, mountEl: elAvatarMount });
  if (loader) loader.style.display = "none";
  addMsg("assistant", "Avatar initialized. I will speak responses.");
}

async function startSTT() {
  if (!window.SpeechSDK) return addMsg("assistant", "SpeechSDK not loaded.");
  if (!window.__speechKey || !window.__speechRegion) {
    await loadConfig();
  }
  const speechKey = window.__speechKey || "";
  const speechRegion = window.__speechRegion || "";
  if (!speechKey || !speechRegion) return addMsg("assistant", "Speech config missing. Check backend /config env.");

  const SpeechSDK = window.SpeechSDK;
  const speechConfig = SpeechSDK.SpeechConfig.fromSubscription(speechKey, speechRegion);
  speechConfig.speechRecognitionLanguage = "en-US";
  const audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
  const recognizer = new SpeechSDK.SpeechRecognizer(speechConfig, audioConfig);

  addMsg("assistant", "Listening… speak now.");
  recognizer.recognizeOnceAsync(async (result) => {
    const text = result.text || "";
    if (!text) return addMsg("assistant", "I didn't catch that. Try again.");
    await sendText(text);
    recognizer.close();
  });
}

document.getElementById("startBtn").addEventListener("click", startSession);
document.getElementById("sendBtn").addEventListener("click", () => {
  const t = elUserText.value.trim();
  if (!t) return;
  elUserText.value = "";
  sendText(t);
});
document.getElementById("micBtn").addEventListener("click", startSTT);

elUserText.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    document.getElementById("sendBtn").click();
  }
});

async function loadConfig() {
  try {
    const r = await fetch(`${backendBaseUrl}/config`);
    if (!r.ok) throw new Error(`config ${r.status}`);
    const cfg = await r.json();
    backendBaseUrl = (cfg.backend_url || backendBaseUrl).replace(/\/$/, "");
    window.__speechKey = cfg.speech_key || "";
    window.__speechRegion = cfg.speech_region || "";
  } catch (err) {
    console.warn("Failed to load config:", err);
  }
}

loadConfig();

document.getElementById("enterBtn").addEventListener("click", handleEnter);
document.getElementById("consentCheck").addEventListener("change", toggleAccessControls);
document.getElementById("accessPassword").addEventListener("keydown", (e) => {
  if (e.key === "Enter") handleEnter();
});
toggleAccessControls();
