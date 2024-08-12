import pandas as pd
from pathlib import Path
import json

# 현재 스크립트의 부모 디렉토리
current_dir = Path(__file__).parent

# 파일의 상대 경로 정의
file_path = current_dir / 'musinsa.csv'

# CSV 파일에서 데이터 로드
df = pd.read_csv(file_path)

# CSV 파일에서 'CATEGORY'와 'gender' 열이 있는지 확인
if 'CATEGORY' in df.columns and 'GENDER' in df.columns:
    # 'CATEGORY'와 'gender' 열의 중복 조합 제거
    unique_df = df.drop_duplicates(subset=['CATEGORY', 'GENDER'])
else:
    raise ValueError("CSV 파일에 'CATEGORY' 또는 'GENDER' 열이 없습니다.")

# 결과 출력
print("Unique CATEGORY and GENDER combinations:")
print(unique_df)

# 리스트로 변환
unique_combinations = unique_df[['CATEGORY', 'GENDER']].values.tolist()

# 결과 리스트 출력
print("\nUnique combinations as a list:")
for combination in unique_combinations:
    print(combination)

# 카테고리 분류
def classify_category(category):
    if category in [
        '반소매 티셔츠', '셔츠/블라우스', '피케/카라 티셔츠', '후드 티셔츠', '맨투맨/ 스웨트셔츠',
        '니트/스웨터', '긴소매 티셔츠', '스포츠 상의', '민소매 티셔츠', '슈트/ 블레이저 재킷',
        '레더/ 라이더스 재킷', '트레이닝 재킷', '겨울 기타 코트', '나일론/ 코치 재킷', '겨울 싱글 코트',
        '숏패딩/ 숏헤비 아우터', '블루종/ MA-1', '트러커 재킷', '패딩 베스트', '아노락 재킷',
        '사파리/ 헌팅 재킷', '겨울 더블 코트', '카디건', '스타디움 재킷', '롱패딩/ 롱헤비 아우터',
        '베스트', '후드 집업', '환절기 코트', '플리스/뽀글이', '무스탕/퍼'
    ]:
        return '상의'
    elif category in [
        '데님 팬츠', '트레이닝/조거 팬츠', '숏 팬츠', '코튼 팬츠', '스포츠 하의',
        '슈트 팬츠/슬랙스', '레깅스'
    ]:
        return '하의'
    elif category in [
        '캔버스/단화', '패션스니커즈화', '스포츠 스니커즈', '구두', '샌들', '블로퍼',
        '힐/펌프스', '슬리퍼', '로퍼', '플랫 슈즈', '모카신/보트 슈즈', '부츠'
    ]:
        return '신발'
    else:
        return '아이템'

# 각 카테고리와 젠더에 분류 추가
categorized_list = [[classify_category(category), category, gender] for category, gender in unique_combinations]

# 결과 출력
df = pd.DataFrame(categorized_list, columns=['category1', 'category2', 'gender'])
print(df)


from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import numpy as np

# 예시 제품 데이터: 각 카테고리별
product_data = df

# 날씨 데이터 예시
weather_data = pd.DataFrame({
    'TMP': [28, 22, 17, 29],
    'PTY': [0, 1, 0, 0],
    'forecast_time': ['09:00', '12:00', '15:00', '18:00']
})

# 학습 프레임 생성
def create_training_frame(weather_df, product_df):
    return pd.merge(weather_df, product_df, how='cross')

# 학습 프레임 생성
training_frame = create_training_frame(weather_data, product_data)
training_frame['user_preference'] = np.random.choice([1, 2, 3, 4], size=len(training_frame))  # 임의의 사용자 선호도

# 범주형 데이터 인코딩
encoder = OneHotEncoder(sparse_output=False)
encoded_product = encoder.fit_transform(training_frame[['category1', 'category2', 'gender', 'forecast_time']])
encoded_product_df = pd.DataFrame(encoded_product, columns=encoder.get_feature_names_out(['category1', 'category2', 'gender', 'forecast_time']))

# 인코딩된 학습 데이터
training_frame_encoded = pd.concat([training_frame.drop(['category1', 'category2', 'gender', 'forecast_time'], axis=1), encoded_product_df], axis=1)

# 결측값 처리
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(training_frame_encoded.drop(['user_preference'], axis=1))

# 특성과 레이블 준비
X = pd.DataFrame(X_imputed, columns=training_frame_encoded.drop(['user_preference'], axis=1).columns)
y = training_frame_encoded['user_preference']

# 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 파이프라인 구성
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier(random_state=42))
])

# 모델 학습
pipeline.fit(X_train, y_train)

# 추천 함수
def recommend_categories(weather_info, product_df, target_gender):
    new_weather_df = pd.DataFrame([weather_info])
    combined_df = create_training_frame(new_weather_df, product_df)

    # 범주형 데이터 인코딩
    encoded_combined = encoder.transform(combined_df[['category1', 'category2', 'gender', 'forecast_time']])
    encoded_combined_df = pd.DataFrame(encoded_combined, columns=encoder.get_feature_names_out(['category1', 'category2', 'gender', 'forecast_time']))

    combined_df_encoded = pd.concat([combined_df.drop(['category1', 'category2', 'gender', 'forecast_time'], axis=1), encoded_combined_df], axis=1)

    combined_df_imputed = imputer.transform(combined_df_encoded)
    combined_df_imputed = pd.DataFrame(combined_df_imputed, columns=combined_df_encoded.columns)
    combined_df_imputed = combined_df_imputed[X.columns]

    predictions = pipeline.predict(combined_df_imputed)
    
    # 추천 제품 필터링 (일단 선호도 1 이상)
    recommended_products = combined_df[np.array(predictions) >= 1]
    
    # 성별에 따라 필터링
    if target_gender == 'unisex':
        recommended_products = recommended_products[recommended_products['gender'] == 'unisex']
    else:
        recommended_products = recommended_products[(recommended_products['gender'] == target_gender) | (recommended_products['gender'] == 'unisex')]
    
    # 각 카테고리에서 2개씩 추천
    categories = ['상의', '하의', '신발', '아이템']
    final_recommendations = pd.DataFrame()

    for category in categories:
        category_recommendations = recommended_products[recommended_products['category1'] == category].head(2)
        final_recommendations = pd.concat([final_recommendations, category_recommendations], ignore_index=True)
    
    recommended_products_musinsa = final_recommendations[['category1', 'category2', 'gender']].copy()
    recommended_products_musinsa.rename(columns={'category1': 'category'}, inplace=True)

    return recommended_products_musinsa

# 추천 결과 생성
weather_info = {'TMP': 28, 'PTY': 0, 'forecast_time': '09:00'}
# 각 성별에 대한 추천
recommended_products_women = recommend_categories(weather_info, product_data, target_gender='w')
recommended_products_men = recommend_categories(weather_info, product_data, target_gender='m')
recommended_products_unisex = recommend_categories(weather_info, product_data, target_gender='unisex')
# 추천 결과를 JSON으로 변환
recommended_products_women_json = recommended_products_women.to_json(orient='records', force_ascii=False)
recommended_products_men_json = recommended_products_men.to_json(orient='records', force_ascii=False)
recommended_products_unisex_json = recommended_products_unisex.to_json(orient='records', force_ascii=False)

# 결과 출력
print("Women's Recommended Products (JSON):")
print(recommended_products_women_json)
print("\nMen's Recommended Products (JSON):")
print(recommended_products_men_json)
print("\nUnisex Recommended Products (JSON):")
print(recommended_products_unisex_json)


from django.http import JsonResponse

def learn(request):
    body = request.body.decode('utf-8')
    print("Request Body:", body)  # 디버깅용 출력

    # JSON 데이터 파싱
    data = json.loads(body)
    weather_info = data.get('weather_info')
    print("data" ,weather_info)
    # 요청에서 날씨 정보 가져오기
    # weather_info = request.GET.get('weather_info')  #일단 post로 했습니다.
    print(weather_info)
    # 예시 : weather_info = {'TMP': 28, 'PTY': 0, 'forecast_time': '09:00'} 이런식으로 들어와야 함

    # 세션에서 선택된 성별 가져오기
    g = request.session.get('selectedGender')

    # 성별에 따라 제품 추천
    if g == 'w':
        recommended_products = recommend_categories(weather_info, product_data, target_gender='w')
    elif g == 'm':
        recommended_products = recommend_categories(weather_info, product_data, target_gender='m')
    else:
        recommended_products = recommend_categories(weather_info, product_data, target_gender='unisex')

    # 추천 결과를 JSON으로 변환
    recommended_products_json = recommended_products.to_json(orient='records', force_ascii=False)

    # JSON 응답 반환
    return JsonResponse(recommended_products_json, safe=False)
