# Airbnb project analysis

import pandas as pd
import streamlit as st
import plotly.express as px

# ----------------------------------------------------------------
# Get and load data
# ----------------------------------------------------------------

@st.cache()
def get_data():
    url = "http://data.insideairbnb.com/spain/catalonia/barcelona/2022-03-10/visualisations/listings.csv"
    return pd.read_csv(url)

df = get_data()

st.title("Proyecto de analysis de Airbnb en Barcelona")
st.markdown("Proyecto de analysis de la distribución de la oferta de Airbnb en la ciudad de Barcelona")

st.header("Listado Airbnb Barcelona")
st.markdown("Los cinco primeros registros del listado de datos cargados")
st.dataframe(df.head())

# ----------------------------------------------------------------

st.code("""
@st.cache
def get_data():
    url = "http://data.insideairbnb.com/spain/catalonia/barcelona/2022-03-10/visualisations/listings.csv"
    return pd.read_csv(url)
""", language="python")

# ----------------------------------------------------------------

st.header("Donde se encuentran localizadas las propiedades mas caras?")
st.subheader("En el mapa")
st.markdown("En el siguiente mapa se encuentran las propiedades mas caras con un precio diario superior a los 400€")
st.map(df.query("price>=400")[["latitude", "longitude"]].dropna(how="any"))
st.subheader("En la tabla de datos")
st.markdown("A continuació se muestran el top 5 de las propiedades mas caras de Airbnb en Barcelona")
st.write(df.query("price>=400").sort_values("price", ascending=False).head())

# ----------------------------------------------------------------

st.subheader("Selección de columnas del dataset")
st.write(f"Out of the {df.shape[1]} columns, you might want to view only a subset. Streamlit has a [multiselect](https://streamlit.io/docs/api.html#streamlit.multiselect) widget for this.")
defaultcols = ["name", "host_name", "neighbourhood", "room_type", "price"]
cols = st.multiselect("Columns", df.columns.tolist(), default=defaultcols)
st.dataframe(df[cols].head(10))

# ----------------------------------------------------------------

st.header("Precio medio por tipo de propiedad")
st.write("También se pueden mostrar tablas estáticas. A diferencia de un dataframe, con una tabla estática, no se puede ordenar haciendo clic en la cabecera de una columna.")
st.table(df.groupby("room_type").price.mean().reset_index()\
    .round(2).sort_values("price", ascending=False)\
    .assign(avg_price=lambda x: x.pop("price").apply(lambda y: "%.2f" % y)))

# ----------------------------------------------------------------

st.header("Qué anfitrión tiene el mayor número de propiedades en Airbnb?")
listingcounts = df.host_id.value_counts()
top_host_1 = df.query('host_id==@listingcounts.index[0]')
top_host_2 = df.query('host_id==@listingcounts.index[1]')
st.write(f"""**{top_host_1.iloc[0].host_name}** is at the top with {listingcounts.iloc[0]} property listings.
**{top_host_2.iloc[1].host_name}** is second with {listingcounts.iloc[1]} listings. Following are randomly chosen
listings from the two displayed as JSON using [`st.json`](https://streamlit.io/docs/api.html#streamlit.json).""")

st.json({top_host_1.iloc[0].host_name: top_host_1\
    [["name", "neighbourhood", "room_type", "minimum_nights", "price"]]\
        .sample(2, random_state=4).to_dict(orient="records"),
        top_host_2.iloc[0].host_name: top_host_2\
    [["name", "neighbourhood", "room_type", "minimum_nights", "price"]]\
        .sample(2, random_state=4).to_dict(orient="records")})

# ----------------------------------------------------------------

st.header("Cual es la distribución de las propiedades por precio?")
st.write("""Select a custom price range from the side bar to update the histogram below displayed as a Plotly chart using
[`st.plotly_chart`](https://streamlit.io/docs/api.html#streamlit.plotly_chart).""")
values = st.sidebar.slider("Price range", float(df.price.min()), float(df.price.clip(upper=1000.).max()), (50., 300.))
f = px.histogram(df.query(f"price.between{values}"), x="price", nbins=15, title="Price distribution")
f.update_xaxes(title="Price")
f.update_yaxes(title="No. of listings")
st.plotly_chart(f)

# ----------------------------------------------------------------

st.header("Cuál es la distribución de la disponibilidad en los distintos barrios?")
st.write("Using a radio button restricts selection to only one option at a time.")
st.write("💡 Notice how we use a static table below instead of a data frame. \
Unlike a data frame, if content overflows out of the section margin, \
a static table does not automatically hide it inside a scrollable area. \
Instead, the overflowing content remains visible.")
neighborhood = st.radio("Neighborhood", df.neighbourhood_group.unique())
show_exp = st.checkbox("Include expensive listings")
show_exp = " and price<200" if not show_exp else ""

@st.cache
def get_availability(show_exp, neighborhood):
    return df.query(f"""neighbourhood_group==@neighborhood{show_exp}\
        and availability_365>0""").availability_365.describe(\
            percentiles=[.1, .25, .5, .75, .9, .99]).to_frame().T

st.table(get_availability(show_exp, neighborhood))
st.write("At 169 days, Brooklyn has the lowest average availability. At 226, Staten Island has the highest average availability.\
    If we include expensive listings (price>=$200), the numbers are 171 and 230 respectively.")
st.markdown("_**Note:** There are 18431 records with `availability_365` 0 (zero), which I've ignored._")

df.query("availability_365>0").groupby("neighbourhood_group")\
    .availability_365.mean().plot.bar(rot=0).set(title="Average availability by neighborhood group",
        xlabel="Neighborhood group", ylabel="Avg. availability (in no. of days)")
st.pyplot()

# ----------------------------------------------------------------

st.header("Propiedades por número de reviews")
st.write("Enter a range of numbers in the sidebar to view properties whose review count falls in that range.")
minimum = st.sidebar.number_input("Minimum", min_value=0)
maximum = st.sidebar.number_input("Maximum", min_value=0, value=5)
if minimum > maximum:
    st.error("Please enter a valid range")
else:
    df.query("@minimum<=number_of_reviews<=@maximum").sort_values("number_of_reviews", ascending=False)\
        .head(50)[["name", "number_of_reviews", "neighbourhood", "host_name", "room_type", "price"]]

st.write("486 is the highest number of reviews and two properties have it. Both are in the East Elmhurst \
    neighborhood and are private rooms with prices $65 and $45. \
    In general, listings with >400 reviews are priced below $100. \
    A few are between $100 and $200, and only one is priced above $200.")
st.header("Images")
pics = {
    "Cat": "https://cdn.pixabay.com/photo/2016/09/24/22/20/cat-1692702_960_720.jpg",
    "Puppy": "https://cdn.pixabay.com/photo/2019/03/15/19/19/puppy-4057786_960_720.jpg",
    "Sci-fi city": "https://storage.needpix.com/rsynced_images/science-fiction-2971848_1280.jpg"
}
pic = st.selectbox("Picture choices", list(pics.keys()), 0)
st.image(pics[pic], use_column_width=True, caption=pics[pic])

st.markdown("## Party time!")
st.write("Yay! You're done with this tutorial of Streamlit. Click below to celebrate.")
btn = st.button("Celebrate!")
if btn:
    st.balloons()