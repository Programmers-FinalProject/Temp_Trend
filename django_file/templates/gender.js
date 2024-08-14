document.addEventListener("DOMContentLoaded", function() {
    console.log("DOM fully loaded and parsed");
    
    const initialButtons = document.getElementById("initial-buttons");
    if (initialButtons) {
        console.log("Found initial-buttons element");
        initialButtons.addEventListener("click", function(event) {
            console.log("Button clicked:", event.target.id);
            if (event.target.id === "genderMale") {
                selectGender('m');
            } else if (event.target.id === "genderFemale") {
                selectGender('w');
            } else if (event.target.id === "genderUnisex") {
                selectGender('unisex');
            }
        });
    } else {
        console.error("Could not find initial-buttons element");
    }

    // 각 버튼에 대해 개별적으로 이벤트 리스너 추가
    ['genderMale', 'genderFemale', 'genderUnisex'].forEach(id => {
        const button = document.getElementById(id);
        if (button) {
            console.log(`Found ${id} button`);
            button.addEventListener('click', () => {
                console.log(`${id} button clicked`);
            });
        } else {
            console.error(`Could not find ${id} button`);
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const genderSelect = document.getElementById('genderSelect');
    if (genderSelect) {
        genderSelect.addEventListener('change', function(event) {
            saveGender(event.target.value);
        });
    } else {
        console.error('Gender select element not found');
    }
});

function selectGender(gender) {
    console.log("selectGender called with:", gender);
    const csrfToken = getCSRFToken();
    console.log("CSRF Token:", csrfToken);

    fetch('/save_gender/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({gender: gender})
    })
    .then(response => {
        console.log("Server response status:", response.status);
        return response.json();
    })
    .then(data => {
        console.log("Server response:", data);
        if (data.status === 'success') {
            console.log("Gender saved successfully");
            localStorage.setItem("selectedGender", gender);
            window.location.href = `/?gender=${gender}`;
            displaySelectedGender(gender);
        } else {
            throw new Error(data.message || 'Unknown error occurred');
        }
    })
    .catch(error => {
        console.error("Error saving gender:", error);
        alert("성별 저장 중 오류가 발생했습니다. 다시 시도해 주세요.");
    })
    
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
            selectedText.textContent = "Unisex";
            break;

            
    }
}

function resetSelection() {
    localStorage.removeItem("selectedGender");

    const initialButtons = document.getElementById("initial-buttons");
    const selectedGender = document.getElementById("selected-gender");

    initialButtons.style.display = "flex";
    selectedGender.style.display = "none";
}

function getCSRFToken() {
    let cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        let [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            console.log("Found CSRF token");
            return decodeURIComponent(value);
        }
    }
    console.error("CSRF token not found in cookies");
    return '';
}