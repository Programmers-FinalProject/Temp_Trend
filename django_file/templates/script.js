document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    const currentLocationBtn = document.getElementById('current-location-btn');
    const currentLocationElement = document.getElementById('current-location');
    const loadingElement = document.getElementById('loading');

    // 세션에 저장된 주소 가져오기
    fetch('/api/session-address/')
        .then(response => response.json())
        .then(data => {
            if (data.address !== "No address in session") {
                currentLocationElement.textContent = `현위치: ${data.address}`;
            }
        })
        .catch(error => console.error('Error:', error));

    if (currentLocationBtn) {
        console.log("Current location button found");
        currentLocationBtn.addEventListener('click', function() {
            if ("geolocation" in navigator) {

                // 로딩 메시지 표시
                loadingElement.style.display = 'block';
                
                navigator.geolocation.getCurrentPosition(function(position) {
                    var latitude = position.coords.latitude;
                    var longitude = position.coords.longitude;

                    // 위치 정보를 서버로 전송
                    const csrftoken = getCookie('csrftoken');
                    console.log("CSRF token:", csrftoken);

                    fetch('/save_location/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        },
                        body: JSON.stringify({
                            latitude: latitude.toFixed(4),
                            longitude: longitude.toFixed(4),
                            location_type: 'current'
                        })
                    })
                    .then(response => {
                        console.log("Server response status:", response.status);
                        return response.json();
                    })
                    .then(data => {
                        console.log('Location saved:', data);
                        // 위치 이름 요청
                        fetch('/location_name/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken'),
                            },
                            body: JSON.stringify({
                                latitude: latitude.toFixed(4),
                                longitude: longitude.toFixed(4)
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (currentLocationElement) {
                                // latitude가 숫자일 경우에만 업데이트
                                if (data.address !== 'No address in session') {
                                    currentLocationElement.textContent = `현위치: ${data.address}`;
                                }
                            }
                        })
                        .catch(error => console.error('Error:', error))
                        .finally(() => {
                            // 로딩 메시지 숨기기
                            loadingElement.style.display = 'none';
                        });
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                    })
                    .finally(() => {
                        // 로딩 메시지 숨기기
                        loadingElement.style.display = 'none';
                    });
                }, function(error) {
                    console.error("Error getting location:", error);
                    // 로딩 메시지 숨기기
                    loadingElement.style.display = 'none';
                });
            } else {
                console.log("Geolocation is not supported by this browser.");
            }
        });
    } else {
        console.error("Button with id 'current-location-btn' not found");
    }
});

// CSRF 토큰을 가져오는 함수
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    console.log(`Cookie '${name}' value:`, cookieValue);
    return cookieValue;
}


// 지역별 위도 및 경도 정보
const locationData = {
    '01': {
        '강남구': {lat: "37.5146", lon: "127.0496"},
        '강동구': {lat: "37.5274", lon: "127.1259"},
        '강북구': {lat: "37.6370", lon: "127.0277"},
        '강서구': {lat: "37.5482", lon: "126.8517"}
    },
    '02': {
        '해운대구': {lat: "35.1600", lon: "129.1658"},
        '수영구': {lat: "35.1425", lon: "129.1154"},
        '사하구': {lat: "35.1014", lon: "128.9770"},
        '부산진구': {lat: "35.1600", lon: "129.0553"}
    },
    '03': {
        '중구': {lat: "37.5610", lon: "126.9996"},
        '남동구': {lat: "37.4445", lon: "126.7338"},
        '연수구': {lat: "37.4071", lon: "126.6804"},
        '부평구': {lat: "37.5043", lon: "126.7241"}
    },
    '04': {
        '중구': {lat: "37.5610", lon: "126.9996"},
        '동구': {lat: "35.1359", lon: "129.0592"},
        '서구': {lat: "35.0948", lon: "129.0264"},
        '달서구': {lat: "35.8269", lon: "128.5351"}
    },
    '05': {
        '유성구': {lat: "36.3594", lon: "127.3583"},
        '서구': {lat: "35.0948", lon: "129.0264"},
        '중구': {lat: "37.5610", lon: "126.9996"},
        '대덕구': {lat: "36.3438", lon: "127.4177"}
    },
    '06': {
        '동구': {lat: "35.1359", lon: "129.0592"},
        '서구': {lat: "35.0948", lon: "129.0264"},
        '남구': {lat: "35.1334", lon: "129.0865"},
        '북구': {lat: "35.1942", lon: "128.9925"}
    },
    '07': {
        '중구': {lat: "37.5610", lon: "126.9996"},
        '남구': {lat: "35.1334", lon: "129.0865"},
        '동구': {lat: "35.1359", lon: "129.0592"},
        '북구': {lat: "35.1942", lon: "128.9925"}
    },
    '08': {
        '세종시': {lat: "36.4800", lon: "127.2890"}
    },
    '09': {
        '수원시': {lat: "37.2635", lon: "127.0286"},
        '고양시': {lat: "37.6583", lon: "126.8320"},
        '성남시': {lat: "37.4448", lon: "127.1378"},
        '용인시': {lat: "37.2410", lon: "127.1776"}
    },
    '10': {
        '충주시': {lat: "36.9882", lon: "127.9281"},
        '제천시': {lat: "37.1298", lon: "128.1932"},
        '청주시': {lat: "36.6424", lon: "127.4890"}
    },
    '11': {
        '공주시': {lat: "36.4436", lon: "127.1211"},
        '보령시': {lat: "36.3306", lon: "126.6149"},
        '천안시': {lat: "36.8154", lon: "127.1130"}
    },
    '12': {
        '목포시': {lat: "34.8088", lon: "126.3944"},
        '여수시': {lat: "34.7573", lon: "127.6644"},
        '순천시': {lat: "34.9476", lon: "127.4893"}
    },
    '13': {
        '경주시': {lat: "35.8532", lon: "129.2270"},
        '김천시': {lat: "36.1369", lon: "128.1158"},
        '포항시': {lat: "36.0190", lon: "129.3435"}
    },
    '14': {
        '진주시': {lat: "35.1770", lon: "128.1100"},
        '통영시': {lat: "34.8513", lon: "128.4353"},
        '창원시': {lat: "35.2279", lon: "128.6811"}
    },
    '15': {
        '춘천시': {lat: "37.8785", lon: "127.7323"},
        '원주시': {lat: "37.3391", lon: "127.9221"},
        '강릉시': {lat: "37.7491", lon: "128.8785"}
    },
    '16': {
        '군산시': {lat: "35.9646", lon: "126.7388"},
        '익산시': {lat: "35.9453", lon: "126.9599"},
        '전주시': {lat: "35.8242", lon: "127.1480"}
    },
    '17': {
        '제주시': {lat: "33.4963", lon: "126.5332"},
        '서귀포시': {lat: "33.2524", lon: "126.5126"}
    }
};



// 폼 제출 함수
async function submitForm() {
    const area1Select = document.getElementById('area1_id');
    const area2Select = document.getElementById('area2_id');
    const cityCode = area1Select.value;
    const district = area2Select.value;
    console.log(area1Select.value)
    console.log(area2Select.value)
    if (cityCode && district) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const lat = locationData[cityCode][district].lat;
        const lon = locationData[cityCode][district].lon;


        fetch('/submit_location/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({cityCode, district, lat, lon})
        })
        .then(response => response.json())
        //데이터post 확인용. 배포시 없앨 예정
        .then(data => {
            if (data.status === 'success') {
                alert('데이터가 성공적으로 전송되었습니다.');
            } else {
                alert('데이터 전송에 실패했습니다.');
            }
        })
        .catch(error => console.error('Error:', error));
    } else {
        alert('모든 필드를 선택해 주세요.');
    }
}