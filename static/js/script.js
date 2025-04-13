// Save player name to localStorage
function savePlayerName() {
  const input = document.getElementById("name-input") || document.getElementById("playerNameInput");
  const newName = input.value.trim() || "Player 1";

  if (confirm(`Change name to "${newName}"?`)) {
    localStorage.setItem("playerName", newName);
    alert("Name updated!");
    updatePlayerNameDisplay();
    if (window.location.pathname.includes("profile.html")) {
      window.location.href = "index.html"; // Redirect after saving
    }
  }
}

// Update player name in UI (called on load and after saving)
function updatePlayerNameDisplay() {
  const display = document.getElementById("playerNameDisplay") || document.getElementById("player-name");
  if (display) {
    const savedName = localStorage.getItem("playerName") || "Player 1";
    display.textContent = `Player: ${savedName}`;
  }
}

// Called when the page is loaded
window.onload = () => {
  const savedName = localStorage.getItem("playerName") || "Player 1";

  // Prefill input if it exists
  const input = document.getElementById("name-input") || document.getElementById("playerNameInput");
  if (input) {
    input.value = savedName;
  }

  // Update player name text
  updatePlayerNameDisplay();
};

const cars = [
  "/static/assets/car.gif",      // Default car (car1)
  "/static/assets/car2.gif",     // Second car
  "/static/assets/car3.gif"      // Third car
];


function cycleCar() {
  let currentCar = localStorage.getItem("selectedCar") || cars[0];
  let index = cars.indexOf(currentCar);
  let nextIndex = (index + 1) % cars.length;
  let nextCar = cars[nextIndex];
  
  localStorage.setItem("selectedCar", nextCar);
  document.getElementById("carImage").src = nextCar;
}

// On load, set the saved car in profile
window.addEventListener("DOMContentLoaded", () => {
  const savedCar = localStorage.getItem("selectedCar") || cars[0];
  const carImg = document.getElementById("carImage");
  if (carImg) carImg.src = savedCar;

  const nameDisplay = document.getElementById("player-name");
  if (nameDisplay) {
    const savedName = localStorage.getItem("playerName") || "Player 1";
    nameDisplay.textContent = `Player: ${savedName}`;
  }

  const menuCar = document.querySelector(".car-gif");
  if (menuCar) {
    const selectedCar = localStorage.getItem("selectedCar") || cars[0];
    menuCar.src = selectedCar;
  }
});

// Load avatar on both profile and home
function loadAvatar() {
  const avatarImg = document.getElementById("avatarImage") || document.getElementById("homeAvatar");
  const storedAvatar = localStorage.getItem("avatarImage");
  if (avatarImg) {
    if (storedAvatar) {
      avatarImg.src = storedAvatar;
    } else {
      avatarImg.src = "/static/assets/avatar.png";
    }
  }
}

// Handle avatar upload
const avatarInput = document.getElementById("avatarUpload");
if (avatarInput) {
  avatarInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (event) {
      const base64Image = event.target.result;
      localStorage.setItem("avatarImage", base64Image);
      document.getElementById("avatarImage").src = base64Image;
    };
    reader.readAsDataURL(file);
  });
}

window.onload = () => {
  // Player name logic
  const savedName = localStorage.getItem("playerName");
  const nameDisplay = document.getElementById("player-name");
  if (nameDisplay && savedName) {
    nameDisplay.textContent = `Player: ${savedName}`;
  }

  const input = document.getElementById("playerNameInput") || document.getElementById("name-input");
  if (input && savedName) {
    input.value = savedName;
  }

  // Car selection
  const savedCar = localStorage.getItem("selectedCar");
  const carImage = document.getElementById("carImage");
  if (carImage && savedCar) {
    carImage.src = savedCar;
  }

  // Avatar sync
  loadAvatar();
};

function triggerAvatarUpload() {
  document.getElementById("avatarUpload").click();
}


// Navigation button actions
function openProfile() {
  window.location.href = "profile.html";
}

function openPlay() {
  alert("Go to Track Selection");
}

function openSettings() {
  alert("Settings popup here!");
}

function quitGame() {
  alert("Thanks for playing!");
}

// Save car color selection
function selectColor(color) {
  localStorage.setItem("carColor", color);
  alert(`Car color set to ${color}`);
}

// Save character selection
function selectCharacter(filename) {
  localStorage.setItem("character", filename);
  alert(`Character selected: ${filename}`);
}
