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
