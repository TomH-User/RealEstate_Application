import calendar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import streamlit as st
import plotly.express as px
import base64
import time
from datetime import datetime


### ------------- Importation des données ---------------------###
@st.cache_data
def get_data():
    # Import de mon fichier csv valeur_fonciere.csv et departements puis jointure
    df_fonciere = pd.read_csv("valeur_fonciere22.csv", sep=",")
    df_departement = pd.read_csv("departements-france.csv", sep=",")
    df = df_fonciere.merge(df_departement, on="code_departement", how="inner")

    # Suppression des colonnes inutiles
    df = df.drop(
        [
            "id_mutation",
            "numero_disposition",
            "adresse_numero",
            "adresse_suffixe",
            "adresse_nom_voie",
            "adresse_code_voie",
            "code_nature_culture",
            "nature_culture",
            "nature_culture_speciale",
            "code_commune",
            "nom_commune",
            "ancien_code_commune",
            "ancien_nom_commune",
            "id_parcelle",
            "ancien_id_parcelle",
            "numero_volume",
            "lot1_numero",
            "lot1_surface_carrez",
            "lot2_numero",
            "lot2_surface_carrez",
            "lot3_numero",
            "lot3_surface_carrez",
            "lot4_numero",
            "lot4_surface_carrez",
            "lot5_numero",
            "lot5_surface_carrez",
            "nombre_lots",
            "code_type_local",
            "code_nature_culture",
            "nature_culture",
            "code_nature_culture_speciale",
            "nature_culture_speciale",
        ],
        axis=1,
    )
    #Remplacer les valeurs nulles dans type_local par "Non Renseigné"
    df["type_local"] = df["type_local"].fillna("Non Renseigné")

    # Supprimer les lignes dont le type_local est "Non Renseigné"
    df = df[df.type_local != "Non Renseigné"]

    # # Nous conservons uniquement les lignes dont le nature_mutation est Vente
    # df = df[df.nature_mutation.isin(["Vente"])]

    # Ajouter une colonne prix au mètre carré
    df["prix_m2"] = df["valeur_fonciere"] / df["surface_reelle_bati"]

    # Suppression des valeurs pour lesquelles le prix au mètre carré est supérieur à 50 000€
    df = df[df["prix_m2"] < 50000]

    return df

### ------------- Internal Streamlit Plots  -------------------###
# (1) st.line : Evolution de la Valeur foncière moyenne au cours de l'année
def St_line_PrixM2_vs_Mois(df):
    # Convertir la colonne de date en un format de date
    df["date_mutation"] = pd.to_datetime(df["date_mutation"])

    # Extraire l'année et le mois à partir de la colonne de date
    # df["annee"] = df["date_mutation"].dt.year
    df["mois"] = df["date_mutation"].dt.month

    # Grouper les données par année et mois, puis calculer la moyenne, le maximum et le minimum des prix pour chaque groupe
    monthly_prices = df.groupby(["mois"])["prix_m2"].agg(["mean"])
    
    # Réinitialisation de l'index pour avoir un index numérique
    monthly_prices = monthly_prices.reset_index()

    # Création d'une nouvelle colonne "mois_str" avec les noms des mois
    monthly_prices["mois_str"] = monthly_prices["mois"].apply(
        lambda x: {
            1: "01.Janvier",
            2: "02.Février",
            3: "03.Mars",
            4: "04.Avril",
            5: "05.Mai",
            6: "06.Juin",
            7: "07.Juillet",
            8: "08.Août",
            9: "09.Septembre",
            10: "10.Octobre",
            11: "11.Novembre",
            12: "12.Décembre",
        }.get(x, "")
    )


    # Utilisation de la nouvelle colonne "mois_str" comme index
    monthly_prices.set_index("mois_str", inplace=True)

    return monthly_prices


# (2) st.bar : Prix_m2 moyen en fonction de la latitude et longitude
def Bar_Chart_Longitude_vs_Prixm2(df):
    return df.groupby("longitude")["prix_m2"].mean()

def Bar_Chart_Latitude_vs_Prixm2(df):
    return df.groupby("latitude")["prix_m2"].mean()


# (3) st.scatter_chart : Prix au mètre carré en fonction de la valeur foncière
def Scatter_Chart_Prixm2_vs_ValeurFonciere(df):
    st.scatter_chart(data=df, x="valeur_fonciere", y="prix_m2")


# (4) st.map : Map de la Corse avec la chaleur en fonction des tranches de prix
def St_Map_Couleur_vs_Prix(df):
    def color(prix_m2):
        if prix_m2 == None:
            return "#00ffff"
        if prix_m2 <= 2935.294118:
            return "#00bfff"
        elif prix_m2 > 2935.294118 and prix_m2 <= 4661.076923:
            return "#0089ff"
        elif prix_m2 > 4661.076923 and prix_m2 <= 6386.859729:
            return "#0052ff"
        elif prix_m2 > 6386.859729 and prix_m2 <= 40000:
            return "#0044ff"
        else:
            return "#ffffff"

    # Supprimer les longitudes et latitudes nulles
    df = df.dropna(subset=["latitude", "longitude"])
    df["latitude"] = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)

    # Ajouter une nouvelle colonne 'point_color' à votre DataFrame en utilisant la fonction color
    df["point_color"] = df["prix_m2"].apply(color)
    df.reset_index(inplace=True)

    # Création d'un scatter plot coloré par prix au mètre carré en utilisant Matplotlib
    st.map(df, zoom=7, color="point_color")


### ------------- External Streamlit Plots  -------------------###
#  (1) Histograms : Nombre de ventes par jour
def Histogram_NombreDeTransactions_vs_Jour(df):
    # Convertir la colonne de date en un format de date approprié si ce n'est pas déjà le cas
    df["date_mutation"] = pd.to_datetime(df["date_mutation"])

    # Compter le nombre de transactions par jour
    daily_counts = df["date_mutation"].dt.date.value_counts().sort_index()

    # Créer un histogramme avec une barre par jour de l'année
    plt.figure(figsize=(12, 6))
    plt.bar(daily_counts.index, daily_counts)
    plt.title("Nombre de Transactions Immobilières par Jour")
    plt.xlabel("Date de Mutation")
    plt.ylabel("Nombre de Transactions")
    plt.xticks(rotation=90)
    return plt


# (2) Bar : Nombre de ventes par tranche de prix
def Bar_NombreDeVentes_vs_Prix(df):
    # Filtrer les données pour ne conserver que les transactions de type "vente"
    df_ventes = df[df["nature_mutation"] == "Vente"]

    # Définir les tranches de prix 
    tranches_de_prix = [
        0,
        100000,
        200000,
        300000,
        400000,
        500000,
        1000000,
        float("inf"),
    ]
    noms_tranches = [
        "<100k",
        "100k-200k",
        "200k-300k",
        "300k-400k",
        "400k-500k",
        "500k-1M",
        "1M+",
    ]

    # Créer une nouvelle colonne pour la tranche de prix à laquelle chaque transaction appartient
    df_ventes["tranche_prix"] = pd.cut(
        df_ventes["valeur_fonciere"], bins=tranches_de_prix, labels=noms_tranches
    )
    # Compter le nombre de transactions de type "vente" dans chaque tranche de prix par type de local
    transactions_par_tranche = (
        df_ventes.groupby(["tranche_prix", "type_local"])["type_local"]
        .count()
        .unstack(fill_value=0)
    )
    # Créer le graphique en barres empilées
    plt.figure(figsize=(20, 6))
    transactions_par_tranche.plot(kind="bar", stacked=True)
    plt.xlabel("Tranche de Prix")
    plt.ylabel("Nombre de Transactions")
    plt.xticks(rotation=45)
    plt.legend(title="Type de Local")
    return plt


# (3) Scatter : Valeur foncière en fonction de la superficie (en m2)
def Scatter_ValeurFonciere_vs_Superficie(df):
    scatter_plot = plt.figure(figsize=(10, 6))
    plt.scatter(df["surface_reelle_bati"], df["valeur_fonciere"], c="DarkBlue")
    plt.xlim(0, 300)
    plt.ylim(0, 900000)
    plt.xlabel("Surface du Bâtiment")
    plt.ylabel("Valeur Foncière")
    # Tracer la ligne sans légende
    return scatter_plot


# 4) Pie charts :  Répartition des ventes par région
def Pie_Chart_Ventes_vs_Region(df_selection):
    
    def definir_region(row):
        min_lat = df_selection["latitude"].min()
        max_lat = df_selection["latitude"].max()
        min_lon = df_selection["longitude"].min()
        max_lon = df_selection["longitude"].max()
        moy_lat = (min_lat + max_lat) / 2
        moy_lon = (min_lon + max_lon) / 2

        if (min_lat <= row["latitude"] <= moy_lat) and (
            min_lon <= row["longitude"] <= moy_lon
        ):
            return "Sud-Ouest"
        elif (min_lat <= row["latitude"] <= moy_lat) and (
            moy_lon <= row["longitude"] <= max_lon
        ):
            return "Sud-Est"
        elif (moy_lat <= row["latitude"] <= max_lat) and (
            min_lon <= row["longitude"] <= moy_lon
        ):
            return "Nord-Ouest"
        elif (moy_lat <= row["latitude"] <= max_lat) and (
            moy_lon <= row["longitude"] <= max_lon
        ):
            return "Nord-Est"
        else:
            return None

    # Création de la nouvelle colonne region
    df_selection["region"] = df_selection.apply(definir_region, axis=1)
    # Création du pie chart
    plt.figure(figsize=(5, 5))
    plt.pie(
        df_selection["region"].value_counts(),
        labels=df_selection["region"].value_counts().index,
        autopct="%1.1f%%",
        startangle=140,
    )
    return plt


### ------------- Interactive Elements  -------------------###
# (1) Sidebar : Paramètres des graphiques
def implement_sidebar(df):


    st.sidebar.header("Choisir ses filtres :")

    region = st.sidebar.selectbox(
        "Sélectionner la Région:",
        options=df["nom_region"].unique(),
        index=1,  # Par défaut la corse est sélectionnée
    )

    type_local = st.sidebar.multiselect(
        "Selectionnez le type de bien :",
        options=df["type_local"].unique(),
        default=df["type_local"].unique(),
    )

    # Élément interactif pour la sélection de "nature_mutation"
    nature_mutation = st.sidebar.radio(
        "Sélectionner le type de Transaction :",
        df["nature_mutation"].unique()
    )

    return type_local, region, nature_mutation



# Création d'une fonction pour télécharger un DataFrame au format CSV
def download_button(df, label="Télécharger le CSV", key="download_csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">{label}</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)


# Fonction qui applique tous nos filtres
def filter_dataframe(df, selected_region, selected_type_local, selected_nature_mutation):
    df_selection = df[
        (df["nom_region"] == selected_region)
        & (df["type_local"].isin(selected_type_local))
        & (df["nature_mutation"] == selected_nature_mutation)
    ]
    return df_selection


def affichage_application(df_selection):
    # Titre et sous-titre de l'application
    st.title(" :bar_chart: Dashboard - Transactions Immobilières 2022")

    st.markdown(
        "<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True
    )
    st.subheader(
        "Bienvenue ! Ce Tableau de Bord vous permettra de visualiser les variables impactant le prix de l'immobilier en France."
    )
    st.markdown(
        "<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True
    )


    st.markdown('<h2 text-align:center; font-size: 20px;">Analyse Spatiale</h2>', unsafe_allow_html=True)

    #   Affichage de la map
    st.markdown('<h5 text-align:center; font-size: 20px;">Map de la chaleur en fonction du prix au mètre carré</h5>', unsafe_allow_html=True)   
    St_Map_Couleur_vs_Prix(df_selection)

    # - Affichage de l'élément 2' : bar_chart (Nouveaux graphes)
    elem3, elem4 = st.columns(2)
    with elem3:
        bar_chart2 = Bar_Chart_Longitude_vs_Prixm2(df_selection)
        st.markdown('<h5 text-align:center; font-size: 20px;">Prix au mètre carré en fonction de la longitude</h5>', unsafe_allow_html=True)
        st.bar_chart(bar_chart2, color=["#00172B"])
    with elem4:
        bar_chart3 = Bar_Chart_Latitude_vs_Prixm2(df_selection)
        st.markdown('<h5 text-align:center; font-size: 20px;">Prix au mètre carré en fonction de la latitude</h5>', unsafe_allow_html=True)
        st.bar_chart(bar_chart3, color=["#00172B"])

    # - Affichage de l'élément 8 : pie_chart
    pie_chart = Pie_Chart_Ventes_vs_Region(df_selection)
    elem8 = st.columns(1)
    with elem8[0]:
        st.markdown('<h5 text-align:center; font-size: 20px;">Répartition du nombre de ventes par région</h5>', unsafe_allow_html=True)
        st.pyplot(pie_chart)

    st.markdown('<h2 text-align:center; font-size: 20px;">Analyse Temporelle</h2>', unsafe_allow_html=True)
    # Création des graphiques
    st_line = St_line_PrixM2_vs_Mois(df_selection)
    histogram = Histogram_NombreDeTransactions_vs_Jour(df_selection)

    # 1 - Affichage des elements 1 & 2 : st.line et histogram
    elem1, elem2 = st.columns(2)
    with elem1:
        st.markdown('<h5 text-align:center; font-size: 20px;">Evolution du Prix au mètre carré Moyen</h5>', unsafe_allow_html=True)
        st.line_chart(st_line, color=["#00172B", "#00172B"])
    with elem2:
        st.markdown('<h5 text-align:center; font-size: 20px;">Nombre de Transactions Immobilières par Jour</h5>', unsafe_allow_html=True)
        st.pyplot(histogram)


    st.markdown('<h2 text-align:center; font-size: 20px;">Autres variables</h2>', unsafe_allow_html=True)
    # 3 - Affichage de l'élément 3' : scatter_chart (Nouveau graphe)
    st.markdown('<h5 text-align:center; font-size: 20px;">Prix au mètre carré en fonction de la valeur foncière</h5>', unsafe_allow_html=True)
    Scatter_Chart_Prixm2_vs_ValeurFonciere(df_selection)

    # 4 - Affichage de l'élément 6 :bar
    bar = Bar_NombreDeVentes_vs_Prix(df_selection)
    elem6 = st.columns(1)
    with elem6[0]:
        st.markdown('<h5 text-align:center; font-size: 20px;">Nombre de Transaction et Types de bien par tranche de prix</h5>', unsafe_allow_html=True)
        st.pyplot(bar)


    # 6 - Affichage de l'élément 7 : scatter
    scatter = Scatter_ValeurFonciere_vs_Superficie(df_selection)
    elem7 = st.columns(1)
    with elem7[0]:
        st.markdown('<h5 text-align:center; font-size: 20px;">Valeur foncière en fonction de la superficie (en m2)</h5>', unsafe_allow_html=True)
        st.pyplot(scatter)

