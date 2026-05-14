# Gasmet Gas Flux Analyzer

A standalone desktop application for processing Gasmet gas flux measurement data files. This Python GUI application replicates the functionality of the original R script with an easy-to-use interface.

## Features

- **User-friendly GUI** - No R knowledge required
- **Automated flux calculations** - Processes CO2 and N2O measurements
- **Outlier detection** - Automatically identifies and removes outliers using studentized residuals
- **Temperature correction** - Optional temperature-adjusted flux calculations
- **Diagnostic plots** - Generates publication-quality PNG plots showing data and regression lines
- **Excel output** - Saves results in familiar Excel format
- **Batch processing** - Processes all .TXT files in a directory

## Installation

### Option 1: Simple Installation (Windows/Mac/Linux)

1. **Install Python** (if not already installed)
   - Download Python 3.8 or newer from https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Install required packages**
   Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:
   ```bash
   pip install pandas numpy matplotlib scipy openpyxl
   ```

3. **Download the application**
   - Save `gasmet_analyzer.py` to your computer

4. **Run the application**
   ```bash
   python gasmet_analyzer.py
   ```

### Option 2: Using a Virtual Environment (Recommended for IT departments)

```bash
# Create virtual environment
python -m venv gasmet_env

# Activate it
# On Windows:
gasmet_env\Scripts\activate
# On Mac/Linux:
source gasmet_env/bin/activate

# Install packages
pip install -r requirements.txt

# Run application
python gasmet_analyzer.py
```

## Usage

### File Format Requirements

Your Gasmet .TXT files should:
- Be tab-separated
- Have columns: `Date`, `Time`, `Carbon.dioxide.CO2`, `Nitrous.oxide.N2O`
- Be named in format: `Location_Rep.TXT` (e.g., `Field1_R1.TXT`, `Field1_R2.TXT`)
- Ideally contain 8 measurement rows (the app will prompt if different)

### Step-by-Step Guide

1. **Launch the application**
   ```bash
   python gasmet_analyzer.py
   ```

2. **Select your data directory**
   - Click "Browse..." to select the folder containing your .TXT files

3. **Configure options**
   - ✓ **Apply temperature correction** - Recommended for accurate flux calculations
   - ✓ **Save diagnostic plots** - Creates PNG plots in a "Plots" folder
   - ✓ **Save results to Excel** - Saves flux values and QC data
   - **Save concatenated measurements** - Optional, saves all raw data to Excel

4. **Temperature data** (if using temperature correction)
   - Option A: Click "Load Temperature File" to load a tab-separated file with format:
     ```
     R1    15.5
     R2    16.2
     R3    14.8
     ```
   - Option B: The app will prompt you to enter temperature for each rep during processing

5. **Process files**
   - Click "Process Files"
   - Monitor progress in the log window
   - Results will be saved to your data directory

### Output Files

The application creates several output files:

1. **`Location_Flux_Values.xlsx`** - Summary results with:
   - CO2 and N2O flux values
   - Regression slopes and intercepts
   - R² values (before and after outlier removal)
   - Number of points used/excluded

2. **`Location_Flux_Check.xlsx`** - Detailed QC data showing:
   - All measurements with timestamps
   - Flags indicating which points were used/excluded
   - Useful for quality checking

3. **`Plots/RepName_diagnostics.png`** - Diagnostic plots showing:
   - CO2 and N2O concentration vs time
   - Regression lines
   - Excluded outliers marked in red
   - R² values

4. **`Location_Gasmet_Measurements.xlsx`** - (Optional) All raw measurements concatenated

## How It Works

The application follows the same workflow as the R script:

1. **Data Loading** - Reads all .TXT files and extracts Location/Rep from filenames
2. **Quality Checks** - Validates column names and row counts
3. **Outlier Detection** - Uses studentized residuals (threshold = 3) to identify outliers
4. **Regression** - Fits linear models with outliers removed
5. **Flux Calculation** - Calculates fluxes using chamber geometry and ideal gas law
6. **Visualization** - Creates diagnostic plots for quality control

### Flux Calculation Formula

```
Flux = slope × (V / Va) / A

Where:
  slope = Linear regression slope (ppm/s)
  V = Chamber volume (0.00967 m³)
  Va = Molar volume adjusted for temperature (0.0224 m³/mol at STP)
  A = Chamber area (0.0314 m²)
```

## Troubleshooting

### "No module named 'pandas'" (or similar)
- You need to install the required packages: `pip install pandas numpy matplotlib scipy openpyxl`

### "No .TXT files found"
- Make sure you selected the correct directory
- Check that files have .TXT extension (uppercase)

### "Columns missing in file"
- Verify your files have the correct column headers (tab-separated)
- Required: `Date`, `Time`, `Carbon.dioxide.CO2`, `Nitrous.oxide.N2O`

### Application won't start
- Ensure Python 3.8+ is installed: `python --version`
- Try reinstalling packages: `pip install --upgrade pandas numpy matplotlib scipy openpyxl`

## Comparison with R Script

This Python application provides the same functionality as the R `gasmet_process()` function:

| Feature | R Script | Python GUI |
|---------|----------|------------|
| Batch processing | ✓ | ✓ |
| Outlier removal | ✓ | ✓ |
| Temperature correction | ✓ | ✓ |
| Diagnostic plots | ✓ | ✓ |
| Excel output | ✓ | ✓ |
| User interface | Command line | Graphical |
| Package installation | Requires R packages | Standard Python packages |

## Technical Details

- **Language**: Python 3.8+
- **GUI Framework**: tkinter (built into Python)
- **Data Processing**: pandas, numpy
- **Statistics**: scipy
- **Plotting**: matplotlib
- **Excel I/O**: openpyxl

## Support

For issues or questions, check that:
1. All .TXT files are in the correct format
2. Python and all packages are properly installed
3. You have write permissions in the data directory

## License

This application replicates the functionality of the original R script for internal use.
