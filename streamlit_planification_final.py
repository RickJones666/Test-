
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def load_data(file):
    df = pd.read_excel(file)

    # Nettoyage et conversion
    df["Début"] = pd.to_datetime(df["Date Start"].astype(str) + " " + df["Time Start"].astype(str), errors="coerce")
    df["Durée (h)"] = df["Run Time"].astype(str).str.replace(",", ".").astype(float) / 1000 * 60
    df["Fin"] = df["Début"] + pd.to_timedelta(df["Durée (h)"], unit='h')

    return df[["salle", "lot", "Produit", "Début", "Fin", "Durée (h)"]].rename(columns={
        "salle": "Salle", "lot": "Lot"
    })

def plot_schedule(df):
    fig, ax = plt.subplots(figsize=(12, 6))

    for i, row in df.iterrows():
        ax.barh(row["Salle"], row["Durée (h)"], left=row["Début"], height=0.5)
        ax.text(row["Début"], row["Salle"], f"{row['Lot']}", va='center', ha='left', fontsize=8)

    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M'))
    plt.xticks(rotation=45)
    plt.xlabel('Heure')
    plt.ylabel('Salle')
    plt.title('Planification interactive - Production')
    plt.tight_layout()
    st.pyplot(fig)

def main():
    st.title("Planification de Production - Semaine interactive")
    uploaded_file = st.file_uploader("Téléversez le fichier 'Test planification.xlsx'", type=["xlsx"])

    if uploaded_file:
        df = load_data(uploaded_file)
        st.success("Fichier chargé avec succès !")
        st.dataframe(df)
        plot_schedule(df)

if __name__ == "__main__":
    main()
