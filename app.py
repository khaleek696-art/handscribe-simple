# =============================================================
#   app.py  —  Handwriting to Text Converter
#   Engine  : EasyOCR
#   UI      : Streamlit
#   Run     : streamlit run app.py
# =============================================================

import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import easyocr
import pytesseract
import numpy as np

# ── Page config  (must be first Streamlit call) ──────────────
st.set_page_config(
    page_title="Handwriting to Text",
    page_icon="✍️",
    layout="wide"
)

# ── Minimal CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fc; }
    .stat-card {
        background: white;
        border: 1.5px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px 10px;
        text-align: center;
    }
    .stat-num   { font-size: 1.8rem; font-weight: 700; color: #4f46e5; }
    .stat-label { font-size: 0.72rem; color: #9ca3af;
                  text-transform: uppercase; letter-spacing: 0.08em; }
</style>
""", unsafe_allow_html=True)


# ── IMAGE PRE-PROCESSING ──────────────────────────────────────
def preprocess(img: Image.Image, doc_type: str) -> np.ndarray:
    """
    Enhances the image based on document type.
    """
    img = img.convert("RGB")

    # Rotate if vertical (portrait) since handwriting OCR often expects left-to-right English
    w, h = img.size
    if h > w:
        img = img.rotate(90, expand=True)
        w, h = img.size

    # Scale up small images
    if max(w, h) < 1400:
        scale = 1400 / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    if doc_type == "Handwritten Note":
        # Aggressive enhance for faint handwriting
        img = ImageEnhance.Contrast(img).enhance(1.8)
        img = ImageEnhance.Sharpness(img).enhance(2.2)
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=130, threshold=3))
    else:
        # Mild enhance for printed tables so we don't blow out thin lines/text
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Sharpness(img).enhance(1.5)

    return np.array(img)


# ── LOAD EASYOCR ────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_ocr():
    """
    Loads EasyOCR once and caches it for the whole session.
    It will download the necessary models (~200MB) on the very first run.
    """
    return easyocr.Reader(['en'])


# ══════════════════════════════════════════════════════════════
#   UI
# ══════════════════════════════════════════════════════════════

st.title("✍️ Handwriting to Text Converter (Powered by EasyOCR)")
st.caption("Upload a photo of handwritten notes and get editable digital text. Runs offline and handles handwriting beautifully.")
st.divider()

# Load OCR engine
with st.spinner("⏳ Loading EasyOCR... (first launch downloads AI models)"):
    try:
        reader = load_ocr()
        st.success("✅ EasyOCR engine ready!")
    except Exception as e:
        st.error(f"❌ Could not load EasyOCR: {e}")
        st.stop()

st.divider()

# Two columns
col_left, col_right = st.columns([1, 1], gap="large")

# ─── LEFT: Upload ─────────────────────────────────────────────
with col_left:
    st.subheader("📸 Step 1 — Upload Image")

    doc_type = st.radio(
        "Select Document Type:",
        ["Handwritten Note", "Printed Table / Form"],
        horizontal=True,
        help="Helps the OCR engine optimize for your specific document."
    )

    uploaded_file = st.file_uploader(
        "Choose a photo",
        type=["png", "jpg", "jpeg", "bmp", "webp", "tiff"],
        help="JPG/PNG work best. Clear, well-lit photo gives best results."
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Your uploaded image", use_container_width=True)
        w, h = image.size
        st.caption(f"Resolution: {w} × {h} px  |  File: {uploaded_file.name}")
        st.divider()
        st.markdown("**💡 Tips for better results:**")
        st.markdown("- ☀️ Bright even light, no shadows")
        st.markdown("- 📐 Camera flat directly above paper")
        st.markdown("- 🖊️ Dark ink on white paper is ideal")
        st.markdown("- 🔍 Keep text in focus, not blurry")
    else:
        st.info("👆 Upload an image above to begin")

# ─── RIGHT: Result ────────────────────────────────────────────
with col_right:
    st.subheader("📄 Step 2 — Get Text")

    if uploaded_file is None:
        st.info("👈 Upload a handwritten image on the left first")
    else:
        run_ocr = st.button(
            "🔍 Extract Text from Image",
            type="primary",
            use_container_width=True
        )

        if run_ocr:
            with st.spinner("🧠 Reading document with EasyOCR & Tesseract..."):
                try:
                    processed_img_arr = preprocess(image, doc_type)
                    
                    # --- 1. RUN TESSERACT ---
                    tesseract_text = ""
                    try:
                        # Convert numpy array back to image for Tesseract
                        tess_img = Image.fromarray(processed_img_arr)
                        # Use psm 4 or 6 for structural parsing (columns/blocks)
                        tesseract_text = pytesseract.image_to_string(tess_img, config='--psm 6').strip()
                    except Exception as e:
                        tesseract_text = f"Tesseract error: {e}"
                    
                    if doc_type == "Handwritten Note":
                        # Run EasyOCR with tuned parameters for handwriting
                        raw_results = reader.readtext(
                            processed_img_arr, 
                            detail=1,
                            paragraph=True,
                            text_threshold=0.5,
                            low_text=0.3,
                            mag_ratio=1.5
                        )
                    else:
                        # Tuned for standard printed documents & tables
                        raw_results = reader.readtext(
                            processed_img_arr, 
                            detail=1,
                            paragraph=False,      # Don't group paragraphs for tables to keep columns apart
                            text_threshold=0.7,
                            low_text=0.4,
                            mag_ratio=1.0
                        )
                    
                    if raw_results:
                        if doc_type == "Handwritten Note":
                            # Standard joining for handwriting logic
                            boxes = []
                            for bbox, text in raw_results:
                                center_y = (bbox[0][1] + bbox[2][1]) / 2
                                boxes.append({'text': text, 'cy': center_y})
                            boxes.sort(key=lambda b: b['cy'])
                            full_text = "\n".join([b['text'] for b in boxes]).strip()
                            results_list = [b['text'] for b in boxes]
                            
                        else:
                            # Advanced spatial formatting for tables
                            boxes = []
                            max_x = 0
                            for bbox, text, prob in raw_results: # detail=1 with paragraph=False returns (bbox, text, prob)
                                center_y = (bbox[0][1] + bbox[2][1]) / 2
                                center_x = (bbox[0][0] + bbox[1][0]) / 2
                                height = bbox[2][1] - bbox[0][1]
                                boxes.append({'text': text, 'cy': center_y, 'cx': center_x, 'h': height})
                                if bbox[1][0] > max_x:
                                    max_x = bbox[1][0]
                                
                            # Sort by Top-to-Bottom
                            boxes.sort(key=lambda b: b['cy'])
                            
                            # Group into Rows
                            rows = []
                            current_row = []
                            current_y = None
                            
                            for box in boxes:
                                if current_y is None:
                                    current_y = box['cy']
                                    current_row.append(box)
                                else:
                                    # Very tight threshold to separate rows: 30% of height
                                    if abs(box['cy'] - current_y) < max(box['h'], 10) * 0.3:
                                        current_row.append(box)
                                        # Update running avg
                                        current_y = sum(b['cy'] for b in current_row) / len(current_row)
                                    else:
                                        rows.append(current_row)
                                        current_row = [box]
                                        current_y = box['cy']
                                        
                            if current_row:
                                rows.append(current_row)
                                
                            # Format text row by row using high-res absolute coordinate mapping
                            formatted_lines = []
                            char_width = 150 # Wide enough to prevent overlapping columns!
                            
                            for row in rows:
                                row.sort(key=lambda b: b['cx'])
                                row_chars = [' '] * char_width
                                
                                for b in row:
                                    if max_x > 0:
                                        char_idx = int((b['cx'] / max_x) * (char_width - len(b['text']) - 2))
                                        char_idx = max(0, min(char_idx, char_width - len(b['text'])))
                                    else:
                                        char_idx = 0
                                        
                                    for i, char in enumerate(b['text']):
                                        if char_idx + i < char_width:
                                            row_chars[char_idx + i] = char
                                            
                                formatted_lines.append("".join(row_chars).rstrip())
                                
                            full_text = "\n".join(formatted_lines)
                            results_list = [b['text'] for b in boxes]
                        
                        # Flat results for stats counting
                        results = results_list
                        
                        # --- DISPLAY TABS ---
                        tab1, tab2 = st.tabs(["✍️ EasyOCR (Best for Handwriting)", "📊 Tesseract (Best for Printed/Tables)"])
                        
                        # Tab 1: EasyOCR Results
                        with tab1:
                            st.markdown("**📊 Stats:**")
                            c1, c2, c3 = st.columns(3)
                            lines_count = len(results)
                            words_count = len(full_text.split())
                            chars_count = len(full_text)
    
                            for col, val, label in [
                                (c1, lines_count, "Lines"),
                                (c2, words_count, "Words"),
                                (c3, chars_count, "Chars")
                            ]:
                                with col:
                                    st.markdown(
                                        f'<div class="stat-card">'
                                        f'<div class="stat-num">{val}</div>'
                                        f'<div class="stat-label">{label}</div>'
                                        f'</div>', unsafe_allow_html=True)
    
                            st.markdown("---")
    
                            # Editable text
                            st.markdown("**✏️ Extracted Text — edit if needed:**")
                            edited_text_e = st.text_area(
                                "easyocr_output",
                                value=full_text,
                                height=350,
                                label_visibility="collapsed"
                            )
    
                            # Download
                            st.download_button(
                                "⬇️ Download EasyOCR as .txt",
                                data=edited_text_e,
                                file_name="easyocr_handwriting.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                            
                        # Tab 2: Tesseract Results
                        with tab2:
                            
                            lines_count_t = len(tesseract_text.split('\n'))
                            words_count_t = len(tesseract_text.split())
                            chars_count_t = len(tesseract_text)
                            
                            st.markdown("**📊 Stats:**")
                            c1, c2, c3 = st.columns(3)
                            for col, val, label in [
                                (c1, lines_count_t, "Lines"),
                                (c2, words_count_t, "Words"),
                                (c3, chars_count_t, "Chars")
                            ]:
                                with col:
                                    st.markdown(
                                        f'<div class="stat-card">'
                                        f'<div class="stat-num">{val}</div>'
                                        f'<div class="stat-label">{label}</div>'
                                        f'</div>', unsafe_allow_html=True)
                                        
                            st.markdown("---")
                            
                            st.markdown("**✏️ Extracted Text — edit if needed:**")
                            edited_text_t = st.text_area(
                                "tess_output",
                                value=tesseract_text,
                                height=350,
                                label_visibility="collapsed"
                            )
                            
                            st.download_button(
                                "⬇️ Download Tesseract as .txt",
                                data=edited_text_t,
                                file_name="tesseract_printed.txt",
                                mime="text/plain",
                                use_container_width=True
                            )

                    else:
                        st.warning("⚠️ No text detected. Try a clearer photo.")

                except Exception as e:
                    st.error(f"❌ Error extracting text: {e}")

