import pandas as pd

def readCSV(filepath):
    try:
        df = pd.read_csv(filepath, delimiter=';', dtype=str)
        print(f"Successfully read data from {filepath}")
        return df
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        raise e

def readCriteriaCSV(filepath):
    try:
        criteria_df = pd.read_csv(filepath, delimiter=';', dtype=str)
        print(f"Successfully read criteria from {filepath}")
        return criteria_df
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        raise e

def filterCSV(df, criteria_df):
    if criteria_df.empty or df.empty:
        return pd.DataFrame()

    condition = pd.Series([False] * len(df))
    for _, row in criteria_df.iterrows():
        temp_condition = pd.Series([True] * len(df))
        for column, value in row.items():
            temp_condition &= df[column].str.lower() == value.lower()
        condition |= temp_condition

    filteredDF = df.loc[condition].copy()
    filteredDF['Vorname_Name'] = filteredDF['Vorname'] + ' ' + filteredDF['Name']
    filteredDF[['PLZ', 'Ortsname']] = filteredDF['Ort'].str.split(' ', n=1, expand=True)
    
    output_columns = ['Vorname_Name', 'Adresse', 'PLZ', 'Ortsname']
    selectDF = filteredDF[output_columns]
    return selectDF

def saveCSV(df, filepath):
    try:
        df.to_csv(filepath, index=False)
        print(f"Successfully saved data to {filepath}")
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        raise e
