// ========== Car Options ==========
const cars = [
  "/static/assets/car.gif",
  "/static/assets/car2.gif",
  "/static/assets/car3.gif"
];

const bgMusic = new Audio("/static/assets/bg-music.mp3");
bgMusic.loop = true;
bgMusic.volume = 0.5;

// ========== Global Background Music ==========
if (localStorage.getItem("musicEnabled") !== "false") {
  bgMusic.play().catch(() => {
    document.body.addEventListener("click", () => bgMusic.play(), { once: true });
  });
} else {
  bgMusic.muted = true;
}

// ========== Save Player Name ==========
function savePlayerName() {
  const input = document.getElementById("playerNameInput") || document.getElementById("name-input");
  const newName = input.value.trim() || "Player 1";

  if (confirm(`Change name to "${newName}"?`)) {
    localStorage.setItem("playerName", newName);

    fetch("/save_name", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName })
    })
    .then(res => res.json())
    .then(data => {
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
    const savedName = localStorage.getItem("playerName") || "Player 1";
    display.textContent = `Player: ${savedName}`;
  }
}

// ========== Car Switch ==========
function cycleCar() {
  const currentCar = localStorage.getItem("selectedCar") || cars[0];
  const index = cars.indexOf(currentCar);
  const nextCar = cars[(index + 1) % cars.length];
  localStorage.setItem("selectedCar", nextCar);
  const carImg = document.getElementById("carImage");
  if (carImg) carImg.src = nextCar;
}

// ========== Avatar Upload ==========
function triggerAvatarUpload() {
  document.getElementById("avatarUpload").click();
}

function loadAvatar() {
  const avatarImg = document.getElementById("avatarImage") || document.getElementById("homeAvatar");
  const storedAvatar = localStorage.getItem("avatarImage");
  if (avatarImg) {
    if (storedAvatar && storedAvatar !== "null") {
      avatarImg.src = storedAvatar;
    } else {
      avatarImg.src = "/static/assets/avatar.png";
    }
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
      localStorage.setItem("avatarImage", base64Image);
      document.getElementById("avatarImage").src = base64Image;
    };
    reader.readAsDataURL(file);
  });
}

// ========== On Load ==========
window.onload = () => {
  if (localStorage.getItem("musicEnabled") !== "false") {
    bgMusic.play();
  }

  const savedName = localStorage.getItem("playerName") || "Player 1";
  const savedCar = localStorage.getItem("selectedCar") || cars[0];

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
  alert("Track selection coming soon...");
}

// ========== Settings ==========
function openSettings() {
  document.getElementById("settingsModal").style.display = "flex";
  const toggle = document.getElementById("audioToggle");
  toggle.checked = localStorage.getItem("musicEnabled") !== "false";
}

function closeSettings() {
  document.getElementById("settingsModal").style.display = "none";
}

function showSettingsTab(tab) {
  document.querySelectorAll(".tab").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".settings-tab").forEach(tabDiv => tabDiv.classList.remove("active"));

  document.getElementById(tab + "-settings").classList.add("active");
  document.getElementById("tab-" + tab).classList.add("active");
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
    // Reset localStorage
    localStorage.setItem("playerName", "Player 1");
    localStorage.setItem("selectedCar", "/static/assets/car.gif");
    localStorage.removeItem("avatarImage");

    // Update DB
    fetch("/save_name", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "Player 1" })
    });

    // Show modal
    document.getElementById("quitModal").style.display = "flex";

    // === Apply changes to UI immediately ===
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
