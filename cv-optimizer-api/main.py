from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
import os
import requests

from BL.Services.gpt_optimizer import adapt_cv
from BL.Utils.formatter import (
    extract_cv_text
)

app = FastAPI()

TEMP_DIR = "temp"
UPLOADED_DOCX_PATH = os.path.join(TEMP_DIR, "uploaded_cv.docx")
INJECTION_JSON_PATH = os.path.join(TEMP_DIR, "injection.json")
OUTPUT_DOCX_PATH = os.path.join(TEMP_DIR, "optimized_cv.docx")

os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/optimize")
async def optimize(file: UploadFile = File(...), job_description: str = Form(...)):
    try:
        print("📥 Received file:", file.filename)
        print("📄 Job description:", job_description)

        # Save uploaded file
        with open(UPLOADED_DOCX_PATH, "wb") as f:
            f.write(await file.read())

        cv_text = extract_cv_text(UPLOADED_DOCX_PATH)

        # Call OpenAI to adapt CV
        try:
            optimized_text = adapt_cv(cv_text, job_description)
        except Exception:
            return JSONResponse(status_code=400, content={"error": "Failed to optimize CV"})

        print("🧠 Optimized text:\n", optimized_text)

        # Save raw GPT response for .NET to parse
        with open(INJECTION_JSON_PATH, "w", encoding="utf-8") as f:
            f.write(optimized_text)

        # ✅ POST to .NET injector (outside the file write block)
        response = requests.post(
            "http://docx-injector:8080/inject",
            data=optimized_text.encode("utf-8"),
            headers={"Content-Type": "text/plain"}
        )

        if response.status_code != 200:
            return JSONResponse(status_code=500, content={"error": "Injection failed", "details": response.text})
        
        print("📤 Injector response:", response.status_code)
        print("📄 Returning file:", OUTPUT_DOCX_PATH)

        return FileResponse(
            OUTPUT_DOCX_PATH,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="optimized_cv.docx"
        )

    except Exception as e:
        import traceback
        print("❌ Exception in /optimize:", str(e))
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})
