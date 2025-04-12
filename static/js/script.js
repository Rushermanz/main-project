function updatePlayerName(newName) {
    const nameDisplay = document.getElementById("player-name");
    nameDisplay.textContent = `Player: ${newName}`;
  }
  function confirmName() {
    const newName = document.getElementById("name-input").value.trim();
    if (newName !== "") {
      if (confirm(`Change name to "${newName}"?`)) {
        localStorage.setItem("playerName", newName);
        alert("Name updated!");
      }
    }
  }
  
  function goBack() {
    window.location.href = "index.html";
  }
  
  function selectColor(color) {
    localStorage.setItem("carColor", color);
    alert(`Car color set to ${color}`);
  }
  
  function selectCharacter(filename) {
    localStorage.setItem("character", filename);
    alert(`Character selected: ${filename}`);
  }
  
  window.onload = () => {
    const savedName = localStorage.getItem("playerName");
    if (savedName) {
      document.getElementById("name-input").value = savedName;
    }
  };
    

function openProfile() {
    alert("Open Profile Section (modal)");
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
  