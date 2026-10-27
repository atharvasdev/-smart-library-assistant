SMART LIBRARY ASSISTANT — SOFTWARE MVP

RUN ON MAC

1. Download and extract this ZIP.
2. Open the extracted smart_library_software_mvp folder in VS Code.
3. In VS Code, choose Terminal > New Terminal.
4. Run these commands one at a time:

   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   streamlit run app.py

5. The app should open in your browser. If not, copy the local URL printed in Terminal
   (usually http://localhost:8501) into your browser.

If a command fails, copy the complete error message and send it for troubleshooting.

FEATURES
- Sample book catalogue
- Search by title
- Category and bin assignment
- Dashboard
- Scan history
- CSV export
- Add books to the catalogue

LIMITATIONS
This is a software-only starter MVP. The catalogue is sample data. It does not yet use OCR,
a live camera, ESP32, LEDs, or a buzzer. Those can be added after this basic version runs.
