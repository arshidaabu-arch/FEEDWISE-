# FEEDWISE Farmer Portal
Streamlit prototype with individual farmer registration/login, camera/upload screening, manual measured-value entry, farmer-specific history, CSV export, nutritional guide and recommendations.

## Run in VS Code (Windows)
1. Install Python 3.10+ and extract this ZIP.
2. Open the extracted folder in VS Code.
3. Terminal → New Terminal:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   streamlit run app.py
   ```
   If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`.
4. Open the local URL printed in the terminal (usually http://localhost:8501).

## Deploy
Push app.py, requirements.txt and README.md to GitHub. In Streamlit Community Cloud, create an app from the repository, branch `main`, main file `app.py`.

## Limitations
The image score is a simple colour/texture heuristic, not a trained fungal classifier. It cannot identify fungal species or detect mycotoxins. Protein and moisture are user-entered measured values; a phone camera cannot measure them. The 12% moisture value is only a demo reference, not a universal safety limit. This local SQLite login is for demonstration; public deployment needs persistent shared storage and a security review. Do not use this app alone for feed-safety decisions.

## Language selector
The login and dashboard include a selector listing India's 22 scheduled languages. Common form and navigation labels have starter translations for Tamil, Malayalam, Hindi, Telugu and Kannada. Other languages currently fall back to English; complete, native-speaker-reviewed translations are needed before claiming full localization.
