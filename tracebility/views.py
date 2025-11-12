from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta, datetime
from collections import defaultdict
import csv
import json
import time
from . import models


# ============================================================================
# MACHINE CONFIGURATIONS - Updated to match new model names
# ============================================================================

MACHINE_CONFIGS = [
    # CNC Machines (previously DMG MORI)
    {'name': 'CNC 1', 'prep_model': models.Cnc1Preprocessing, 'post_model': models.Cnc1Postprocessing, 'type': 'cnc'},
    {'name': 'CNC 2', 'prep_model': models.Cnc2Preprocessing, 'post_model': models.Cnc2Postprocessing, 'type': 'cnc'},
    {'name': 'CNC 3', 'prep_model': models.Cnc3Preprocessing, 'post_model': models.Cnc3Postprocessing, 'type': 'cnc'},
    {'name': 'CNC 4', 'prep_model': models.Cnc4Preprocessing, 'post_model': models.Cnc4Postprocessing, 'type': 'cnc'},
    {'name': 'CNC 5', 'prep_model': models.Cnc5Preprocessing, 'post_model': models.Cnc5Postprocessing, 'type': 'cnc'},
    {'name': 'CNC 6', 'prep_model': models.Cnc6Preprocessing, 'post_model': models.Cnc6Postprocessing, 'type': 'cnc'},
    
    # Gauge Machines
    {'name': 'Gauge 1', 'prep_model': models.Gauge1Preprocessing, 'post_model': models.Gauge1Postprocessing, 'type': 'gauge'},
    {'name': 'Gauge 2', 'prep_model': models.Gauge2Preprocessing, 'post_model': models.Gauge2Postprocessing, 'type': 'gauge'},
    {'name': 'Gauge 3', 'prep_model': models.Gauge3Preprocessing, 'post_model': models.Gauge3Postprocessing, 'type': 'gauge'},
    
    # Honing Machines
    {'name': 'Honing 1', 'prep_model': models.Honing1Preprocessing, 'post_model': models.Honing1Postprocessing, 'type': 'honing'},
    {'name': 'Honing 2', 'prep_model': models.Honing2Preprocessing, 'post_model': models.Honing2Postprocessing, 'type': 'honing'},
    
    # Processing Machines
    {'name': 'Deburring', 'prep_model': models.DeburringPreprocessing, 'post_model': models.DeburringPostprocessing, 'type': 'processing'},
    {'name': 'Prewashing', 'prep_model': models.PrewashingPreprocessing, 'post_model': models.PrewashingPostprocessing, 'type': 'processing'},
    {'name': 'Final Washing', 'prep_model': models.FinalwashingPreprocessing, 'post_model': models.FinalwashingPostprocessing, 'type': 'processing'},
    
    # Painting
    {'name': 'Painting', 'prep_model': models.PaintingPreprocessing, 'post_model': models.PaintingPostprocessing, 'type': 'painting'},
    
    # Lubrication
    {'name': 'Lubrication', 'prep_model': models.LubPreprocessing, 'post_model': models.LubPostprocessing, 'type': 'lubrication'},
]

# Assembly machines (OP40 series)
ASSEMBLY_CONFIGS = [
    {'name': 'Assembly OP40A', 'prep_model': models.Op40AProcessing, 'post_model': models.Op40AProcessing, 'type': 'assembly'},
    {'name': 'Assembly OP40B', 'prep_model': models.Op40BProcessing, 'post_model': models.Op40BProcessing, 'type': 'assembly'},
    {'name': 'Assembly OP40C', 'prep_model': models.Op40CProcessing, 'post_model': models.Op40CProcessing, 'type': 'assembly'},
    {'name': 'Assembly OP40D', 'prep_model': models.Op40DProcessing, 'post_model': models.Op40DProcessing, 'type': 'assembly'},
]

# OP80 - Leak Test
OP80_CONFIG = {
    'name': 'OP80 Leak Test', 
    'prep_model': models.Op80Preprocessing, 
    'post_model': models.Op80Postprocessing, 
    'type': 'op80'
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_machine_data(prep_model, post_model, machine_type='standard'):
    """Aggregate preprocessing and postprocessing data"""
    records = []
    prep_records = prep_model.objects.all()[:100]
    
    for prep in prep_records:
        # Determine QR code field based on machine type
        if machine_type == 'painting':
            # Painting: Match prep.qr_data_housing with post.qr_data_housing
            qr_value_housing_prep = prep.qr_data_housing
            qr_value_piston_prep = prep.qr_data_piston
            post = post_model.objects.filter(qr_data_housing=qr_value_housing_prep).first()
            
        elif machine_type == 'lubrication':
            # Lubrication: Match prep.qr_data_piston with post.qr_data_piston
            qr_value = prep.qr_data_piston
            qr_value_housing = prep.qr_data_housing
            post = post_model.objects.filter(qr_data_piston=qr_value).first()
            
        elif machine_type == 'op80':
            # OP80: Match prep.qr_data_housing with post.qr_data_housing (NOT housing_new!)
            qr_value_piston = prep.qr_data_piston
            qr_value_housing = prep.qr_data_housing
            post = post_model.objects.filter(qr_data_housing=qr_value_housing).first()
            
        else:
            # Standard machines: use qr_data
            qr_value = prep.qr_data
            post = post_model.objects.filter(qr_data=qr_value).first()
        
        # Determine overall status
        if post:
            overall_status = post.status
            status_class = 'completed-ok' if post.status == 'OK' else 'completed-ng'
            post_id = post.id
            post_timestamp = post.timestamp
            post_status = post.status
        else:
            overall_status = 'Pending'
            status_class = 'in-progress'
            post_id = None
            post_timestamp = None
            post_status = 'Pending'
        
        # Get gauge values if applicable
        gauge_values = {}
        if post and hasattr(post, 'value1'):
            for i in range(1, 7):
                val = getattr(post, f'value{i}', None)
                if val is not None:
                    gauge_values[f'value{i}'] = val
        
        # Get machine name
        machine_name = getattr(prep, 'machine_name', 'N/A')
        
        # Build record dictionary
        record = {
            'prep_id': prep.id,
            'prep_timestamp': prep.timestamp,
            'prep_machine_name': machine_name,
            'prep_status': 'OK',
            'qr_code': qr_value if machine_type not in ['painting', 'op80'] else (qr_value_housing_prep if machine_type == 'painting' else qr_value_piston),
            'post_id': post_id,
            'post_timestamp': post_timestamp,
            'post_status': post_status,
            'overall_status': overall_status,
            'status_class': status_class,
            'gauge_values': gauge_values,
            'sort_priority': 1 if post else 2,
        }
        
        # Add additional fields for special machines
        if machine_type == 'painting':
            # PAINTING: Separate housing and piston QRs for prep and post
            record['qr_housing_prep'] = qr_value_housing_prep
            record['qr_housing_post'] = post.qr_data_housing if post else None
            record['qr_piston_prep'] = qr_value_piston_prep
            record['qr_piston_post'] = post.qr_data_piston if post else None
            # PAINTING: Add status fields
            record['previous_machine_status'] = prep.previous_machine_status
            record['pre_status'] = prep.pre_status
            
        elif machine_type == 'lubrication':
            record['qr_housing'] = qr_value_housing
            
        elif machine_type == 'op80':
            # OP80 PREP: piston and housing
            record['qr_piston'] = qr_value_piston
            record['qr_housing_prep'] = qr_value_housing
            # OP80 PREP STATUS: only previous_machine_status
            record['previous_machine_status'] = prep.previous_machine_status
            
            # OP80 POST: housing and housing_new, match_status
            if post:
                record['qr_housing_post'] = post.qr_data_housing
                record['qr_housing_new'] = post.qr_data_housing_new
                record['match_status'] = post.match_status
        
        records.append(record)
    
    records.sort(key=lambda x: (x['sort_priority'], -x['prep_id']))
    return records
    

def get_assembly_machine_data(prep_model, post_model):
    """Special handler for assembly machines (OP40 series)"""
    records = []
    prep_records = prep_model.objects.all()[:100]
    
    for prep in prep_records:
        qr_internal = prep.qr_data_internal
        
        # For OP40 models, prep and post are the same table
        # Check if external and housing data exists
        if prep.qr_data_external and prep.qr_data_housing:
            overall_status = prep.status or 'COMPLETE'
            status_class = 'completed-ok' if prep.status == 'OK' else 'completed-ng'
            post_id = prep.id
            qr_external = prep.qr_data_external
            qr_housing = prep.qr_data_housing
            post_timestamp = prep.timestamp_external or prep.timestamp_internal
            post_status = prep.status or 'OK'
        else:
            overall_status = 'Pending'
            status_class = 'in-progress'
            post_id = None
            qr_external = '-'
            qr_housing = '-'
            post_timestamp = None
            post_status = 'Pending'
        
        records.append({
            'prep_id': prep.id,
            'prep_timestamp': prep.timestamp_internal,
            'prep_machine_name': 'Assembly',
            'prep_status': 'OK',
            'qr_code': qr_internal,
            'qr_external': qr_external,
            'qr_housing': qr_housing,
            'post_id': post_id,
            'post_timestamp': post_timestamp,
            'post_status': post_status,
            'overall_status': overall_status,
            'status_class': status_class,
            'sort_priority': 1 if post_id else 2,
        })
    
    records.sort(key=lambda x: (x['sort_priority'], -x['prep_id']))
    return records


def parse_timestamp_to_datetime(timestamp):
    """Convert timestamp string "10/11/2025, 3:40:33 pm" to datetime object"""
    if timestamp is None:
        return None
    
    # Already a datetime
    if hasattr(timestamp, 'strftime'):
        return timestamp
    
    # Try parsing string
    if isinstance(timestamp, str):
        # Try DD/MM/YYYY format: "10/11/2025, 3:40:33 pm"
        try:
            return datetime.strptime(timestamp, '%d/%m/%Y, %I:%M:%S %p')
        except:
            pass
        
        # Try MM/DD/YYYY format (US)
        try:
            return datetime.strptime(timestamp, '%m/%d/%Y, %I:%M:%S %p')
        except:
            pass
        
        # Try other common formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%d-%m-%Y %H:%M:%S',
            '%m-%d-%Y %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp, fmt)
            except:
                continue
        
        # Try ISO format
        try:
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            pass
    
    return None

def check_machine_status(prep_model):
    """Check if machine is active - FIXED TIMEZONE VERSION"""
    threshold = timezone.now() - timedelta(minutes=21)
    
    try:
        latest_record = prep_model.objects.first()
        if not latest_record:
            return False
        
        # Get timestamp field
        try:
            timestamp = latest_record.timestamp_internal
            field_name = 'timestamp_internal'
        except AttributeError:
            timestamp = latest_record.timestamp
            field_name = 'timestamp'
        
        # If it's a DateTimeField
        if hasattr(timestamp, 'timestamp'):
            # Make sure timestamp is timezone-aware
            if timezone.is_naive(timestamp):
                timestamp = timezone.make_aware(timestamp)
            
            is_active = timestamp >= threshold
            return is_active
        
        # If it's a CharField
        if isinstance(timestamp, str):
            parsed_dt = parse_timestamp_to_datetime(timestamp)
            
            if parsed_dt:
                # Make sure parsed datetime is timezone-aware
                if timezone.is_naive(parsed_dt):
                    parsed_dt = timezone.make_aware(parsed_dt)
                
                is_active = parsed_dt >= threshold
                return is_active
            else:
                return False
        
        return False
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False

   

def get_latest_machine_record(prep_model, post_model, machine_type='standard'):
    """Get the latest record for a machine"""
    latest_prep = prep_model.objects.first()
    if not latest_prep:
        return None
    
    # Determine QR code field based on machine type - FINAL CORRECTED MAPPINGS
    if machine_type == 'painting':
        # Painting: Match prep.qr_data_housing with post.qr_data_housing
        qr_value = latest_prep.qr_data_housing  # Primary display & matching
        qr_piston = latest_prep.qr_data_piston  # Secondary display only
        post = post_model.objects.filter(qr_data_housing=qr_value).first()
        
    elif machine_type == 'lubrication':
        # Lubrication: Match prep.qr_data_piston with post.qr_data_piston
        qr_value = latest_prep.qr_data_piston  # Primary display & matching
        qr_housing = latest_prep.qr_data_housing  # Secondary display only
        post = post_model.objects.filter(qr_data_piston=qr_value).first()
        
    elif machine_type == 'op80':
        # OP80: Match prep.qr_data_housing with post.qr_data_housing_new
        # Display piston as primary, but match using housing!
        qr_value = latest_prep.qr_data_piston  # Primary display (piston)
        qr_housing = latest_prep.qr_data_housing  # This is what we match!
        post = post_model.objects.filter(qr_data_housing_new=qr_housing).first()
        
    else:
        # Standard machines: use qr_data
        qr_value = latest_prep.qr_data
        post = post_model.objects.filter(qr_data=qr_value).first()
    
    # Get gauge values if applicable
    gauge_values = {}
    if post and hasattr(post, 'value1'):
        for i in range(1, 7):
            val = getattr(post, f'value{i}', None)
            if val is not None:
                gauge_values[f'value{i}'] = val
    
    # Format timestamp - handle both DateTimeField and CharField
    prep_timestamp = latest_prep.timestamp
    if hasattr(prep_timestamp, 'isoformat'):
        timestamp_str = prep_timestamp.isoformat()
    else:
        try:
            from datetime import datetime
            if isinstance(prep_timestamp, str):
                try:
                    dt = datetime.fromisoformat(prep_timestamp.replace('Z', '+00:00'))
                    timestamp_str = dt.isoformat()
                except:
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%d-%m-%Y %H:%M:%S']:
                        try:
                            dt = datetime.strptime(prep_timestamp, fmt)
                            timestamp_str = dt.isoformat()
                            break
                        except:
                            continue
                    else:
                        timestamp_str = prep_timestamp
            else:
                timestamp_str = str(prep_timestamp)
        except:
            timestamp_str = str(prep_timestamp)
    
    result = {
        'qr_code': qr_value,
        'prep_timestamp': timestamp_str,
        'post_status': post.status if post else 'Pending',
        'has_post': post is not None,
        'gauge_values': gauge_values,
    }
    
    # Add additional QR codes for special machines
    if machine_type == 'painting':
        result['qr_piston'] = qr_piston
    elif machine_type == 'lubrication':
        result['qr_housing'] = qr_housing
    elif machine_type == 'op80':
        result['qr_housing'] = qr_housing
    
    return result


     
         

def get_latest_assembly_record(prep_model, post_model):
    """Get the latest record for assembly machine"""
    latest_prep = prep_model.objects.first()
    if not latest_prep:
        return None
    
    qr_internal = latest_prep.qr_data_internal
    
    # Format timestamp - handle DateTimeField
    prep_timestamp = latest_prep.timestamp_internal
    if hasattr(prep_timestamp, 'isoformat'):
        timestamp_str = prep_timestamp.isoformat()
    else:
        timestamp_str = str(prep_timestamp)
    
    return {
        'qr_code': qr_internal,
        'qr_external': latest_prep.qr_data_external if latest_prep.qr_data_external else '-',
        'qr_housing': latest_prep.qr_data_housing if latest_prep.qr_data_housing else '-',
        'prep_timestamp': timestamp_str,
        'post_status': latest_prep.status if latest_prep.status else 'Pending',
        'has_post': latest_prep.qr_data_external is not None,
    }


# ============================================================================
# MAIN VIEWS
# ============================================================================

def dashboard_view(request):
    """Main dashboard showing all machines"""
    machines_data = []
    
    for config in MACHINE_CONFIGS:
        is_active = check_machine_status(config['prep_model'])
        
        # Determine machine type for data retrieval
        machine_type = 'standard'
        if config['name'] == 'Painting':
            machine_type = 'painting'
        elif config['name'] == 'Lubrication':
            machine_type = 'lubrication'
        
        latest_record = get_latest_machine_record(config['prep_model'], config['post_model'], machine_type)
        
        machines_data.append({
            'name': config['name'],
            'type': config['type'],
            'is_active': is_active,
            'is_assembly': False,
            'machine_id': config['name'].lower().replace(' ', '_').replace('-', '_'),
            'latest_record': latest_record,
        })
    
    for config in ASSEMBLY_CONFIGS:
        is_active = check_machine_status(config['prep_model'])
        latest_record = get_latest_assembly_record(config['prep_model'], config['post_model'])
        
        machines_data.append({
            'name': config['name'],
            'type': 'assembly',
            'is_active': is_active,
            'is_assembly': True,
            'machine_id': config['name'].lower().replace(' ', '_'),
            'latest_record': latest_record,
        })
    
    # Add OP80 - Don't loop, just access the dictionary directly
    is_active = check_machine_status(OP80_CONFIG['prep_model'])
    latest_record = get_latest_machine_record(
        OP80_CONFIG['prep_model'], 
        OP80_CONFIG['post_model'], 
        'op80'
    )
    
    machines_data.append({
        'name': OP80_CONFIG['name'],
        'type': 'op80',
        'is_active': is_active,
        'is_assembly': False,
        'machine_id': 'op80_leak_test',
        'latest_record': latest_record,
    })
    
    return render(request, 'dashboard/dashboard.html', {'machines': machines_data})

def machine_detail_view(request, machine_name):
    """Detail view for specific machine"""
    config = None
    is_assembly = False
    
    for m in MACHINE_CONFIGS:
        if m['name'].lower().replace(' ', '_').replace('-', '_') == machine_name:
            config = m
            break
    
    if not config:
        for m in ASSEMBLY_CONFIGS:
            if m['name'].lower().replace(' ', '_') == machine_name:
                config = m
                is_assembly = True
                break
    # Check OP80
    if not config and machine_name == 'op80_leak_test':
        config = OP80_CONFIG
    
    if not config:
        return render(request, 'dashboard/machine_detail.html', {'error': 'Machine not found'})
    
    if is_assembly:
        records = get_assembly_machine_data(config['prep_model'], config['post_model'])
    else:
        machine_type = 'standard'
        if config['name'] == 'Painting':
            machine_type = 'painting'
        elif config['name'] == 'Lubrication':
            machine_type = 'lubrication'
        elif config['name'] == 'OP80 Leak Test':
            machine_type = 'op80'
        records = get_machine_data(config['prep_model'], config['post_model'], machine_type)
    
    is_active = check_machine_status(config['prep_model'])
    
    # Convert datetime objects to strings for JSON
    records_json = []
    for record in records:
        record_copy = record.copy()
        if hasattr(record['prep_timestamp'], 'isoformat'):
            record_copy['prep_timestamp'] = record['prep_timestamp'].isoformat()
        if record['post_timestamp'] and hasattr(record['post_timestamp'], 'isoformat'):
            record_copy['post_timestamp'] = record['post_timestamp'].isoformat()
        records_json.append(record_copy)
    
    context = {
        'machine_name': config['name'],
        'machine_type': machine_type,  # Add machine_type to context
        'is_active': is_active,
        'records': records,
        'records_json': json.dumps(records_json, cls=DjangoJSONEncoder),
        'is_assembly': is_assembly,
    }
    
    return render(request, 'dashboard/machine_detail.html', context)




@csrf_exempt
def machine_data_api(request, machine_name):
    """API endpoint for real-time updates and modal data"""
    config = None
    is_assembly = False
    
    for m in MACHINE_CONFIGS:
        if m['name'].lower().replace(' ', '_').replace('-', '_') == machine_name:
            config = m
            break
    
    if not config:
        for m in ASSEMBLY_CONFIGS:
            if m['name'].lower().replace(' ', '_') == machine_name:
                config = m
                is_assembly = True
                break
    
    # Check OP80
    if not config and machine_name == 'op80_leak_test':
        config = OP80_CONFIG

    if not config:
        return JsonResponse({'error': 'Machine not found'}, status=404)
    
    if is_assembly:
        records = get_assembly_machine_data(config['prep_model'], config['post_model'])
        machine_type = 'assembly'
    else:
        machine_type = 'standard'
        if config['name'] == 'Painting':
            machine_type = 'painting'
        elif config['name'] == 'Lubrication':
            machine_type = 'lubrication'
        elif config['name'] == 'OP80 Leak Test':
            machine_type = 'op80'
        
        records = get_machine_data(config['prep_model'], config['post_model'], machine_type)
    
    is_active = check_machine_status(config['prep_model'])
    
    for record in records:
        if hasattr(record['prep_timestamp'], 'isoformat'):
            record['prep_timestamp'] = record['prep_timestamp'].isoformat()
        if record['post_timestamp'] and hasattr(record['post_timestamp'], 'isoformat'):
            record['post_timestamp'] = record['post_timestamp'].isoformat()
    
    return JsonResponse({
        'machine_name': config['name'],
        'machine_type': machine_type,  # Add machine_type to response
        'is_active': is_active,
        'records': records,
        'is_assembly': is_assembly,
    })


def search_qr_code(request):
    """Search QR code across all machines"""
    qr_code = request.GET.get('qr', '')
    
    if not qr_code:
        return JsonResponse({'error': 'No QR code provided'}, status=400)
    
    results = []
    
    for config in MACHINE_CONFIGS:
        if config['name'] == 'Painting':
            # Painting: search both qr_data_housing and qr_data_piston in prep
            # Search qr_data_housing in post
            prep_records = config['prep_model'].objects.filter(
                Q(qr_data_housing__icontains=qr_code) | Q(qr_data_piston__icontains=qr_code)
            )
            post_records = config['post_model'].objects.filter(qr_data_housing__icontains=qr_code)
        elif config['name'] == 'Lubrication':
            # Lubrication: search both qr_data_piston and qr_data_housing in prep
            # Search qr_data_piston in post
            prep_records = config['prep_model'].objects.filter(
                Q(qr_data_piston__icontains=qr_code) | Q(qr_data_housing__icontains=qr_code)
            )
            post_records = config['post_model'].objects.filter(qr_data_piston__icontains=qr_code)
        elif config['name'] == 'OP80 Leak Test':
            # OP80: search qr_data_piston and qr_data_housing in prep
            # Search qr_data_housing_new in post (FIXED!)
            prep_records = config['prep_model'].objects.filter(
                Q(qr_data_piston__icontains=qr_code) | Q(qr_data_housing__icontains=qr_code)
            )
            post_records = config['post_model'].objects.filter(qr_data_housing_new__icontains=qr_code)  # CHANGED
        else:
            # Standard machines: use qr_data
            prep_records = config['prep_model'].objects.filter(qr_data__icontains=qr_code)
            post_records = config['post_model'].objects.filter(qr_data__icontains=qr_code)
        
        if prep_records.exists() or post_records.exists():
            results.append({
                'machine': config['name'],
                'preprocessing_count': prep_records.count(),
                'postprocessing_count': post_records.count(),
            })
    
    for config in ASSEMBLY_CONFIGS:
        prep_records = config['prep_model'].objects.filter(
            Q(qr_data_internal__icontains=qr_code) |
            Q(qr_data_external__icontains=qr_code) |
            Q(qr_data_housing__icontains=qr_code)
        )
        
        if prep_records.exists():
            results.append({
                'machine': config['name'],
                'preprocessing_count': prep_records.count(),
                'postprocessing_count': 0,
            })
    
    # Search OP80 (if not already covered in MACHINE_CONFIGS)
    if 'OP80 Leak Test' not in [config['name'] for config in MACHINE_CONFIGS]:
        prep_records = OP80_CONFIG['prep_model'].objects.filter(
            Q(qr_data_piston__icontains=qr_code) | Q(qr_data_housing__icontains=qr_code)
        )
        post_records = OP80_CONFIG['post_model'].objects.filter(qr_data_housing_new__icontains=qr_code)  # CHANGED
        
        if prep_records.exists() or post_records.exists():
            results.append({
                'machine': OP80_CONFIG['name'],
                'preprocessing_count': prep_records.count(),
                'postprocessing_count': post_records.count(),
            })

    return JsonResponse({'qr_code': qr_code, 'results': results})




def export_machine_data(request, machine_name):
    """Export machine data to CSV"""
    config = None
    is_assembly = False
    
    for m in MACHINE_CONFIGS:
        if m['name'].lower().replace(' ', '_').replace('-', '_') == machine_name:
            config = m
            break
    
    if not config:
        for m in ASSEMBLY_CONFIGS:
            if m['name'].lower().replace(' ', '_') == machine_name:
                config = m
                is_assembly = True
                break
    if not config and machine_name == 'op80_leak_test':
        config = OP80_CONFIG

    if not config:
        return HttpResponse('Machine not found', status=404)
    
    if is_assembly:
        records = get_assembly_machine_data(config['prep_model'], config['post_model'])
    else:
        machine_type = 'standard'
        if config['name'] == 'Painting':
            machine_type = 'painting'
        elif config['name'] == 'Lubrication':
            machine_type = 'lubrication'
        records = get_machine_data(config['prep_model'], config['post_model'], machine_type)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{machine_name}_data.csv"'
    
    writer = csv.writer(response)
    
    if is_assembly:
        writer.writerow(['ID', 'QR Internal', 'QR External', 'QR Housing', 'Prep Timestamp', 
                        'Post Timestamp', 'Status', 'Overall Status'])
        for record in records:
            writer.writerow([
                record['prep_id'], record['qr_code'], record.get('qr_external', '-'),
                record.get('qr_housing', '-'), record['prep_timestamp'],
                record['post_timestamp'] or '-', record['post_status'] or '-',
                record['overall_status'],
            ])
    else:
        writer.writerow(['ID', 'QR Code', 'Prep Timestamp', 'Post Timestamp', 
                        'Status', 'Overall Status', 'Gauge Values'])
        for record in records:
            writer.writerow([
                record['prep_id'], record['qr_code'], record['prep_timestamp'],
                record['post_timestamp'] or '-', record['post_status'] or '-',
                record['overall_status'], record.get('gauge_values', '-') or '-',
            ])
    
    return response


# ============================================================================
# REAL-TIME STREAMING (SSE)
# ============================================================================

def get_latest_record_count(model):
    """Get the count of records for change detection"""
    return model.objects.count()


def get_dashboard_summary():
    """Get summary data for all machines"""
    machines_data = []
    
    for config in MACHINE_CONFIGS:
        is_active = check_machine_status(config['prep_model'])
        machine_type = 'standard'
        if config['name'] == 'Painting':
            machine_type = 'painting'
        elif config['name'] == 'Lubrication':
            machine_type = 'lubrication'
        
        latest_record = get_latest_machine_record(config['prep_model'], config['post_model'], machine_type)
        
        machines_data.append({
            'name': config['name'],
            'machine_id': config['name'].lower().replace(' ', '_').replace('-', '_'),
            'is_active': is_active,
            'latest_record': latest_record,
        })
    
    for config in ASSEMBLY_CONFIGS:
        is_active = check_machine_status(config['prep_model'])
        latest_record = get_latest_assembly_record(config['prep_model'], config['post_model'])
        
        machines_data.append({
            'name': config['name'],
            'machine_id': config['name'].lower().replace(' ', '_'),
            'is_active': is_active,
            'latest_record': latest_record,
            'is_assembly': True,
        })
    
    return machines_data


def sse_dashboard_stream(request):
    """Server-Sent Events stream for dashboard updates"""
    
    def event_stream():
        last_counts = {}
        
        # Initialize counts for all models
        for config in MACHINE_CONFIGS + ASSEMBLY_CONFIGS + [OP80_CONFIG]:
            prep_table = config['prep_model']._meta.db_table
            post_table = config['post_model']._meta.db_table
            last_counts[prep_table] = get_latest_record_count(config['prep_model'])
            last_counts[post_table] = get_latest_record_count(config['post_model'])
        
        while True:
            try:
                # Check for changes
                changed = False
                for config in MACHINE_CONFIGS + ASSEMBLY_CONFIGS:
                    prep_table = config['prep_model']._meta.db_table
                    post_table = config['post_model']._meta.db_table
                    
                    current_prep_count = get_latest_record_count(config['prep_model'])
                    current_post_count = get_latest_record_count(config['post_model'])
                    
                    if (current_prep_count != last_counts[prep_table] or 
                        current_post_count != last_counts[post_table]):
                        changed = True
                        last_counts[prep_table] = current_prep_count
                        last_counts[post_table] = current_post_count
                
                if changed:
                    # Get fresh data
                    machines_data = get_dashboard_summary()
                    
                    # Prepare data for JSON serialization
                    for machine in machines_data:
                        if machine.get('latest_record') and machine['latest_record'].get('prep_timestamp'):
                            if hasattr(machine['latest_record']['prep_timestamp'], 'isoformat'):
                                machine['latest_record']['prep_timestamp'] = machine['latest_record']['prep_timestamp'].isoformat()
                    
                    data = json.dumps({
                        'type': 'update',
                        'machines': machines_data
                    }, cls=DjangoJSONEncoder)
                    
                    yield f"data: {data}\n\n"
                
                # Send heartbeat every 15 seconds
                yield f": heartbeat\n\n"
                time.sleep(2)  # Check every 2 seconds
                
            except GeneratorExit:
                break
            except Exception as e:
                print(f"SSE Error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                time.sleep(5)
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def sse_machine_stream(request, machine_name):
    """Server-Sent Events stream for specific machine updates"""
    
    # Find the machine configuration
    config = None
    is_assembly = False
    
    for m in MACHINE_CONFIGS:
        if m['name'].lower().replace(' ', '_').replace('-', '_') == machine_name:
            config = m
            break
    
    if not config:
        for m in ASSEMBLY_CONFIGS:
            if m['name'].lower().replace(' ', '_') == machine_name:
                config = m
                is_assembly = True
                break
            
    if not config and machine_name == 'op80_leak_test':
        config = OP80_CONFIG

    
    if not config:
        return StreamingHttpResponse("Machine not found", status=404)
    
    def event_stream():
        last_prep_count = get_latest_record_count(config['prep_model'])
        last_post_count = get_latest_record_count(config['post_model'])
        
        while True:
            try:
                current_prep_count = get_latest_record_count(config['prep_model'])
                current_post_count = get_latest_record_count(config['post_model'])
                
                if (current_prep_count != last_prep_count or 
                    current_post_count != last_post_count):
                    
                    last_prep_count = current_prep_count
                    last_post_count = current_post_count
                    
                    # Get updated machine data
                    if is_assembly:
                        records = get_assembly_machine_data(config['prep_model'], config['post_model'])
                    else:
                        machine_type = 'standard'
                        if config['name'] == 'Painting':
                            machine_type = 'painting'
                        elif config['name'] == 'Lubrication':
                            machine_type = 'lubrication'
                        records = get_machine_data(config['prep_model'], config['post_model'], machine_type)
                    
                    is_active = check_machine_status(config['prep_model'])
                    
                    # Serialize timestamps
                    for record in records:
                        if hasattr(record['prep_timestamp'], 'isoformat'):
                            record['prep_timestamp'] = record['prep_timestamp'].isoformat()
                        if record['post_timestamp'] and hasattr(record['post_timestamp'], 'isoformat'):
                            record['post_timestamp'] = record['post_timestamp'].isoformat()
                    
                    data = json.dumps({
                        'type': 'update',
                        'machine_name': config['name'],
                        'is_active': is_active,
                        'records': records,
                        'is_assembly': is_assembly,
                    }, cls=DjangoJSONEncoder)
                    
                    yield f"data: {data}\n\n"
                
                # Send heartbeat
                yield f": heartbeat\n\n"
                time.sleep(2)  # Check every 2 seconds
                
            except GeneratorExit:
                break
            except Exception as e:
                print(f"SSE Error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                time.sleep(5)
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


# ============================================================================
# ANALYTICS VIEWS - FINAL WORKING VERSION
# Add this section to your views.py (replace the existing analytics section)
# ============================================================================

from collections import defaultdict
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import csv


def analytics_view(request):
    """Main analytics page"""
    return render(request, 'dashboard/analytics.html')


def parse_timestamp_to_datetime(timestamp):
    """Convert timestamp string "10/11/2025, 3:40:33 pm" to datetime object"""
    if timestamp is None:
        return None
    
    # Already a datetime
    if hasattr(timestamp, 'strftime'):
        return timestamp
    
    # Try parsing string
    if isinstance(timestamp, str):
        # Try DD/MM/YYYY format: "10/11/2025, 3:40:33 pm"
        try:
            return datetime.strptime(timestamp, '%d/%m/%Y, %I:%M:%S %p')
        except:
            pass
        
        # Try MM/DD/YYYY format (US)
        try:
            return datetime.strptime(timestamp, '%m/%d/%Y, %I:%M:%S %p')
        except:
            pass
        
        # Try other common formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%d-%m-%Y %H:%M:%S',
            '%m-%d-%Y %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp, fmt)
            except:
                continue
        
        # Try ISO format
        try:
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            pass
    
    return None


def is_in_date_range(timestamp, start_date, end_date):
    """Check if timestamp is in date range"""
    dt = parse_timestamp_to_datetime(timestamp)
    if not dt:
        return False
    
    # Make timezone aware if needed
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    
    return start_date <= dt <= end_date


def get_date_range(start_date_str, end_date_str):
    """Parse date range from request parameters"""
    try:
        if start_date_str:
            naive_start = datetime.strptime(start_date_str, '%Y-%m-%d')
            start_date = timezone.make_aware(naive_start)
        else:
            start_date = timezone.now() - timedelta(days=7)
        
        if end_date_str:
            naive_end = datetime.strptime(end_date_str, '%Y-%m-%d')
            naive_end = naive_end.replace(hour=23, minute=59, second=59)
            end_date = timezone.make_aware(naive_end)
        else:
            end_date = timezone.now()
        
        return start_date, end_date
    except ValueError:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        return start_date, end_date


def get_machine_config_by_id(machine_id):
    """Get machine config by machine_id"""
    if machine_id == 'all':
        return None
    
    for config in MACHINE_CONFIGS:
        config_id = config['name'].lower().replace(' ', '_').replace('-', '_')
        if config_id == machine_id:
            return config
    
    for config in ASSEMBLY_CONFIGS:
        config_id = config['name'].lower().replace(' ', '_')
        if config_id == machine_id:
            return config
    # Check OP80
    if machine_id == 'op80_leak_test':
        return OP80_CONFIG

    return None

def collect_analytics_data(start_date, end_date, machine_filter='all', status_filter='all'):
    """Collect analytics data from all machines"""
    data = {
        'total_parts': 0,
        'ok_parts': 0,
        'ng_parts': 0,
        'pending_parts': 0,
        'machine_stats': [],
        'timeline_data': {'labels': [], 'ok': [], 'ng': []},
        'hourly_data': {'labels': [], 'values': []},
        'trend_data': {'labels': [], 'values': []},
        'detailed_data': [],
        'active_machines': 0
    }
    
    all_records = []
    
    # Determine which machines to query
    configs_to_query = []
    if machine_filter == 'all':
        configs_to_query = MACHINE_CONFIGS + ASSEMBLY_CONFIGS + [OP80_CONFIG]
    else:
        config = get_machine_config_by_id(machine_filter)
        if config:
            configs_to_query = [config]
    
    # Collect data from each machine
    for config in configs_to_query:
        machine_name = config['name']
        is_assembly = 'Assembly' in machine_name
        
        # Check if machine is active (has recent records)
        try:
            recent_count = config['prep_model'].objects.all()[:5].count()
            if recent_count > 0:
                data['active_machines'] += 1
        except:
            pass
        
        # Get ALL preprocessing records
        try:
            prep_records = config['prep_model'].objects.all()
        except Exception as e:
            continue
        
        machine_stats = {
            'machine': machine_name,
            'ok': 0,
            'ng': 0,
            'pending': 0
        }
        
        for prep in prep_records:
            # Get timestamp
            if is_assembly:
                timestamp = prep.timestamp_internal
            else:
                timestamp = prep.timestamp
            
            # Check if in date range (filter in Python)
            if not is_in_date_range(timestamp, start_date, end_date):
                continue
            
            # Get QR code and status based on machine type - FINAL CORRECTED MAPPINGS
            if is_assembly:
                qr_value = prep.qr_data_internal
                status = prep.status if prep.qr_data_external and prep.qr_data_housing else 'Pending'
                
            elif machine_name == 'Painting':
                # Painting: Match prep.qr_data_housing with post.qr_data_housing
                qr_value = prep.qr_data_housing
                post = config['post_model'].objects.filter(qr_data_housing=qr_value).first()
                status = post.status if post else 'Pending'
                
            elif machine_name == 'Lubrication':
                # Lubrication: Match prep.qr_data_piston with post.qr_data_piston
                qr_value = prep.qr_data_piston
                post = config['post_model'].objects.filter(qr_data_piston=qr_value).first()
                status = post.status if post else 'Pending'
                
            elif machine_name == 'OP80 Leak Test':
                # OP80: Match prep.qr_data_housing with post.qr_data_housing_new
                qr_value = prep.qr_data_piston  # Display this
                qr_housing = prep.qr_data_housing  # Match this
                post = config['post_model'].objects.filter(qr_data_housing_new=qr_housing).first()
                status = post.status if post else 'Pending'
                
            else:
                # Standard machines: use qr_data
                qr_value = prep.qr_data
                post = config['post_model'].objects.filter(qr_data=qr_value).first()
                status = post.status if post else 'Pending'
            
            # Apply status filter
            if status_filter != 'all' and status != status_filter:
                continue
            
            # Update counts
            data['total_parts'] += 1
            if status == 'OK':
                data['ok_parts'] += 1
                machine_stats['ok'] += 1
            elif status == 'NG':
                data['ng_parts'] += 1
                machine_stats['ng'] += 1
            else:
                data['pending_parts'] += 1
                machine_stats['pending'] += 1
            
            # Store record for timeline
            all_records.append({
                'machine': machine_name,
                'qr_code': qr_value,
                'timestamp': timestamp,
                'status': status,
            })
        
        # Add machine stats if it has data
        if machine_stats['ok'] + machine_stats['ng'] + machine_stats['pending'] > 0:
            data['machine_stats'].append(machine_stats)
    
    # Sort records by timestamp - FIX FOR TIMEZONE ISSUE
    def safe_sort_key(record):
        """Convert timestamp to timezone-aware datetime for sorting"""
        dt = parse_timestamp_to_datetime(record['timestamp'])
        if dt is None:
            # Return a very old timezone-aware datetime for None values
            return timezone.make_aware(datetime.min.replace(year=1900))
        
        # Ensure datetime is timezone-aware
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        
        return dt
    
    all_records.sort(key=safe_sort_key)
    
    # Generate timeline data (daily aggregation)
    daily_data = defaultdict(lambda: {'ok': 0, 'ng': 0})
    hourly_data = defaultdict(int)
    
    for record in all_records:
        timestamp = record['timestamp']
        dt = parse_timestamp_to_datetime(timestamp)
        
        if dt:
            date_key = dt.strftime('%Y-%m-%d')
            hour_key = dt.strftime('%H:00')
        else:
            continue
        
        # Daily aggregation for timeline
        if record['status'] == 'OK':
            daily_data[date_key]['ok'] += 1
        elif record['status'] == 'NG':
            daily_data[date_key]['ng'] += 1
        
        # Hourly aggregation (count all parts regardless of status)
        hourly_data[hour_key] += 1
    
    # Timeline data (daily OK/NG breakdown)
    sorted_dates = sorted(daily_data.keys())
    data['timeline_data']['labels'] = sorted_dates
    data['timeline_data']['ok'] = [daily_data[date]['ok'] for date in sorted_dates]
    data['timeline_data']['ng'] = [daily_data[date]['ng'] for date in sorted_dates]
    
    # Hourly data (parts produced per hour)
    if hourly_data:
        sorted_hours = sorted(hourly_data.keys())
        data['hourly_data']['labels'] = sorted_hours
        data['hourly_data']['values'] = [hourly_data[hour] for hour in sorted_hours]
    
    # Trend data (yield rate by day)
    for date in sorted_dates:
        ok_count = daily_data[date]['ok']
        ng_count = daily_data[date]['ng']
        total_completed = ok_count + ng_count
        yield_rate = (ok_count / total_completed * 100) if total_completed > 0 else 0
        data['trend_data']['labels'].append(date)
        data['trend_data']['values'].append(round(yield_rate, 2))
    
    # Store detailed data (limit to 100 most recent)
    data['detailed_data'] = all_records[-100:]
    
    return data


@csrf_exempt
def analytics_api(request):
    """API endpoint for analytics data"""
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    machine_filter = request.GET.get('machine', 'all')
    status_filter = request.GET.get('status', 'all')
    
    start_date, end_date = get_date_range(start_date_str, end_date_str)
    
    data = collect_analytics_data(start_date, end_date, machine_filter, status_filter)
    
    # Convert datetime objects to strings
    for record in data['detailed_data']:
        if hasattr(record['timestamp'], 'isoformat'):
            record['timestamp'] = record['timestamp'].isoformat()
        else:
            record['timestamp'] = str(record['timestamp'])
    
    return JsonResponse(data)


@csrf_exempt
def analytics_export(request):
    """Export analytics data to CSV"""
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    machine_filter = request.GET.get('machine', 'all')
    status_filter = request.GET.get('status', 'all')
    
    start_date, end_date = get_date_range(start_date_str, end_date_str)
    
    data = collect_analytics_data(start_date, end_date, machine_filter, status_filter)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="analytics_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write summary statistics
    writer.writerow(['Production Analytics Report'])
    writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Date Range:', f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"])
    writer.writerow([])
    
    writer.writerow(['Summary Statistics'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Parts', data['total_parts']])
    writer.writerow(['OK Parts', data['ok_parts']])
    writer.writerow(['NG Parts', data['ng_parts']])
    writer.writerow(['Pending Parts', data['pending_parts']])
    
    if data['ok_parts'] + data['ng_parts'] > 0:
        yield_rate = (data['ok_parts'] / (data['ok_parts'] + data['ng_parts'])) * 100
        writer.writerow(['Yield Rate', f"{yield_rate:.2f}%"])
    
    writer.writerow(['Active Machines', data['active_machines']])
    writer.writerow([])
    
    # Write machine breakdown
    writer.writerow(['Machine Breakdown'])
    writer.writerow(['Machine', 'OK', 'NG', 'Pending', 'Total', 'Yield Rate %'])
    for machine in data['machine_stats']:
        total = machine['ok'] + machine['ng'] + machine['pending']
        completed = machine['ok'] + machine['ng']
        yield_rate = (machine['ok'] / completed * 100) if completed > 0 else 0
        writer.writerow([
            machine['machine'],
            machine['ok'],
            machine['ng'],
            machine['pending'],
            total,
            f"{yield_rate:.2f}"
        ])
    writer.writerow([])
    
    # Write detailed data
    writer.writerow(['Detailed Records'])
    writer.writerow(['Machine', 'QR Code', 'Timestamp', 'Status'])
    for record in data['detailed_data']:
        timestamp_str = record['timestamp'] if isinstance(record['timestamp'], str) else record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([
            record['machine'],
            record['qr_code'],
            timestamp_str,
            record['status'],
        ])
    
    return response