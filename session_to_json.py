import streamlit as st
import os
from PIL import Image
import google.genai as genai


st.set_page_config(
    page_title="Running session image to json",
    layout="wide",
    initial_sidebar_state="auto",
)

st.title("Running session image to json")

st.sidebar.header("Model Selection")
model = st.sidebar.selectbox("Model", ["gemini-3-flash-preview", "gemini-2.5-flash-lite"])
if model == "gemini-3-flash-preview":
    st.sidebar.info("you choose gemini-3-flash-preview, it's free")
elif model == "gemini-2.5-flash-lite":
    st.sidebar.info("you choose gemini-2.5-flash-lite, it's really cheap")



client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def classify_image(prompt, img_list, model):
    response = client.models.generate_content(
        model=model, 
        contents=[prompt] + img_list
    )
    return response.text



prompt = """
**Role:** Professional Running Data Analyst.
**Task:** Extract detailed running metrics from the provided images and organize them into a structured JSON.

**Image Sequence Guide:**
1. **First Image:** Overall summary (Distance, Time, Pace, Date, etc.).
2. **Second Image:** Heart rate analysis. 
   - **Note:** The Maximum Heart Rate (Max HR) value is specifically located in the **top-right corner of the heart rate graph.**
3. **Third Image onwards:** Detailed Split (Pace) charts. Each row typically contains KM, Pace, Average Heart Rate, and Cadence. Combine all pages into one sequential list.

**Extraction Requirements:**
- Extract numerical values only (omit units like 'km', 'bpm', 'spm').
- Maintain time formats: `HH:MM:SS` or `MM:SS`.
- **Splits Data:** For each kilometer, ensure you capture `pace`, `avg_hr`, and `cadence`.
- **Merge Logic:** If images overlap (e.g., KM 10 appears on both Image 3 and 4), merge them to ensure the `splits` list is unique and chronological.
- If a specific value (like cadence) is missing for a split, use `null`.

**Output Format (JSON):**
```json
{
  "summary": {
    "total_distance_km": 00.00,
    "total_time": "00:00:00",
    "average_pace": "0'00\"",
    "date": "YYYY-MM-DD"
  },
  "heart_rate_overall": {
    "average_bpm": 0,
    "max_bpm": 0,
    "zones_minutes": {
      "zone1": "mm:ss",
      "zone2": "mm:ss",
      "zone3": "mm:ss",
      "zone4": "mm:ss",
      "zone5": "mm:ss"
    }
  },
  "splits": [
    {
      "km": 1,
      "pace": "0'00\"",
      "avg_hr": 0,
      "cadence": 0
    },
    {
      "km": 2,
      "pace": "0'00\"",
      "avg_hr": 0,
      "cadence": 0
    }
  ]
}
"""

uploaded_images = st.file_uploader("러닝 세션 이미지 파일을 업로드해주세요", type=["jpg","jpeg","png"], accept_multiple_files=True)

if uploaded_images: # 파일이 업로드 되었을 때
    img_list = [Image.open(img) for img in uploaded_images]
    
    # 1. 이미지 개수만큼 컬럼을 생성합니다.
    cols = st.columns(len(img_list))
    
    # 2. 각 컬럼과 이미지를 매칭하여 출력합니다.
    for i, img in enumerate(img_list):
        with cols[i]:
            st.image(img, use_container_width=True)
    
    if st.button("Change to JSON"):
        with st.spinner("Now changing to JSON..."):
            result = classify_image(prompt, img_list, model=model)
        st.write(result)
