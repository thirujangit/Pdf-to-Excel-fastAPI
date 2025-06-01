from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import pdfplumber
import pandas as pd
import traceback

app = FastAPI()

@app.post("/convert-pdf-to-excel/")
async def convert_pdf_to_excel(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        with open("temp.pdf", "wb") as f:
            f.write(await file.read())

        # Extract table(s)
        tables = []
        with pdfplumber.open("temp.pdf") as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    tables.append(df)

        if not tables:
            return JSONResponse(content={"error": "No tables found in PDF."}, status_code=400)

        # Combine and export to Excel
        result_df = pd.concat(tables)
        output_path = "output.xlsx"
        result_df.to_excel(output_path, index=False)

        return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="result.xlsx")

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Render!"}