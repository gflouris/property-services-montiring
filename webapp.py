import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os


class BuildingServicesMonitor:
    def __init__(self, csv_path="complaints.csv"):
        self.csv_path = csv_path
        # Load existing data or create a new DataFrame
        self.load_or_create_data()

    def load_or_create_data(self):
        """Load existing CSV or create a new one if it doesn't exist"""
        if os.path.exists(self.csv_path):
            self.complaints_df = pd.read_csv(self.csv_path, parse_dates=["timestamp"])
        else:
            # Create an empty DataFrame with the correct columns
            self.complaints_df = pd.DataFrame(
                columns=[
                    "timestamp",
                    "service",
                    "severity",
                    "description",
                    "resident_name",
                    "building_name",
                    "apartment_number",
                ]
            )
            # Save the empty DataFrame to create the file
            self.complaints_df.to_csv(self.csv_path, index=False)

    def save_complaint(self, complaint):
        """Save a new complaint to CSV"""
        # Convert complaint to DataFrame
        new_complaint_df = pd.DataFrame([complaint])

        # Append to existing DataFrame
        self.complaints_df = pd.concat(
            [self.complaints_df, new_complaint_df], ignore_index=True
        )

        # Save to CSV
        self.complaints_df.to_csv(self.csv_path, index=False)

    def complaint_input_section(self):
        """Create input section for new complaints"""
        st.header("Report Service Issues")

        # Complaint details inputs
        col1, col2 = st.columns(2)

        with col1:
            service = st.selectbox(
                "Select Service", ["Heating", "Hot Water", "Lift", "Doorbell", "Other"]
            )

        with col2:
            severity = st.select_slider(
                "Severity", options=["Low", "Medium", "High", "Critical"]
            )

        description = st.text_area("Describe the Problem")

        # Additional optional details
        col3, col4, col5 = st.columns(3)
        with col3:
            resident_name = st.text_input("Your Name (Optional)")
        with col4:
            building_name = st.selectbox("Building Name", ["Nyland", "Malmo"])
        with col5:
            apartment_number = st.text_input("Apartment Number")

        if st.button("Submit Complaint"):
            complaint = {
                "timestamp": datetime.now(),
                "service": service,
                "severity": severity,
                "description": description,
                "resident_name": resident_name or "Anonymous",
                "building_name": building_name,
                "apartment_number": apartment_number,
            }
            self.save_complaint(complaint)
            st.success("Complaint Submitted Successfully!")

    def analysis_section(self):
        """Create analysis and visualization section"""
        if self.complaints_df.empty:
            st.info("No complaints recorded yet.")
            return

        st.header("Service Issues Analysis")

        # Service Distribution by Building
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Complaints by Service")
            service_counts = self.complaints_df["service"].value_counts()
            fig1 = px.pie(
                values=service_counts.values,
                names=service_counts.index,
                title="Service Issue Distribution",
            )
            st.plotly_chart(fig1)

        with col2:
            st.subheader("Severity Distribution")
            severity_order = ["Low", "Medium", "High", "Critical"]
            severity_counts = (
                self.complaints_df["severity"].value_counts().reindex(severity_order)
            )
            fig2 = px.bar(
                x=severity_counts.index,
                y=severity_counts.values,
                title="Issue Severity Breakdown",
                labels={"x": "Severity", "y": "Number of Complaints"},
            )
            st.plotly_chart(fig2)

        # Time Series Analysis with Rolling Average
        st.subheader("Time Series of Complaints by Building and Service")

        # Ensure timestamp is in datetime format
        df = self.complaints_df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Group by timestamp (hourly), building, and service
        time_series_data = (
            df.groupby(
                [pd.Grouper(key="timestamp", freq="H"), "building_name", "service"]
            )
            .size()
            .reset_index(name="count")
        )

        # Prepare data for rolling average and plotting
        # First, ensure we have a complete time range
        time_range = pd.date_range(
            start=time_series_data["timestamp"].min(),
            end=time_series_data["timestamp"].max(),
            freq="H",
        )
        
        # Create a list to store rolling average data
        rolling_avg_data = []

        # Calculate rolling average for each building and service combination
        for building in df["building_name"].unique():
            for service in df["service"].unique():
                # Filter data for specific building and service
                subset = time_series_data[
                    (time_series_data["building_name"] == building)
                    & (time_series_data["service"] == service)
                ]

                # Reindex to ensure all hours are represented
                reindexed = subset.set_index("timestamp").reindex(
                    time_range, fill_value=0
                )

                # Calculate 12-hour rolling sum
                rolling_avg = (
                    reindexed["count"].rolling(window=12, min_periods=1).sum()
                )

                # Prepare data for plotting
                temp_df = pd.DataFrame(
                    {
                        "timestamp": rolling_avg.index,
                        "Rolling Sum Complaints": rolling_avg.values,
                        "Building": building,
                        "Service": service,
                    }
                )

                rolling_avg_data.append(temp_df)

        # Combine all rolling average data
        plot_data = pd.concat(rolling_avg_data, ignore_index=True)
        print(plot_data)
        # Create multi-line plot with rolling average
        fig3 = px.line(
            plot_data,
            x="timestamp",
            y="Rolling Sum Complaints",
            color="Building",
            line_dash="Service",
            title="12-Hour Rolling Sum of Complaints by Building and Service",
            labels={
                "Rolling Sum Complaints": "Total Complaints",
                "timestamp": "Date",
            },
            markers=True,
        )
        st.plotly_chart(fig3)

        # Detailed Complaints Table
        st.subheader("Complaint Log")
        st.dataframe(df)

    def main(self):
        """Main Streamlit app configuration"""
        st.title("Fix my building")

        # Create tabs
        tab1, tab2 = st.tabs(["Report Issue", "Service Analytics"])

        with tab1:
            self.complaint_input_section()

        with tab2:
            self.analysis_section()


def main():
    app = BuildingServicesMonitor()
    app.main()


if __name__ == "__main__":
    main()
