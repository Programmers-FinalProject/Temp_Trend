document.addEventListener("DOMContentLoaded", function() {
    console.log("DOM fully loaded and parsed");

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

async function selectGender(gender) {
    console.log("selectGender called with:", gender);
    const csrfToken = getCSRFToken();
    console.log("CSRF Token:", csrfToken);

    try {
        const response = await fetch('/save_gender/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ gender: gender })
        });

        console.log("Server response status:", response.status);
        const data = await response.json();
        console.log("Server response:", data);
        if (data.status === 'success') {
            console.log("Gender saved successfully");
        } else {
            throw new Error(data.message || 'Unknown error occurred');
        }
    } catch (error) {
        console.error("Error saving gender:", error);
        alert("성별 저장 중 오류가 발생했습니다. 다시 시도해 주세요.");
    }
}
async function fetchProducts(gender) {
    const loadingElement1 = document.getElementById('loading-spinner'); 
    const musinsa = document.getElementsByClassName('center-content')[0];
    let content = `
        <div class="musinsa_categories">
        </div>`;
    document.getElementById('musinsaContent').innerHTML = content;
    
    try {
        musinsa.style.display = 'block';
        loadingElement1.style.display = 'block';
        // selectGender가 비동기 함수라 await로 처리
        await selectGender(gender);
        console.log("젠더선택")

        // processWeatherData가 비동기 함수라 await로 처리
        await processWeatherData();
        console.log("날씨저장")

        // 첫 번째 fetch 요청
        let response = await fetch('/learn/');
        console.log("Server response status (learn):", response.status);

        let data = await response.json();
        console.log("Server response (learn):", data);

        // 두 번째 fetch 요청
        response = await fetch('/musinsajjj/');
        console.log("Server response status (musinsajjj):", response.status);

        data = await response.json();
        console.log("Server response (musinsajjj):", data);
        loadingElement1.style.display = 'none';
        renderProducts(data.products);  // `products` 객체를 넘겨줌
    } catch (error) {
        console.error("Error during fetch process:", error);
    }
    
}


function renderProducts(products) {
    let content = `
        <div class="musinsa_categories">
            ${products.상의 ? renderCategory('상의', products.상의) : ''}
            ${products.하의 ? renderCategory('하의', products.하의) : ''}
            ${products.신발 ? renderCategory('신발', products.신발) : ''}
            ${products.아이템 ? renderCategory('아이템', products.아이템) : ''}
        </div>`;
    document.getElementById('musinsaContent').innerHTML = content;
}

function renderCategory(categoryName, items) {
    let itemHtml = items.map(item => `
        <li>
            <a href="${item.product_link}">
                <img src="${item.image_link}" alt="${item.product_name}">
            </a>
            <div class="product-info">
                <p>${item.rank} : ${item.product_name}</p>
                <p>성별 : ${item.gender}</p>
                <p>${item.price} ₩</p>
            </div>
        </li>`).join('');
    return `
        <div class="musinsa_category">
            <h3>${categoryName}</h3>
            <div class="musinsa_list">
                <ul>${itemHtml}</ul>
            </div>
        </div>`;
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