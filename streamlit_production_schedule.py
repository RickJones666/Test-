
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Charger le fichier Excel (assurez-vous que le fichier est dans le même répertoire)
def load_data(file_path):
    df = pd.read_excel(file_path)
    df["Début"] = pd.to_datetime(df["Date Start"].astype(str) + " " + df["Time Start"].astype(str))
    df["Durée (h)"] = df["Run Time"].astype(float) / 1000 * 60  # Convert to hours
    df["Fin"] = df["Début"] + pd.to_timedelta(df["Durée (h)"], unit='h')
    return df

# Plotting the schedule in a visual format
def plot_schedule(df):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Convert Début and Fin to datetime for plotting
    df['Début'] = pd.to_datetime(df['Début'])
    df['Fin'] = pd.to_datetime(df['Fin'])
    
    # Plotting each event as a horizontal bar
    for i, row in df.iterrows():
        ax.barh(row["Salle"], row["Durée (h)"], left=row["Début"], height=0.5, align='center', label=row["Lot"])

    # Format the x-axis to show time
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)
    plt.xlabel('Heure')
    plt.ylabel('Salle')
    plt.title('Cédule de production')
    plt.tight_layout()
    
    # Show the plot
    st.pyplot(fig)

# Streamlit App
def main():
    st.title("Planification de Production - Semaine 13")
    
    # Upload the file
    uploaded_file = st.file_uploader("Téléversez votre fichier Excel", type=["xlsx"])
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.write(df)  # Display the data in the app
        
        # Plotting the schedule
        plot_schedule(df)

if __name__ == "__main__":
    main()
