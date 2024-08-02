document.addEventListener("DOMContentLoaded", () => {
    const savedGender = sessionStorage.getItem("selectedGender");
    if (savedGender) {
        displaySelectedGender(savedGender);
    }
});

function selectGender(gender) {
    sessionStorage.setItem("selectedGender", gender);
    displaySelectedGender(gender);
}

function displaySelectedGender(gender) {
    const initialButtons = document.getElementById("initial-buttons");
    const selectedGender = document.getElementById("selected-gender");
    const selectedText = document.getElementById("selected-text");

    initialButtons.style.display = "none";
    selectedGender.style.display = "flex";

    switch (gender) {
        case "m":
            selectedText.textContent = "남자";
            break;
        case "w":
            selectedText.textContent = "여자";
            break;
        case "unisex":
            selectedText.textContent = "unisex";
            break;
    }
}

function resetSelection() {
    sessionStorage.removeItem("selectedGender");

    const initialButtons = document.getElementById("initial-buttons");
    const selectedGender = document.getElementById("selected-gender");

    initialButtons.style.display = "flex";
    selectedGender.style.display = "none";
}