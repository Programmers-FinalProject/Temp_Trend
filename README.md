# Temp_Trend

## 주제
날씨정보에 맞는 트렌디한 옷 추천 서비스

## 프로젝트 개요
### 1. 내용

본 프로젝트는 일별 기상 데이터와 뉴스 데이터를 수집하고, 대표적인 국내 온라인 셀렉트샵인 무신사와 29CM의 각 카테고리별 베스트 상품 데이터를 활용하여, 
날씨에 따른 카테고리 추천 모델을 구축하였습니다. 
이를 통해 사용자에게 현재 날씨와 관련된 인기 상품을 추천함으로써, 사용자에게 날씨와 가장 연관된 아이템 정보를 제공하고, 궁극적으로 쇼핑 경험을 개선하고자 하였습니다.

### 2. 기간

2024.07.22 ~ 2024.08.16

### 3. 활용데이터

| Source | Data                        | Link                                                                                      |
|--------|-----------------------------|-------------------------------------------------------------------------------------------|
| 29CM   | ProductName,Category,Price,Rank,Gender,...| [29CM](https://shop.29cm.co.kr/best-items?category_large_code=268100100)   |
| Musinsa   | ProductName,Category,Price,Rank,Gender,...| [Musinsa](https://www.musinsa.com/main/)   |
| 전국날씨 | Date,WeatherCode,fcstdate,fcsttime,fcstvalue,nx,ny| [공공데이터포털](https://www.data.go.kr/data/15084084/openapi.do)   |
| 기상뉴스 | id,Title,Description,Link,Pubdate,imageURL| [네이버뉴스](https://developers.naver.com/docs/serviceapi/search/news/news.md)   |

### 4. 활용기술 및 프레임워크

| 분류                | 기술                                          |
|---------------------|-----------------------------------------------|
| 프로그래밍언어       |<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white">  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=JavaScript&logoColor=white"> |
| 웹 프레임워크        |<img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=Django&logoColor=white"> |
| 데이터베이스         |<img src="https://img.shields.io/badge/Postgres-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=Redis&logoColor=white">  <img src="https://img.shields.io/badge/Redshift-8C4FFF?style=for-the-badge&logo=amazonredshift&logoColor=white">|
| 클라우드 서비스      | <img src="https://img.shields.io/badge/EC2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white">  <img src="https://img.shields.io/badge/RDS-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white">  <img src="https://img.shields.io/badge/Redshift-8C4FFF?style=for-the-badge&logo=amazonredshift&logoColor=white">  <img src="https://img.shields.io/badge/Lambda-FF9900?style=for-the-badge&logo=awslambda&logoColor=white">  <img src="https://img.shields.io/badge/EventBridge-232F3E?style=for-the-badge&logo=amazonwebservices&logoColor=white">  <img src="https://img.shields.io/badge/Glue-232F3E?style=for-the-badge&logo=amazonwebservices&logoColor=white">  <img src="https://img.shields.io/badge/GCP-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white">  |
| 데이터 파이프라인    |<img src="https://img.shields.io/badge/Airflow-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white"> |
| 버전 관리            |<img src="https://img.shields.io/badge/Github-181717?style=for-the-badge&logo=apacheairflow&logoColor=white">  <img src="https://img.shields.io/badge/GitActions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white">|

### 5. 프로젝트 보고서

[Temp_Trend PPT 보러가기](https://www.canva.com/design/DAGNoDAbJ6s/zMFla5cpJsxTEQtNYdDiLA/edit)

### 6. 팀원 및 역할

| 이름 | 역할                        | 기여도                                                                                      |
|--------|-----------------------------|-------------------------------------------------------------------------------------------|
| 안재영 | 전국 기상데이터 수집, 웹페이지 구현-기상데이터                      |   25%        |
| 이정화 | 날씨 관련 뉴스 데이터 수집, CI/CD 관리, Django 배포 및 환경구성                      |   25%        |
| 박도윤 | 패션 데이터 수집 - 무신사, 웹페이지 구현-패션데이터                      |   25%        |
| 이하영 | 패션 데이터 수집 - 29CM, AWS 인프라 구축 및 관리                      |   25%        |

## 프로젝트 세부결과
### 1. 아키텍쳐
![Architecture](img/temp_trend_arch.png)

### 2. 구현

- 메인 페이지 구성
![MainPage](img/web_main.png)

- 날씨와 성별에 따른 추천 아이템 목록
![ManRecommend](img/man_recommend.png)
![WomenRecommend](img/women_recommend.png)

- 시연영상 <br>
![60초풀영상](https://github.com/user-attachments/assets/4874d5b7-13f2-4007-8fa7-091a674dd508)
