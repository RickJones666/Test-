import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def load_data(file):
    # Load the Excel file
    df = pd.read_excel(file)
    
    # Ensure required columns exist
    required_columns = ["salle", "lot", "Produit", "Date Start", "Time Start", "Run Time"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Missing columns in file: {missing}")
        return None

    # Parse datetime using dayfirst=True
    df["Début"] = pd.to_datetime(
        df["Date Start"].astype(str) + " " + df["Time Start"].astype(str),
        errors="coerce", dayfirst=True
    )
    # Drop rows where date parsing failed
    df = df.dropna(subset=["Début"])
    
    # Convert "Run Time" to a float and compute duration in hours
    try:
        df["Durée (h)"] = df["Run Time"].astype(str).str.replace(",", ".").astype(float) / 1000 * 60
    except Exception as e:
        st.error("Error converting Run Time: " + str(e))
        return None

    df["Fin"] = df["Début"] + pd.to_timedelta(df["Durée (h)"], unit='h')
    
    # Force the "Salle" column to be a string
    df["Salle"] = df["salle"].astype(str)
    
    # Return a cleaned DataFrame with renamed columns
    return df[["Salle", "lot", "Produit", "Début", "Fin", "Durée (h)"]].rename(columns={
        "lot": "Lot"
    })

def plot_schedule(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot each event as a horizontal bar
    for _, row in df.iterrows():
        ax.barh(row["Salle"], row["Durée (h)"], left=row["Début"], height=0.5)
        ax.text(row["Début"], row["Salle"], f"{row['Lot']}", va='center', ha='left', fontsize=8)
    
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M'))
    plt.xticks(rotation=45)
    plt.xlabel('Time')
    plt.ylabel('Salle')
    plt.title('Interactive Production Schedule')
    plt.tight_layout()
    st.pyplot(fig)

def main():
    st.title("Interactive Production Schedule")
    uploaded_file = st.file_uploader("Upload your Excel file 'Test planification.xlsx'", type=["xlsx"])
    
    if uploaded_file:
        df = load_data(uploaded_file)
        if df is not None:
            st.success("File loaded successfully!")
            st.write("Data preview:")
            st.write(df)
            plot_schedule(df)

if __name__ == "__main__":
    main()
