from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from shiny import App, render, ui

here = Path(__file__).parent

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
both = pd.read_csv(here / "valproate_prevalence_both_sexes.csv")
sex = pd.read_csv(here / "valproate_prevalence_male_female.csv")
char = pd.read_csv(here / "characteristics.csv")

char["_section"] = None
char.loc[char["Count (n = 8,621)"].isna() | (char["Count (n = 8,621)"] == ""), "_section"] = char["Characteristic"]
char["_section"] = char["_section"].ffill()
char = char[~char["Characteristic"].isin(char["_section"].unique())]

du = pd.read_csv(here / "valproate_drug_utilization.csv")
du_wide = du.pivot(index="Variable", columns="Estimate", values="Value")

exposure_both = pd.read_csv(here / "valproate_exposure_per_patient_both.csv")

indication = pd.read_csv(here / "valproate_indication.csv")
indication_pct = indication[indication["estimate_name"] == "percentage"][
    ["variable_level", "estimate_value"]
].rename(columns={"variable_level": "Indication", "estimate_value": "Percentage"})
indication_pct = indication_pct[~indication_pct["Indication"].isin(["not in observation"])]

COLOR_BOTH = "#2b2d42"
COLOR_MALE = "#3a86ff"
COLOR_FEMALE = "#ef476f"

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
app_ui = ui.page_navbar(
    ui.head_content(ui.tags.link(rel="stylesheet", href="custom.css")),
    ui.nav_panel(
        "Background",
        ui.layout_columns(
            ui.card(
                ui.card_header("VALUE Study — Background & Aim"),
                ui.markdown(
                    """
**Regulatory approaches to Valproate across Asia-Pacific countries using OMOP-CDM**

**Aim:** Describe the real-world use of sodium valproate before, during, and after
multi-wave safety warnings among women and men of reproductive age, and describe how
prescribing dynamics varied across countries with differing regulatory approaches.

**Design:** The study includes males and females of reproductive age with evidence
of valproate exposure during the study period.

**Period:** January 1, 2000 – December 31, 2025. Each participating database
contributes data from the earliest date meeting data-quality requirements through
the most recent date available at the time of study execution.

**Treatment cohort:** Valproate users are identified using OMOP standard concepts
corresponding to sodium valproate / valproate / valproic acid and all descendant
concepts (RxNorm ID 745466, Code 40254). Both monotherapy and combination
(multicomponent) formulations containing valproate are included and tracked.
"""
                ),
                ui.download_button("download_package", "Download VALUE2026 R package (.zip)"),
            ),
            ui.card(
                ui.card_header("This report"),
                ui.markdown(
                    """
This report presents results generated from the
**TMU Clinical Research Database (TMUCRD)**, one participating data
partner in the VALUE study, covering 2005–2023 among ages 18–49.

Use the tabs above to explore:

- **Prevalence & Incidence** — interactive year-by-year prevalence and
  incidence of valproate use, overall and stratified by sex.
- **Drug Utilization** — treatment duration, dose, prescribing
  intensity, and recorded indications for valproate use.
- **Characteristics** — demographic, comorbidity, and co-medication
  profile of the valproate-user cohort (Table 1).
"""
                ),
            ),
            col_widths=[7, 5],
        ),
        ui.layout_columns(
            ui.card(
                ui.card_header("Cohort definition"),
                ui.markdown(
                    """
**Name:** Valproate (new user cohort)

**Concept set:** Valproate / valproate semisodium / valproate sodium
(RxNorm ingredient 745466, Code 40254) and all descendant concepts,
including monotherapy and multicomponent formulations.

**Entry event:** First qualifying drug exposure to a concept in the
Valproate concept set, with quantity > 1, during an observation period
between 2000-01-01 and 2023-12-31.

**Inclusion rule:** "Valproate among Childbearing Age" — at least one
qualifying drug exposure recorded around the index date.

**Cohort exit:** End of continuous drug exposure (persistence window).
"""
                ),
            ),
            ui.card(
                ui.card_header("Cohort size"),
                ui.layout_columns(
                    ui.value_box(
                        "Patients",
                        "8,621",
                        showcase=None,
                    ),
                    ui.value_box(
                        "Records",
                        "8,621",
                        showcase=None,
                    ),
                    col_widths=[6, 6],
                ),
                ui.markdown(
                    "Counts reflect the valproate outcome cohort used for baseline "
                    "characterization and drug utilization analyses (TMUCRD, ages 18–49)."
                ),
            ),
            col_widths=[7, 5],
        ),
    ),
    ui.nav_panel(
        "Prevalence & Incidence",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_checkbox_group(
                    "series",
                    "Show series",
                    choices={"both": "Both sexes", "male": "Male", "female": "Female"},
                    selected=["both", "male", "female"],
                ),
                ui.input_slider(
                    "yr_range",
                    "Year range",
                    min=int(both["Year"].min()),
                    max=int(both["Year"].max()),
                    value=(int(both["Year"].min()), int(both["Year"].max())),
                    step=1,
                    sep="",
                ),
            ),
            ui.card(
                ui.card_header("Rate of valproate use per year, TMUCRD"),
                ui.output_plot("prevalence_plot"),
            ),
            ui.card(
                ui.card_header("Underlying data"),
                ui.output_table("prevalence_table"),
            ),
            ui.card(
                ui.card_header(
                    "Incidence by sex (full study period, 2005–2023 — not affected by year filter above)"
                ),
                ui.img(src="Incidence_by_sex_0.png", style="max-width:100%;"),
            ),
            ui.card(
                ui.card_header(
                    "Person-years by calendar year (full study period, 2005–2023)"
                ),
                ui.img(src="Incidence_person_years_0.png", style="max-width:100%;"),
            ),
        ),
    ),
    ui.nav_panel(
        "Drug Utilization",
        ui.navset_tab(
            ui.nav_panel(
                "Utilization",
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Utilization summary (median, IQR)"),
                        ui.img(src="Drug_Utilization_Summary.png", style="max-width:100%;"),
                    ),
                    ui.card(
                        ui.card_header("Prescription rate per 1,000 population"),
                        ui.img(src="Prescription_Rate_Both.png", style="max-width:100%;"),
                    ),
                    ui.card(
                        ui.card_header("Trends over time (median by index year)"),
                        ui.img(src="Drug_Utilization_Trends_by_Year.png", style="max-width:100%;"),
                    ),
                    ui.card(
                        ui.card_header("Prescription rate by sex"),
                        ui.img(src="Prescription_Rate_by_Sex.png", style="max-width:100%;"),
                    ),
                    ui.card(
                        ui.card_header("Summary statistics"),
                        ui.output_table("drug_utilization_table"),
                    ),
                    col_widths=[6, 6, 6, 6, 12],
                ),
            ),
            ui.nav_panel(
                "Indication",
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Indication for valproate use (30 days before to index date)"),
                        ui.img(src="Indication_valproate.png", style="max-width:100%;"),
                    ),
                    ui.card(
                        ui.card_header("Indication proportions"),
                        ui.output_table("indication_table"),
                    ),
                    col_widths=[7, 5],
                ),
            ),
        ),
    ),
    ui.nav_panel(
        "Characteristics",
        ui.card(
            ui.card_header("Table 1 — Valproate-user cohort characteristics, TMUCRD"),
            ui.output_table("char_table"),
        ),
    ),
    title=ui.tags.span(
        ui.tags.img(src="ohdsi-logo.png", height="32px", style="margin-right:10px;vertical-align:middle;"),
        "VALUE Study — TMUCRD Report",
        style="display:flex;align-items:center;",
    ),
    id="navbar",
)


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
def server(input, output, session):
    @render.download(filename="VALUE2026.zip")
    def download_package():
        yield (here / "VALUE2026.zip").read_bytes()

    @output
    @render.plot
    def prevalence_plot():
        lo, hi = input.yr_range()
        b = both[(both["Year"] >= lo) & (both["Year"] <= hi)]
        s = sex[(sex["Year"] >= lo) & (sex["Year"] <= hi)]

        fig, ax = plt.subplots(figsize=(8, 4.5))
        if "both" in input.series():
            ax.plot(b["Year"], b["Rate of valproate use (both)"] * 100, marker="o", label="Both sexes", color=COLOR_BOTH)
        if "male" in input.series():
            ax.plot(s["Year"], s["Rate of valproate use (male)"] * 100, marker="o", label="Male", color=COLOR_MALE)
        if "female" in input.series():
            ax.plot(s["Year"], s["Rate of valproate use (female)"] * 100, marker="o", label="Female", color=COLOR_FEMALE)

        ax.set_xlabel("Year")
        ax.set_ylabel("Rate of valproate use (%)")
        ax.set_title("Valproate use prevalence, TMUCRD")
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        return fig

    @output
    @render.table
    def prevalence_table():
        lo, hi = input.yr_range()
        merged = both.merge(sex, on="Year")
        merged = merged[(merged["Year"] >= lo) & (merged["Year"] <= hi)]
        return merged

    @output
    @render.table
    def char_table():
        return char[["_section", "Characteristic", "Count (n = 8,621)", "%"]].rename(
            columns={"_section": "Section"}
        )

    @output
    @render.table
    def drug_utilization_table():
        cols = [c for c in ["count", "mean", "sd", "min", "q25", "median", "q75", "max"] if c in du_wide.columns]
        return du_wide.reset_index()[["Variable", *cols]]

    @output
    @render.table
    def indication_table():
        return indication_pct.sort_values("Percentage", ascending=False).round(2)


app = App(app_ui, server, static_assets=here)
