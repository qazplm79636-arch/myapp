import streamlit as st
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="팀 예산 관리 시스템", layout="wide")

# 2. Secrets 설정 확인
if "GAS_URL" not in st.secrets:
    st.error("오류: Streamlit Cloud Settings의 [Secrets]에 GAS_URL이 설정되지 않았습니다.")
    st.stop()

GAS_URL = st.secrets["GAS_URL"]

# 3. 데이터 가져오기 함수 (에러 처리 포함)
@st.cache_data(ttl=5)
def fetch_data():
    try:
        response = requests.get(GAS_URL, timeout=10)
        response.raise_for_status() # HTTP 에러 체크
        data = response.json()
        
        if not data: # 데이터가 빈 리스트인 경우
            return pd.DataFrame(columns=["date", "member", "month", "category", "amount"])
        
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류 발생: {e}")
        return pd.DataFrame()

# 4. 앱 메인 화면
st.title("📊 팀 예산 관리 시스템")

# 탭 구성
tab1, tab2 = st.tabs(["데이터 입력", "전체 대시보드"])

with tab1:
    st.subheader("📝 내역 입력")
    with st.form("budget_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        member = col1.selectbox("팀원 선택", ["부장님", "팀원1", "팀원2", "팀원3", "팀원4"])
        month = col2.text_input("해당 월 (예: 2026-07)")
        category = st.selectbox("예산 항목", ["수선유지비", "비품", "개량공사"])
        amount = st.number_input("사용 금액 (숫자만 입력)", min_value=0, step=1000)
        
        if st.form_submit_button("기록 저장하기"):
            if not month:
                st.warning("해당 월을 입력해주세요.")
            else:
                payload = {"member": member, "month": month, "category": category, "amount": amount}
                try:
                    res = requests.post(GAS_URL, json=payload, timeout=10)
                    if res.status_code == 200:
                        st.success("기록 완료! (새로고침을 눌러 확인하세요)")
                    else:
                        st.error(f"전송 실패: {res.status_code}")
                except Exception as e:
                    st.error(f"전송 에러: {e}")

with tab2:
    st.subheader("📂 데이터 대시보드")
    df = fetch_data()
    
    if not df.empty and "amount" in df.columns:
        # 지표 요약
        c1, c2, c3 = st.columns(3)
        c1.metric("전체 누적 사용액", f"{df['amount'].sum():,}원")
        c2.metric("전체 데이터 건수", f"{len(df)}건")
        
        # 차트
        st.markdown("---")
        st.write("### 항목별 예산 분포")
        st.bar_chart(df.groupby('category')['amount'].sum())
        
        # 테이블
        st.write("### 상세 내역")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("데이터가 없습니다. 첫 데이터를 입력해 보세요!")
