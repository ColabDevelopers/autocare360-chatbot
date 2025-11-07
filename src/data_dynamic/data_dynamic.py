"""
Database operations for dynamic data retrieval.
"""
import mysql.connector
from mysql.connector import Error
import logging
from typing import List, Dict, Any, Optional, cast
from contextlib import contextmanager
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MySQL database connections and queries."""

    def __init__(self, host: str, user: str, password: str, database: str):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
        }

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            yield connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()

    def get_recent_service_records(self, limit: int = 5) -> str:
        """
        Retrieve recent service records from database.

        Args:
            limit: Maximum number of records to retrieve

        Returns:
            str: Formatted service records
        """
        query = """
        SELECT id, vehicle_id, service_type, service_date, description
        FROM service_records
        ORDER BY service_date DESC
        LIMIT %s
        """

        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, (limit,))
                records = cast(List[Dict[str, Any]], cursor.fetchall())

                if not records:
                    return "No recent service records found."

                formatted_records = []
                for record in records:
                    formatted_records.append(
                        f"Service ID: {record['id']}\n"
                        f"Vehicle: {record['vehicle_id']}\n"
                        f"Type: {record['service_type']}\n"
                        f"Date: {record['service_date']}\n"
                        f"Description: {record['description']}\n"
                    )

                return "Recent Service Records:\n" + "\n".join(formatted_records)

        except Error as e:
            logger.error(f"Error retrieving service records: {e}")
            return f"Error retrieving service records: {str(e)}"

    def get_vehicle_history(self, vehicle_id: str) -> str:
        """
        Get service history for a specific vehicle.

        Args:
            vehicle_id: The vehicle identifier

        Returns:
            str: Formatted vehicle service history
        """
        query = """
        SELECT id, service_type, service_date, description
        FROM service_records
        WHERE vehicle_id = %s
        ORDER BY service_date DESC
        """

        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, (vehicle_id,))
                records = cast(List[Dict[str, Any]], cursor.fetchall())

                if not records:
                    return f"No service history found for vehicle {vehicle_id}."

                formatted_records = []
                for record in records:
                    formatted_records.append(
                        f"Date: {record['service_date']} - {record['service_type']}: {record['description']}"
                    )

                return f"Service History for Vehicle {vehicle_id}:\n" + "\n".join(
                    formatted_records
                )

        except Error as e:
            logger.error(f"Error retrieving vehicle history: {e}")
            return f"Error retrieving vehicle history: {str(e)}"

    def search_services_by_type(self, service_type: str) -> str:
        """
        Search for services by type.

        Args:
            service_type: Type of service to search for

        Returns:
            str: Formatted search results
        """
        query = """
        SELECT id, vehicle_id, service_date, description
        FROM service_records
        WHERE service_type LIKE %s
        ORDER BY service_date DESC
        LIMIT 10
        """

        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, (f"%{service_type}%",))
                records = cast(List[Dict[str, Any]], cursor.fetchall())

                if not records:
                    return f"No services found matching '{service_type}'."

                formatted_records = []
                for record in records:
                    formatted_records.append(
                        f"Vehicle {record['vehicle_id']} - {record['service_date']}: {record['description']}"
                    )

                return f"Services matching '{service_type}':\n" + "\n".join(
                    formatted_records
                )

        except Error as e:
            logger.error(f"Error searching services: {e}")
            return f"Error searching services: {str(e)}"

    def get_available_appointment_slots(
        self, date: str, service_type: str = None
    ) -> str:
        """
        Get available appointment slots for a given date.

        Args:
            date: Date in YYYY-MM-DD format
            service_type: Optional service type filter

        Returns:
            str: Formatted available slots
        """
        # Check if the date is a weekend (Saturday = 5, Sunday = 6)
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            if date_obj.weekday() >= 5:  # Saturday or Sunday
                today = datetime.now().strftime("%Y-%m-%d")
                tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                if date == today:
                    date_display = "today"
                elif date == tomorrow:
                    date_display = "tomorrow"
                else:
                    date_display = date
                return f"No available appointment slots for {date_display}. We're closed on weekends."
        except ValueError:
            return f"Invalid date format: {date}"

        # Define working hours (9 AM to 5 PM, Monday-Friday)
        working_hours = [
            ("09:00", "09:30"),
            ("09:30", "10:00"),
            ("10:00", "10:30"),
            ("10:30", "11:00"),
            ("11:00", "11:30"),
            ("11:30", "12:00"),
            ("13:00", "13:30"),
            ("13:30", "14:00"),
            ("14:00", "14:30"),
            ("14:30", "15:00"),
            ("15:00", "15:30"),
            ("15:30", "16:00"),
            ("16:00", "16:30"),
            ("16:30", "17:00"),
        ]

        query = """
        SELECT appointment_time, duration_minutes, technician
        FROM appointments
        WHERE appointment_date = %s AND status IN ('scheduled', 'confirmed')
        ORDER BY appointment_time
        """

        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, (date,))
                booked_slots = cast(List[Dict[str, Any]], cursor.fetchall())

                # Create a set of booked time slots
                booked_times = set()
                for slot in booked_slots:
                    start_time = slot["appointment_time"]
                    duration = slot["duration_minutes"]
                    # Mark time slots as booked based on duration
                    # Handle both datetime and timedelta types
                    if isinstance(start_time, timedelta):
                        # Convert timedelta to time string (HH:MM)
                        total_seconds = int(start_time.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        time_str = f"{hours:02d}:{minutes:02d}"
                    else:
                        # Handle datetime or time objects
                        time_str = start_time.strftime("%H:%M")
                    booked_times.add(time_str)

                available_slots = []
                for start, end in working_hours:
                    if start not in booked_times:
                        available_slots.append(f"{start}-{end}")

                if not available_slots:
                    today = datetime.now().strftime("%Y-%m-%d")
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    if date == today:
                        date_display = "today"
                    elif date == tomorrow:
                        date_display = "tomorrow"
                    else:
                        date_display = date
                    return f"No available appointment slots for {date_display}."

                service_filter = f" for {service_type}" if service_type else ""
                today = datetime.now().strftime("%Y-%m-%d")
                tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                if date == today:
                    date_display = "today"
                elif date == tomorrow:
                    date_display = "tomorrow"
                else:
                    date_display = date
                return (
                    f"Available appointment slots for {date_display}{service_filter}:\n"
                    + "\n".join(available_slots)
                )

        except Error as e:
            logger.error(f"Error retrieving available slots: {e}")
            return f"Error retrieving available slots: {str(e)}"

    def check_appointment_availability(
        self, date: str, time: str, technician: str = None
    ) -> bool:
        """
        Check if a specific appointment slot is available.

        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            technician: Optional technician name

        Returns:
            bool: True if available, False if booked
        """
        query = """
        SELECT COUNT(*) as count
        FROM appointments
        WHERE appointment_date = %s AND appointment_time = %s AND status IN ('scheduled', 'confirmed')
        """

        params = [date, time]
        if technician:
            query += " AND technician = %s"
            params.append(technician)

        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params)
                result = cast(Dict[str, Any], cursor.fetchone())
                return result["count"] == 0
        except Error as e:
            logger.error(f"Error checking appointment availability: {e}")
            return False

    def get_upcoming_appointments(self, limit: int = 5) -> str:
        """
        Get upcoming appointments.

        Args:
            limit: Maximum number of appointments to retrieve

        Returns:
            str: Formatted upcoming appointments
        """
        query = """
        SELECT vehicle_id, service_type, appointment_date, appointment_time, technician, status
        FROM appointments
        WHERE appointment_date >= CURDATE() AND status IN ('scheduled', 'confirmed')
        ORDER BY appointment_date, appointment_time
        LIMIT %s
        """

        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, (limit,))
                appointments = cast(List[Dict[str, Any]], cursor.fetchall())

                if not appointments:
                    return "No upcoming appointments found."

                formatted_appointments = []
                for apt in appointments:
                    # Handle appointment_time which may be a timedelta
                    appointment_time = apt["appointment_time"]
                    if isinstance(appointment_time, timedelta):
                        # Convert timedelta to time string (HH:MM)
                        total_seconds = int(appointment_time.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        time_str = f"{hours:02d}:{minutes:02d}"
                    else:
                        # Handle datetime or time objects
                        time_str = appointment_time.strftime("%H:%M")

                    formatted_appointments.append(
                        f"Date: {apt['appointment_date']} {time_str}\n"
                        f"Vehicle: {apt['vehicle_id']}\n"
                        f"Service: {apt['service_type']}\n"
                        f"Technician: {apt['technician']}\n"
                        f"Status: {apt['status']}\n"
                    )

                return "Upcoming Appointments:\n" + "\n".join(formatted_appointments)

        except Error as e:
            logger.error(f"Error retrieving upcoming appointments: {e}")
            return f"Error retrieving upcoming appointments: {str(e)}"
