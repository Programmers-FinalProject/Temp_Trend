import json
from django.shortcuts import redirect, render
import pandas as pd
import random
from django.http import HttpResponse, JsonResponse
import boto3
import io
from io import BytesIO, StringIO
from botocore.exceptions import NoCredentialsError
import pytz
from datetime import datetime
import joblib
#import tempfile

#def load_model_from_s3(bucket_name, s3_key):
#    s3 = boto3.client('s3')
    
#    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#        s3.download_fileobj(bucket_name, s3_key, temp_file)
#        temp_file_path = temp_file.name

#    model = joblib.load(temp_file_path)
#    return model

# S3 경로
#bucket_name = 'team-hori-1-bucket'
#s3_key = 'learning_model/model/model.joblib'

# 모델 로드
#model = load_model_from_s3(bucket_name, s3_key)

def is_model_trained(model):
    if isinstance(model, RandomForestClassifier):
        return hasattr(model, 'n_features_in_')
    # 다른 모델 유형에 대한 검사를 추가할 수 있습니다
    return False

"""#모델검사
model = joblib.load('path/to/your/model.joblib')
if is_model_trained(model):
    print("Model has been trained.")
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
    print("Model has not been trained yet.")
"""
def get_korea_time():
    korea_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(korea_tz)

def save_to_s3(dataframe, file_name):
    # S3 클라이언트 생성
    s3_client = boto3.client('s3')
    
    # DataFrame을 CSV로 변환
    csv_buffer = io.StringIO()
    dataframe.to_csv(csv_buffer, index=False)
    
    # S3에 업로드
    try:
        s3_client.put_object(Bucket="team-hori-1-bucket", Key=f"learning_model/file/{file_name}", Body=csv_buffer.getvalue())
        print(f"Successfully uploaded {file_name} to hori-1")
        return True
    except NoCredentialsError:
        print("Credentials not available")
        return False

def save_model_metadata(bucket, key, accuracy):
    s3 = boto3.client('s3')
    metadata = {
        'trained': True,
        'accuracy': float(accuracy),  # 확실하게 float로 변환
        'training_date': get_korea_time().isoformat()
    }
    try:
        s3.put_object(Body=json.dumps(metadata), Bucket=bucket, Key=key)
        print(f"Metadata successfully saved to {bucket}/{key}")
    except Exception as e:
        print(f"Error saving metadata: {str(e)}")
        

def save_model_to_s3(model, bucket, key):
    s3 = boto3.client('s3')
    buffer = BytesIO()
    joblib.dump(model, buffer)
    s3.put_object(Body=buffer.getvalue(), Bucket=bucket, Key=key)


from weather.models import musinsaData
# Redshift 데이터베이스에서 데이터 쿼리
data = musinsaData.objects.using('redshift').all()

# 특정 필드만 선택하여 둘의 유니크한 DataFrame 생성
d = categories_and_genders = musinsaData.objects.using('redshift').values_list('category', 'gender').distinct()
df = pd.DataFrame(d, columns=['category', 'gender'])
# 모든 필드를 포함한 DataFrame 생성
df2 = pd.DataFrame(data.values_list(), columns=[field.name for field in musinsaData._meta.fields])

# DataFrame에서 'category'와 'gender' 열이 있는지 확인
if 'category' in df.columns and 'gender' in df.columns:
    # 결과 출력
    print("Unique CATEGORY and GENDER combinations:")
    print(df)
else:
    raise ValueError("DataFrame에 'category' 또는 'gender' 열이 없습니다.")

# 결과 리스트 출력
print("\nUnique combinations as a list:")
for combination in d:
    print(combination)

# 카테고리 분류
def classify_category(category):
    if category in [
        '반소매 티셔츠', '셔츠/블라우스', '피케/카라 티셔츠', '후드 티셔츠', '맨투맨/ 스웨트셔츠',
        '니트/스웨터', '긴소매 티셔츠', '스포츠 상의', '민소매 티셔츠', '슈트/ 블레이저 재킷',
        '레더/ 라이더스 재킷', '트레이닝 재킷', '겨울 기타 코트', '나일론/ 코치 재킷', '겨울 싱글 코트',
        '숏패딩/ 숏헤비 아우터', '블루종/ MA-1', '트러커 재킷', '패딩 베스트', '아노락 재킷',
        '사파리/ 헌팅 재킷', '겨울 더블 코트', '카디건', '스타디움 재킷', '롱패딩/ 롱헤비 아우터',
        '베스트', '후드 집업', '환절기 코트', '플리스/뽀글이', '무스탕/퍼','미니 원피스','맥시 원피스'
    ]:
        return '상의'
    elif category in [
        '데님 팬츠', '트레이닝/조거 팬츠', '숏 팬츠', '코튼 팬츠', '스포츠 하의',
        '슈트 팬츠/슬랙스', '레깅스','미디스커트','미니스커트','롱스커트'
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
categorized_list = [[classify_category(category), category, gender] for category, gender in d]

# 결과 출력
df = pd.DataFrame(categorized_list, columns=['category1', 'category2', 'gender'])
print(df)


from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import numpy as np

def generate_weather_data(num_samples):
    # 무작위 날씨 데이터 생성
    weather_data = []
    for _ in range(num_samples):
        temp = random.randint(-20, 30)  # 온도 생성
        temp = (np.floor((temp + 1) / 2) * 2).astype(int)
        if temp < -2:
            possible_pty = [0, 3]  # 0: 없음, 3: 눈
        elif -2 <= temp <0:
            possible_pty = [0, 2, 3]       
        elif 0 < temp < 6:
            possible_pty = [0, 1, 2, 3]  # 0: 없음, 2: 비/눈, 3: 눈
        else:  # temp >= 5
            possible_pty = [0, 1, 4]  # 0: 없음, 1:비, 4: 소나기
            
        pty = random.choice(possible_pty)
    
        weather_data.append({'TMP': temp, 'PTY': pty})
    return pd.DataFrame(weather_data)

# 학습 데이터 리스트
matched_data_list = []

# 인덱스를 기억하기 위한 변수
current_index = 0

BATCH_SIZE = 10  

def index(request):
    global current_index, matched_data_list, BATCH_SIZE
    num_samples = len(df)

    # 최초 시작 시 날씨 데이터 생성 및 매칭
    if current_index == 0:
        weather_data = generate_weather_data(num_samples)
        global matched_data
        matched_data = pd.concat([weather_data, df.sample(n=num_samples, replace=False).reset_index(drop=True)], axis=1)

    # 현재 인덱스의 데이터를 가져오기
    if current_index < len(matched_data):
        current_data = matched_data.iloc[current_index]
        original_df2 = df2.copy()
        filtered_df2 = original_df2[original_df2['category'] == current_data['category2']]
        filtered_df2 = filtered_df2[filtered_df2['gender'] == current_data['gender']]
    else:
        # 모든 데이터를 처리했을 경우
        return HttpResponse("모든 데이터의 선호도 입력이 완료되었습니다.")

    # 사용자 선호도 받기
    if request.method == 'POST':
        preference = int(request.POST.get('preference'))
        matched_data_list.append({**current_data.to_dict(), 'preference': preference})
        current_index += 1
        # 10개의 데이터가 모이면 S3에 저장
        if len(matched_data_list) >= BATCH_SIZE:
            ko = get_korea_time()
            batch_data = pd.DataFrame(matched_data_list)
            file_name = f'learning_data_batch_{ko.strftime("%Y%m%d_%H%M%S")}.csv'
            if save_to_s3(batch_data, file_name):
                print(f"Batch of {BATCH_SIZE} samples saved to S3")
                matched_data_list.clear()  # 저장한 데이터 클리어
            else:
                print("Failed to save batch to S3")

        # 모든 데이터에 대해 선호도를 입력받은 경우
        if current_index >= num_samples:
            # 남은 데이터가 있다면 마지막으로 저장
            if matched_data_list:
                ko = get_korea_time()
                final_batch = pd.DataFrame(matched_data_list)
                file_name = f'learning_data_final_{ko.strftime("%Y%m%d_%H%M%S")}.csv'
                save_to_s3(final_batch, file_name)

        # 모든 데이터에 대해 선호도를 입력받은 경우
        if current_index >= num_samples:
            # 선호도 입력 완료 시, 학습 데이터 생성 및 초기화
            global learning_data
            ko = get_korea_time()
            learning_data = pd.DataFrame(matched_data_list)
            file_name = f'learning_data_{ko.strftime("%Y%m%d_%H%M%S")}.csv'
            if save_to_s3(learning_data, file_name):
                # 초기화
                current_index = 0
                matched_data_list.clear()
                return HttpResponse("선호도 입력이 완료되었습니다. 학습 데이터가 S3에 저장되었습니다.")

        # 다음 데이터로 이동
        return redirect('index_learn')
    
    

    context = {
        'products': filtered_df2.to_dict(orient='records'),
        'current_index' : current_index,
        'num_samples' : num_samples,
        'TMP': current_data['TMP'],
        'PTY': get_pty_description(current_data['PTY']),
        'category1': current_data['category1'],
        'category2': current_data['category2'],
        'gender': current_data['gender'],
    } 

    return render(request, 'learning.html', context)

def get_pty_description(pty_code):
    pty_descriptions = {
        0: "없음",
        1: "비",
        2: "비/눈",
        3: "눈",
        4: "소나기"
    }
    return pty_descriptions.get(pty_code, "알 수 없음")

import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def encode_categorical_data(data, categorical_columns):
    """
    범주형 열을 OneHotEncoder를 사용하여 인코딩합니다.
    
    매개변수:
    data (DataFrame): 데이터를 포함하는 DataFrame.
    categorical_columns (list): 인코딩할 열의 이름 목록.
    
    반환값:
    DataFrame: 원-핫 인코딩된 열이 포함된 DataFrame.
    """
    encoder = OneHotEncoder(sparse_output=False)
    encoded_features = encoder.fit_transform(data[categorical_columns])
    encoded_features_df = pd.DataFrame(encoded_features, columns=encoder.get_feature_names_out(categorical_columns))
    return encoded_features_df

def preprocess_data(learning_data):
    """
    학습 데이터를 전처리하여 범주형 데이터 인코딩 및 결측값 처리를 수행합니다.
    
    매개변수:
    learning_data (DataFrame): 학습 데이터를 포함하는 DataFrame.
    
    반환값:
    DataFrame, Series: 특성 DataFrame과 대상 Series.
    """
    # 인코딩할 열 목록
    categorical_columns = ['category1', 'category2', 'gender']
    
    # 범주형 데이터 인코딩
    encoded_features_df = encode_categorical_data(learning_data, categorical_columns)
    
    # 인코딩된 데이터 통합
    learning_data_encoded = pd.concat([learning_data.drop(categorical_columns, axis=1), encoded_features_df], axis=1)
# 예시 제품 데이터: 각 카테고리별
product_data = df

# 24시간의 시간대 생성
hours = [f"{i:02d}:00" for i in range(24)]

# 임의의 온도 데이터 생성 (10도에서 30도 사이)
temperatures = np.random.randint(10, 31, 24)

# 임의의 강수 형태 데이터 생성 (0: 없음, 1: 비, 2: 진눈깨비, 3: 눈)
precipitation_types = np.random.choice([0, 1, 2, 3], 24, p=[0.7, 0.2, 0.05, 0.05])

# 데이터프레임 생성
weather_data = pd.DataFrame({
    'forecast_time': hours,
    'TMP': temperatures,
    'PTY': precipitation_types
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
    X_imputed = imputer.fit_transform(learning_data_encoded.drop(['preference'], axis=1))

    # 특성과 레이블 준비
    X = pd.DataFrame(X_imputed, columns=learning_data_encoded.drop(['preference'], axis=1).columns)
    y = learning_data_encoded['preference']
    
    return X, y

def split_data(X, y, test_size=0.2, random_state=42):
    """
    데이터를 학습 및 테스트 세트로 분할합니다.
    
    매개변수:
    X (DataFrame): 특성 DataFrame.
    y (Series): 대상 Series.
    test_size (float): 테스트 분할에 포함할 데이터셋의 비율.
    random_state (int): 재현성을 위한 랜덤 상태.
    
    반환값:
    DataFrame, DataFrame, Series, Series: 학습 및 테스트 특성과 대상.
    """
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

def build_pipeline():
    """
    스케일링 및 RandomForestClassifier를 포함하는 머신 러닝 파이프라인을 구성합니다.
    
    반환값:
    Pipeline: 머신 러닝 파이프라인.
    """
    return Pipeline([
        ('scaler', StandardScaler()),
        ('model', RandomForestClassifier(random_state=42))
    ])

def train_model(X_train, y_train, pipeline):
    """
    제공된 학습 데이터와 파이프라인을 사용하여 모델을 학습시킵니다.
    
    매개변수:
    X_train (DataFrame): 학습 특성.
    y_train (Series): 학습 대상.
    pipeline (Pipeline): 머신 러닝 파이프라인.
    
    반환값:
    Pipeline: 학습된 파이프라인.
    """
    pipeline.fit(X_train, y_train)
    return pipeline

def evaluate_model(X_test, y_test, pipeline):
    """
    테스트 데이터를 사용하여 학습된 모델을 평가합니다.
    
    매개변수:
    X_test (DataFrame): 테스트 특성.
    y_test (Series): 테스트 대상.
    pipeline (Pipeline): 학습된 파이프라인.
    
    반환값:
    float: 테스트 데이터에 대한 모델의 정확도.
    """
    y_pred = pipeline.predict(X_test)
    return accuracy_score(y_test, y_pred)

def main(learning_data):
    # 데이터 전처리
    X, y = preprocess_data(learning_data)
    
    # 데이터 분할
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # 파이프라인 구성
    pipeline = build_pipeline()
    
    # 모델 학습
    trained_pipeline = train_model(X_train, y_train, pipeline)
    
    # 모델 평가
    accuracy = evaluate_model(X_test, y_test, trained_pipeline)
    
    # 메타데이터 저장
    timestamp = get_korea_time().strftime("%Y%m%d_%H%M%S")
    metadata_key = f'learning_model/model/model_metadata_{timestamp}_{accuracy:.4f}.json'
    save_model_metadata('team-hori-1-bucket', metadata_key, accuracy)
    
    print(f"Model Accuracy: {accuracy:.4f}")
    
    # 학습에 사용한 인코더 및 임퓨터 준비
    encoder = OneHotEncoder(sparse_output=False)
    encoder.fit(learning_data[['category1', 'category2', 'gender']])
    
    imputer = SimpleImputer(strategy='mean')
    imputer.fit(X)
    
    # 모델 저장
    model_key = f'learning_model/model/trained_model_{timestamp}.joblib'
    save_model_to_s3(trained_pipeline, 'team-hori-1-bucket', model_key)
    
    encoder_key = f'learning_model/model/encoder_{timestamp}.joblib'
    save_model_to_s3(encoder, 'team-hori-1-bucket', encoder_key)
    
    imputer_key = f'learning_model/model/imputer_{timestamp}.joblib'
    save_model_to_s3(imputer, 'team-hori-1-bucket', imputer_key)
    
    print(f"Model and associated objects saved to S3 with timestamp: {timestamp}")
    
    return trained_pipeline, encoder, imputer, X

def recommend_categories(weather_info, product_df, target_gender, pipeline, encoder, imputer, X):
    """
    주어진 날씨 정보와 성별에 맞는 제품을 추천합니다.

    매개변수:
    weather_info (dict): 날씨 정보를 담고 있는 딕셔너리 {'TMP': int, 'PTY': int}
    product_df (DataFrame): 추천할 제품 정보가 담긴 데이터프레임
    target_gender (str): 대상 성별 ('w', 'm', 'unisex')
    pipeline (Pipeline): 학습된 머신 러닝 모델 파이프라인
    encoder (OneHotEncoder): 학습된 인코더
    imputer (SimpleImputer): 학습된 결측값 처리기
    X (DataFrame): 학습 데이터의 특성 (모델 훈련에 사용된 특성)

    반환값:
    DataFrame: 추천 제품 리스트
    """
    try:
        # 날씨 정보와 제품 데이터 결합
        original_dict = weather_info
        keys_to_keep = ['TMP', 'PTY']
        weather_info = {k: original_dict[k] for k in keys_to_keep if k in original_dict}
        weather_df = pd.DataFrame([weather_info])
        combined_df = weather_df.loc[weather_df.index.repeat(len(product_df))].reset_index(drop=True)
        combined_df = pd.concat([combined_df, product_df], axis=1)

        # 범주형 데이터 인코딩
        encoded_combined = encoder.transform(combined_df[['category1', 'category2', 'gender']])
        encoded_combined_df = pd.DataFrame(encoded_combined, columns=encoder.get_feature_names_out(['category1', 'category2', 'gender']))

        # 인코딩된 데이터 통합
        combined_df_encoded = pd.concat([combined_df.drop(['category1', 'category2', 'gender'], axis=1), encoded_combined_df], axis=1)

        # 결측값 처리
        combined_df_imputed = imputer.transform(combined_df_encoded)
        combined_df_imputed = pd.DataFrame(combined_df_imputed, columns=combined_df_encoded.columns)
        combined_df_imputed = combined_df_imputed[X.columns]  # 학습 데이터의 열과 맞추기

        # 모델을 사용하여 예측
        predictions = pipeline.predict(combined_df_imputed)
        
        # 추천 제품 필터링 (예: 선호도가 2 이상인 제품만 추천)
        recommended_products = combined_df[np.array(predictions) >= 1]
        
        # 성별에 따라 필터링
        if target_gender == 'unisex':
            recommended_products = recommended_products[recommended_products['gender'] == 'unisex']
        else:
            recommended_products = recommended_products[(recommended_products['gender'] == target_gender) | (recommended_products['gender'] == 'unisex')]
        
        # 각 카테고리에서 3개씩 추천
        categories = ['상의', '하의', '신발', '아이템']
        final_recommendations = pd.DataFrame()

        for category in categories:
            category_recommendations = recommended_products[recommended_products['category1'] == category].head(3)
            final_recommendations = pd.concat([final_recommendations, category_recommendations], ignore_index=True)
        
        # 최종 추천 제품
        recommended_products_musinsa = final_recommendations[['category1', 'category2', 'gender']].copy()
        recommended_products_musinsa.rename(columns={'category1': 'category'}, inplace=True)

        return recommended_products_musinsa , "ok"
    
    except ValueError as e:
        print(f"Error during recommendation: {e}")
        # 에러 메시지에서 학습되지 않은 카테고리를 추출
        unknown_categories = set(str(e).split('[')[1].split(']')[0].replace("'", "").split(', '))
        print("Untrained categories:", unknown_categories)
        # 학습되지 않은 카테고리를 데이터프레임에서 필터링
        return df[df['category2'].isin(unknown_categories)] , "retry"

# 예시 날씨 정보
# weather_info = {'TMP': 28, 'PTY': 0}

# 제품 데이터 로드


#product_df = pd.DataFrame({
#    'category1': ['상의', '하의', '신발', '악세사리'] * 25,
#    'category2': ['반소매 티셔츠', '청바지', '운동화', '시계'] * 25,
#    'gender': ['w', 'm', 'unisex'] * 33 + ['w']
#})


#trained_pipeline,encoder,imputer,X = main(learning_data)
# 예시 추천 함수 호출
#recommended_products = recommend_categories(weather_info, df, target_gender='w', pipeline=trained_pipeline, encoder=encoder, imputer=imputer, X=X)
#print("추천 제품 목록:")
#print(recommended_products)

    


# 추천 결과 생성
#weather_info = {'TMP': 28, 'PTY': 0}
# 각 성별에 대한 추천
#recommended_products_women = recommend_categories(weather_info, product_data, target_gender='w')
#recommended_products_men = recommend_categories(weather_info, product_data, target_gender='m')
#recommended_products_unisex = recommend_categories(weather_info, product_data, target_gender='unisex')
# 추천 결과를 JSON으로 변환
#recommended_products_women_json = recommended_products_women.to_json(orient='records', force_ascii=False)
#recommended_products_men_json = recommended_products_men.to_json(orient='records', force_ascii=False)
#recommended_products_unisex_json = recommended_products_unisex.to_json(orient='records', force_ascii=False)

# 결과 출력
#print("Women's Recommended Products (JSON):")
#print(recommended_products_women_json)
#print("\nMen's Recommended Products (JSON):")
#print(recommended_products_men_json)
#print("\nUnisex Recommended Products (JSON):")
#print(recommended_products_unisex_json)



def learn(request):
    body = request.body.decode('utf-8')
    print("Request Body:", body)  # 디버깅용 출력

    # JSON 데이터 파싱
    data = json.loads(body)
    weather_info = data.get('weather_info')
    print("data" ,weather_info)
    # 요청에서 날씨 정보 가져오기
    #data = json.loads(request.body)
    #weather_info = data.get('weather_info', {})
    weather_info = {'TMP': 28, 'PTY': 0, 'forecast_time': '09:00'}
    weather_info["TMP"] = (np.floor((weather_info["TMP"] + 1) / 2) * 2).astype(int)
    a = ""
    # weather_info = request.GET.get('weather_info')  #일단 post로 했습니다.
    print(weather_info)
    # 예시 : weather_info = {'TMP': 28, 'PTY': 0, 'forecast_time': '09:00'} 이런식으로 들어와야 함

    # 세션에서 선택된 성별 가져오기
    g = request.session.get('selectedGender')
    bucket_name = 'team-hori-1-bucket'
    learning_data = concatenate_csv_files_from_s3(bucket_name)
    if learning_data is not None and weather_info:     
        trained_pipeline,encoder,imputer,X = main(learning_data)

    # 성별에 따라 제품 추천
    if g == 'w':
        recommended_products , a = recommend_categories(weather_info, df, target_gender='w',pipeline=trained_pipeline, encoder=encoder, imputer=imputer, X=X)
    elif g == 'm':
        recommended_products, a = recommend_categories(weather_info, df, target_gender='m',pipeline=trained_pipeline, encoder=encoder, imputer=imputer, X=X)
    else:
        recommended_products, a = recommend_categories(weather_info, df, target_gender='unisex',pipeline=trained_pipeline, encoder=encoder, imputer=imputer, X=X)

    # DataFrame을 딕셔너리 리스트로 변환
    recommended_products = recommended_products.to_dict(orient='records')

    context = {
        'a' : a,
        'recommended_products' : recommended_products,
    }

    # JSON 응답 반환
    return JsonResponse(context)

'''
import pandas as pd
import pandas as pd
import boto3
from io import StringIO
from datetime import datetime
import pytz

# boto3 클라이언트 생성 (자격 증명 자동 사용)
s3_client = boto3.client('s3', region_name='ap-northeast-2')

seoul_tz = pytz.timezone('Asia/Seoul')
seoul_now = datetime.now(seoul_tz) #시간
today = seoul_now.strftime("%Y%m월%d일") #날짜

today = 20240811 #아직 현재 날짜거가 없어서..

bucket_name = 'team-hori-1-bucket'
file_key = f'crawling/29cm_bestitem_{today}.csv'
try:
    # S3에서 객체 가져오기
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    # 객체의 Body에서 내용을 읽어오기
    csv_content = response['Body'].read().decode('utf-8')

    # CSV 내용으로부터 DataFrame 생성
    df = pd.read_csv(StringIO(csv_content))
    df = df[['category1', 'category2', 'category3', 'gender']]
    df = df.drop_duplicates(subset=['category1', 'category2', 'category3', 'gender'])

    print("CSV 파일을 성공적으로 읽어왔습니다.")
    print(df.head())
except Exception as e:
    print(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")'''
    
    
import boto3
import pandas as pd
import re
from io import StringIO

def concatenate_csv_files_from_s3(bucket_name, prefix='learning_model/file/'):
    # S3 클라이언트 초기화
    s3 = boto3.client('s3')
    
    # S3 버킷의 객체를 나열하기 위한 페이지네이터
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    
    # 파일 이름이 'learning_data'로 시작하고 '.csv'로 끝나는 패턴 정의
    pattern = re.compile(r'learning_data.*\.csv$')
    
    # 데이터프레임을 저장할 리스트
    dataframes = []
    
    # 페이지를 통해 객체 검색
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                key = obj['Key']
                # 디버깅: 각 키 출력
                print(f"Checking key: {key}")
                # 파일이 패턴과 일치하는지 확인
                if pattern.search(key.split('/')[-1]):  # key에서 파일명만 추출하여 매칭
                    try:
                        # 파일 내용 읽기
                        response = s3.get_object(Bucket=bucket_name, Key=key)
                        content = response['Body'].read().decode('utf-8')
                        df = pd.read_csv(StringIO(content))
                        dataframes.append(df)
                        print(f"Read file: {key}")
                    except Exception as e:
                        print(f"Failed to read {key}: {e}")

    if not dataframes:
        print("No matching CSV files found.")
        return None
                    
    # 모든 데이터프레임 연결
    combined_df = pd.concat(dataframes, ignore_index=True)
    print(f"Combined {len(dataframes)} files into a single DataFrame.")
    
    return combined_df