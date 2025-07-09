from shiny import reactive         
from shiny.express import ui, render, input
from shinywidgets import render_plotly

import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from palmerpenguins import load_penguins

penguins = load_penguins()
ui.page_opts(title="Brenda's Penguin Data", fillable=True)

# Sidebar 
with ui.sidebar(open="open"):
    ui.h2("Palmer Penguins Sidebar")
    ui.input_selectize(
        "selected_attribute", "Choose attribute",
        ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"],
        selected="bill_length_mm",
    )
    ui.input_slider("n_bins", "Seaborn bins", 1, 100, 30)
    ui.input_checkbox_group(
        "selected_species", "Species in table",
        ["Adelie", "Gentoo", "Chinstrap"],
        selected=["Adelie", "Gentoo", "Chinstrap"],
        inline=True,
    )
    ui.input_numeric("plotly_bin_count", "Plotly bins", 30, min=5, max=100)
    ui.hr()
    ui.a("Brenda's GitHub Repo",
         href="https://github.com/bfuemmeler/cintel-02-data",
         target="_blank")

# Data tables
with ui.layout_columns():
    @render.data_frame
    def data_table():
        return penguins[penguins["species"].isin(input.selected_species())]

    @render.data_frame
    def penguins_grid():
        return penguins                     # full data set

# Histograms side‑by‑side
with ui.layout_columns(gap="2rem"):
    with ui.card():
        ui.card_header("Plotly Histogram")
        @render_plotly
        def plotly_histogram():
            df = penguins[penguins["species"].isin(input.selected_species())]
            fig = px.histogram(
                df,
                x=input.selected_attribute(),
                nbins=input.plotly_bin_count(),
                color="species",
                title=f"{input.selected_attribute()} Histogram by Species",
            )
            fig.update_layout(xaxis_title=input.selected_attribute(),
                              yaxis_title="Count")
            return fig

    @render.plot(alt="A Seaborn histogram on penguin body mass in grams.")
    def seaborn_histogram():
                histplot = sns.histplot(data=load_penguins, x="body_mass_g", bins=input.seaborn_bin_count() )
                histplot.set_title("Palmer Penguins")
                histplot.set_xlabel("Mass (g)")
                histplot.set_ylabel("Count")
                return histplot

# scatterplot
with ui.card(full_screen=True):
    ui.card_header("Plotly Scatterplot")
    @render_plotly
    def plotly_scatterplot():
        df = penguins[penguins["species"].isin(input.selected_species())]

        df = df.dropna(subset=["bill_length_mm", "body_mass_g", input.selected_attribute()])

        attr = input.selected_attribute()
        fig = px.scatter(
            df,
            x=attr, y="body_mass_g",
            color="species", symbol="species",
            size="bill_length_mm", size_max=6,
            hover_data=["flipper_length_mm", "bill_depth_mm"],
            title=f"{attr} vs Body Mass",
        )
        fig.update_layout(
            xaxis_title=attr,
            yaxis_title="Body Mass (g)",
            legend_title="Species"
        )
        return fig

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

# Add a reactive calculation to filter the data
# By decorating the function with @reactive, we can use the function to filter the data
# The function will be called whenever an input functions used to generate that output changes.
# Any output that depends on the reactive function (e.g., filtered_data()) will be updated when the data changes.

@reactive.calc
def filtered_data():
    return load_penguins
