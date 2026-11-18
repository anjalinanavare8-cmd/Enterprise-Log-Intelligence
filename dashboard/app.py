import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# ============================================================
# ENTERPRISE LOG INTELLIGENCE & SYSTEM MONITORING DASHBOARD
# Streamlit frontend connected to the project's FastAPI backend
# ============================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Enterprise Log Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------- THEME ---------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: #0b0f19 !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stHeader"],
    [data-testid="stToolbar"] {
        background: #0b0f19 !important;
    }
    [data-testid="stSidebar"] {
        background: #080c15 !important;
        border-right: 1px solid #29364b;
        min-width: 250px;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 1.4rem 1rem;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #cbd5e1 !important;
    }
    .block-container {
        max-width: 1600px;
        padding-top: 1.6rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #e2e8f0 !important;
    }
    [data-testid="stMetric"] {
        background: #141c2c;
        border: 1px solid #29364b;
        border-radius: 9px;
        padding: 15px;
    }
    [data-testid="stMetricLabel"] {
        color: #91a0b8 !important;
    }
    [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
    }
    .alert-banner {
        background: #25151c;
        border: 1px solid #7f2936;
        color: #ff8790;
        border-radius: 7px;
        padding: 12px 15px;
        font-weight: 600;
        margin-bottom: 15px;
    }
    .service-card {
        background: #111827;
        border: 1px solid #29364b;
        border-left: 4px solid #64748b;
        border-radius: 7px;
        padding: 13px;
        margin-bottom: 9px;
    }
    .muted {
        color: #91a0b8;
        font-size: 12px;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid #29364b;
        border-radius: 8px;
    }
    div[data-baseweb="select"] > div {
        background-color: #141c2c;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------- CHART SETTINGS ----------------------

CHART_COLORS = [
    "#3B82F6",
    "#EF4444",
    "#F59E0B",
    "#22C55E",
    "#A78BFA",
    "#06B6D4",
    "#EC4899",
]


def style_chart(fig, ax, title=None):
    """Apply the dashboard's dark style to a Matplotlib chart."""
    fig.patch.set_facecolor("#111827")
    ax.set_facecolor("#111827")
    ax.tick_params(colors="#cbd5e1")
    ax.xaxis.label.set_color("#cbd5e1")
    ax.yaxis.label.set_color("#cbd5e1")
    ax.title.set_color("#f1f5f9")
    for spine in ax.spines.values():
        spine.set_color("#29364b")
    ax.grid(axis="y", color="#29364b", linestyle="--", alpha=0.65)
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, color="#f1f5f9", pad=12)


def show_chart(fig):
    """Display a chart and close its Matplotlib figure afterwards."""
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ------------------------- API HELPERS -----------------------

@st.cache_data(ttl=5, show_spinner=False)
def fetch_api_data(endpoint):
    """Get JSON data from one FastAPI endpoint."""
    response = requests.get(f"{API_URL}{endpoint}", timeout=10)
    response.raise_for_status()
    return response.json()


def load_endpoint(endpoint, default):
    try:
        return fetch_api_data(endpoint)
    except requests.RequestException as exc:
        st.error(f"Could not load {endpoint}: {exc}")
        return default


def run_anomaly_detection():
    """Ask FastAPI to detect anomalies and create database incidents."""
    response = requests.post(
        f"{API_URL}/incidents/detect-anomalies",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


# ------------------------- SIDEBAR ---------------------------

with st.sidebar:
    st.markdown("## 📡 E L I P")
    st.caption("ENTERPRISE MONITORING")
    st.divider()

    selected_page = st.radio(
        "NAVIGATION",
        ["Overview", "Analytics", "Services", "Incidents", "Live Logs"],
        key="navigation",
    )

    st.divider()
    st.markdown("### SYSTEM STATUS")
    st.markdown("🟢 FastAPI monitoring")
    st.markdown("🟢 SQLite database")
    st.caption("Python • Streamlit • FastAPI")

    st.divider()
    if st.button("↻ Refresh dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption("Enterprise Log Intelligence Platform")
    st.caption("Project version 1.0")


# -------------------------- LOAD DATA ------------------------

with st.spinner("Loading monitoring data..."):
    service_data = load_endpoint("/services/", {})
    incident_data = load_endpoint("/incidents/", [])
    log_data = load_endpoint("/logs/?limit=500", [])

if not isinstance(service_data, dict):
    service_data = {}
if not isinstance(incident_data, list):
    incident_data = []
if not isinstance(log_data, list):
    log_data = []

services = service_data.get("services", [])
incidents = incident_data
logs = log_data

services_df = pd.DataFrame(services)
incidents_df = pd.DataFrame(incidents)
logs_df = pd.DataFrame(logs)

# Ensure expected columns exist, including when an endpoint returns no rows.
for column in [
    "service", "total_logs", "errors", "warnings",
    "error_rate_percent", "average_response_time_ms", "health"
]:
    if column not in services_df.columns:
        services_df[column] = pd.Series(dtype="object")

for column in [
    "id", "incident_code", "service", "severity", "status",
    "detection_method", "reasons", "created_at"
]:
    if column not in incidents_df.columns:
        incidents_df[column] = pd.Series(dtype="object")

for column in [
    "id", "timestamp", "service", "level", "error_code",
    "message", "response_time"
]:
    if column not in logs_df.columns:
        logs_df[column] = pd.Series(dtype="object")

if not logs_df.empty:
    logs_df["level"] = logs_df["level"].fillna("UNKNOWN").astype(str).str.upper()
    logs_df["timestamp_parsed"] = pd.to_datetime(
        logs_df["timestamp"], errors="coerce", utc=True
    )
    logs_df["response_time"] = pd.to_numeric(
        logs_df["response_time"], errors="coerce"
    )
else:
    logs_df["timestamp_parsed"] = pd.Series(dtype="datetime64[ns, UTC]")

if not incidents_df.empty:
    incidents_df["status"] = incidents_df["status"].fillna("Unknown").astype(str)
    incidents_df["severity"] = incidents_df["severity"].fillna("Unknown").astype(str).str.upper()

# ------------------------- KPI VALUES ------------------------

total_logs = len(logs_df)
total_services = len(services_df)
total_errors = int(pd.to_numeric(services_df["errors"], errors="coerce").fillna(0).sum())
total_warnings = int(pd.to_numeric(services_df["warnings"], errors="coerce").fillna(0).sum())

if not incidents_df.empty:
    active_incidents = int(
        incidents_df["status"].isin(["Open", "Investigating"]).sum()
    )
else:
    active_incidents = 0

critical_services = int(
    (services_df["health"].astype(str).str.upper() == "CRITICAL").sum()
) if not services_df.empty else 0

# ------------------------- PAGE HEADER -----------------------

banner_text = (
    f"⚠️ SYSTEM MONITORING  |  {active_incidents} ACTIVE INCIDENT(S)  |  "
    f"{critical_services} CRITICAL SERVICE(S)"
)
st.markdown(
    f'<div class="alert-banner">{banner_text}</div>',
    unsafe_allow_html=True,
)

st.title("Enterprise Log Intelligence")
st.caption("Service health • Application logs • Incident management • Analytics")

# -------------------- AUTOMATIC ANOMALY DETECTION --------------------

action_col, info_col = st.columns([1, 3])

with action_col:
    if st.button(
        "Run Anomaly Detection",
        type="primary",
        use_container_width=True,
        help="Analyze database logs and create incidents for newly detected anomalies.",
    ):
        try:
            with st.spinner("Analyzing logs and creating incidents..."):
                detection_result = run_anomaly_detection()

            st.session_state["last_anomaly_result"] = detection_result
            st.cache_data.clear()
            st.rerun()

        except requests.RequestException as exc:
            st.error(f"Could not run anomaly detection: {exc}")
        except ValueError as exc:
            st.error(f"The API returned an invalid response: {exc}")

with info_col:
    st.caption(
        "Runs rule-based and Isolation Forest detection using logs stored "
        "in SQLite. Existing Open or Investigating incidents are not duplicated."
    )

# Show the most recent result after the dashboard refreshes.
if "last_anomaly_result" in st.session_state:
    detection_result = st.session_state["last_anomaly_result"]

    st.success(
        "Anomaly detection completed. "
        f"{detection_result.get('incidents_created', 0)} new incident(s) created; "
        f"{detection_result.get('existing_incidents_skipped', 0)} existing incident(s) skipped."
    )

    with st.expander("View latest anomaly detection results", expanded=True):
        st.write(
            f"**Services analyzed:** "
            f"{detection_result.get('total_services_analyzed', 0)}"
        )
        st.write(
            f"**Anomalies detected:** "
            f"{detection_result.get('total_anomalies_detected', 0)}"
        )

        created = detection_result.get("created_incidents", [])
        skipped = detection_result.get("skipped_incidents", [])

        st.markdown("**New incidents**")
        if created:
            st.dataframe(
                pd.DataFrame(created),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No new incidents were created.")

        st.markdown("**Skipped services**")
        if skipped:
            st.dataframe(
                pd.DataFrame(skipped),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No services were skipped.")

# KPI row
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("TOTAL LOGS", f"{total_logs:,}")
k2.metric("ERRORS", f"{total_errors:,}")
k3.metric("WARNINGS", f"{total_warnings:,}")
k4.metric("ACTIVE INCIDENTS", f"{active_incidents:,}")
k5.metric("SERVICES", f"{total_services:,}")

st.write("")


# ============================================================
# OVERVIEW
# ============================================================

if selected_page == "Overview":

    st.subheader("Log Volume & Error Trend")

    if not logs_df.empty and logs_df["timestamp_parsed"].notna().any():
        trend_df = logs_df.dropna(subset=["timestamp_parsed"]).copy()
        trend_df["time_group"] = trend_df["timestamp_parsed"].dt.strftime("%H:%M")
        trend = (
            trend_df.groupby("time_group")
            .agg(
                total_logs=("level", "size"),
                errors=("level", lambda values: values.isin(["ERROR", "CRITICAL"]).sum()),
            )
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(12, 3.4))
        ax.plot(
            trend["time_group"], trend["total_logs"],
            color="#3B82F6", marker="o", linewidth=2, label="Log volume"
        )
        ax.plot(
            trend["time_group"], trend["errors"],
            color="#EF4444", marker="o", linewidth=2, label="Errors"
        )
        ax.set_xlabel("Time")
        ax.set_ylabel("Number of logs")
        ax.legend(facecolor="#111827", labelcolor="white")
        style_chart(fig, ax, "Log Volume vs Errors")
        show_chart(fig)
    else:
        st.info("No valid timestamps are available for the trend chart yet.")

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("Service Health")
        if services_df.empty:
            st.info("No services are available yet.")
        else:
            for _, service in services_df.iterrows():
                health = str(service["health"]).upper()
                if health == "CRITICAL":
                    color, icon = "#EF4444", "🔴"
                elif health == "WARNING":
                    color, icon = "#F59E0B", "🟠"
                else:
                    color, icon = "#22C55E", "🟢"

                st.markdown(
                    f"""
                    <div class="service-card" style="border-left-color:{color}">
                        {icon} <b>{service['service']}</b>
                        <span style="float:right;color:{color};font-weight:700">{health}</span>
                        <br><span class="muted">
                        {service['total_logs']} logs &nbsp;|&nbsp;
                        {service['errors']} errors &nbsp;|&nbsp;
                        {service['error_rate_percent']}% error rate
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with right:
        st.subheader("Top Error Patterns")
        error_rows = logs_df[logs_df["level"].isin(["ERROR", "CRITICAL"])]
        if error_rows.empty:
            st.info("No error records are available.")
        else:
            error_patterns = (
                error_rows["error_code"].fillna("Unknown")
                .value_counts()
                .rename_axis("Error Code")
                .reset_index(name="Occurrences")
            )
            st.dataframe(error_patterns, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Monitoring Charts")
    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown("**Log Level Distribution**")
        if logs_df.empty:
            st.info("No log data is available.")
        else:
            counts = logs_df["level"].value_counts()
            fig, ax = plt.subplots(figsize=(6, 4))
            fig.patch.set_facecolor("#111827")
            ax.set_facecolor("#111827")
            ax.pie(
                counts.values,
                labels=counts.index,
                autopct="%1.1f%%",
                colors=CHART_COLORS[:len(counts)],
                textprops={"color": "white"},
                startangle=90,
            )
            ax.set_title("Logs by Level", color="white")
            show_chart(fig)

    with chart_right:
        st.markdown("**Errors by Service**")
        if services_df.empty:
            st.info("No service data is available.")
        else:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(services_df["service"], services_df["errors"], color="#EF4444")
            ax.set_ylabel("Error count")
            style_chart(fig, ax, "Service Error Comparison")
            show_chart(fig)

    st.divider()
    st.subheader("Recent Application Logs")
    if logs_df.empty:
        st.info("No recent logs are available.")
    else:
        recent = logs_df.drop(columns=["timestamp_parsed"], errors="ignore").head(10)
        st.dataframe(recent, use_container_width=True, hide_index=True)


# ============================================================
# ANALYTICS
# ============================================================

elif selected_page == "Analytics":

    st.title("Advanced Analytics")
    st.caption("Compare service performance and investigate error patterns.")

    # Chart 1: error rate by service
    st.subheader("1. Error Rate by Service")
    if not services_df.empty:
        fig, ax = plt.subplots(figsize=(10, 3.5))
        ax.bar(
            services_df["service"],
            pd.to_numeric(services_df["error_rate_percent"], errors="coerce").fillna(0),
            color="#EF4444",
        )
        ax.set_ylabel("Error rate (%)")
        style_chart(fig, ax, "Service Error Rate")
        show_chart(fig)
    else:
        st.info("No service data is available.")

    # Chart 2: average response time
    st.subheader("2. Average Response Time")
    if not services_df.empty:
        fig, ax = plt.subplots(figsize=(10, 3.5))
        ax.barh(
            services_df["service"],
            pd.to_numeric(services_df["average_response_time_ms"], errors="coerce").fillna(0),
            color="#3B82F6",
        )
        ax.set_xlabel("Milliseconds")
        style_chart(fig, ax, "Average Response Time by Service")
        show_chart(fig)
    else:
        st.info("No response-time data is available.")

    # Charts 3 and 4: incident distributions
    st.subheader("3. Incident Analysis")
    sev_col, status_col = st.columns(2)

    with sev_col:
        st.markdown("**Incident Severity**")
        if incidents_df.empty:
            st.info("No incidents are available.")
        else:
            severity_counts = incidents_df["severity"].value_counts()
            fig, ax = plt.subplots(figsize=(6, 4))
            fig.patch.set_facecolor("#111827")
            ax.pie(
                severity_counts.values,
                labels=severity_counts.index,
                autopct="%1.1f%%",
                colors=CHART_COLORS[:len(severity_counts)],
                textprops={"color": "white"},
                startangle=90,
            )
            ax.set_title("Severity Distribution", color="white")
            show_chart(fig)

    with status_col:
        st.markdown("**Incident Status**")
        if incidents_df.empty:
            st.info("No incidents are available.")
        else:
            status_counts = incidents_df["status"].value_counts()
            fig, ax = plt.subplots(figsize=(6, 4))
            fig.patch.set_facecolor("#111827")
            ax.pie(
                status_counts.values,
                labels=status_counts.index,
                autopct="%1.1f%%",
                colors=CHART_COLORS[:len(status_counts)],
                wedgeprops={"width": 0.45},
                textprops={"color": "white"},
                startangle=90,
            )
            ax.set_title("Incident Status", color="white")
            show_chart(fig)

    # Chart 5: most frequent error codes
    st.subheader("4. Most Frequent Error Codes")
    error_rows = logs_df[logs_df["level"].isin(["ERROR", "CRITICAL"])]
    if error_rows.empty:
        st.info("No error-code records are available.")
    else:
        code_counts = error_rows["error_code"].fillna("Unknown").value_counts().head(10)
        fig, ax = plt.subplots(figsize=(10, 3.5))
        ax.bar(code_counts.index.astype(str), code_counts.values, color="#F59E0B")
        ax.set_ylabel("Occurrences")
        style_chart(fig, ax, "Error Code Frequency")
        show_chart(fig)

    # Chart 6: response time distribution
    st.subheader("5. Response Time Distribution")
    response_values = logs_df["response_time"].dropna()
    if response_values.empty:
        st.info("No response-time values are available.")
    else:
        fig, ax = plt.subplots(figsize=(10, 3.5))
        ax.hist(
            response_values,
            bins=min(10, max(1, len(response_values))),
            color="#A78BFA",
            edgecolor="#111827",
        )
        ax.set_xlabel("Response time (ms)")
        ax.set_ylabel("Number of logs")
        style_chart(fig, ax, "Response Time Distribution")
        show_chart(fig)

    # Chart 7: warning and error counts by service
    st.subheader("6. Errors and Warnings by Service")
    if not services_df.empty:
        x = range(len(services_df))
        width = 0.36
        fig, ax = plt.subplots(figsize=(10, 3.5))
        ax.bar(
            [i - width / 2 for i in x],
            pd.to_numeric(services_df["errors"], errors="coerce").fillna(0),
            width=width,
            label="Errors",
            color="#EF4444",
        )
        ax.bar(
            [i + width / 2 for i in x],
            pd.to_numeric(services_df["warnings"], errors="coerce").fillna(0),
            width=width,
            label="Warnings",
            color="#F59E0B",
        )
        ax.set_xticks(list(x))
        ax.set_xticklabels(services_df["service"])
        ax.legend(facecolor="#111827", labelcolor="white")
        ax.set_ylabel("Count")
        style_chart(fig, ax, "Errors vs Warnings")
        show_chart(fig)

    st.subheader("Service Analytics Table")
    if not services_df.empty:
        st.dataframe(services_df, use_container_width=True, hide_index=True)


# ============================================================
# SERVICES
# ============================================================

elif selected_page == "Services":

    st.title("Service Monitoring")
    st.caption("Health indicators and performance for each monitored service.")

    if services_df.empty:
        st.info("No services have been recorded yet.")
    else:
        for _, service in services_df.iterrows():
            health = str(service["health"]).upper()
            with st.container(border=True):
                title_col, status_col = st.columns([3, 1])
                title_col.subheader(str(service["service"]))
                status_col.markdown(f"**{health}**")

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Logs", int(service["total_logs"]))
                m2.metric("Errors", int(service["errors"]))
                m3.metric("Warnings", int(service["warnings"]))
                m4.metric("Error Rate", f"{service['error_rate_percent']}%")

                error_rate = float(service["error_rate_percent"])
                st.progress(min(max(error_rate / 100, 0.0), 1.0))
                st.caption(
                    f"Average response time: "
                    f"{service['average_response_time_ms']} ms"
                )


# ============================================================
# INCIDENTS
# ============================================================

elif selected_page == "Incidents":

    st.title("Incident Management")
    st.caption("Review incident severity, status and investigation records.")

    if incidents_df.empty:
        st.info("No incidents have been recorded yet.")
    else:
        filter1, filter2 = st.columns(2)

        status_options = ["All"] + sorted(incidents_df["status"].dropna().unique().tolist())
        severity_options = ["All"] + sorted(incidents_df["severity"].dropna().unique().tolist())

        chosen_status = filter1.selectbox("Filter by status", status_options)
        chosen_severity = filter2.selectbox("Filter by severity", severity_options)

        filtered_incidents = incidents_df.copy()

        if chosen_status != "All":
            filtered_incidents = filtered_incidents[
                filtered_incidents["status"] == chosen_status
            ]

        if chosen_severity != "All":
            filtered_incidents = filtered_incidents[
                filtered_incidents["severity"] == chosen_severity
            ]

        st.write(f"Incidents displayed: {len(filtered_incidents)}")
        st.dataframe(
            filtered_incidents,
            use_container_width=True,
            hide_index=True,
        )

        incident_csv = filtered_incidents.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Incident Report",
            data=incident_csv,
            file_name="incident_report.csv",
            mime="text/csv",
        )


# ============================================================
# LIVE LOGS
# ============================================================

elif selected_page == "Live Logs":

    st.title("Application Log Explorer")
    st.caption("Filter, inspect and download application logs.")

    if logs_df.empty:
        st.info("No application logs have been recorded yet.")
    else:
        filter1, filter2 = st.columns(2)

        service_options = ["All"] + sorted(logs_df["service"].dropna().unique().tolist())
        level_options = ["All"] + sorted(logs_df["level"].dropna().unique().tolist())

        chosen_service = filter1.selectbox("Filter by service", service_options)
        chosen_level = filter2.selectbox("Filter by log level", level_options)

        filtered_logs = logs_df.copy()

        if chosen_service != "All":
            filtered_logs = filtered_logs[filtered_logs["service"] == chosen_service]

        if chosen_level != "All":
            filtered_logs = filtered_logs[filtered_logs["level"] == chosen_level]

        display_logs = filtered_logs.drop(
            columns=["timestamp_parsed"], errors="ignore"
        )

        st.write(f"Matching records: {len(display_logs)}")
        st.dataframe(display_logs, use_container_width=True, hide_index=True)

        log_csv = display_logs.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Filtered Logs CSV",
            data=log_csv,
            file_name="application_logs.csv",
            mime="text/csv",
        )


# --------------------------- FOOTER --------------------------

st.divider()
st.markdown(
    """
    <div style="text-align:center;color:#8290a6;font-size:12px;">
        ENTERPRISE LOG INTELLIGENCE & PREDICTIVE SYSTEM MONITORING PLATFORM
        <br>
        Built with Python • Streamlit • FastAPI • SQLite • Pandas
    </div>
    """,
    unsafe_allow_html=True,
)
