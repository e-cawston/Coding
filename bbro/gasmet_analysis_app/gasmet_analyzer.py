#!/usr/bin/env python3
"""
Gasmet Gas Flux Analyzer
A standalone desktop application for processing Gasmet gas flux measurement data.
Replicates the functionality of the R gasmet_process script with a user-friendly GUI.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import stats
import os
from datetime import datetime


class GasmetAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Gasmet Gas Flux Analyzer")
        self.root.geometry("900x700")
        
        # Variables
        self.working_dir = tk.StringVar()
        self.use_temp = tk.BooleanVar(value=True)
        self.save_concat = tk.BooleanVar(value=False)
        self.save_plots = tk.BooleanVar(value=True)
        self.save_results = tk.BooleanVar(value=True)
        
        self.file_table = None
        self.temperatures = {}
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Gasmet Gas Flux Analyzer", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Working Directory Selection
        dir_frame = ttk.LabelFrame(main_frame, text="Data Directory", padding="10")
        dir_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(dir_frame, text="Working Directory:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(dir_frame, textvariable=self.working_dir, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_directory).grid(row=0, column=2)
        
        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Processing Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Checkbutton(options_frame, text="Apply temperature correction", 
                       variable=self.use_temp).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Save concatenated measurements", 
                       variable=self.save_concat).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Save diagnostic plots", 
                       variable=self.save_plots).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Save results to Excel", 
                       variable=self.save_results).grid(row=3, column=0, sticky=tk.W)
        
        # Temperature Input Frame
        temp_frame = ttk.LabelFrame(main_frame, text="Temperature Data (Optional)", padding="10")
        temp_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(temp_frame, text="Load Temperature File", 
                  command=self.load_temperature_file).grid(row=0, column=0, padx=5)
        ttk.Label(temp_frame, text="or temperatures will be prompted during processing").grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Process Button
        ttk.Button(main_frame, text="Process Files", command=self.process_files,
                  style='Accent.TButton').grid(row=4, column=0, columnspan=3, pady=20)
        
        # Progress/Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def log(self, message):
        """Add message to log window"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def browse_directory(self):
        """Browse for working directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.working_dir.set(directory)
            self.log(f"Working directory set to: {directory}")
            
    def load_temperature_file(self):
        """Load temperature data from tab-separated file"""
        filename = filedialog.askopenfilename(
            title="Select Temperature File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                temp_df = pd.read_csv(filename, sep='\t', header=None)
                self.temperatures = dict(zip(temp_df.iloc[:, 0], temp_df.iloc[:, 1]))
                self.log(f"Loaded temperatures for {len(self.temperatures)} reps")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load temperature file: {str(e)}")
                
    def get_temperature(self, rep):
        """Get temperature for a rep - from file or user input"""
        if rep in self.temperatures:
            return self.temperatures[rep]
        
        # Prompt user for temperature
        temp_window = tk.Toplevel(self.root)
        temp_window.title(f"Temperature for {rep}")
        temp_window.geometry("300x100")
        
        ttk.Label(temp_window, text=f"Enter temperature (°C) for {rep}:").pack(pady=10)
        temp_var = tk.StringVar()
        entry = ttk.Entry(temp_window, textvariable=temp_var)
        entry.pack(pady=5)
        entry.focus()
        
        result = [None]
        
        def submit():
            try:
                result[0] = float(temp_var.get())
                temp_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
                
        entry.bind('<Return>', lambda e: submit())
        ttk.Button(temp_window, text="OK", command=submit).pack(pady=5)
        
        temp_window.wait_window()
        return result[0]
        
    def process_files(self):
        """Main processing function"""
        if not self.working_dir.get():
            messagebox.showerror("Error", "Please select a working directory")
            return
            
        try:
            os.chdir(self.working_dir.get())
            self.log("=" * 60)
            self.log("Starting Gasmet data processing...")
            self.log("=" * 60)
            
            # Get list of TXT files
            file_list = list(Path('.').glob('*.TXT'))
            
            if not file_list:
                messagebox.showerror("Error", "No .TXT files found in directory")
                return
                
            self.log(f"Found {len(file_list)} .TXT files")
            
            # Create file table
            file_data = []
            for file in file_list:
                parts = file.stem.split('_')
                if len(parts) >= 2:
                    file_data.append({
                        'file_name': file.name,
                        'Location': parts[0],
                        'Rep': parts[1]
                    })
                    
            self.file_table = pd.DataFrame(file_data)
            self.log(f"Processing {len(self.file_table)} files")
            
            # Concatenate files
            concat_files = self.concatenate_files()
            
            if concat_files.empty:
                messagebox.showerror("Error", "No valid data found")
                return
                
            # Calculate fluxes
            summary_output, calc_measures = self.calculate_fluxes(concat_files)
            
            # Save results
            if self.save_results.get():
                self.save_output(concat_files, summary_output, calc_measures)
                
            self.log("=" * 60)
            self.log("Processing completed successfully!")
            self.log("=" * 60)
            messagebox.showinfo("Success", "Processing completed successfully!")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
            
    def concatenate_files(self):
        """Read and concatenate all measurement files"""
        concat_list = []
        
        for idx, row in self.file_table.iterrows():
            file = row['file_name']
            
            try:
                # Read file
                df = pd.read_csv(file, sep='\t')
                
                # Check required columns
                required_cols = ['Date', 'Time', 'Carbon.dioxide.CO2', 'Nitrous.oxide.N2O']
                if not all(col in df.columns for col in required_cols):
                    self.log(f"WARNING: Columns missing in {file}; skipped")
                    continue
                    
                # Check row count
                if len(df) != 8:
                    response = messagebox.askyesno(
                        "Warning", 
                        f"File {file} does not have 8 rows (has {len(df)}). Include anyway?"
                    )
                    if not response:
                        self.log(f"Skipped {file}")
                        continue
                        
                # Add metadata
                df['Location'] = row['Location']
                df['Rep'] = row['Rep']
                df['Raw_Data_Location'] = file
                
                # Rename columns
                df = df.rename(columns={
                    'Carbon.dioxide.CO2': 'Carbon_Dioxide',
                    'Nitrous.oxide.N2O': 'Nitrous_Oxide'
                })
                
                concat_list.append(df)
                
            except Exception as e:
                self.log(f"ERROR reading {file}: {str(e)}")
                continue
                
        if not concat_list:
            return pd.DataFrame()
            
        concat_files = pd.concat(concat_list, ignore_index=True)
        
        # Convert time to seconds
        concat_files['Time_Seconds'] = concat_files['Time'].apply(self.time_to_seconds)
        
        self.log(f"Processed {concat_files['Rep'].nunique()} unique reps")
        
        # Optionally save concatenated data
        if self.save_concat.get():
            location = concat_files['Location'].iloc[0]
            filename = f"{location}_Gasmet_Measurements.xlsx"
            concat_files.to_excel(filename, index=False)
            self.log(f"Saved concatenated measurements to {filename}")
            
        return concat_files
        
    def time_to_seconds(self, time_str):
        """Convert HH:MM:SS to seconds"""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s = map(float, parts)
                return h * 3600 + m * 60 + s
            return 0
        except:
            return 0
            
    def calculate_fluxes(self, concat_files):
        """Calculate CO2 and N2O fluxes for each rep"""
        summary_list = []
        calc_measures = concat_files.copy()
        calc_measures['CO2_Used'] = True
        calc_measures['N2O_Used'] = True
        
        # Create plots directory if needed
        if self.save_plots.get() and not Path('Plots').exists():
            Path('Plots').mkdir()
            
        for rep in concat_files['Rep'].unique():
            self.log(f"Processing rep: {rep}")
            
            temp_data = calc_measures[calc_measures['Rep'] == rep].copy()
            
            if len(temp_data) < 2:
                self.log(f"WARNING: Rep {rep} has fewer than 2 data points; skipped")
                continue
                
            # Get temperature if needed
            if self.use_temp.get():
                temperature = self.get_temperature(rep)
                if temperature is None:
                    self.log(f"WARNING: No temperature for {rep}; skipped")
                    continue
                va = 0.0224 * (273.15 / (temperature + 273.15))
            else:
                va = 0.0224
                
            # Chamber parameters
            v = 0.00967  # m³
            A = 0.0314   # m²
            
            # Process CO2
            co2_result = self.fit_with_outlier_removal(
                temp_data, 'Time_Seconds', 'Carbon_Dioxide', 'CO2'
            )
            
            # Process N2O
            n2o_result = self.fit_with_outlier_removal(
                temp_data, 'Time_Seconds', 'Nitrous_Oxide', 'N2O'
            )
            
            if co2_result is None or n2o_result is None:
                continue
                
            # Update used flags
            calc_measures.loc[calc_measures['Rep'] == rep, 'CO2_Used'] = co2_result['used_mask']
            calc_measures.loc[calc_measures['Rep'] == rep, 'N2O_Used'] = n2o_result['used_mask']
            
            # Calculate fluxes
            co2_flux = co2_result['slope'] * ((v / va) / A)
            n2o_flux = n2o_result['slope'] * ((v / va) / A)
            
            # Store summary
            summary_list.append({
                'Rep': rep,
                'CO2_Slope': co2_result['slope'],
                'CO2_Intercept': co2_result['intercept'],
                'CO2_R2_Original': co2_result['r2_original'],
                'CO2_R2_Clean': co2_result['r2_clean'],
                'CO2_N_used': co2_result['n_used'],
                'CO2_N_total': co2_result['n_total'],
                'CO2_Flux': co2_flux,
                'N2O_Slope': n2o_result['slope'],
                'N2O_Intercept': n2o_result['intercept'],
                'N2O_R2_Original': n2o_result['r2_original'],
                'N2O_R2_Clean': n2o_result['r2_clean'],
                'N2O_N_used': n2o_result['n_used'],
                'N2O_N_total': n2o_result['n_total'],
                'N2O_Flux': n2o_flux
            })
            
            # Generate plots
            if self.save_plots.get():
                self.create_diagnostic_plots(
                    temp_data, co2_result, n2o_result, rep
                )
                
        summary_output = pd.DataFrame(summary_list)
        return summary_output, calc_measures
        
    def fit_with_outlier_removal(self, data, x_col, y_col, gas_name):
        """Fit linear model with outlier detection"""
        X = data[x_col].values
        y = data[y_col].values
        
        if len(X) < 2:
            return None
            
        # Initial fit
        slope_1, intercept_1, r_value_1, _, _ = stats.linregress(X, y)
        y_pred_1 = slope_1 * X + intercept_1
        residuals_1 = y - y_pred_1
        
        # Calculate studentized residuals
        n = len(X)
        mse = np.sum(residuals_1**2) / (n - 2)
        h = np.array([1/n + (x - X.mean())**2 / np.sum((X - X.mean())**2) for x in X])
        student_resid = residuals_1 / (np.sqrt(mse * (1 - h)))
        
        # Flag outliers (|studentized residual| > 3)
        used_mask = np.abs(student_resid) <= 3
        
        # Refit without outliers
        X_clean = X[used_mask]
        y_clean = y[used_mask]
        
        if len(X_clean) < 2:
            self.log(f"WARNING: Too many outliers in {gas_name}; using all points")
            used_mask = np.ones(len(X), dtype=bool)
            X_clean = X
            y_clean = y
            
        slope_2, intercept_2, r_value_2, _, _ = stats.linregress(X_clean, y_clean)
        
        return {
            'slope': slope_2,
            'intercept': intercept_2,
            'r2_original': r_value_1**2,
            'r2_clean': r_value_2**2,
            'n_used': len(X_clean),
            'n_total': len(X),
            'used_mask': used_mask
        }
        
    def create_diagnostic_plots(self, data, co2_result, n2o_result, rep):
        """Create diagnostic plots for CO2 and N2O"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # CO2 plot
        used_co2 = data['CO2_Used'].values if 'CO2_Used' in data.columns else co2_result['used_mask']
        ax1.scatter(data['Time_Seconds'][used_co2], data['Carbon_Dioxide'][used_co2], 
                   c='blue', label='Used', s=50)
        ax1.scatter(data['Time_Seconds'][~used_co2], data['Carbon_Dioxide'][~used_co2], 
                   c='red', label='Excluded', s=50, marker='x')
        
        # Add regression line
        x_line = np.array([data['Time_Seconds'].min(), data['Time_Seconds'].max()])
        y_line = co2_result['slope'] * x_line + co2_result['intercept']
        ax1.plot(x_line, y_line, 'k-', linewidth=2)
        
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('CO2 (ppm)')
        ax1.set_title(f"{rep} - CO2\nR² = {co2_result['r2_clean']:.4f}")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # N2O plot
        used_n2o = data['N2O_Used'].values if 'N2O_Used' in data.columns else n2o_result['used_mask']
        ax2.scatter(data['Time_Seconds'][used_n2o], data['Nitrous_Oxide'][used_n2o], 
                   c='blue', label='Used', s=50)
        ax2.scatter(data['Time_Seconds'][~used_n2o], data['Nitrous_Oxide'][~used_n2o], 
                   c='red', label='Excluded', s=50, marker='x')
        
        # Add regression line
        y_line = n2o_result['slope'] * x_line + n2o_result['intercept']
        ax2.plot(x_line, y_line, 'k-', linewidth=2)
        
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('N2O (ppm)')
        ax2.set_title(f"{rep} - N2O\nR² = {n2o_result['r2_clean']:.4f}")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"Plots/{rep}_diagnostics.png", dpi=300, bbox_inches='tight')
        plt.close()
        
    def save_output(self, concat_files, summary_output, calc_measures):
        """Save results to Excel files"""
        location = concat_files['Location'].iloc[0]
        
        # Save flux values
        flux_file = f"{location}_Flux_Values.xlsx"
        summary_output.to_excel(flux_file, index=False)
        self.log(f"Saved flux values to {flux_file}")
        
        # Save flux check data
        check_file = f"{location}_Flux_Check.xlsx"
        calc_measures.to_excel(check_file, index=False)
        self.log(f"Saved flux check data to {check_file}")


def main():
    root = tk.Tk()
    app = GasmetAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
