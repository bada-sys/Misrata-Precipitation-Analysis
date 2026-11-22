
from pathlib import Path
from io import BytesIO
import zipfile
import pandas as pd
import streamlit as st

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Misrata Precipitation Analysis",
    page_icon="🌧️",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
ZIP_NAME = "Misrata_Five_Platforms_Analysis_Complete_2001_2025.zip"
ZIP_PATH = BASE_DIR / ZIP_NAME

# =========================================================
# 2. LANGUAGE
# =========================================================
language = st.sidebar.selectbox(
    "Language / اللغة",
    ["العربية", "English"]
)
AR = language == "العربية"

if AR:
    title = "تحليل هطول الأمطار في مصراتة"
    subtitle = "تحليل خمسة منتجات مطرية خلال الفترة 2001–2025"
    overview = "نظرة عامة"
    figures_tab = "الرسوم البيانية"
    tables_tab = "الجداول والبيانات"
    comparison_tab = "المقارنة التفاعلية"
    methods_tab = "المنهجية ومصادر البيانات"
    downloads_tab = "تنزيل النتائج"
    select_figure = "اختر الرسم البياني"
    select_table = "اختر الجدول"
    no_data = "لا توجد بيانات متاحة للعرض."
    missing_zip = "لم يتم العثور على ملف النتائج ZIP في المستودع."
    comparison_title = "مقارنة تفاعلية بين المنتجات"
    choose_x = "اختر المحور الأفقي"
    choose_y = "اختر المتغيرات للمقارنة"
    products_title = "منتجات بيانات الأمطار"
else:
    title = "Misrata Precipitation Analysis"
    subtitle = "Analysis of five precipitation products, 2001–2025"
    overview = "Overview"
    figures_tab = "Figures"
    tables_tab = "Tables and Data"
    comparison_tab = "Interactive Comparison"
    methods_tab = "Methodology and Data Sources"
    downloads_tab = "Download Results"
    select_figure = "Select a figure"
    select_table = "Select a table"
    no_data = "No data available."
    missing_zip = "The results ZIP file was not found in the repository."
    comparison_title = "Interactive Product Comparison"
    choose_x = "Select horizontal axis"
    choose_y = "Select variables to compare"
    products_title = "Precipitation Data Products"

# =========================================================
# 3. LOAD PROJECT ZIP
# =========================================================
@st.cache_data
def load_zip(path):
    with zipfile.ZipFile(path, "r") as archive:
        return {
            name: archive.read(name)
            for name in archive.namelist()
            if not name.endswith("/")
        }

if not ZIP_PATH.exists():
    st.error(missing_zip)
    st.info(
        f"Expected file: {ZIP_NAME}"
    )
    st.stop()

try:
    project_files = load_zip(ZIP_PATH)
except Exception as error:
    st.error(f"Could not read ZIP file: {error}")
    st.stop()

figures = sorted(
    name for name in project_files
    if name.startswith("Figures/") and name.lower().endswith(".png")
)

tables = sorted(
    name for name in project_files
    if name.startswith("Tables/") and name.lower().endswith(".csv")
)

# =========================================================
# 4. READ CSV TABLES
# =========================================================

@st.cache_data
def read_table(file_name, file_bytes):
    try:
        if "Monthly_Climatology" in file_name:
            df = pd.read_csv(
                BytesIO(file_bytes),
                header=[0, 1],
                encoding="utf-8-sig"
            )
            df.columns = [
                " - ".join(
                    str(part) for part in col
                    if str(part) != "nan"
                )
                for col in df.columns
            ]
        else:
            df = pd.read_csv(
                BytesIO(file_bytes),
                encoding="utf-8-sig"
            )
    except Exception:
        df = pd.read_csv(BytesIO(file_bytes))

    # Make every column name unique
    seen = {}
    unique_columns = []

    for column in df.columns:
        name = str(column).strip()
        count = seen.get(name, 0)

        if count == 0:
            unique_columns.append(name)
        else:
            unique_columns.append(f"{name} ({count + 1})")

        seen[name] = count + 1

    df.columns = unique_columns

    return df


# =========================================================
# 5. HEADER
# =========================================================
st.title("🌧️ " + title)
st.subheader(subtitle)

st.markdown(
    "**Misrata Airport, Libya | 2001–2025**"
    if not AR else
    "**مطار مصراتة، ليبيا | 2001–2025**"
)

st.divider()

# =========================================================
# 6. OVERVIEW
# =========================================================
st.header(overview)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Figures / الرسوم",
    len(figures)
)
c2.metric(
    "Tables / الجداول",
    len(tables)
)
c3.metric(
    "Years / السنوات",
    "25"
)
c4.metric(
    "Products / المنتجات",
    "5"
)

st.markdown(
    """
    This research project analyzes precipitation data for Misrata Airport,
    Libya, using five precipitation products over 25 years (2001–2025).
    """
    if not AR else
    """
    يعرض هذا المشروع تحليل بيانات الأمطار عند نقطة مطار مصراتة في ليبيا،
    باستخدام خمسة منتجات مطرية خلال 25 سنة من 2001 إلى 2025.
    """
)

st.subheader(products_title)

if AR:
    product_names = [
        "CHIRPS V3 SAT Daily — يومي",
        "CHIRPS V3 RNL Daily — يومي",
        "CHIRPS V3 Pentadal — خماسي",
        "NASA POWER Daily — يومي",
        "ERA5-Land Daily UTC — يومي"
    ]
else:
    product_names = [
        "CHIRPS V3 SAT Daily",
        "CHIRPS V3 RNL Daily",
        "CHIRPS V3 Pentadal",
        "NASA POWER Daily",
        "ERA5-Land Daily UTC"
    ]

for product in product_names:
    st.markdown(f"- {product}")

# =========================================================
# 7. MAIN TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    overview if AR else "Overview",
    figures_tab,
    tables_tab,
    comparison_tab,
    methods_tab + " / " + downloads_tab
])

# =========================================================
# 8. FIGURES GALLERY
# =========================================================
with tab2:
    st.header(figures_tab)

    if figures:
        figure_labels = {
            name: name.split("/")[-1]
            for name in figures
        }

        selected_figure = st.selectbox(
            select_figure,
            figures,
            format_func=lambda x: figure_labels[x]
        )

        st.image(
            BytesIO(project_files[selected_figure]),
            caption=figure_labels[selected_figure],
            use_container_width=True
        )

        st.divider()

        st.subheader(
            "معرض الرسوم الكامل" if AR else "Complete Figures Gallery"
        )

        for start in range(0, len(figures), 2):
            cols = st.columns(2)
            for col, figure in zip(cols, figures[start:start + 2]):
                with col:
                    st.image(
                        BytesIO(project_files[figure]),
                        caption=figure.split("/")[-1],
                        use_container_width=True
                    )
    else:
        st.warning(no_data)

# =========================================================
# 9. TABLES
# =========================================================
with tab3:
    st.header(tables_tab)

    if tables:
        selected_table = st.selectbox(
            select_table,
            tables,
            format_func=lambda x: x.split("/")[-1]
        )

        try:
            df = read_table(
                selected_table,
                project_files[selected_table]
            )

            st.caption(
                f"Rows: {len(df):,} | Columns: {len(df.columns)}"
            )

            st.dataframe(
                df,
                use_container_width=True,
                height=500
            )

            st.download_button(
                "تنزيل الجدول CSV" if AR else "Download CSV table",
                data=project_files[selected_table],
                file_name=selected_table.split("/")[-1],
                mime="text/csv"
            )
        except Exception as error:
            st.error(str(error))
    else:
        st.warning(no_data)

# =========================================================
# 10. INTERACTIVE COMPARISON
# =========================================================
with tab4:
    st.header(comparison_title)

    comparison_tables = [
        name for name in tables
        if any(key in name for key in [
            "Daily_Common_Data",
            "Pentadal_Matched",
            "Annual_Totals",
            "Monthly_Totals",
            "Seasonal_Totals"
        ])
    ]

    if comparison_tables:
        selected_comparison = st.selectbox(
            "جدول المقارنة" if AR else "Comparison dataset",
            comparison_tables,
            format_func=lambda x: x.split("/")[-1]
        )

        data = read_table(
            selected_comparison,
            project_files[selected_comparison]
        )

        numeric_columns = data.select_dtypes(
            include="number"
        ).columns.tolist()

        all_columns = data.columns.tolist()

        if numeric_columns:
            possible_x = [
                col for col in all_columns
                if col not in numeric_columns
            ]

            x_options = possible_x if possible_x else all_columns

            x_col = st.selectbox(
                choose_x,
                x_options
            )

            y_cols = st.multiselect(
                choose_y,
                numeric_columns,
                default=numeric_columns[:min(3, len(numeric_columns))]
            )

            if y_cols:
                chart_data = data[[x_col] + y_cols].copy()
                chart_data = chart_data.set_index(x_col)

                st.line_chart(chart_data)

                st.dataframe(
                    data[[x_col] + y_cols],
                    use_container_width=True
                )
            else:
                st.info(
                    "اختر متغيرًا رقميًا واحدًا على الأقل."
                    if AR else
                    "Select at least one numeric variable."
                )
        else:
            st.warning(
                "لا يحتوي الجدول المختار على أعمدة رقمية مناسبة."
                if AR else
                "The selected table has no suitable numeric columns."
            )
    else:
        st.warning(no_data)

# =========================================================
# 11. METHODOLOGY AND DOWNLOADS
# =========================================================
with tab5:
    st.header(methods_tab)

    st.markdown(
        """
        **منطقة الدراسة:** مطار مصراتة، ليبيا.

        **الفترة الزمنية:** 2001–2025.

        **المنتجات المطرية:**
        - CHIRPS V3 SAT Daily
        - CHIRPS V3 RNL Daily
        - CHIRPS V3 Pentadal
        - NASA POWER Daily
        - ERA5-Land Daily UTC

        **التحليلات المنفذة:**
        - المجاميع السنوية والشهرية والموسمية.
        - المناخ الشهري والفترات الخماسية.
        - الإحصاءات الوصفية.
        - المقارنات الإحصائية الزوجية.
        - مراقبة جودة البيانات.
        - الرسوم البيانية والجداول المقارنة.

        **ملاحظة منهجية مهمة:**
        تمثل النتائج بيانات نقطة الدراسة عند مطار مصراتة،
        ولا تمثل متوسطًا مكانيًا لكامل مدينة مصراتة.

        كما أن منتجات الأمطار تختلف في منهجيات إنتاجها
        وتعريفاتها الزمنية؛ لذلك لا ينبغي تفسير جميع الفروق
        بينها على أنها تغير حقيقي في كمية الأمطار فقط.
        """
        if AR else
        """
        **Study area:** Misrata Airport, Libya.

        **Analysis period:** 2001–2025.

        **Precipitation products:**
        - CHIRPS V3 SAT Daily
        - CHIRPS V3 RNL Daily
        - CHIRPS V3 Pentadal
        - NASA POWER Daily
        - ERA5-Land Daily UTC

        **Analyses:** Annual, monthly and seasonal totals,
        climatology, pentadal analysis, descriptive statistics,
        pairwise comparisons, quality control, figures and tables.

        **Important methodological note:**
        Results represent the study point at Misrata Airport,
        not a spatial average for the entire city.

        The precipitation products have different production
        methodologies and temporal definitions. Differences
        should not automatically be interpreted as actual
        precipitation changes.
        """
    )

    st.divider()
    st.header(downloads_tab)

    download_items = [
        (
            "Misrata_Five_Platforms_Precipitation_Analysis_2001_2025.xlsx",
            "Excel"
        ),
        (
            "Misrata_Precipitation_Analysis_Report_2001_2025.docx",
            "Word"
        )
    ]

    for file_name, label in download_items:
        if file_name in project_files:
            st.download_button(
                f"تنزيل {label}" if AR else f"Download {label}",
                data=project_files[file_name],
                file_name=file_name,
                key=file_name
            )

    st.download_button(
        "تنزيل حزمة النتائج الكاملة ZIP"
        if AR else "Download complete results ZIP",
        data=ZIP_PATH.read_bytes(),
        file_name=ZIP_NAME,
        mime="application/zip"
    )

    st.caption(
        "جميع ملفات النتائج المعروضة مأخوذة من حزمة المشروع الأصلية."
        if AR else
        "All displayed results are read from the original project archive."
    )

# =========================================================
# 12. FOOTER
# =========================================================
st.divider()

st.markdown(
    """
    **إعداد وتحليل: Dr. Badr Geo**

    Misrata, Libya | 2001–2025
    """
)
