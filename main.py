import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Camera Evolution Dashboard", layout="wide")
st.title("Evolution of Camera Technology & Pricing")

#https://docs.streamlit.io/develop/concepts/custom-components/intro#streamlitcomponentsv1html  some reference that I used
#https://developer.mozilla.org/en-US/docs/Web/CSS/background-image this is the link that i folowed to put the background image for the dashboard

st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.pexels.com/photos/8274147/pexels-photo-8274147.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    iframe {
        background-color: transparent !important;
    }

    .block-container {
        background-color: rgba(0, 0, 0, 0.2); 
        border-radius: 10px;
        padding: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Loading and cleaning the data
df = pd.read_csv("camera_dataset.csv")

# Dropping missing/zero entries
clean_cols = ["Dimensions", "Weight (inc. batteries)", "Price", "Storage included"]
df = df.dropna(subset=clean_cols)
for col in clean_cols:
    df = df[df[col] > 0]

# Computing Zoom Ratio
df['Zoom Ratio'] = df['Zoom tele (T)'] / df['Zoom wide (W)']
# Extracting Brand to select and view indivvidual brand
df['Brand'] = df['Model'].str.split().str[0]


# To put the sidebar this is what i used for reference https://docs.streamlit.io/develop/api-reference/layout/st.sidebar
st.sidebar.header("🎛 Filters")

# Years filtering
years = sorted(df['Release date'].dropna().unique())
if len(years) > 1:
    yr_min, yr_max = int(min(years)), int(max(years))
    year_range = st.sidebar.slider("Release date", yr_min, yr_max, (yr_min, yr_max))
else:
    year_range = (int(years[0]), int(years[0]))

# Brands dropdown
brands = ["All"] + sorted(df['Brand'].unique())
sel_brand = st.sidebar.selectbox("Brand", brands)


# Zoom Ratio filter
zoom_min = float(df['Zoom Ratio'].min())
zoom_max = float(df['Zoom Ratio'].max())
zoom_range = st.sidebar.slider(
    "Zoom Ratio", zoom_min, zoom_max, (zoom_min, zoom_max), step=0.1
)

# Apply filters
mask = (
    (df['Release date'] >= year_range[0]) &
    (df['Release date'] <= year_range[1])
)
if sel_brand != "All":
    mask &= df['Brand'] == sel_brand

mask &= (
    (df['Zoom Ratio'] >= zoom_range[0]) &
    (df['Zoom Ratio'] <= zoom_range[1])
)

df_f = df[mask].copy()

# references used for the columns part
# https://docs.streamlit.io/develop/api-reference/layout/st.columns
# https://discuss.streamlit.io/t/how-to-distribute-columns-across-the-entire-screen/53520
# https://www.youtube.com/watch?v=Oq-bAa531tY This video helped a lot in understanding after reading the articles

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Cameras Released Per Year
with col1:
    st.subheader("Cameras Released Per Year")
    if not df_f.empty:
        release_counts = df_f['Release date'].value_counts().sort_index().reset_index()
        release_counts.columns = ['Release date', 'Camera Count']
        fig1 = px.line(
            release_counts,
            x='Release date',
            y='Camera Count',
            markers=True,
            title=f"Camera Launches Over the Years ({sel_brand})"
        )

        # prompt I used for chatgpt :How can I make my Plotly chart in Streamlit look better on a dark background image? Right now it’s completely dark i want to make it translucent
        # ans: To improve readability on a dark background in Streamlit, you can customize your Plotly chart layout with a semi-transparent black plotting area and white text. Here's how to update your figure:
        #fig.update_layout(
        #     paper_bgcolor='rgba(0,0,0,0)',        # Transparent full background
        #     plot_bgcolor='rgba(0,0,0,0.8)',       # Dark translucent plot background
        # )
        #i updated my code accordingly


        fig1.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.6)',
            font=dict(color='white'),
            xaxis=dict(color='white'),
            yaxis=dict(color='white')
        )

        st.plotly_chart(fig1, use_container_width=True)

    else:
        st.info("No data for selected filters.")


# Price vs Effective Pixels
with col2:
    st.subheader("Price vs Resolution")
    if not df_f.empty:
        fig2 = px.scatter(
            df_f,
            x='Effective pixels',
            y='Price',
            color='Brand',
            size='Storage included',
            hover_data=['Model'],
            labels={'Effective pixels': 'Effective Pixels (MP)'},
            title='Price vs Effective Pixels'
        )

        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.6)',
            font=dict(color='white'),
            xaxis=dict(color='white'),
            yaxis=dict(color='white')
        )
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("No data for selected filters.")

# Top Heaviest & Lightest
with col3:
    st.subheader("Top 10 Heaviest & Lightest Cameras")
    if not df_f.empty:
        heavy = df_f.nlargest(10, 'Weight (inc. batteries)')
        light = df_f.nsmallest(10, 'Weight (inc. batteries)')
        bar = pd.concat([heavy, light])
        fig3 = px.bar(
            bar,
            x='Weight (inc. batteries)',
            y='Model',
            orientation='h',
            color='Brand',
            title='Heaviest & Lightest Cameras'
        )

        fig3.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.6)',
            font=dict(color='white'),
            xaxis=dict(color='white'),
            yaxis=dict(color='white')
        )
        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.info("No data for selected filters.")

# Price Distribution by Zoom Ratio
with col4:
    st.subheader("Price Distribution by Zoom Ratio")
    if not df_f.empty:
        # Bin Zoom Ratio into 4 intervals and convert to string for JSON
        bins = pd.cut(df_f['Zoom Ratio'], bins=4)
        df_f['Zoom Bin'] = bins.astype(str)
        fig4 = px.box(
            df_f,
            x='Zoom Bin',
            y='Price',
            color='Zoom Bin',
            title='Price Distribution across Zoom Levels'
        )
        fig4.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.6)',
            font=dict(color='white'),
            xaxis=dict(color='white'),
            yaxis=dict(color='white')
        )
        st.plotly_chart(fig4, use_container_width=True)

    else:
        st.info("No data for selected filters.")

st.markdown("---")
st.caption("Data source: 1000 camera_dataset.csv from Kaggle")
