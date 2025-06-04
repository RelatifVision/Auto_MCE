# utils/business_manager.py
from datetime import datetime, timedelta
from utils.company_utils import get_rate_company, get_company_name, get_task, get_company_data
from utils.excel_utils import load_dataframe
from config import EXCEL_FILE_PATH

class BusinessManager:
    def __init__(self):
        self.events = []

    def load_events(self, events):
        """Cargar eventos desde Google Calendar."""
        self.events = events

    def calculate_hours_per_company(self):
        """Calcular las horas totales por empresa."""
        hours_data = {}
        for event in self.events:
            company = get_company_name(event) 
            start = datetime.fromisoformat(event['start']['dateTime'])
            end = datetime.fromisoformat(event['end']['dateTime'])
            duration = (end - start).total_seconds() / 3600
            if company is not None:
                hours_data[company] = hours_data.get(company, 0) + duration
            else:
                print(f"Error: No se pudo obtener el nombre de la empresa para el evento: {event}")
        return hours_data

    def calculate_days_per_company(self):
        """Calcular los días únicos por empresa y mes."""
        days_data = {}
        for event in self.events:
            start = datetime.fromisoformat(event['start']['dateTime']).date()
            end = datetime.fromisoformat(event['end']['dateTime']).date()
            company = get_company_name(event)
            current_date = start
            while current_date <= end:
                month_year = current_date.strftime("%Y-%m")
                key = (company, month_year)
                days_data[key] = days_data.get(key, 0) + 1
                current_date += timedelta(days=1)
        return days_data
    
    def calculate_daystring_list_per_company(self):
        """Calcular los días únicos por empresa y mes."""
        days_data = {}
        for event in self.events:
            start = datetime.fromisoformat(event['start']['dateTime']).date()
            end = datetime.fromisoformat(event['end']['dateTime']).date()
            company = get_company_name(event)
            current_date = start
            while current_date <= end:
                month_year = current_date.strftime("%Y-%m")
                key = (company, month_year)
                if key not in days_data:
                    days_data[key] = []
                days_data[key].append(current_date.strftime("%d"))
                current_date += timedelta(days=1)
        return days_data
    
    def calculate_import_per_company_month(self, company, month):
        """Calcular los días únicos por empresa y mes."""
        total = 0
        for event in self.events:
            if (get_company_name(event) == company 
                and event['start']['dateTime'].startswith(month)):
                start = datetime.fromisoformat(event['start']['dateTime']).date()
                end = datetime.fromisoformat(event['end']['dateTime']).date()
                company = get_company_name(event)
                current_date = start
                while current_date <= end:
                    month_year = current_date.strftime("%Y-%m")
                    key = (company, month_year)
                    if key not in total:
                        total[key] = []
                    total[key].append(current_date)
                    current_date += timedelta(days=1)
        return total

    def calculate_hours_per_task(self):
        """Calcular las horas totales por tarea."""
        tasks_data = {}
        for event in self.events:
            start = datetime.fromisoformat(event['start']['dateTime'])
            end = datetime.fromisoformat(event['end']['dateTime'])
            duration = (end - start).total_seconds() / 3600
            task = get_task(event)
            tasks_data[task] = tasks_data.get(task, 0) + duration
        return tasks_data

    def calculate_import_per_company(self):
        importe_data = {}
        for event in self.events:
            company = get_company_name(event)
            if company is None:
                print(f"Error: No se pudo obtener el nombre de la empresa para el evento: {event}")
                continue
            company_info = get_company_data(company, load_dataframe(EXCEL_FILE_PATH, sheet_name='datos_empresa')) 
            if not company_info:
                print(f"Error: No se encontraron datos para la empresa: {company}")
                continue
            start = datetime.fromisoformat(event['start']['dateTime'])
            end = datetime.fromisoformat(event['end']['dateTime'])
            duration = (end - start).total_seconds() / 3600
            jornada_precio = company_info.get('Jornada_Precio', 0)
            jornada_horas = company_info.get('Jornada_Horas', 8)
            precio_hora = company_info.get('Precio_Hora', 0)
            # Calcular horas normales y extras
            horas_extra = max(duration - jornada_horas, 0)
            importe = jornada_precio + (horas_extra * precio_hora)
            importe_data[company] = importe_data.get(company, 0) + importe
        return importe_data

    def calculate_import_per_task(self):
        """Calcular el importe total por tarea."""
        tasks_importe_data = {}
        for event in self.events:
            start = datetime.fromisoformat(event['start']['dateTime']).date()
            end = datetime.fromisoformat(event['end']['dateTime']).date()
            rate, _ = get_rate_company(event['description'])
            if rate is None:
                continue
            try:
                rate_value = float(rate.replace('€', '').strip())
            except ValueError:
                continue
            duration = (end - start).total_seconds() / 3600
            task = get_task(event)
            tasks_importe_data[task] = tasks_importe_data.get(task, 0) + rate_value * duration
        return tasks_importe_data

    def get_task(event):
        """Obtener la tarea desde extendedProperties."""
        return event.get('extendedProperties', {}).get('private', {}).get('task', 'Sin tarea')
    
    def get_servicios(self, company, month):
        """Obtener servicios (tareas) de una empresa en un mes."""
        servicios = set()
        for event in self.events:
            if (get_company_name(event) == company 
                and event['start']['dateTime'].startswith(month)):
                servicio = self.get_task(event)
                servicios.add(servicio)
        return list(servicios)

    def get_description(rate, company):
        """Obtener la descripción del evento (tarifa + nombre empresa)."""
        return f"{rate} {company}"

    def get_rate_company(description):
        """Obtener la tarifa y el nombre de la empresa desde la descripción del evento."""
        parts = description.split('€')
        if len(parts) != 2:
            return None, None
        rate = parts[0].strip()
        company = parts[1].strip()
        return rate, company