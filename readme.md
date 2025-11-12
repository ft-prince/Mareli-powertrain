
# Manufacturing Quality Control System

A Django-based real-time quality control and tracking system for manufacturing operations, featuring QR code tracking, machine monitoring, and comprehensive analytics.



## Overview

This system tracks parts through multiple manufacturing stages including CNC machining, gauging, honing, washing, assembly, painting, and lubrication. Each part is identified via QR codes and monitored through preprocessing and postprocessing stages.



## Features

- **Real-time Machine Monitoring**: Live dashboard showing status of all machines (active/inactive)
- **QR Code Tracking**: Track parts through the entire manufacturing process
- **Quality Control**: OK/NG status tracking at each processing stage
- **Server-Sent Events (SSE)**: Real-time updates without page refresh
- **Analytics Dashboard**: Production metrics, yield rates, and trend analysis
- **Data Export**: CSV export functionality for reports
- **Multi-stage Processing**: Support for 20+ different machine types



## System Architecture

### Machine Types

1. **CNC Machines (6 units)**: Primary machining operations
2. **Gauge Machines (3 units)**: Precision measurement with 5-6 measurement values
3. **Honing Machines (2 units)**: Surface finishing
4. **Deburring Machine**: Edge smoothing
5. **Washing Machines**: Pre-washing and final washing
6. **Assembly Machines (OP40A-D)**: Component assembly with internal/external/housing parts
7. **OP80 Leak Test**: Leak testing and O-ring assembly
8. **Painting Machine**: Surface coating
9. **Lubrication Machine**: Final lubrication stage



## Database Models

### Standard Machine Models
Each standard machine has two models:
- **Preprocessing**: Records part entry with QR code and timestamp
- **Postprocessing**: Records completion status (OK/NG) and timestamp



### Special Machine Models

**Gauge Machines**: Include measurement values (value1-value6)



**Assembly Machines (OP40)**: Track three QR codes:
- `qr_data_internal`: Internal component
- `qr_data_external`: External component  
- `qr_data_housing`: Housing component



**OP80 Leak Test**: Matches piston and housing QR codes



**Painting**: Links housing and piston QR codes



**Lubrication**: Final stage tracking



## API Endpoints

### Dashboard & Machine Views
- `GET /`: Main dashboard showing all machines
- `GET /machine/<machine_name>/`: Detailed view for specific machine
- `GET /api/machine/<machine_name>/`: JSON API for machine data
- `GET /sse/dashboard/`: Server-Sent Events stream for dashboard updates
- `GET /sse/machine/<machine_name>/`: SSE stream for specific machine



### Analytics
- `GET /analytics/`: Analytics dashboard page
- `GET /api/analytics/`: Analytics data API
  - Query params: `start_date`, `end_date`, `machine`, `status`
- `GET /analytics/export/`: Export analytics to CSV



### Search & Export
- `GET /search/?qr=<qr_code>`: Search QR code across all machines
- `GET /machine/<machine_name>/export/`: Export machine data to CSV



## Installation

### Prerequisites
```bash
Python 3.8+
Django 4.0+
MySQL/PostgreSQL (recommended for production)
```


### Setup

1. **Clone the repository**
```bash
git clone https://github.com/ft-prince/Mareli-powertrain.git
cd Mareli-powertrain
```


2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```


3. **Install dependencies**
```bash
pip install django mysqlclient  # or psycopg2 for PostgreSQL
```


4. **Configure database** in `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```


5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```


6. **Create superuser**
```bash
python manage.py createsuperuser
```


7. **Run development server**
```bash
python manage.py runserver
```


## Usage

### Dashboard
Navigate to `http://localhost:8000/` to view the main dashboard showing:
- Active/inactive status of all machines
- Latest QR code processed
- Real-time updates via SSE



### Machine Detail View
Click any machine to view:
- Last 100 records
- Preprocessing and postprocessing data
- QR codes and timestamps
- Status (OK/NG/Pending)
- Gauge measurement values (for gauge machines)



### Analytics
Access `http://localhost:8000/analytics/` for:
- Date range filtering
- Machine-specific or all-machine view
- Status filtering (OK/NG/all)
- Charts: Timeline, Hourly Production, Yield Trends
- Machine breakdown statistics
- CSV export



### QR Code Search
Use the search function to find a specific QR code across all machines and view its complete journey.



## Configuration

### Machine Activity Detection
Machines are considered **active** if they have records within the last 21 minutes. Adjust in `views.py`:

```python
def check_machine_status(prep_model):
    threshold = timezone.now() - timedelta(minutes=21)  # Modify this value
    # ...
```


### Real-time Update Frequency
SSE streams check for updates every 2 seconds. Modify in `sse_dashboard_stream()` and `sse_machine_stream()`:

```python
time.sleep(2)  # Change update frequency
```


## Data Flow

1. **Part Entry**: QR code scanned → Preprocessing record created
2. **Processing**: Part goes through machine operation
3. **Quality Check**: QR code scanned → Postprocessing record with OK/NG status
4. **Assembly**: Multiple parts (internal/external/housing) combined
5. **Final Stages**: Painting → Lubrication → Complete



## Key Functions

### Helper Functions
- `get_machine_data()`: Aggregates preprocessing/postprocessing data
- `get_assembly_machine_data()`: Handles assembly machine data
- `check_machine_status()`: Determines if machine is active
- `parse_timestamp_to_datetime()`: Handles multiple timestamp formats



### Analytics Functions
- `collect_analytics_data()`: Aggregates data across date ranges
- `is_in_date_range()`: Filters records by date
- Timeline, hourly, and trend data generation



## Database Tables

All tables follow the naming convention:
- `{machine}_preprocessing`: Entry records
- `{machine}_postprocessing`: Completion records

Examples: `cnc1_preprocessing`, `gauge2_postprocessing`, `op40a_processing`



## Development

### Adding New Machines

1. **Create models** in `models.py`:
```python
class NewMachinePreprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    # Add custom fields
    
    class Meta:
        db_table = 'newmachine_preprocessing'
        ordering = ['-id']

class NewMachinePostprocessing(models.Model):
    # Similar structure
    pass
```


2. **Add to configuration** in `views.py`:
```python
MACHINE_CONFIGS = [
    # ...
    {'name': 'New Machine', 
     'prep_model': models.NewMachinePreprocessing, 
     'post_model': models.NewMachinePostprocessing, 
     'type': 'custom'},
]
```


3. **Run migrations**:
```bash
python manage.py makemigrations
python manage.py migrate
```


## Production Deployment

### Recommendations
- Use **Gunicorn** or **uWSGI** as WSGI server
- Set up **Nginx** as reverse proxy
- Enable **Redis** for caching (optional)
- Use **PostgreSQL** or **MySQL** for production database
- Configure proper logging
- Set `DEBUG = False` in production
- Use environment variables for sensitive data



### Example Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /sse/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
    }
}
```


## Troubleshooting

### Machines Show as Inactive
- Check timestamp format consistency
- Verify database records exist
- Adjust activity threshold (default 21 minutes)



### SSE Not Working
- Ensure proxy buffering is disabled (Nginx/Apache)
- Check browser compatibility (all modern browsers support SSE)
- Verify firewall allows long-lived connections



### Data Not Appearing
- Check database connections
- Verify model names match database tables
- Run migrations if schema changed



## License

[Specify your license here]



## Contributing

[Add contribution guidelines]



## Support

For issues and questions, please [create an issue](link-to-issues) or contact [your contact info].



***

**Built with Django** | Real-time Manufacturing Quality Control System

