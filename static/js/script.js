document.getElementById('saveName').addEventListener('click', function() {
  const newName = document.getElementById('playerName').value.trim();
  if (newName !== "") {
      if (confirm(`Change name to "${newName}"?`)) {
          fetch('/save_name', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({ name: newName })
          })
          .then(response => response.json())
          .then(data => {
              if (data.status === 'success') {
                  alert("Name updated!");
                  window.location.href = 'index.html'; // Redirect to home page
              }
          });
      }
  }
});

window.onload = () => {
  fetch('/get_name')
  .then(response => response.json())
  .then(data => {
      const nameDisplay = document.getElementById("player-name");
      nameDisplay.textContent = `Player: ${data.name}`;
  });
};

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
  