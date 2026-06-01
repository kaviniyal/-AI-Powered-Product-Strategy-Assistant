import io
import pandas as pd
from pypdf import PdfReader


# ── Known sales CSV columns ───────────────────────────────────────────────────
SALES_COLS = {"Revenue_USD", "Profit_USD", "Units_Sold", "Customer_Rating"}


def _is_sales_csv(df: pd.DataFrame) -> bool:
    return SALES_COLS.issubset(set(df.columns))


# ── File extractors ───────────────────────────────────────────────────────────
def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            pages = [p.extract_text() or "" for p in reader.pages]
            text = "\n".join(pages)
            return text[:4000]  # cap to keep tokens lean
        except Exception as e:
            return f"[Could not parse PDF: {e}]"

    if ext == "txt":
        try:
            return file_bytes.decode("utf-8", errors="ignore")[:4000]
        except Exception:
            return "[Could not read text file]"

    if ext == "csv":
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
            return df.head(50).to_string(index=False)[:3000]
        except Exception:
            return "[Could not parse CSV]"

    return f"[Unsupported file type: {ext}]"


# ── Sales CSV ─────────────────────────────────────────────────────────────────
def load_and_summarize(file_path: str) -> dict:
    df = pd.read_csv(file_path, parse_dates=["Date"])

    product_stats = (
        df.groupby(["Product_ID", "Product_Name", "Category"])
        .agg(
            Total_Revenue=("Revenue_USD", "sum"),
            Total_Profit=("Profit_USD", "sum"),
            Total_Units=("Units_Sold", "sum"),
            Avg_Rating=("Customer_Rating", "mean"),
            Total_Returns=("Returns", "sum"),
            Total_New_Customers=("New_Customers", "sum"),
            Total_Marketing=("Marketing_Spend_USD", "sum"),
        )
        .reset_index()
        .round(2)
    )
    product_stats["Profit_Margin_Pct"] = (
        (product_stats["Total_Profit"] / product_stats["Total_Revenue"]) * 100
    ).round(1)
    product_stats["Return_Rate_Pct"] = (
        (product_stats["Total_Returns"] / product_stats["Total_Units"]) * 100
    ).round(2)

    cat_stats = (
        df.groupby("Category")
        .agg(Revenue=("Revenue_USD", "sum"), Profit=("Profit_USD", "sum"), Units=("Units_Sold", "sum"))
        .reset_index().round(2)
    )
    region_stats = (
        df.groupby("Region")
        .agg(Revenue=("Revenue_USD", "sum"), Units=("Units_Sold", "sum"))
        .reset_index().round(2)
    )
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    monthly = (
        df.groupby("Month")
        .agg(Revenue=("Revenue_USD", "sum"), Profit=("Profit_USD", "sum"))
        .reset_index().round(2)
    )

    reviews = []
    for pid, grp in df.groupby("Product_Name"):
        top = grp.nlargest(2, "Customer_Rating")[["Product_Name", "Customer_Rating", "Review"]]
        bot = grp.nsmallest(1, "Customer_Rating")[["Product_Name", "Customer_Rating", "Review"]]
        reviews.append(pd.concat([top, bot]))
    review_sample = pd.concat(reviews)[["Product_Name", "Customer_Rating", "Review"]].to_dict("records")

    kpis = {
        "total_revenue":       float(round(df["Revenue_USD"].sum(), 2)),
        "total_profit":        float(round(df["Profit_USD"].sum(), 2)),
        "total_units":         int(df["Units_Sold"].sum()),
        "avg_rating":          float(round(df["Customer_Rating"].mean(), 2)),
        "total_returns":       int(df["Returns"].sum()),
        "total_new_customers": int(df["New_Customers"].sum()),
        "date_range":          f"{df['Date'].min().date()} to {df['Date'].max().date()}",
        "num_products":        int(df["Product_Name"].nunique()),
        "num_regions":         int(df["Region"].nunique()),
    }

    return {
        "kpis": kpis,
        "product_stats":  product_stats.to_dict("records"),
        "category_stats": cat_stats.to_dict("records"),
        "region_stats":   region_stats.to_dict("records"),
        "monthly_trend":  monthly.to_dict("records"),
        "review_sample":  review_sample,
        "raw_df":         df,
    }


def load_from_bytes(file_bytes: bytes) -> dict:
    """Load a sales CSV from raw bytes (uploaded file)."""
    import tempfile, os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    result = load_and_summarize(tmp_path)
    os.unlink(tmp_path)
    return result


# ── Build contexts ────────────────────────────────────────────────────────────
def build_context_string(summary: dict) -> str:
    kpis = summary["kpis"]
    lines = [
        "=== BUSINESS DATA SUMMARY ===",
        f"Period: {kpis['date_range']}",
        f"Total Revenue: ${kpis['total_revenue']:,}",
        f"Total Profit: ${kpis['total_profit']:,}",
        f"Total Units Sold: {kpis['total_units']:,}",
        f"Avg Customer Rating: {kpis['avg_rating']}/5",
        f"Total Returns: {kpis['total_returns']}",
        f"Total New Customers: {kpis['total_new_customers']:,}",
        f"Products: {kpis['num_products']}, Regions: {kpis['num_regions']}",
        "",
        "=== PRODUCT PERFORMANCE ===",
    ]
    for p in summary["product_stats"]:
        lines.append(
            f"- {p['Product_Name']} ({p['Category']}): Revenue=${p['Total_Revenue']:,}, "
            f"Profit=${p['Total_Profit']:,}, Margin={p['Profit_Margin_Pct']}%, "
            f"Units={p['Total_Units']:,}, Rating={p['Avg_Rating']}, Returns={p['Return_Rate_Pct']}%"
        )
    lines += ["", "=== CATEGORY BREAKDOWN ==="]
    for c in summary["category_stats"]:
        lines.append(f"- {c['Category']}: Revenue=${c['Revenue']:,}, Profit=${c['Profit']:,}")

    lines += ["", "=== REGIONAL SALES ==="]
    for r in summary["region_stats"]:
        lines.append(f"- {r['Region']}: Revenue=${r['Revenue']:,}, Units={r['Units']:,}")

    lines += ["", "=== MONTHLY TREND ==="]
    for m in summary["monthly_trend"]:
        lines.append(f"- {m['Month']}: Revenue=${m['Revenue']:,}, Profit=${m['Profit']:,}")

    lines += ["", "=== CUSTOMER REVIEWS SAMPLE ==="]
    for r in summary["review_sample"]:
        lines.append(f"- [{r['Product_Name']} | Rating:{r['Customer_Rating']}] {r['Review']}")

    return "\n".join(lines)


def build_extra_context(extra_docs: list) -> str:
    """
    extra_docs: list of dicts with keys: category, filename, content
    """
    if not extra_docs:
        return ""
    lines = ["", "=== ADDITIONAL UPLOADED DOCUMENTS ==="]
    for doc in extra_docs:
        lines.append(f"\n--- {doc['category'].upper()}: {doc['filename']} ---")
        lines.append(doc["content"].strip())
    return "\n".join(lines)
