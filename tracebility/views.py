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
# MACHINE CONFIGURATIONS - UPDATED WITH SEPARATE LOAD/UNLOAD FOR WASHING
# ============================================================================

MACHINE_CONFIGS = [
    # CNC Machines (DMG MORI)
    {'name': 'DMG MORI1(op-110A)', 'display_name': 'CNC 1', 'ip': '192.168.1.101', 'op_code': 'op-110A', 'prep_model': models.Cnc1Preprocessing, 'post_model': models.Cnc1Postprocessing, 'type': 'cnc'},
    {'name': 'DMG MORI2(op-110B)', 'display_name': 'CNC 2', 'ip': '192.168.1.102', 'op_code': 'op-110B', 'prep_model': models.Cnc2Preprocessing, 'post_model': models.Cnc2Postprocessing, 'type': 'cnc'},
    {'name': 'DMG MORI3(op-130D)', 'display_name': 'CNC 3', 'ip': '192.168.1.103', 'op_code': 'op-130D', 'prep_model': models.Cnc3Preprocessing, 'post_model': models.Cnc3Postprocessing, 'type': 'cnc'},
    {'name': 'DMG MORI4(op-130C)', 'display_name': 'CNC 4', 'ip': '192.168.1.104', 'op_code': 'op-130C', 'prep_model': models.Cnc4Preprocessing, 'post_model': models.Cnc4Postprocessing, 'type': 'cnc'},
    {'name': 'DMG MORI5(op-130B)', 'display_name': 'CNC 5', 'ip': '192.168.1.105', 'op_code': 'op-130B', 'prep_model': models.Cnc5Preprocessing, 'post_model': models.Cnc5Postprocessing, 'type': 'cnc'},
    {'name': 'DMG MORI6(op-130A)', 'display_name': 'CNC 6', 'ip': '192.168.1.106', 'op_code': 'op-130A', 'prep_model': models.Cnc6Preprocessing, 'post_model': models.Cnc6Postprocessing, 'type': 'cnc'},
    
    # Gauge Machines
    {'name': 'Gauge1(op-115)', 'display_name': 'Gauge 1', 'ip': '192.168.1.107', 'op_code': 'op-115', 'prep_model': models.Gauge1Preprocessing, 'post_model': models.Gauge1Postprocessing, 'type': 'gauge'},
    {'name': 'Gauge2(op-135B)', 'display_name': 'Gauge 2', 'ip': '192.168.1.108', 'op_code': 'op-135B', 'prep_model': models.Gauge2Preprocessing, 'post_model': models.Gauge2Postprocessing, 'type': 'gauge'},
    {'name': 'Gauge3(op-135A)', 'display_name': 'Gauge 3', 'ip': '192.168.1.109', 'op_code': 'op-135A', 'prep_model': models.Gauge3Preprocessing, 'post_model': models.Gauge3Postprocessing, 'type': 'gauge'},
    
    # Honing Machines
    {'name': 'Honing1(140A)', 'display_name': 'Honing 1', 'ip': '192.168.1.110', 'op_code': 'op-140A', 'prep_model': models.Honing1Preprocessing, 'post_model': models.Honing1Postprocessing, 'type': 'honing'},
    {'name': 'Honing2(140B)', 'display_name': 'Honing 2', 'ip': '192.168.1.111', 'op_code': 'op-140B', 'prep_model': models.Honing2Preprocessing, 'post_model': models.Honing2Postprocessing, 'type': 'honing'},
    
    # UPDATED: Washing Machines - Separate Load and Unload
    {'name': 'Prewashing_Loading(op-150)', 'display_name': 'Prewashing Load', 'ip': '192.168.1.112', 'op_code': 'op-150', 'prep_model': models.PrewashingPreprocessing, 'post_model': None, 'type': 'washing', 'operation': 'load'},
    {'name': 'Prewashing_Unloading(op-150)', 'display_name': 'Prewashing Unload', 'ip': '192.168.1.113', 'op_code': 'op-150', 'prep_model': None, 'post_model': models.PrewashingPostprocessing, 'type': 'washing', 'operation': 'unload'},
    {'name': 'Deburring(op-160)', 'display_name': 'Deburring', 'ip': '192.168.1.131', 'op_code': 'op-160', 'prep_model': models.DeburringPreprocessing, 'post_model': models.DeburringPostprocessing, 'type': 'processing'},
    {'name': 'Finlwashing_loading(op-170)', 'display_name': 'Final Washing Load', 'ip': '192.168.1.115', 'op_code': 'op-170', 'prep_model': models.FinalwashingPreprocessing, 'post_model': None, 'type': 'washing', 'operation': 'load'},
    {'name': 'Finlwashing_Unloading(op-170)', 'display_name': 'Final Washing Unload', 'ip': '192.168.1.116', 'op_code': 'op-170', 'prep_model': None, 'post_model': models.FinalwashingPostprocessing, 'type': 'washing', 'operation': 'unload'},
    
    # Painting
    {'name': 'Painting(op85)', 'display_name': 'Painting', 'ip': '192.168.1.122', 'op_code': 'op-85', 'prep_model': models.PaintingPreprocessing, 'post_model': models.PaintingPostprocessing, 'type': 'painting'},
    
    # Lubrication
    {'name': 'Lubrication(op90)', 'display_name': 'Lubrication', 'ip': '192.168.1.123', 'op_code': 'op-90', 'prep_model': models.LubPreprocessing, 'post_model': models.LubPostprocessing, 'type': 'lubrication'},
]

# Assembly machines (OP40 series)
ASSEMBLY_CONFIGS = [
    {'name': 'OP40A', 'display_name': 'Assembly OP40A', 'ip': '192.168.1.117', 'op_code': 'op-40A', 'prep_model': models.Op40AProcessing, 'post_model': models.Op40AProcessing, 'type': 'assembly'},
    {'name': 'OP40B', 'display_name': 'Assembly OP40B', 'ip': '192.168.1.118', 'op_code': 'op-40B', 'prep_model': models.Op40BProcessing, 'post_model': models.Op40BProcessing, 'type': 'assembly'},
    {'name': 'OP40C', 'display_name': 'Assembly OP40C', 'ip': '192.168.1.119', 'op_code': 'op-40C', 'prep_model': models.Op40CProcessing, 'post_model': models.Op40CProcessing, 'type': 'assembly'},
    {'name': 'OP40D', 'display_name': 'Assembly OP40D', 'ip': '192.168.1.120', 'op_code': 'op-40D', 'prep_model': models.Op40DProcessing, 'post_model': models.Op40DProcessing, 'type': 'assembly'},
]

# OP80 - Leak Test
OP80_CONFIG = {
    'name': 'Oring_leak(OP80)', 
    'display_name': 'OP80 Leak Test',
    'ip': '192.168.1.121',
    'op_code': 'op-80',
    'prep_model': models.Op80Preprocessing, 
    'post_model': models.Op80Postprocessing, 
    'type': 'op80'
}


# ============================================================================
# API to get machine list with IPs (for frontend dropdowns)
# ============================================================================
@csrf_exempt
def get_machines_list_api(request):
    """API endpoint to get all machines with their IPs and details"""
    machines = []
    
    # Add regular machines
    for config in MACHINE_CONFIGS:
        machines.append({
            'id': config['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_'),
            'name': config['name'],
            'display_name': config['display_name'],
            'ip': config['ip'],
            'op_code': config['op_code'],
            'type': config['type']
        })
    
    # Add assembly machines
    for config in ASSEMBLY_CONFIGS:
        machines.append({
            'id': config['name'].lower().replace(' ', '_'),
            'name': config['name'],
            'display_name': config['display_name'],
            'ip': config['ip'],
            'op_code': config['op_code'],
            'type': config['type']
        })
    
    # Add OP80
    machines.append({
        'id': 'op80_leak_test',
        'name': OP80_CONFIG['name'],
        'display_name': OP80_CONFIG['display_name'],
        'ip': OP80_CONFIG['ip'],
        'op_code': OP80_CONFIG['op_code'],
        'type': OP80_CONFIG['type']
    })
    
    return JsonResponse({'machines': machines})


# ============================================================================
# NEW: WASHING MACHINE HELPER FUNCTIONS
# ============================================================================

def get_washing_load_data(prep_model):
    """Get Load data for washing machines (Preprocessing only)"""
    records = []
    
    if not prep_model:
        return records
    
    prep_records = prep_model.objects.all()[:100]
    
    for prep in prep_records:
        model_name = getattr(prep, 'model_name', 'N/A')
        
        record = {
            'prep_id': prep.id,
            'prep_timestamp': prep.timestamp,
            'qr_code': getattr(prep, 'qr_data', '-'),
            'prep_status': getattr(prep, 'status', 'OK'),
            'previous_machine_status': getattr(prep, 'previous_machine_status', '-'),
            'model_name': model_name,
            'post_id': None,
            'post_timestamp': None,
            'post_status': 'N/A',  # Load doesn't have postprocessing
            'overall_status': getattr(prep, 'status', 'OK'),
            'status_class': 'load-only',
            'sort_priority': 1,
        }
        records.append(record)
    
    return records


def get_washing_unload_data(post_model):
    """Get Unload data for washing machines (Postprocessing only)"""
    records = []
    
    if not post_model:
        return records
    
    post_records = post_model.objects.all()[:100]
    
    for post in post_records:
        model_name = getattr(post, 'model_name', 'N/A')
        
        record = {
            'prep_id': None,
            'prep_timestamp': None,
            'qr_code': getattr(post, 'qr_data', '-'),
            'prep_status': 'N/A',  # Unload doesn't have preprocessing
            'previous_machine_status': getattr(post, 'previous_machine_status', '-'),
            'model_name': model_name,
            'post_id': post.id,
            'post_timestamp': post.timestamp,
            'post_status': getattr(post, 'status', 'OK'),
            'overall_status': getattr(post, 'status', 'OK'),
            'status_class': 'unload-only',
            'sort_priority': 1,
        }
        records.append(record)
    
    return records


def get_latest_washing_load_record(prep_model):
    """Get the latest load (preprocessing) record"""
    if not prep_model:
        return None
    
    try:
        prep = prep_model.objects.first()
        if not prep:
            return None
        
        # Format timestamp
        prep_timestamp = prep.timestamp
        if hasattr(prep_timestamp, 'isoformat'):
            timestamp_str = prep_timestamp.isoformat()
        else:
            timestamp_str = str(prep_timestamp)
        
        return {
            'prep_timestamp': timestamp_str,
            'qr_code': getattr(prep, 'qr_data', '-'),
            'post_status': 'LOAD',  # Indicate this is a load operation
            'prep_status': getattr(prep, 'status', 'OK'),
            'previous_machine_status': getattr(prep, 'previous_machine_status', '-'),
            'model_name': getattr(prep, 'model_name', 'N/A'),
        }
    except Exception as e:
        print(f"Error getting latest load record: {e}")
        return None


def get_latest_washing_unload_record(post_model):
    """Get the latest unload (postprocessing) record"""
    if not post_model:
        return None
    
    try:
        post = post_model.objects.first()
        if not post:
            return None
        
        # Format timestamp
        post_timestamp = post.timestamp
        if hasattr(post_timestamp, 'isoformat'):
            timestamp_str = post_timestamp.isoformat()
        else:
            timestamp_str = str(post_timestamp)
        
        return {
            'prep_timestamp': timestamp_str,  # Use post timestamp as main timestamp
            'qr_code': getattr(post, 'qr_data', '-'),
            'post_status': getattr(post, 'status', 'OK'),
            'prep_status': 'UNLOAD',  # Indicate this is an unload operation
            'previous_machine_status': getattr(post, 'previous_machine_status', '-'),
            'model_name': getattr(post, 'model_name', 'N/A'),
        }
    except Exception as e:
        print(f"Error getting latest unload record: {e}")
        return None


# ============================================================================
# EXISTING HELPER FUNCTIONS (Keep all your existing functions here)
# ============================================================================

def get_machine_data(prep_model, post_model, machine_type='standard'):
    """Aggregate preprocessing and postprocessing data - UPDATED to include model_name"""
    records = []
    prep_records = prep_model.objects.all()[:100]
    
    for prep in prep_records:
        # Determine QR code field based on machine type
        if machine_type == 'painting':
            qr_value_housing_prep = prep.qr_data_housing
            qr_value_piston_prep = prep.qr_data_piston
            post = post_model.objects.filter(qr_data_housing=qr_value_housing_prep).first()
            
        elif machine_type == 'lubrication':
            qr_value = prep.qr_data_piston
            qr_value_housing = prep.qr_data_housing
            post = post_model.objects.filter(qr_data_piston=qr_value).first()
            
        elif machine_type == 'op80':
            qr_value_piston = prep.qr_data_piston
            qr_value_housing = prep.qr_data_housing
            post = post_model.objects.filter(qr_data_housing=qr_value_housing).first()
            
        else:
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
        
        machine_name = getattr(prep, 'machine_name', 'N/A')
        model_name = getattr(prep, 'model_name', 'N/A')
        
        record = {
            'prep_id': prep.id,
            'prep_timestamp': prep.timestamp,
            'prep_machine_name': machine_name,
            'model_name': model_name,
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
            record['qr_housing_prep'] = qr_value_housing_prep
            record['qr_housing_post'] = post.qr_data_housing if post else None
            record['qr_piston_prep'] = qr_value_piston_prep
            record['qr_piston_post'] = post.qr_data_piston if post else None
            record['previous_machine_status'] = prep.previous_machine_status
            record['pre_status'] = prep.pre_status
            record['model_name_housing'] = getattr(prep, 'model_name_housing', 'N/A')
            record['model_name_piston'] = getattr(prep, 'model_name_piston', 'N/A')
            
        elif machine_type == 'lubrication':
            record['qr_housing'] = qr_value_housing
            record['model_name_piston'] = getattr(prep, 'model_name_piston', 'N/A')
            record['model_name_housing'] = getattr(prep, 'model_name_housing', 'N/A')
            
        elif machine_type == 'op80':
            record['qr_piston'] = qr_value_piston
            record['qr_housing_prep'] = qr_value_housing
            record['previous_machine_status'] = prep.previous_machine_status
            record['model_name_internal'] = getattr(prep, 'model_name_internal', 'N/A')
            record['model_name_external'] = getattr(prep, 'model_name_external', 'N/A')
            
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
        
        model_name_internal = getattr(prep, 'model_name_internal', 'N/A')
        model_name_external = getattr(prep, 'model_name_external', 'N/A')
        model_name_housing = getattr(prep, 'model_name_housing', 'N/A')
        
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
            'model_name_internal': model_name_internal,
            'model_name_external': model_name_external,
            'model_name_housing': model_name_housing,
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
    """Convert timestamp string to datetime object"""
    if timestamp is None:
        return None
    
    if hasattr(timestamp, 'strftime'):
        return timestamp
    
    if isinstance(timestamp, str):
        try:
            return datetime.strptime(timestamp, '%d/%m/%Y, %I:%M:%S %p')
        except:
            pass
        
        try:
            return datetime.strptime(timestamp, '%m/%d/%Y, %I:%M:%S %p')
        except:
            pass
        
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
        
        try:
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            pass
    
    return None


def check_machine_status(prep_model):
    """Check if machine is active"""
    threshold = timezone.now() - timedelta(minutes=21)
    
    try:
        latest_record = prep_model.objects.first()
        if not latest_record:
            return False
        
        try:
            timestamp = latest_record.timestamp_internal
            field_name = 'timestamp_internal'
        except AttributeError:
            timestamp = latest_record.timestamp
            field_name = 'timestamp'
        
        if hasattr(timestamp, 'timestamp'):
            if timezone.is_naive(timestamp):
                timestamp = timezone.make_aware(timestamp)
            
            is_active = timestamp >= threshold
            return is_active
        
        if isinstance(timestamp, str):
            parsed_dt = parse_timestamp_to_datetime(timestamp)
            
            if parsed_dt:
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
    
    model_name = getattr(latest_prep, 'model_name', 'N/A')
    
    if machine_type == 'painting':
        qr_value = latest_prep.qr_data_housing
        qr_piston = latest_prep.qr_data_piston
        post = post_model.objects.filter(qr_data_housing=qr_value).first()
        model_name_housing = getattr(latest_prep, 'model_name_housing', 'N/A')
        model_name_piston = getattr(latest_prep, 'model_name_piston', 'N/A')
        
    elif machine_type == 'lubrication':
        qr_value = latest_prep.qr_data_piston
        qr_housing = latest_prep.qr_data_housing
        post = post_model.objects.filter(qr_data_piston=qr_value).first()
        model_name_piston = getattr(latest_prep, 'model_name_piston', 'N/A')
        model_name_housing = getattr(latest_prep, 'model_name_housing', 'N/A')
        
    elif machine_type == 'op80':
        qr_value = latest_prep.qr_data_piston
        qr_housing = latest_prep.qr_data_housing
        post = post_model.objects.filter(qr_data_housing_new=qr_housing).first()
        model_name_internal = getattr(latest_prep, 'model_name_internal', 'N/A')
        model_name_external = getattr(latest_prep, 'model_name_external', 'N/A')
        
    else:
        qr_value = latest_prep.qr_data
        post = post_model.objects.filter(qr_data=qr_value).first()
    
    gauge_values = {}
    if post and hasattr(post, 'value1'):
        for i in range(1, 7):
            val = getattr(post, f'value{i}', None)
            if val is not None:
                gauge_values[f'value{i}'] = val
    
    prep_timestamp = latest_prep.timestamp
    if hasattr(prep_timestamp, 'isoformat'):
        timestamp_str = prep_timestamp.isoformat()
    else:
        timestamp_str = str(prep_timestamp)
    
    result = {
        'qr_code': qr_value,
        'prep_timestamp': timestamp_str,
        'post_status': post.status if post else 'Pending',
        'has_post': post is not None,
        'gauge_values': gauge_values,
        'model_name': model_name,
    }
    
    if machine_type == 'painting':
        result['qr_piston'] = qr_piston
        result['model_name_housing'] = model_name_housing
        result['model_name_piston'] = model_name_piston
    elif machine_type == 'lubrication':
        result['qr_housing'] = qr_housing
        result['model_name_piston'] = model_name_piston
        result['model_name_housing'] = model_name_housing
    elif machine_type == 'op80':
        result['qr_housing'] = qr_housing
        result['model_name_internal'] = model_name_internal
        result['model_name_external'] = model_name_external
    
    return result


def get_latest_assembly_record(prep_model, post_model):
    """Get the latest record for assembly machine"""
    latest_prep = prep_model.objects.first()
    if not latest_prep:
        return None
    
    qr_internal = latest_prep.qr_data_internal
    
    model_name_internal = getattr(latest_prep, 'model_name_internal', 'N/A')
    model_name_external = getattr(latest_prep, 'model_name_external', 'N/A')
    model_name_housing = getattr(latest_prep, 'model_name_housing', 'N/A')
    
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
        'model_name_internal': model_name_internal,
        'model_name_external': model_name_external,
        'model_name_housing': model_name_housing,
    }


# ============================================================================
# MAIN VIEWS - UPDATED WITH WASHING MACHINE SUPPORT
# ============================================================================

def dashboard_view(request):
    """Main dashboard showing all machines - UPDATED for washing machines"""
    machines_data = []
    
    for config in MACHINE_CONFIGS:
        # Handle washing machines separately
        if config.get('type') == 'washing':
            operation = config.get('operation', 'load')
            
            if operation == 'load' and config['prep_model']:
                is_active = check_machine_status(config['prep_model'])
                latest_record = get_latest_washing_load_record(config['prep_model'])
            elif operation == 'unload' and config['post_model']:
                try:
                    latest_post = config['post_model'].objects.first()
                    if latest_post:
                        threshold = timezone.now() - timedelta(minutes=21)
                        timestamp = latest_post.timestamp
                        if hasattr(timestamp, 'timestamp'):
                            if timezone.is_naive(timestamp):
                                timestamp = timezone.make_aware(timestamp)
                            is_active = timestamp >= threshold
                        else:
                            parsed_dt = parse_timestamp_to_datetime(timestamp)
                            if parsed_dt:
                                if timezone.is_naive(parsed_dt):
                                    parsed_dt = timezone.make_aware(parsed_dt)
                                is_active = parsed_dt >= threshold
                            else:
                                is_active = False
                    else:
                        is_active = False
                except:
                    is_active = False
                
                latest_record = get_latest_washing_unload_record(config['post_model'])
            else:
                is_active = False
                latest_record = None
        else:
            # Regular machines
            is_active = check_machine_status(config['prep_model'])
            
            machine_type = 'standard'
            if 'Painting' in config['name']:
                machine_type = 'painting'
            elif 'Lubrication' in config['name']:
                machine_type = 'lubrication'
            
            latest_record = get_latest_machine_record(config['prep_model'], config['post_model'], machine_type)
        
        machines_data.append({
            'name': config['name'],
            'display_name': config['display_name'],
            'ip': config['ip'],
            'op_code': config['op_code'],
            'type': config['type'],
            'is_active': is_active,
            'is_assembly': False,
            'machine_id': config['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_'),
            'latest_record': latest_record,
        })
    
    for config in ASSEMBLY_CONFIGS:
        is_active = check_machine_status(config['prep_model'])
        latest_record = get_latest_assembly_record(config['prep_model'], config['post_model'])
        
        machines_data.append({
            'name': config['name'],
            'display_name': config['display_name'],
            'ip': config['ip'],
            'op_code': config['op_code'],
            'type': 'assembly',
            'is_active': is_active,
            'is_assembly': True,
            'machine_id': config['name'].lower().replace(' ', '_'),
            'latest_record': latest_record,
        })
    
    # Add OP80
    is_active = check_machine_status(OP80_CONFIG['prep_model'])
    latest_record = get_latest_machine_record(
        OP80_CONFIG['prep_model'], 
        OP80_CONFIG['post_model'], 
        'op80'
    )
    
    machines_data.append({
        'name': OP80_CONFIG['name'],
        'display_name': OP80_CONFIG['display_name'],
        'ip': OP80_CONFIG['ip'],
        'op_code': OP80_CONFIG['op_code'],
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
        machine_id = m['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
        if machine_id == machine_name:
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
        return render(request, 'dashboard/machine_detail.html', {'error': 'Machine not found'})
    
    if is_assembly:
        records = get_assembly_machine_data(config['prep_model'], config['post_model'])
        machine_type = 'assembly'
    elif config.get('type') == 'washing':
        operation = config.get('operation', 'load')
        machine_type = 'washing'
        
        if operation == 'load':
            records = get_washing_load_data(config['prep_model'])
        else:
            records = get_washing_unload_data(config['post_model'])
    else:
        machine_type = 'standard'
        if 'Painting' in config['name']:
            machine_type = 'painting'
        elif 'Lubrication' in config['name']:
            machine_type = 'lubrication'
        elif 'Oring_leak' in config['name']:
            machine_type = 'op80'
        records = get_machine_data(config['prep_model'], config['post_model'], machine_type)
    
    is_active = check_machine_status(config['prep_model']) if config['prep_model'] else False
    
    records_json = []
    for record in records:
        record_copy = record.copy()
        if record.get('prep_timestamp') and hasattr(record['prep_timestamp'], 'isoformat'):
            record_copy['prep_timestamp'] = record['prep_timestamp'].isoformat()
        if record.get('post_timestamp') and hasattr(record['post_timestamp'], 'isoformat'):
            record_copy['post_timestamp'] = record['post_timestamp'].isoformat()
        records_json.append(record_copy)
    
    context = {
        'machine_name': config['name'],
        'display_name': config.get('display_name', config['name']),
        'ip': config.get('ip', 'N/A'),
        'op_code': config.get('op_code', 'N/A'),
        'machine_type': machine_type,
        'is_active': is_active,
        'records': records,
        'records_json': json.dumps(records_json, cls=DjangoJSONEncoder),
        'is_assembly': is_assembly,
    }
    
    return render(request, 'dashboard/machine_detail.html', context)


@csrf_exempt
def machine_data_api(request, machine_name):
    """API endpoint for real-time updates and modal data - UPDATED for washing machines"""
    config = None
    is_assembly = False
    
    for m in MACHINE_CONFIGS:
        machine_id = m['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
        if machine_id == machine_name:
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
        return JsonResponse({'error': 'Machine not found'}, status=404)
    
    # Handle washing machines
    if config.get('type') == 'washing':
        operation = config.get('operation', 'load')
        machine_type = 'washing'
        
        if operation == 'load':
            records = get_washing_load_data(config['prep_model'])
            is_active = check_machine_status(config['prep_model']) if config['prep_model'] else False
        else:
            records = get_washing_unload_data(config['post_model'])
            try:
                latest_post = config['post_model'].objects.first()
                if latest_post:
                    threshold = timezone.now() - timedelta(minutes=21)
                    timestamp = latest_post.timestamp
                    if hasattr(timestamp, 'timestamp'):
                        if timezone.is_naive(timestamp):
                            timestamp = timezone.make_aware(timestamp)
                        is_active = timestamp >= threshold
                    else:
                        is_active = False
                else:
                    is_active = False
            except:
                is_active = False
        
        for record in records:
            if record.get('prep_timestamp') and hasattr(record['prep_timestamp'], 'isoformat'):
                record['prep_timestamp'] = record['prep_timestamp'].isoformat()
            if record.get('post_timestamp') and hasattr(record['post_timestamp'], 'isoformat'):
                record['post_timestamp'] = record['post_timestamp'].isoformat()
        
        return JsonResponse({
            'machine_name': config['name'],
            'display_name': config.get('display_name', config['name']),
            'ip': config.get('ip', 'N/A'),
            'op_code': config.get('op_code', 'N/A'),
            'machine_type': machine_type,
            'operation': operation,
            'is_active': is_active,
            'records': records,
            'is_assembly': False,
        })
    
    if is_assembly:
        records = get_assembly_machine_data(config['prep_model'], config['post_model'])
        machine_type = 'assembly'
    else:
        machine_type = 'standard'
        if 'Painting' in config['name']:
            machine_type = 'painting'
        elif 'Lubrication' in config['name']:
            machine_type = 'lubrication'
        elif 'Oring_leak' in config['name']:
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
        'display_name': config.get('display_name', config['name']),
        'ip': config.get('ip', 'N/A'),
        'op_code': config.get('op_code', 'N/A'),
        'machine_type': machine_type,
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
        # Skip washing machines or handle specially
        if config.get('type') == 'washing':
            operation = config.get('operation', 'load')
            if operation == 'load' and config['prep_model']:
                prep_records = config['prep_model'].objects.filter(qr_data__icontains=qr_code)
                if prep_records.exists():
                    results.append({
                        'machine': config['name'],
                        'display_name': config.get('display_name', config['name']),
                        'preprocessing_count': prep_records.count(),
                        'postprocessing_count': 0,
                    })
            elif operation == 'unload' and config['post_model']:
                post_records = config['post_model'].objects.filter(qr_data__icontains=qr_code)
                if post_records.exists():
                    results.append({
                        'machine': config['name'],
                        'display_name': config.get('display_name', config['name']),
                        'preprocessing_count': 0,
                        'postprocessing_count': post_records.count(),
                    })
            continue
        
        if 'Painting' in config['name']:
            prep_records = config['prep_model'].objects.filter(
                Q(qr_data_housing__icontains=qr_code) | Q(qr_data_piston__icontains=qr_code)
            )
            post_records = config['post_model'].objects.filter(qr_data_housing__icontains=qr_code)
        elif 'Lubrication' in config['name']:
            prep_records = config['prep_model'].objects.filter(
                Q(qr_data_piston__icontains=qr_code) | Q(qr_data_housing__icontains=qr_code)
            )
            post_records = config['post_model'].objects.filter(qr_data_piston__icontains=qr_code)
        elif 'Oring_leak' in config['name']:
            prep_records = config['prep_model'].objects.filter(
                Q(qr_data_piston__icontains=qr_code) | Q(qr_data_housing__icontains=qr_code)
            )
            post_records = config['post_model'].objects.filter(qr_data_housing_new__icontains=qr_code)
        else:
            prep_records = config['prep_model'].objects.filter(qr_data__icontains=qr_code)
            post_records = config['post_model'].objects.filter(qr_data__icontains=qr_code) if config['post_model'] else []
        
        if prep_records.exists() or (post_records and post_records.exists()):
            results.append({
                'machine': config['name'],
                'display_name': config.get('display_name', config['name']),
                'preprocessing_count': prep_records.count(),
                'postprocessing_count': post_records.count() if post_records else 0,
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
                'display_name': config.get('display_name', config['name']),
                'preprocessing_count': prep_records.count(),
                'postprocessing_count': 0,
            })
    
    prep_records = OP80_CONFIG['prep_model'].objects.filter(
        Q(qr_data_piston__icontains=qr_code) | Q(qr_data_housing__icontains=qr_code)
    )
    post_records = OP80_CONFIG['post_model'].objects.filter(qr_data_housing_new__icontains=qr_code)
    
    if prep_records.exists() or post_records.exists():
        results.append({
            'machine': OP80_CONFIG['name'],
            'display_name': OP80_CONFIG.get('display_name', OP80_CONFIG['name']),
            'preprocessing_count': prep_records.count(),
            'postprocessing_count': post_records.count(),
        })

    return JsonResponse({'qr_code': qr_code, 'results': results})


def export_machine_data(request, machine_name):
    """Export machine data to CSV"""
    config = None
    is_assembly = False
    
    for m in MACHINE_CONFIGS:
        machine_id = m['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
        if machine_id == machine_name:
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
    elif config.get('type') == 'washing':
        operation = config.get('operation', 'load')
        if operation == 'load':
            records = get_washing_load_data(config['prep_model'])
        else:
            records = get_washing_unload_data(config['post_model'])
    else:
        machine_type = 'standard'
        if 'Painting' in config['name']:
            machine_type = 'painting'
        elif 'Lubrication' in config['name']:
            machine_type = 'lubrication'
        records = get_machine_data(config['prep_model'], config['post_model'], machine_type)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{machine_name}_data.csv"'
    
    writer = csv.writer(response)
    
    if is_assembly:
        writer.writerow(['ID', 'QR Internal', 'QR External', 'QR Housing', 'Model Internal', 'Model External', 'Model Housing',
                        'Prep Timestamp', 'Post Timestamp', 'Status', 'Overall Status'])
        for record in records:
            writer.writerow([
                record['prep_id'], record['qr_code'], record.get('qr_external', '-'),
                record.get('qr_housing', '-'), 
                record.get('model_name_internal', 'N/A'), record.get('model_name_external', 'N/A'), record.get('model_name_housing', 'N/A'),
                record['prep_timestamp'],
                record['post_timestamp'] or '-', record['post_status'] or '-',
                record['overall_status'],
            ])
    else:
        writer.writerow(['ID', 'QR Code', 'Model Name', 'Prep Timestamp', 'Post Timestamp', 
                        'Status', 'Overall Status', 'Gauge Values'])
        for record in records:
            writer.writerow([
                record.get('prep_id') or record.get('post_id'), record['qr_code'], record.get('model_name', 'N/A'),
                record.get('prep_timestamp') or '-',
                record.get('post_timestamp') or '-', record.get('post_status') or '-',
                record['overall_status'], record.get('gauge_values', '-') or '-',
            ])
    
    return response


# ============================================================================
# REAL-TIME STREAMING (SSE) - UPDATED FOR WASHING MACHINES
# ============================================================================

def get_latest_record_count(model):
    """Get the count of records for change detection"""
    if not model:
        return 0
    return model.objects.count()


def get_dashboard_summary():
    """Get summary data for all machines"""
    machines_data = []
    
    for config in MACHINE_CONFIGS:
        if config.get('type') == 'washing':
            operation = config.get('operation', 'load')
            
            if operation == 'load' and config['prep_model']:
                is_active = check_machine_status(config['prep_model'])
                latest_record = get_latest_washing_load_record(config['prep_model'])
            elif operation == 'unload' and config['post_model']:
                try:
                    latest_post = config['post_model'].objects.first()
                    if latest_post:
                        threshold = timezone.now() - timedelta(minutes=21)
                        timestamp = latest_post.timestamp
                        if hasattr(timestamp, 'timestamp'):
                            if timezone.is_naive(timestamp):
                                timestamp = timezone.make_aware(timestamp)
                            is_active = timestamp >= threshold
                        else:
                            is_active = False
                    else:
                        is_active = False
                except:
                    is_active = False
                
                latest_record = get_latest_washing_unload_record(config['post_model'])
            else:
                is_active = False
                latest_record = None
        else:
            is_active = check_machine_status(config['prep_model'])
            machine_type = 'standard'
            if 'Painting' in config['name']:
                machine_type = 'painting'
            elif 'Lubrication' in config['name']:
                machine_type = 'lubrication'
            
            latest_record = get_latest_machine_record(config['prep_model'], config['post_model'], machine_type)
        
        machines_data.append({
            'name': config['name'],
            'display_name': config.get('display_name', config['name']),
            'ip': config.get('ip', 'N/A'),
            'op_code': config.get('op_code', 'N/A'),
            'machine_id': config['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_'),
            'is_active': is_active,
            'latest_record': latest_record,
            'type': config['type'],
        })
    
    for config in ASSEMBLY_CONFIGS:
        is_active = check_machine_status(config['prep_model'])
        latest_record = get_latest_assembly_record(config['prep_model'], config['post_model'])
        
        machines_data.append({
            'name': config['name'],
            'display_name': config.get('display_name', config['name']),
            'ip': config.get('ip', 'N/A'),
            'op_code': config.get('op_code', 'N/A'),
            'machine_id': config['name'].lower().replace(' ', '_'),
            'is_active': is_active,
            'latest_record': latest_record,
            'is_assembly': True,
            'type': 'assembly',
        })
    
    is_active = check_machine_status(OP80_CONFIG['prep_model'])
    latest_record = get_latest_machine_record(
        OP80_CONFIG['prep_model'], 
        OP80_CONFIG['post_model'], 
        'op80'
    )
    
    machines_data.append({
        'name': OP80_CONFIG['name'],
        'display_name': OP80_CONFIG.get('display_name', OP80_CONFIG['name']),
        'ip': OP80_CONFIG.get('ip', 'N/A'),
        'op_code': OP80_CONFIG.get('op_code', 'N/A'),
        'machine_id': 'op80_leak_test',
        'is_active': is_active,
        'latest_record': latest_record,
        'type': 'op80',
    })
    
    return machines_data


def sse_dashboard_stream(request):
    """Server-Sent Events stream for dashboard updates"""
    
    def event_stream():
        last_counts = {}
        
        for config in MACHINE_CONFIGS + ASSEMBLY_CONFIGS + [OP80_CONFIG]:
            if config.get('prep_model'):
                prep_table = config['prep_model']._meta.db_table
                last_counts[prep_table] = get_latest_record_count(config['prep_model'])
            if config.get('post_model'):
                post_table = config['post_model']._meta.db_table
                last_counts[post_table] = get_latest_record_count(config['post_model'])
        
        while True:
            try:
                changed = False
                for config in MACHINE_CONFIGS + ASSEMBLY_CONFIGS + [OP80_CONFIG]:
                    if config.get('prep_model'):
                        prep_table = config['prep_model']._meta.db_table
                        current_prep_count = get_latest_record_count(config['prep_model'])
                        
                        if current_prep_count != last_counts.get(prep_table, 0):
                            changed = True
                            last_counts[prep_table] = current_prep_count
                    
                    if config.get('post_model'):
                        post_table = config['post_model']._meta.db_table
                        current_post_count = get_latest_record_count(config['post_model'])
                        
                        if current_post_count != last_counts.get(post_table, 0):
                            changed = True
                            last_counts[post_table] = current_post_count
                
                if changed:
                    machines_data = get_dashboard_summary()
                    
                    for machine in machines_data:
                        if machine.get('latest_record') and machine['latest_record'].get('prep_timestamp'):
                            if hasattr(machine['latest_record']['prep_timestamp'], 'isoformat'):
                                machine['latest_record']['prep_timestamp'] = machine['latest_record']['prep_timestamp'].isoformat()
                    
                    data = json.dumps({
                        'type': 'update',
                        'machines': machines_data
                    }, cls=DjangoJSONEncoder)
                    
                    yield f"data: {data}\n\n"
                
                yield f": heartbeat\n\n"
                time.sleep(2)
                
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
    """Server-Sent Events stream for specific machine updates - UPDATED for washing machines"""
    
    config = None
    is_assembly = False
    
    for m in MACHINE_CONFIGS:
        machine_id = m['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
        if machine_id == machine_name:
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
        # Handle washing machines separately for counting
        if config.get('type') == 'washing':
            operation = config.get('operation', 'load')
            if operation == 'load':
                last_prep_count = get_latest_record_count(config['prep_model']) if config['prep_model'] else 0
                last_post_count = 0
            else:
                last_prep_count = 0
                last_post_count = get_latest_record_count(config['post_model']) if config['post_model'] else 0
        else:
            last_prep_count = get_latest_record_count(config.get('prep_model'))
            last_post_count = get_latest_record_count(config.get('post_model'))
        
        while True:
            try:
                if config.get('type') == 'washing':
                    operation = config.get('operation', 'load')
                    if operation == 'load':
                        current_prep_count = get_latest_record_count(config['prep_model']) if config['prep_model'] else 0
                        current_post_count = 0
                    else:
                        current_prep_count = 0
                        current_post_count = get_latest_record_count(config['post_model']) if config['post_model'] else 0
                else:
                    current_prep_count = get_latest_record_count(config.get('prep_model'))
                    current_post_count = get_latest_record_count(config.get('post_model'))
                
                if (current_prep_count != last_prep_count or 
                    current_post_count != last_post_count):
                    
                    last_prep_count = current_prep_count
                    last_post_count = current_post_count
                    
                    # Get updated machine data
                    if config.get('type') == 'washing':
                        operation = config.get('operation', 'load')
                        machine_type = 'washing'
                        
                        if operation == 'load':
                            records = get_washing_load_data(config['prep_model'])
                            is_active = check_machine_status(config['prep_model']) if config['prep_model'] else False
                        else:
                            records = get_washing_unload_data(config['post_model'])
                            try:
                                latest_post = config['post_model'].objects.first()
                                if latest_post:
                                    threshold = timezone.now() - timedelta(minutes=21)
                                    timestamp = latest_post.timestamp
                                    if hasattr(timestamp, 'timestamp'):
                                        if timezone.is_naive(timestamp):
                                            timestamp = timezone.make_aware(timestamp)
                                        is_active = timestamp >= threshold
                                    else:
                                        is_active = False
                                else:
                                    is_active = False
                            except:
                                is_active = False
                    
                    elif is_assembly:
                        records = get_assembly_machine_data(config['prep_model'], config['post_model'])
                        machine_type = 'assembly'
                        is_active = check_machine_status(config['prep_model'])
                    else:
                        machine_type = 'standard'
                        if 'Painting' in config['name']:
                            machine_type = 'painting'
                        elif 'Lubrication' in config['name']:
                            machine_type = 'lubrication'
                        elif 'Oring_leak' in config['name']:
                            machine_type = 'op80'
                        records = get_machine_data(config['prep_model'], config['post_model'], machine_type)
                        is_active = check_machine_status(config['prep_model'])
                    
                    for record in records:
                        if record.get('prep_timestamp') and hasattr(record['prep_timestamp'], 'isoformat'):
                            record['prep_timestamp'] = record['prep_timestamp'].isoformat()
                        if record.get('post_timestamp') and hasattr(record['post_timestamp'], 'isoformat'):
                            record['post_timestamp'] = record['post_timestamp'].isoformat()
                    
                    response_data = {
                        'type': 'update',
                        'machine_name': config['name'],
                        'display_name': config.get('display_name', config['name']),
                        'ip': config.get('ip', 'N/A'),
                        'op_code': config.get('op_code', 'N/A'),
                        'machine_type': machine_type,
                        'is_active': is_active,
                        'records': records,
                        'is_assembly': is_assembly,
                    }
                    
                    if config.get('type') == 'washing':
                        response_data['operation'] = config.get('operation', 'load')
                    
                    data = json.dumps(response_data, cls=DjangoJSONEncoder)
                    
                    yield f"data: {data}\n\n"
                
                yield f": heartbeat\n\n"
                time.sleep(2)
                
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
# ANALYTICS VIEWS
# ============================================================================

def analytics_view(request):
    """Main analytics page"""
    return render(request, 'dashboard/analytics.html')


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
        config_id = config['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
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
    """Collect analytics data from all machines - UPDATED to include model_name info"""
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
        'active_machines': 0,
        'model_breakdown': {}  # NEW: breakdown by model_name
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
        is_assembly = 'OP40' in machine_name
        
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
            'display_name': config.get('display_name', machine_name),
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
            
            # Get model_name (NEW)
            if is_assembly:
                model_name = getattr(prep, 'model_name_internal', 'N/A')
            else:
                model_name = getattr(prep, 'model_name', 'N/A')
            
            # Get QR code and status based on machine type
            if is_assembly:
                qr_value = prep.qr_data_internal
                status = prep.status if prep.qr_data_external and prep.qr_data_housing else 'Pending'
                
            elif 'Painting' in machine_name:
                qr_value = prep.qr_data_housing
                post = config['post_model'].objects.filter(qr_data_housing=qr_value).first()
                status = post.status if post else 'Pending'
                
            elif 'Lubrication' in machine_name:
                qr_value = prep.qr_data_piston
                post = config['post_model'].objects.filter(qr_data_piston=qr_value).first()
                status = post.status if post else 'Pending'
                
            elif 'Oring_leak' in machine_name:
                qr_value = prep.qr_data_piston
                qr_housing = prep.qr_data_housing
                post = config['post_model'].objects.filter(qr_data_housing_new=qr_housing).first()
                status = post.status if post else 'Pending'
                
            else:
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
            
            # Track model breakdown (NEW)
            if model_name not in data['model_breakdown']:
                data['model_breakdown'][model_name] = {'ok': 0, 'ng': 0, 'pending': 0, 'total': 0}
            data['model_breakdown'][model_name]['total'] += 1
            if status == 'OK':
                data['model_breakdown'][model_name]['ok'] += 1
            elif status == 'NG':
                data['model_breakdown'][model_name]['ng'] += 1
            else:
                data['model_breakdown'][model_name]['pending'] += 1
            
            # Store record for timeline
            all_records.append({
                'machine': machine_name,
                'display_name': config.get('display_name', machine_name),
                'qr_code': qr_value,
                'timestamp': timestamp,
                'status': status,
                'model_name': model_name,  # NEW
            })
        
        # Add machine stats if it has data
        if machine_stats['ok'] + machine_stats['ng'] + machine_stats['pending'] > 0:
            data['machine_stats'].append(machine_stats)
    
    # Sort records by timestamp - FIX FOR TIMEZONE ISSUE
    def safe_sort_key(record):
        """Convert timestamp to timezone-aware datetime for sorting"""
        dt = parse_timestamp_to_datetime(record['timestamp'])
        if dt is None:
            return timezone.make_aware(datetime.min.replace(year=1900))
        
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
    writer.writerow(['Machine', 'Display Name', 'OK', 'NG', 'Pending', 'Total', 'Yield Rate %'])
    for machine in data['machine_stats']:
        total = machine['ok'] + machine['ng'] + machine['pending']
        completed = machine['ok'] + machine['ng']
        yield_rate = (machine['ok'] / completed * 100) if completed > 0 else 0
        writer.writerow([
            machine['machine'],
            machine.get('display_name', machine['machine']),
            machine['ok'],
            machine['ng'],
            machine['pending'],
            total,
            f"{yield_rate:.2f}"
        ])
    writer.writerow([])
    
    # Write model breakdown (NEW)
    if data['model_breakdown']:
        writer.writerow(['Model Breakdown'])
        writer.writerow(['Model Name', 'OK', 'NG', 'Pending', 'Total', 'Yield Rate %'])
        for model_name, stats in data['model_breakdown'].items():
            completed = stats['ok'] + stats['ng']
            yield_rate = (stats['ok'] / completed * 100) if completed > 0 else 0
            writer.writerow([
                model_name,
                stats['ok'],
                stats['ng'],
                stats['pending'],
                stats['total'],
                f"{yield_rate:.2f}"
            ])
        writer.writerow([])
                                        
    # Write detailed data
    writer.writerow(['Detailed Records'])
    writer.writerow(['Machine', 'Display Name', 'Model Name', 'QR Code', 'Timestamp', 'Status'])
    for record in data['detailed_data']:
        timestamp_str = record['timestamp'] if isinstance(record['timestamp'], str) else record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([
            record['machine'],
            record.get('display_name', record['machine']),
            record.get('model_name', 'N/A'),
            record['qr_code'],
            timestamp_str,
            record['status'],
        ])
    
    return response