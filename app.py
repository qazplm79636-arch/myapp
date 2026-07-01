import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="팀 예산 관리 시스템", layout="wide")
GAS_URL = st.secrets["GAS_URL"]

st.title("📊 팀 예산 관리 시스템")

# 1. 데이터 가져오기
@st.cache_data(ttl=10)
def fetch_data():
    res = requests.get(GAS_URL)
    return pd.DataFrame(res.json())

df = fetch_data()

# 2. 탭 구성
tab1, tab2 = st.tabs(["데이터 입력", "전체 대시보드"])

with tab1:
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        member = col1.selectbox("팀원", ["부장님", "팀원1", "팀원2", "팀원3", "팀원4"])
        month = col2.text_input("해당 월 (YYYY-MM)", placeholder="2026-07")
        category = st.selectbox("항목", ["수선유지비", "비품", "개량공사"])
        amount = st.number_input("금액", min_value=0)
        
        if st.form_submit_button("기록 저장하기"):
            payload = {"member": member, "month": month, "category": category, "amount": amount}
            requests.post(GAS_URL, json=payload)
            st.success("저장 완료! 새로고침하여 확인하세요.")

with tab2:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("누적 사용액", f"{df['amount'].sum():,}원")
        c2.metric("전체 건수", f"{len(df)}건")
        
        st.subheader("항목별 분포")
        st.bar_chart(df.groupby('category')['amount'].sum())
        
        st.subheader("월별/항목별 요약")
        st.dataframe(df.pivot_table(index='month', columns='category', values='amount', aggfunc='sum', fill_value=0))
