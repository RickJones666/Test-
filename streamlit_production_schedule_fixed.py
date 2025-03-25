
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def load_data(file):
    df = pd.read_excel(file)

    # Identify likely column names dynamically
    date_col = next((col for col in df.columns if "date" in col.lower()), None)
    time_col = next((col for col in df.columns if "time" in col.lower()), None)
    salle_col = next((col for col in df.columns if "resource" in col.lower()), None)
    lot_col = next((col for col in df.columns if "order" in col.lower()), None)
    produit_col = next((col for col in df.columns if "desc" in col.lower()), None)
    run_col = next((col for col in df.columns if "run" in col.lower()), None)

    if not all([date_col, time_col, salle_col, lot_col, produit_col, run_col]):
        st.error("One or more required columns are missing or misnamed.")
        return None

    df["Début"] = pd.to_datetime(df[date_col].astype(str) + " " + df[time_col].astype(str), errors="coerce")
    df["Durée (h)"] = df[run_col].astype(str).str.replace(",", ".").astype(float) / 1000 * 60
    df["Fin"] = df["Début"] + pd.to_timedelta(df["Durée (h)"], unit='h')

    return df[[salle_col, lot_col, produit_col, "Début", "Fin", "Durée (h)"]].rename(columns={
        salle_col: "Salle", lot_col: "Lot", produit_col: "Produit"
    })

def plot_schedule(df):
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, row in df.iterrows():
        ax.barh(row["Salle"], row["Durée (h)"], left=row["Début"], height=0.4)
        ax.text(row["Début"], i, f"{row['Lot']}", va='center', fontsize=8)

    ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M'))
    plt.xticks(rotation=45)
    plt.xlabel('Heure')
    plt.ylabel('Salle')
    plt.title('Cédule de production - Vue interactive')
    plt.tight_layout()
    st.pyplot(fig)

def main():
    st.title("Planification de Production - Semaine 13")
    uploaded_file = st.file_uploader("Téléversez votre fichier Excel", type=["xlsx"])

    if uploaded_file:
        df = load_data(uploaded_file)
        if df is not None:
            st.success("Fichier chargé avec succès !")
            st.dataframe(df)
            plot_schedule(df)

if __name__ == "__main__":
    main()
