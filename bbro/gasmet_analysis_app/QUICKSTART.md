# QUICK START GUIDE
# Gasmet Gas Flux Analyzer

## For Complete Beginners

### Step 1: Install Python (One-time setup)

**Windows:**
1. Go to https://www.python.org/downloads/
2. Click "Download Python 3.12" (or latest version)
3. Run the installer
4. ✓ IMPORTANT: Check "Add Python to PATH" before clicking Install
5. Click "Install Now"

**Mac:**
1. Open Terminal (Applications → Utilities → Terminal)
2. Type: `python3 --version`
3. If not installed, download from https://www.python.org/downloads/

### Step 2: Install Required Packages (One-time setup)

**Windows:**
1. Open Command Prompt (search for "cmd" in Start menu)
2. Type this command and press Enter:
   ```
   pip install pandas numpy matplotlib scipy openpyxl
   ```
3. Wait for installation to complete (1-2 minutes)

**Mac:**
1. Open Terminal
2. Type:
   ```
   pip3 install pandas numpy matplotlib scipy openpyxl
   ```

### Step 3: Get the Application Files

1. Download these files to a folder (e.g., `C:\GasmetAnalyzer`):
   - gasmet_analyzer.py
   - run_gasmet.bat (Windows) or run_gasmet.sh (Mac/Linux)

### Step 4: Run the Application

**Windows:**
- Double-click `run_gasmet.bat`
- OR open Command Prompt, navigate to folder, type: `python gasmet_analyzer.py`

**Mac/Linux:**
- Open Terminal
- Navigate to folder: `cd /path/to/GasmetAnalyzer`
- Type: `python3 gasmet_analyzer.py`

### Step 5: Use the Application

1. Click "Browse..." to select the folder with your .TXT files
2. Check options (temperature correction recommended)
3. (Optional) Load temperature file or enter manually when prompted
4. Click "Process Files"
5. Watch the progress log
6. Find your results in the same folder:
   - `Location_Flux_Values.xlsx` - Your main results
   - `Plots/` folder - Diagnostic graphs

## Your Data Files Must Be:

✓ Tab-separated .TXT files
✓ Named like: Field1_R1.TXT, Field1_R2.TXT, etc.
✓ Have columns: Date, Time, Carbon.dioxide.CO2, Nitrous.oxide.N2O
✓ Ideally 8 rows of measurements per file

## Example Temperature File (optional):

Save as .txt with tab between Rep name and temperature:
```
R1    15.5
R2    16.2
R3    14.8
```

## Test It First!

A `sample_data` folder is included with test files.
Try running the app on these first to make sure everything works!

## Need Help?

Common issues:
- "Python not found" → Reinstall Python and check "Add to PATH"
- "No module named pandas" → Run the pip install command again
- "No .TXT files found" → Check you selected the right folder
- App closes immediately → Run from Command Prompt to see error messages

## For IT Departments: Deployment

To deploy to multiple computers:

1. Install Python 3.8+ on all machines
2. Create a shared network folder with:
   - gasmet_analyzer.py
   - requirements.txt
3. Create a desktop shortcut pointing to run_gasmet.bat
4. Users can run without admin rights after initial Python install

Alternative: Create a standalone executable with PyInstaller (no Python installation needed):
```
pip install pyinstaller
pyinstaller --onefile --windowed gasmet_analyzer.py
```
This creates a single .exe file that can be distributed.
