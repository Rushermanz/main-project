// static/js/script.js

// ========== Car Options ==========
const cars = [
  "/static/assets/car.gif",
  "/static/assets/car2.gif",
  "/static/assets/car3.gif"
];

// Track Slugs → DB IDs
const TRACK_NAME_TO_ID = {
  bahrain: 1,
  baku: 2,
  usa: 3,
  spain: 4,
  silverstone: 5
};

// ========== Music ==========
if (!window.bgMusic) {
  window.bgMusic = new Audio("/static/assets/bg-music.mp3");
  bgMusic.loop = true;
  bgMusic.volume = 0.5;

  const musicEnabled = localStorage.getItem("musicEnabled");
  bgMusic.muted = musicEnabled === "false";

  if (!bgMusic.muted) {
    bgMusic.currentTime = parseFloat(sessionStorage.getItem("musicTime")) || 0;
    bgMusic.play().catch(() => {
      document.body.addEventListener("click", () => bgMusic.play(), { once: true });
    });
  }

  window.addEventListener("beforeunload", () => {
    sessionStorage.setItem("musicTime", bgMusic.currentTime);
  });
}

document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    bgMusic.pause();
  } else if (localStorage.getItem("musicEnabled") !== "false") {
    bgMusic.play().catch(() => {
      document.body.addEventListener("click", () => bgMusic.play(), { once: true });
    });
  }
});

// ========== Navigation ==========
function openProfile()   { window.location.href = "/profile"; }
function openPlay()      { window.location.href = "/tracks"; }
function returnHome()    { window.location.href = "/"; }
function closeTab()      { alert("Please close this tab manually."); }

function openSettings() {
  const modal = document.getElementById("settingsModal");
  if (modal) modal.style.display = "flex";
}
function closeSettings() {
  const modal = document.getElementById("settingsModal");
  if (modal) modal.style.display = "none";
}
function showSettingsTab(tab) {
  document.querySelectorAll(".tab-switch .tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".settings-tab").forEach(c => c.classList.remove("active"));
  document.getElementById(`tab-${tab}`)?.classList.add("active");
  document.getElementById(`${tab}-settings`)?.classList.add("active");
}
function toggleAudio() {
  const toggle = document.getElementById("audioToggle");
  if (!toggle) return;
  const isOn = toggle.checked;
  localStorage.setItem("musicEnabled", isOn);
  bgMusic.muted = !isOn;
  isOn ? bgMusic.play() : bgMusic.pause();
}

// ========== Quit ==========
function quitGame() {
  if (!confirm("Quit and reset your profile?")) return;

  sessionStorage.setItem("playerName", "Player 1");
  sessionStorage.setItem("selectedCar", cars[0]);
  sessionStorage.removeItem("avatarImage");
  sessionStorage.removeItem("musicTime");
  localStorage.removeItem("musicEnabled");

  fetch("/save_name", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: "Player 1" })
  });

  const modal = document.getElementById("quitModal");
  if (modal) modal.style.display = "flex";

  updatePlayerNameDisplay();
  loadAvatar();

  const input = document.getElementById("playerNameInput") || document.getElementById("name-input");
  if (input) input.value = "Player 1";

  const carImg = document.getElementById("carImage");
  if (carImg) carImg.src = cars[0];

  const menuCar = document.querySelector(".car-gif");
  if (menuCar) menuCar.src = cars[0];
}

// ========== Profile ==========
function updatePlayerNameDisplay() {
  const el = document.getElementById("playerNameDisplay") || document.getElementById("player-name");
  if (el) el.textContent = `Player: ${sessionStorage.getItem("playerName") || "Player 1"}`;
}

function savePlayerName() {
  const input = document.getElementById("playerNameInput") || document.getElementById("name-input");
  if (!input) return;

  const newName = input.value.trim() || "Player 1";
  if (!confirm(`Change name to "${newName}"?`)) return;

  sessionStorage.setItem("playerName", newName);
  fetch("/save_name", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: newName })
  }).then(res => res.json())
    .then(() => {
      alert("Name updated!");
      updatePlayerNameDisplay();
      if (window.location.pathname.includes("profile")) window.location.href = "/";
    });
}

function cycleCar() {
  const current = sessionStorage.getItem("selectedCar") || cars[0];
  const next = cars[(cars.indexOf(current) + 1) % cars.length];
  sessionStorage.setItem("selectedCar", next);
  const img = document.getElementById("carImage");
  if (img) img.src = next;
  const menu = document.querySelector(".car-gif");
  if (menu) menu.src = next;
}

function triggerAvatarUpload() {
  document.getElementById("avatarUpload")?.click();
}
function loadAvatar() {
  const avatar = sessionStorage.getItem("avatarImage");
  const img = document.getElementById("avatarImage") || document.getElementById("homeAvatar");
  if (img) img.src = avatar && avatar !== "null" ? avatar : "/static/assets/avatar.png";
}

// ========== Avatar Upload ==========
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("avatarUpload")?.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = ev => {
      sessionStorage.setItem("avatarImage", ev.target.result);
      const img = document.getElementById("avatarImage");
      if (img) img.src = ev.target.result;
    };
    reader.readAsDataURL(file);
  });
});

// ========== Leaderboard ==========
function loadLeaderboard(trackId) {
  fetch(`/leaderboard/${trackId}`)
    .then(r => r.json())
    .then(data => {
      const tbody = document.querySelector("#leaderboard-tab table tbody");
      if (!tbody) return;
      tbody.innerHTML = "";
      data.forEach((entry, i) => {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${i + 1}</td><td>${entry.player}</td><td>${entry.lap_time.toFixed(2)}s</td>`;
        tbody.appendChild(row);
      });
    });
}

// ========== Track Modal ==========
function showTrackTab(tab) {
  document.querySelectorAll(".track-tab-switch .tab").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".track-tab").forEach(div => div.classList.remove("active"));
  document.getElementById(`tab-${tab}`)?.classList.add("active");
  document.getElementById(`${tab}-tab`)?.classList.add("active");

  if (tab === "leaderboard") {
    const name = document.getElementById("popupTrackName").innerText.trim().toLowerCase();
    loadLeaderboard(TRACK_NAME_TO_ID[name]);
  }
}
function closeTrackPopup() {
  document.getElementById("trackPopup").style.display = "none";
}

// ========== Game Launcher ==========

document.addEventListener("click", e => {
  const btn = e.target.closest(".race-btn");
  if (!btn) return;

  const { track, mode } = btn.dataset;
  if (!track || !mode) return;

  sessionStorage.setItem("musicTime", bgMusic.currentTime);
  bgMusic.pause();

  launchGame(track, mode);
});

function launchGame(track, mode) {
  const name = sessionStorage.getItem("playerName") || "Player 1";

  // Send player name to temporary file via backend
  fetch("/set_current_player", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  });

  fetch("/start_game", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ track, mode })
  })


  fetch("/start_game", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ track, mode })
  })
    .then(res => {
      if (res.ok) {
        const label = mode.replace(/_/g, " ").toUpperCase();
        alert(`Launching ${label} on ${track.toUpperCase()}!`);
      } else {
        alert("Game launch failed.");
      }
    })
    .catch(() => alert("Error launching game."));
}


// ========== Init ========== 
document.addEventListener("DOMContentLoaded", () => {
  updatePlayerNameDisplay();
  loadAvatar();

  const savedCar = sessionStorage.getItem("selectedCar") || cars[0];
  document.getElementById("carImage")?.setAttribute("src", savedCar);
  document.querySelector(".car-gif")?.setAttribute("src", savedCar);

  const input = document.getElementById("playerNameInput") || document.getElementById("name-input");
  if (input) input.value = sessionStorage.getItem("playerName") || "Player 1";

  document.querySelectorAll(".track-card").forEach(card => {
    card.addEventListener("click", () => {
      const name = card.querySelector(".track-name").innerText.trim();
      const difficulty = card.querySelector(".track-difficulty").innerText;
      const img = card.querySelector("img").getAttribute("src");
      const slug = name.toLowerCase();

      document.getElementById("popupTrackName").innerText = name;
      document.getElementById("popupTrackImage").src = img;
      document.getElementById("popupDescription").innerText = `This is a ${difficulty.toLowerCase()} track with unique challenges.`;

      const diffEl = document.getElementById("popupTrackDifficulty");
      diffEl.innerText = difficulty;
      diffEl.className = `popup-difficulty-tag ${difficulty.toLowerCase()}-tag`;

      document.querySelectorAll(".race-btn").forEach(btn => {
        btn.dataset.track = slug;
        btn.dataset.mode = btn.classList.contains("pink") ? "race_bot"
                          : btn.classList.contains("cyan") ? "pvp"
                          : "time_trial";
      });

      document.getElementById("trackPopup").style.display = "flex";
      showTrackTab("info");
    });
  });
});
