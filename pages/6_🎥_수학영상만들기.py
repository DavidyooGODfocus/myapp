import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import streamlit as st
from openai import OpenAI, OpenAIError


ROOT = Path(__file__).resolve().parents[1]
MODEL = "gpt-6-luna"
SYSTEM_PROMPT = """당신은 한국어 수학 애니메이션을 설계하는 교사입니다.
사용자의 요청을 3~8개의 짧은 장면으로 구성하세요. 코드를 작성하지 마세요.
다음 JSON 형식만 출력하세요.
{"title":"영상 제목", "steps":[{"kind":"text", "text":"장면 설명", "formula":"화면 중앙에 표시할 내용", "seconds":3}]}
kind는 text, equation, graph, shape 중 하나입니다.
모든 장면에는 text(한글 90자 이내), formula(80자 이내, 없으면 빈 문자열), seconds(1~6)가 필요합니다.
graph 장면에는 coefficients 배열을 추가하세요. 내림차순 다항식 계수이며 최대 4개, 각 값은 -20~20입니다.
예: y=x²는 [1,0,0], y=2x+1은 [2,1]입니다. 좌표 범위는 x,y 모두 -5~5입니다.
shape 장면에는 shape를 circle, square, triangle 중 하나로 추가하세요.
text와 equation 장면의 formula는 유니코드 일반 텍스트입니다. 예: x² + 2x + 1 = (x + 1)².
LaTeX, 마크다운, 실행 코드, 파일 경로를 사용하지 마세요.
이 기능은 자막과 도형으로 구성된 무음 영상입니다. 지원되는 장면으로 수학 개념을 정확하고 간결하게 설명하세요.
"""


def validate_plan(raw):
    plan = json.loads(raw)
    if not isinstance(plan, dict):
        raise ValueError("영상 구성이 올바른 JSON 객체가 아닙니다.")
    title = plan.get("title")
    steps = plan.get("steps")
    if not isinstance(title, str) or not title.strip() or len(title) > 100:
        raise ValueError("영상 제목이 올바르지 않습니다.")
    if not isinstance(steps, list) or not 1 <= len(steps) <= 8:
        raise ValueError("장면은 1~8개여야 합니다.")
    cleaned = []
    for step in steps:
        if not isinstance(step, dict) or step.get("kind") not in {"text", "equation", "graph", "shape"}:
            raise ValueError("지원하지 않는 장면입니다.")
        text, formula = step.get("text"), step.get("formula", "")
        seconds = step.get("seconds", 3)
        if not isinstance(text, str) or not text.strip() or len(text) > 180:
            raise ValueError("장면 설명은 1~180자여야 합니다.")
        if not isinstance(formula, str) or len(formula) > 120:
            raise ValueError("수식이 너무 길거나 올바르지 않습니다.")
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or not 1 <= seconds <= 6:
            raise ValueError("장면 길이는 1~6초여야 합니다.")
        item = {"kind": step["kind"], "text": text, "formula": formula, "seconds": seconds}
        if step["kind"] == "graph":
            coefficients = step.get("coefficients")
            if not isinstance(coefficients, list) or not 1 <= len(coefficients) <= 4:
                raise ValueError("그래프의 다항식 계수가 올바르지 않습니다.")
            if any(type(c) not in (int, float) or not math.isfinite(c) or abs(c) > 20 for c in coefficients):
                raise ValueError("그래프 계수는 -20~20 사이의 수여야 합니다.")
            item["coefficients"] = coefficients
        if step["kind"] == "shape":
            if step.get("shape") not in {"circle", "square", "triangle"}:
                raise ValueError("지원하지 않는 도형입니다.")
            item["shape"] = step["shape"]
        cleaned.append(item)
    return {"title": title, "steps": cleaned}


def render_video(plan):
    # 모델의 출력은 자료로만 읽고, 실행 파일은 프로젝트의 고정된 코드를 사용합니다.
    with tempfile.TemporaryDirectory(prefix="math_video_") as folder:
        work = Path(folder)
        shutil.copyfile(ROOT / "video_renderer" / "scene.py", work / "scene.py")
        (work / "scene.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        # 렌더링 프로세스에 API 키를 전달하지 않습니다.
        env = {k: v for k, v in os.environ.items() if not any(word in k.upper() for word in ("KEY", "SECRET", "TOKEN", "PASSWORD"))}
        command = [sys.executable, "-m", "manim", "-ql", "--format", "mp4", "--disable_caching",
                   "--media_dir", str(work / "media"), "-o", "math_video", str(work / "scene.py"), "MathVideo"]
        try:
            result = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=240)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("렌더링이 4분을 초과했습니다. 장면 수를 줄여 다시 생성해주세요.") from exc
        if result.returncode:
            raise RuntimeError("영상 렌더링에 실패했습니다.\n" + (result.stderr or result.stdout)[-6000:])
        videos = list((work / "media" / "videos").glob("**/math_video.mp4"))
        if not videos:
            raise RuntimeError("렌더링 결과에서 영상 파일을 찾지 못했습니다.")
        return videos[0].read_bytes()


st.title("🎥 수학 영상 만들기")
st.info("수학 개념을 입력하면 gpt-6-luna가 장면을 구성하고 Manim이 무음 영상을 만듭니다.")

if not st.session_state.get("학번"):
    st.warning("메인 화면에서 학번을 먼저 입력해주세요.")
    st.stop()

expected_code = st.secrets.get("SECRET_CODE", "")
if not expected_code:
    st.error("앱 Secrets에 SECRET_CODE를 설정해주세요.")
    st.stop()
if st.text_input("수업코드", type="password", key="math_video_class_code") != expected_code:
    st.info("수업코드를 입력해주세요.")
    st.stop()

api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("앱 Secrets에 OPENAI_API_KEY를 설정해주세요.")
    st.stop()

with st.form("math_video_form"):
    prompt = st.text_area("어떤 수학 영상을 만들까요?", placeholder="예: 일차함수 y=2x+1의 기울기와 y절편을 중학생에게 설명해주세요.", height=150, max_chars=2000)
    submitted = st.form_submit_button("영상 만들기", type="primary")

if submitted:
    if not prompt.strip():
        st.warning("영상으로 만들 내용을 입력해주세요.")
    else:
        try:
            with st.status("영상 장면을 구성하고 있습니다…", expanded=True) as status:
                with OpenAI(api_key=api_key, timeout=90, max_retries=1) as client:
                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt.strip()}],
                        response_format={"type": "json_object"},
                    )
                plan = validate_plan(response.choices[0].message.content or "")
                st.write(f"{len(plan['steps'])}개 장면을 렌더링하고 있습니다. 최대 4분 정도 걸릴 수 있습니다.")
                video = render_video(plan)
                st.session_state["math_video_result"] = {"video": video, "plan": plan}
                status.update(label="영상이 완성되었습니다.", state="complete", expanded=False)
        except OpenAIError as exc:
            st.error("모델 호출에 실패했습니다. API 키, 잔액, gpt-6-luna 모델 접근 권한을 확인해주세요.")
            with st.expander("오류 상세"):
                st.code(str(exc))
        except (ValueError, RuntimeError, OSError) as exc:
            st.error("영상을 생성하지 못했습니다.")
            with st.expander("오류 상세"):
                st.code(str(exc))

result = st.session_state.get("math_video_result")
if result:
    st.subheader(result["plan"]["title"])
    st.video(result["video"])
    st.download_button("영상 내려받기", result["video"], "math_video.mp4", "video/mp4")
    with st.expander("영상 구성 보기"):
        for number, step in enumerate(result["plan"]["steps"], 1):
            st.write(f"{number}. {step['text']}")
