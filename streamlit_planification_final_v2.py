import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def load_data(file):
    """Loads and cleans the Excel file with the following columns:
    - salle
    - lot
    - Produit
    - Date Start
    - Time Start
    - Run Time
    """
    df = pd.read_excel(file)

    # Ensure required columns
    required = ["salle", "lot", "Produit", "Date Start", "Time Start", "Run Time"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        st.error(f"Missing columns: {missing}")
        return None

    # Parse date/time (use dayfirst=True if your file is DD/MM/YYYY)
    df["Début"] = pd.to_datetime(
        df["Date Start"].astype(str) + " " + df["Time Start"].astype(str),
        errors="coerce",
        dayfirst=True
    )
    # Drop rows where date parsing failed
    df.dropna(subset=["Début"], inplace=True)

    # Convert Run Time to hours
    df["Durée (h)"] = (
        df["Run Time"]
        .astype(str)
        .str.replace(",", ".")
        .astype(float)
        / 1000
        * 60
    )

    # Calculate end time
    df["Fin"] = df["Début"] + pd.to_timedelta(df["Durée (h)"], unit="h")

    # Ensure salle is a string
    df["Salle"] = df["salle"].astype(str)

    # Return cleaned DataFrame
    return df[["Salle", "lot", "Produit", "Début", "Fin", "Durée (h)"]].rename(columns={"lot": "Lot"})


def plot_week_schedule(df):
    """Plots a Monday–Sunday timeline with 1-hour increments,
    coloring each bar by the 'Produit' value.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # 1) Figure out the Monday of the earliest date in your data
    earliest = df["Début"].min().normalize()  # e.g. 2025-03-24 00:00
    monday = earliest - pd.Timedelta(days=earliest.weekday())  # shift back to Monday
    sunday = monday + pd.Timedelta(days=7) - pd.Timedelta(seconds=1)  # Sunday 23:59:59

    # 2) Assign a unique color to each distinct product
    unique_products = df["Produit"].unique()
    # Use a colormap with enough distinct colors (e.g., tab20 for up to 20 products)
    color_map = plt.cm.get_cmap("tab20", len(unique_products))
    product_to_color = {}
    for i, product in enumerate(unique_products):
        product_to_color[product] = color_map(i)

    # 3) Plot each lot as a horizontal bar, using the product color
    for _, row in df.iterrows():
        color = product_to_color[row["Produit"]]
        ax.barh(
            y=row["Salle"],
            width=row["Durée (h)"],
            left=row["Début"],
            height=0.5,
            color=color
        )
        # Optionally label the bar with the lot number
        ax.text(
            x=row["Début"],
            y=row["Salle"],
            s=str(row["Lot"]),
            va="center",
            ha="left",
            fontsize=8
        )

    # 4) Configure the x-axis from Monday 00:00 to Sunday 23:59
    ax.set_xlim([monday, sunday])

    # Show major ticks every hour
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    # Format as e.g. "Mon 01:00"
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M'))
    plt.xticks(rotation=45)

    ax.set_xlabel("Heure")
    ax.set_ylabel("Salle")
    ax.set_title("Planification Lundi–Dimanche (1h increments, colored by Produit)")

    plt.tight_layout()
    st.pyplot(fig)


def main():
    st.title("Planification de Production - Lundi à Dimanche")
    uploaded_file = st.file_uploader("Chargez votre fichier Excel", type=["xlsx"])

    if uploaded_file:
        df = load_data(uploaded_file)
        if df is not None:
            st.success("Fichier chargé avec succès !")
            st.write("Aperçu des données :")
            st.write(df)
            plot_week_schedule(df)

if __name__ == "__main__":
    main()
