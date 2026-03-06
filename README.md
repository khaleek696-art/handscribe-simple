# ✍️ Handwriting to Text Converter

Convert photos of handwritten notes into editable digital text using **PaddleOCR** and **Streamlit**.

---

## 📁 Project Files — What Each File Does

```
handscribe_simple/
│
├── app.py              ← THE MAIN APP (all the code lives here)
├── requirements.txt    ← list of Python packages to install
└── README.md           ← this file
```

### `app.py` — explained in plain English

| Section | What it does |
|---|---|
| `preprocess(img)` | Makes the image clearer before OCR — scales it up, boosts contrast & sharpness |
| `load_ocr()` | Loads the PaddleOCR AI engine once and keeps it in memory |
| `extract_text(img, ocr)` | Sends image to PaddleOCR, collects the detected text lines |
| UI — Left column | File uploader + image preview |
| UI — Right column | Extract button + editable text output + download button |

### `requirements.txt` — packages that get installed

```
streamlit       ← runs the web UI in your browser
Pillow          ← opens and enhances image files
numpy           ← converts images into arrays for PaddleOCR
paddlepaddle    ← the AI framework PaddleOCR runs on
paddleocr       ← the OCR engine that reads handwriting
```

---

## 🚀 How to Run — Step by Step in VS Code

### ✅ One-time setup (do this only ONCE)

**Step 1 — Open the project in VS Code**
```
File → Open Folder → select handscribe_simple → Open
```

**Step 2 — Open VS Code terminal**
```
Press:  Ctrl + `   (backtick key, top-left of keyboard near Escape)
```

**Step 3 — Create the virtual environment (venv)**
```bash
python3 -m venv venv
```
> A folder called `venv/` appears inside your project. ✅

**Step 4 — Activate the venv**
```bash
source venv/bin/activate
```
> Your terminal prompt now shows `(venv)` at the start. ✅
> You MUST see (venv) before running the next step.

**Step 5 — Install all packages including PaddleOCR**
```bash
pip install -r requirements.txt
```
> This downloads ~400 MB. Takes 5–10 minutes. Let it finish. ✅
>
> What gets downloaded into your venv:
> - streamlit (~30 MB)
> - Pillow + numpy (~25 MB)
> - paddlepaddle (~200 MB)
> - paddleocr (~150 MB)

---

### ▶️ Run the app (every time)

**Step 6 — Start the app**
```bash
streamlit run app.py
```

> First launch: PaddleOCR downloads AI model files (~100 MB). Wait for the green tick. ✅
> After that: app starts in ~5 seconds every time.
>
> Your browser opens automatically at:  http://localhost:8501

**Step 7 — Use the app**
1. Upload a photo of handwriting on the LEFT side
2. Click **"🔍 Extract Text from Image"** on the RIGHT side
3. Wait a few seconds — text appears in the box
4. Edit any mistakes
5. Download as `.txt` file

**To stop the app:**
```
Press Ctrl + C   in the VS Code terminal
```

---

### 🔄 Every time after first setup (just 2 commands)

```bash
source venv/bin/activate
streamlit run app.py
```

---

## 📥 How PaddleOCR Downloads Work

PaddleOCR has **2 automatic downloads**. You don't do anything manually:

| When | What | Size |
|---|---|---|
| `pip install` (Step 5) | PaddlePaddle + PaddleOCR code | ~400 MB |
| First `streamlit run` | AI model files (detection, recognition, angle) | ~100 MB |

**Everything is stored inside your `venv/` folder — nothing is installed globally on your Mac.**

---

## 💡 Tips for Best OCR Results

| Tip | Why it helps |
|---|---|
| ☀️ Bright even lighting | Dark shadows confuse the OCR engine |
| 📐 Camera directly above paper | Angled shots distort letter shapes |
| 🖊️ Dark ink on white paper | Maximum contrast = maximum accuracy |
| 🔍 Keep text in focus | Blurry images = garbled output |
| 📏 Fill the frame with writing | Larger text in image = better detection |

---

## 🐛 Common Errors and Fixes

| Error | Fix |
|---|---|
| `ModuleNotFoundError: paddleocr` | Run `pip install paddleocr paddlepaddle` with venv active |
| `(venv)` not showing | Run `source venv/bin/activate` first |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |
| No text detected | Use a clearer, brighter photo |
| App crashes on first run | Wait — PaddleOCR may still be downloading models |
| Browser doesn't open | Manually go to http://localhost:8501 |

---

## 🔁 How the Code Works — Line by Line Explanation

```python
# 1. preprocess(img)
#    Takes your uploaded photo and makes it better for OCR:
#    - Converts to RGB (handles all image types)
#    - Scales up if too small (OCR needs at least 1400px)
#    - Boosts contrast (ink pops out more)
#    - Boosts sharpness (letter edges get cleaner)
#    - Applies unsharp mask (fine details become crisper)

# 2. load_ocr()
#    Loads PaddleOCR AI engine.
#    @st.cache_resource means it loads ONCE per session, not on every click.
#    use_angle_cls=True → detects tilted text
#    lang='en'          → English handwriting

# 3. extract_text(img, ocr)
#    - Preprocesses the image
#    - Converts to numpy array (format PaddleOCR needs)
#    - Runs OCR → gets a list of text boxes
#    - Sorts boxes top-to-bottom (so text is in reading order)
#    - Filters out low confidence results (below 30%)
#    - Returns list of text lines + confidence scores

# 4. UI
#    Left column:  upload image, show preview
#    Right column: Extract button, show results, download button
```

---

## ✅ Quick Command Reference

```bash
# Create venv (only once)
python3 -m venv venv

# Activate venv (every time)
source venv/bin/activate

# Install packages (only once)
pip install -r requirements.txt

# Run the app (every time)
streamlit run app.py

# Stop the app
Ctrl + C
```
