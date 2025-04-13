// ========== Car Options ==========
const cars = [
  "/static/assets/car.gif",
  "/static/assets/car2.gif",
  "/static/assets/car3.gif"
];

// ========== Global Background Music ==========
if (!window.bgMusic) {
  window.bgMusic = new Audio("/static/assets/bg-music.mp3");
  bgMusic.loop = true;
  bgMusic.volume = 0.5;

  const musicEnabled = localStorage.getItem("musicEnabled");

  if (musicEnabled === null) {
    localStorage.setItem("musicEnabled", "true"); // default ON
    bgMusic.muted = false;
  } else {
    bgMusic.muted = musicEnabled === "false";
  }

  if (!bgMusic.muted) {
    const savedTime = parseFloat(sessionStorage.getItem("musicTime")) || 0;
    bgMusic.currentTime = savedTime;

    bgMusic.play().catch(() => {
      document.body.addEventListener("click", () => bgMusic.play(), { once: true });
    });
  }

  window.addEventListener("beforeunload", () => {
    sessionStorage.setItem("musicTime", bgMusic.currentTime);
  });
}

// ========== Save Player Name ==========
function savePlayerName() {
  const input = document.getElementById("playerNameInput") || document.getElementById("name-input");
  const newName = input.value.trim() || "Player 1";

  if (confirm(`Change name to "${newName}"?`)) {
    sessionStorage.setItem("playerName", newName);

    fetch("/save_name", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName })
    })
    .then(res => res.json())
    .then(() => {
      alert("Name updated!");
      updatePlayerNameDisplay();
      if (window.location.pathname.includes("profile")) {
        window.location.href = "/";
      }
    });
  }
}

function updatePlayerNameDisplay() {
  const display = document.getElementById("playerNameDisplay") || document.getElementById("player-name");
  if (display) {
    const savedName = sessionStorage.getItem("playerName") || "Player 1";
    display.textContent = `Player: ${savedName}`;
  }
}

// ========== Car Switch ==========
function cycleCar() {
  const currentCar = sessionStorage.getItem("selectedCar") || cars[0];
  const index = cars.indexOf(currentCar);
  const nextCar = cars[(index + 1) % cars.length];
  sessionStorage.setItem("selectedCar", nextCar);

  const carImg = document.getElementById("carImage");
  if (carImg) carImg.src = nextCar;
}

// ========== Avatar Upload ==========
function triggerAvatarUpload() {
  document.getElementById("avatarUpload").click();
}

function loadAvatar() {
  const avatarImg = document.getElementById("avatarImage") || document.getElementById("homeAvatar");
  const storedAvatar = sessionStorage.getItem("avatarImage");
  if (avatarImg) {
    avatarImg.src = storedAvatar && storedAvatar !== "null"
      ? storedAvatar
      : "/static/assets/avatar.png";
  }
}

const avatarInput = document.getElementById("avatarUpload");
if (avatarInput) {
  avatarInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const base64Image = event.target.result;
      sessionStorage.setItem("avatarImage", base64Image);
      document.getElementById("avatarImage").src = base64Image;
    };
    reader.readAsDataURL(file);
  });
}

// ========== On Load ==========
window.onload = () => {
  const savedName = sessionStorage.getItem("playerName") || "Player 1";
  const savedCar = sessionStorage.getItem("selectedCar") || cars[0];

  const input = document.getElementById("playerNameInput") || document.getElementById("name-input");
  if (input) input.value = savedName;

  updatePlayerNameDisplay();

  const carImg = document.getElementById("carImage");
  if (carImg) carImg.src = savedCar;

  const menuCar = document.querySelector(".car-gif");
  if (menuCar) menuCar.src = savedCar;

  loadAvatar();
};

// ========== Navigation ==========
function openProfile() {
  window.location.href = "profile.html";
}

function openPlay() {
  window.location.href = "/tracks"; // or "/tracks" if routed by Flask
}


// ========== Settings ==========
function openSettings() {
  document.getElementById("settingsModal").style.display = "flex";
  const toggle = document.getElementById("audioToggle");

  const musicSetting = localStorage.getItem("musicEnabled");
  toggle.checked = musicSetting === null || musicSetting !== "false"; // default ON
}

function closeSettings() {
  document.getElementById("settingsModal").style.display = "none";
}

function showSettingsTab(tab) {
  document.querySelectorAll(".tab").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".settings-tab").forEach(tabDiv => tabDiv.classList.remove("active"));

  document.getElementById(`${tab}-settings`).classList.add("active");
  document.getElementById(`tab-${tab}`).classList.add("active");
}

function toggleAudio() {
  const isEnabled = document.getElementById("audioToggle").checked;
  localStorage.setItem("musicEnabled", isEnabled);
  bgMusic.muted = !isEnabled;

  if (isEnabled) {
    bgMusic.play();
  } else {
    bgMusic.pause();
  }
}

// ========== Quit ==========
function quitGame() {
  if (confirm("Are you sure you want to quit and reset your profile?")) {
    sessionStorage.setItem("playerName", "Player 1");
    sessionStorage.setItem("selectedCar", "/static/assets/car.gif");
    sessionStorage.removeItem("avatarImage");
    sessionStorage.removeItem("musicTime");

    localStorage.removeItem("musicEnabled");

    fetch("/save_name", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "Player 1" })
    });

    document.getElementById("quitModal").style.display = "flex";

    updatePlayerNameDisplay();
    loadAvatar();

    const input = document.getElementById("playerNameInput") || document.getElementById("name-input");
    if (input) input.value = "Player 1";

    const carImg = document.getElementById("carImage");
    if (carImg) carImg.src = "/static/assets/car.gif";

    const menuCar = document.querySelector(".car-gif");
    if (menuCar) menuCar.src = "/static/assets/car.gif";
  }
}

function closeTab() {
  alert("Please close this tab manually.");
}

function returnHome() {
  window.location.href = "/";
}

const popup = document.getElementById("trackPopup");
const popupName = document.getElementById("popupTrackName");
const popupDesc = document.getElementById("popupDescription");

document.querySelectorAll(".track-card").forEach((card, index) => {
  card.addEventListener("click", () => {
    const name = card.querySelector(".track-name").innerText;
    const difficulty = card.querySelector(".track-difficulty").innerText;
    popupName.innerText = name;
    popupDesc.innerText = `This is a ${difficulty.toLowerCase()} track with unique challenges.`; // Placeholder
    popup.style.display = "flex";
    showTrackTab("info");
  });
});

function closeTrackPopup() {
  popup.style.display = "none";
}

function showTrackTab(tab) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".track-tab").forEach(t => t.classList.remove("active"));
  document.getElementById(`tab-${tab}`).classList.add("active");
  document.getElementById(`${tab}-tab`).classList.add("active");
}
