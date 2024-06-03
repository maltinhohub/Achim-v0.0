import tkinter as tk
from tkinter import filedialog, messagebox
from csv_operations import readCSV, readCriteriaCSV, filterCSV, saveCSV
import pandas as pd

class EditableTable(tk.Frame):
    def __init__(self, parent, columns, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.columns = columns
        self.entries = []
        self.create_table()

    def create_table(self):
        self.header_entries = []
        for i, col in enumerate(self.columns):
            entry = tk.Entry(self, width=15)
            entry.insert(0, col)
            entry.grid(row=0, column=i)
            self.header_entries.append(entry)
        self.add_row()

    def add_row(self, values=None):
        if values is None:
            values = [''] * len(self.columns)
        row_entries = []
        for i, value in enumerate(values):
            entry = tk.Entry(self, width=15)
            entry.insert(0, value)
            entry.grid(row=len(self.entries) + 1, column=i)
            row_entries.append(entry)
        self.entries.append(row_entries)

    def delete_row(self):
        if self.entries:
            for entry in self.entries[-1]:
                entry.destroy()
            self.entries.pop()

    def get_data(self):
        return [[entry.get() for entry in row_entries] for row_entries in self.entries]

    def get_column_names(self):
        return [entry.get() for entry in self.header_entries]

    def set_columns(self, columns):
        self.columns = columns
        self.create_table()

class CSVFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV-Filter")

        self.data_filepath = ''
        self.criteria_filepath = ''
        self.criteria_columns = ['Gemkg-Name', 'Flur', 'Flurstuecksnummer']

        # Daten-Dateiauswahl
        tk.Label(root, text="Daten CSV-Datei:").grid(row=0, column=0, padx=10, pady=10)
        self.entry_data_filepath = tk.Entry(root, width=50)
        self.entry_data_filepath.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(root, text="Durchsuchen", command=self.open_data_file_dialog).grid(row=0, column=2, padx=10, pady=10)

        # Kriterien-Dateiauswahl
        tk.Label(root, text="Kriterien CSV-Datei:").grid(row=1, column=0, padx=10, pady=10)
        self.entry_criteria_filepath = tk.Entry(root, width=50)
        self.entry_criteria_filepath.grid(row=1, column=1, padx=10, pady=10)
        tk.Button(root, text="Durchsuchen", command=self.open_criteria_file_dialog).grid(row=1, column=2, padx=10, pady=10)

        # Kriterien-Eingabebereich
        tk.Label(root, text="Kriterien eingeben:").grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        self.table_frame = tk.Frame(root)
        self.table_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        self.criteria_table = EditableTable(self.table_frame, self.criteria_columns)
        self.criteria_table.pack()

        # Hinzufügen und Löschen von Zeilen
        tk.Button(root, text="Zeile hinzufügen", command=self.criteria_table.add_row).grid(row=4, column=0, padx=10, pady=10)
        tk.Button(root, text="Zeile löschen", command=self.criteria_table.delete_row).grid(row=4, column=1, padx=10, pady=10)

        # Filter- und Speichern-Button
        tk.Button(root, text="Filtern und Speichern", command=self.filter_and_save).grid(row=5, column=0, columnspan=3, pady=20)

    def open_data_file_dialog(self):
        self.data_filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.data_filepath:
            self.entry_data_filepath.delete(0, tk.END)
            self.entry_data_filepath.insert(0, self.data_filepath)

    def open_criteria_file_dialog(self):
        self.criteria_filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.criteria_filepath:
            self.entry_criteria_filepath.delete(0, tk.END)
            self.entry_criteria_filepath.insert(0, self.criteria_filepath)
            try:
                criteria_df = readCriteriaCSV(self.criteria_filepath)
                self.criteria_columns = list(criteria_df.columns)
                self.criteria_table.destroy()
                self.criteria_table = EditableTable(self.table_frame, self.criteria_columns)
                self.criteria_table.pack()
                for _, row in criteria_df.iterrows():
                    self.criteria_table.add_row(row.tolist())
            except Exception as e:
                messagebox.showerror("Fehler", f"Konnte Kriterien-Datei nicht lesen: {str(e)}")

    def filter_and_save(self):
        criteria_data = self.criteria_table.get_data()
        criteria_columns = self.criteria_table.get_column_names()
        criteria_df = pd.DataFrame(criteria_data, columns=criteria_columns)

        if not self.data_filepath:
            messagebox.showwarning("Eingabefehler", "Bitte Daten CSV-Datei auswählen")
            return

        if criteria_df.empty:
            messagebox.showwarning("Eingabefehler", "Bitte Kriterien eingeben oder Datei auswählen")
            return

        try:
            df = readCSV(self.data_filepath)
        except Exception as e:
            messagebox.showerror("Fehler beim Lesen der Datei", str(e))
            return

        try:
            result_df = filterCSV(df, criteria_df)
            if result_df.empty:
                messagebox.showinfo("Keine Ergebnisse", "Es wurden keine übereinstimmenden Datensätze gefunden.")
                return
        except KeyError as e:
            messagebox.showerror("Fehler", f"Spalte '{e.args[0]}' nicht gefunden")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if save_path:
            try:
                saveCSV(result_df, save_path)
                messagebox.showinfo("Erfolg", f"Gefilterte Daten erfolgreich in '{save_path}' gespeichert")
            except Exception as e:
                messagebox.showerror("Fehler beim Speichern der Datei", str(e))
