import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# Python 3.12+ no longer includes distutils. koreanize-matplotlib still imports
# LooseVersion from it, so provide the compatible implementation bundled by setuptools.
import sys
import types
from setuptools._distutils.version import LooseVersion

distutils = types.ModuleType("distutils")
distutils_version = types.ModuleType("distutils.version")
distutils_version.LooseVersion = LooseVersion
distutils.version = distutils_version
sys.modules.setdefault("distutils", distutils)
sys.modules.setdefault("distutils.version", distutils_version)
import koreanize_matplotlib
plt.rcParams["font.family"] = ["NanumGothic", "AppleGothic", "Malgun Gothic"]

from urllib.parse import quote # 한글 탭 이름을 주소에 넣을 수 있게 바꾸는 함수

st.title("두 반의 통학시간 비교하기")
st.info("구글시트와 연동하여 통학시간 자료를 반별 상자그림으로 나타내기")

sheet_id = "14r7sB9Eb3xenskK7af2D3h9Drwf7lzWuMUT7fJiiJNc"
tab = "측정자료"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&headers=1&sheet={quote(tab)}"
df = pd.read_csv(url)

with st.expander("자료 보기"):
    # st.write(df)
    st.dataframe(df[["반", "통학 시간(분)"]], hide_index = True)

fig, ax = plt.subplots(figsize = (8, 3))
sns.boxplot(data = df, x = "통학 시간(분)", y = "반", 
ax = ax, whis = (0, 100)) # whis 옵션 : 교과서 참고
st.pyplot(fig)
