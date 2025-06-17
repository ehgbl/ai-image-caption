
import streamlit as st
import os
import tempfile
from pathlib import Path
import mimetypes

from google import genai
from google.genai import types
from google.api_core import exceptions as core_exc

def run_upload_page():
    st.markdown(
        """
        <style>
          /* Page header */
          .title { color: #3730A3; font-size: 2.5rem; font-weight: bold; text-align: center; }
          .subtitle { color: #4C51BF; font-size: 1.2rem; text-align: center; }
          [data-testid="stSidebar"] > div:first-child { background-color: #5C6AC4; padding: 1rem; }
          [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label { color: white !important; }
          footer, header { visibility: hidden; }
          .stButton > button:hover { background-color: #4C51BF !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="title">Image Caption Generator</h1>',
        unsafe_allow_html=True,
    )
    st.markdown('<h2 class="subtitle">Upload your images below and get AI-powered captions</h2>',
                unsafe_allow_html=True)

    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("API Key", type="password")
        caption_mode = st.selectbox(
            "Caption Length",
            ["short (≤125 chars)", "detailed"],
            help="WCAG recommends alt-text ≤125 characters",
        )

    if not api_key:
        st.warning("Please enter your API Key.")
        st.stop()
   
    try:
        client = genai.Client(api_key=api_key)
        client.models.list()
        
    except core_exc.Unauthenticated:
        st.error("Use correct API key has access to the GenAI API.")
        st.stop()
    except core_exc.PermissionDenied:
        st.error("Permission denied. Ensure your API key has access to the GenAI API.")
        st.stop()
    except core_exc.InvalidArgument as e:
        msg = str(e)
        if "API_KEY_INVALID" in msg:
            st.error("Invalid API Key. Please use a valid key with access to the Generative Language API.")
        else:
            st.error(f"Bad request: {msg}")
        st.stop()
    except Exception as e:
        st.error(f"Error connecting to GenAI API: {str(e)}")
        st.stop()
    st.success("API Key validated successfully!")

    st.subheader("Upload Image(s)")
    uploaded_files = st.file_uploader(
        "Choose JPG/PNG files…",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
    )
    if not uploaded_files:
        st.info("📁 Please upload at least one image.")
        st.stop()

    st.success(f"📂 Uploaded {len(uploaded_files)} image(s)")

    mimetypes.add_type("image/jpeg", ".jpg")
    mimetypes.add_type("image/png", ".png")
    cols = st.columns(min(len(uploaded_files), 4))
    for idx, img in enumerate(uploaded_files):
        with cols[idx % 4]:
            st.image(img, caption=img.name, width=150)

    if not st.button("Generate Captions", type="primary"):
        st.stop()

    st.info("🤖 Generating captions…")
    client = genai.Client(api_key=api_key)
    max_tokens = 40 if caption_mode.startswith("short") else 80
    config = types.GenerateContentConfig(
        temperature=0.7,
        candidate_count=1,
        max_output_tokens=max_tokens,
    )

    for uploaded_file in uploaded_files:
        # write to temp file so genai can read it
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        file_resp = client.files.upload(file=tmp_path)

        base_prompt = [
            "Generate exactly one descriptive caption for this image in a single sentence.",
            file_resp,
        ]
        alt_prompt = [
            "Write one alternate caption for the same image, also in a single sentence.",
            file_resp,
        ]

        main_out = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=base_prompt,
            config=config,
        )
        alt_out = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=alt_prompt,
            config=config,
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Caption for {uploaded_file.name}:**")
            st.write(main_out.text.strip())
        with c2:
            st.markdown("**Alternative Caption:**")
            st.write(alt_out.text.strip())

        st.divider()
        os.unlink(tmp_path)

    st.success("✅ Done!")
