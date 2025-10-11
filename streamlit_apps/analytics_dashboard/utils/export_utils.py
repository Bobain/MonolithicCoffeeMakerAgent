"""
Export Utilities for Analytics Dashboard

This module provides functions for generating CSV and PDF reports from analytics data.
Supports data export for download via Streamlit's download_button component.

Author: Analytics Dashboard Team
Created: 2025-10-11
"""

import io
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
import streamlit as st


def generate_csv_export(df: pd.DataFrame, filename: str = "export.csv") -> bytes:
    """
    Generate CSV export data from a pandas DataFrame.

    Converts the DataFrame to CSV format and returns it as bytes,
    suitable for use with Streamlit's download_button.

    Args:
        df: pandas DataFrame to export
        filename: Name for the exported file (default: "export.csv")

    Returns:
        bytes: UTF-8 encoded CSV data

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        >>> csv_bytes = generate_csv_export(df, "my_data.csv")
        >>> st.download_button(
        ...     label="Download CSV",
        ...     data=csv_bytes,
        ...     file_name="my_data.csv",
        ...     mime="text/csv"
        ... )

    Note:
        - Uses UTF-8 encoding with BOM for Excel compatibility
        - Includes index in export by default
        - Handles missing values appropriately
    """
    # Create a string buffer
    buffer = io.StringIO()

    # Write DataFrame to CSV in the buffer
    df.to_csv(buffer, index=True, encoding="utf-8-sig")

    # Get the CSV string and encode to bytes
    csv_string = buffer.getvalue()
    csv_bytes = csv_string.encode("utf-8-sig")

    return csv_bytes


def generate_pdf_report(
    stats_dict: Dict[str, Any], charts_data: Optional[Dict[str, Any]] = None, filename: str = "report.pdf"
) -> bytes:
    """
    Generate a PDF report with summary statistics and chart information.

    Creates a simple text-based PDF report using reportlab if available,
    otherwise falls back to a plain text format.

    Args:
        stats_dict: Dictionary containing summary statistics to include
        charts_data: Optional dictionary with information about charts/visualizations
        filename: Name for the exported file (default: "report.pdf")

    Returns:
        bytes: PDF data or plain text data if reportlab unavailable

    Example:
        >>> stats = {
        ...     'total_tasks': 150,
        ...     'completed_tasks': 120,
        ...     'avg_completion_time': '2.5 hours'
        ... }
        >>> charts = {
        ...     'task_distribution': 'Bar chart showing task types',
        ...     'completion_trends': 'Line chart showing completion over time'
        ... }
        >>> pdf_bytes = generate_pdf_report(stats, charts, "analytics_report.pdf")
        >>> st.download_button(
        ...     label="Download PDF Report",
        ...     data=pdf_bytes,
        ...     file_name="analytics_report.pdf",
        ...     mime="application/pdf"
        ... )

    Note:
        - Requires reportlab package for full PDF generation
        - Falls back to text format if reportlab is not available
        - Includes generation timestamp
    """
    try:
        # Try to import reportlab for PDF generation
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors

        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            "CustomTitle", parent=styles["Heading1"], fontSize=24, textColor=colors.HexColor("#1f77b4"), spaceAfter=30
        )
        story.append(Paragraph("Analytics Dashboard Report", title_style))
        story.append(Spacer(1, 12))

        # Generation date
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"<b>Generated:</b> {date_str}", styles["Normal"]))
        story.append(Spacer(1, 20))

        # Summary Statistics Section
        story.append(Paragraph("Summary Statistics", styles["Heading2"]))
        story.append(Spacer(1, 12))

        # Create table for statistics
        stats_data = [["Metric", "Value"]]
        for key, value in stats_dict.items():
            # Format key: replace underscores with spaces and title case
            formatted_key = key.replace("_", " ").title()
            stats_data.append([formatted_key, str(value)])

        stats_table = Table(stats_data, colWidths=[3 * inch, 3 * inch])
        stats_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )
        story.append(stats_table)
        story.append(Spacer(1, 20))

        # Charts Information Section
        if charts_data:
            story.append(Paragraph("Visualizations Included", styles["Heading2"]))
            story.append(Spacer(1, 12))

            for chart_name, chart_description in charts_data.items():
                formatted_name = chart_name.replace("_", " ").title()
                story.append(Paragraph(f"<b>{formatted_name}:</b> {chart_description}", styles["Normal"]))
                story.append(Spacer(1, 8))

            story.append(Spacer(1, 12))
            story.append(
                Paragraph(
                    "<i>Note: This is a summary report. For full interactive visualizations, "
                    "please use the dashboard interface.</i>",
                    styles["Italic"],
                )
            )

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    except ImportError:
        # Fallback: Create a simple text-based report
        buffer = io.StringIO()

        # Write report header
        buffer.write("=" * 80 + "\n")
        buffer.write("ANALYTICS DASHBOARD REPORT\n")
        buffer.write("=" * 80 + "\n\n")

        # Generation date
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        buffer.write(f"Generated: {date_str}\n\n")

        # Summary Statistics
        buffer.write("-" * 80 + "\n")
        buffer.write("SUMMARY STATISTICS\n")
        buffer.write("-" * 80 + "\n\n")

        # Find the longest key for formatting
        max_key_length = max(len(key.replace("_", " ").title()) for key in stats_dict.keys())

        for key, value in stats_dict.items():
            formatted_key = key.replace("_", " ").title()
            buffer.write(f"{formatted_key:<{max_key_length + 2}}: {value}\n")

        buffer.write("\n")

        # Charts Information
        if charts_data:
            buffer.write("-" * 80 + "\n")
            buffer.write("VISUALIZATIONS INCLUDED\n")
            buffer.write("-" * 80 + "\n\n")

            for chart_name, chart_description in charts_data.items():
                formatted_name = chart_name.replace("_", " ").title()
                buffer.write(f"{formatted_name}:\n")
                buffer.write(f"  {chart_description}\n\n")

            buffer.write("\n")
            buffer.write("NOTE: This is a summary report. For full interactive visualizations,\n")
            buffer.write("please use the dashboard interface.\n\n")

        buffer.write("=" * 80 + "\n")
        buffer.write("END OF REPORT\n")
        buffer.write("=" * 80 + "\n")

        # Get text and encode as bytes
        text_content = buffer.getvalue()
        text_bytes = text_content.encode("utf-8")

        return text_bytes


def create_download_button(
    data: bytes,
    filename: str,
    label: str = "Download",
    mime_type: str = "application/octet-stream",
    key: Optional[str] = None,
    help_text: Optional[str] = None,
    use_container_width: bool = False,
) -> None:
    """
    Create a Streamlit download button with consistent styling.

    Helper function to create download buttons with standardized parameters
    and optional customization.

    Args:
        data: Bytes data to download
        filename: Name for the downloaded file
        label: Button label text (default: "Download")
        mime_type: MIME type of the file (default: "application/octet-stream")
        key: Optional unique key for the button widget
        help_text: Optional tooltip text
        use_container_width: Whether button should use full container width

    Returns:
        None (creates Streamlit widget directly)

    Example:
        >>> # CSV download
        >>> csv_data = generate_csv_export(df)
        >>> create_download_button(
        ...     data=csv_data,
        ...     filename="data_export.csv",
        ...     label="Download CSV Data",
        ...     mime_type="text/csv",
        ...     key="csv_download_1",
        ...     help_text="Download the filtered data as CSV"
        ... )

        >>> # PDF download
        >>> pdf_data = generate_pdf_report(stats)
        >>> create_download_button(
        ...     data=pdf_data,
        ...     filename="analytics_report.pdf",
        ...     label="Download PDF Report",
        ...     mime_type="application/pdf",
        ...     key="pdf_download_1"
        ... )

    Note:
        - Automatically handles button state and download trigger
        - Returns True when button is clicked
        - Key parameter should be unique for each button
    """
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime_type,
        key=key,
        help=help_text,
        use_container_width=use_container_width,
    )


# Example usage and testing
if __name__ == "__main__":
    """
    Example usage demonstrating export functionality.
    Run with: streamlit run export_utils.py
    """
    import streamlit as st
    import pandas as pd

    st.title("Export Utilities Demo")

    # Create sample data
    sample_data = pd.DataFrame(
        {
            "Task ID": range(1, 11),
            "Task Name": [f"Task {i}" for i in range(1, 11)],
            "Status": ["Completed"] * 7 + ["In Progress"] * 3,
            "Priority": ["High", "Medium", "Low"] * 3 + ["High"],
            "Duration (hours)": [2.5, 1.0, 3.5, 2.0, 1.5, 4.0, 2.5, 3.0, 1.5, 2.0],
        }
    )

    st.subheader("Sample Data")
    st.dataframe(sample_data)

    # CSV Export
    st.subheader("CSV Export")
    csv_data = generate_csv_export(sample_data, "sample_export.csv")
    create_download_button(
        data=csv_data,
        filename="sample_export.csv",
        label="Download Sample Data as CSV",
        mime_type="text/csv",
        key="csv_example",
        help_text="Download the sample data in CSV format",
        use_container_width=True,
    )

    # PDF Export
    st.subheader("PDF Report Export")

    # Prepare statistics
    stats = {
        "total_tasks": len(sample_data),
        "completed_tasks": len(sample_data[sample_data["Status"] == "Completed"]),
        "in_progress_tasks": len(sample_data[sample_data["Status"] == "In Progress"]),
        "avg_duration_hours": round(sample_data["Duration (hours)"].mean(), 2),
        "total_duration_hours": round(sample_data["Duration (hours)"].sum(), 2),
        "high_priority_tasks": len(sample_data[sample_data["Priority"] == "High"]),
    }

    # Prepare charts info
    charts = {
        "task_status_distribution": "Bar chart showing completed vs in-progress tasks",
        "priority_breakdown": "Pie chart showing task priority distribution",
        "duration_analysis": "Histogram of task durations",
        "completion_timeline": "Line chart showing task completion over time",
    }

    pdf_data = generate_pdf_report(stats, charts, "sample_report.pdf")

    create_download_button(
        data=pdf_data,
        filename="sample_report.pdf",
        label="Download Analytics Report as PDF",
        mime_type="application/pdf",
        key="pdf_example",
        help_text="Download a summary report with statistics",
        use_container_width=True,
    )

    st.info(
        "Note: PDF generation uses reportlab if available. "
        "If not installed, a text-based report will be generated instead. "
        "Install with: pip install reportlab"
    )
