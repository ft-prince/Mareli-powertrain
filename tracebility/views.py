from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from . import models
import csv


# Configuration for all machines
MACHINE_CONFIGS = [
    # DMG MORI Machines
    {'name': 'DMG MORI 1', 'prep_model': models.DmgMori1Preprocessing, 'post_model': models.DmgMori1Postprocessing, 'type': 'dmg_mori'},
    {'name': 'DMG MORI 2', 'prep_model': models.DmgMori2Preprocessing, 'post_model': models.DmgMori2Postprocessing, 'type': 'dmg_mori'},
    {'name': 'DMG MORI 3', 'prep_model': models.DmgMori3Preprocessing, 'post_model': models.DmgMori3Postprocessing, 'type': 'dmg_mori'},
    {'name': 'DMG MORI 4', 'prep_model': models.DmgMori4Preprocessing, 'post_model': models.DmgMori4Postprocessing, 'type': 'dmg_mori'},
    {'name': 'DMG MORI 5', 'prep_model': models.DmgMori5Preprocessing, 'post_model': models.DmgMori5Postprocessing, 'type': 'dmg_mori'},
    {'name': 'DMG MORI 6', 'prep_model': models.DmgMori6Preprocessing, 'post_model': models.DmgMori6Postprocessing, 'type': 'dmg_mori'},
    
    # Gauge Machines
    {'name': 'Gauge 1', 'prep_model': models.Gauge1Preprocessing, 'post_model': models.Gauge1Postprocessing, 'type': 'gauge'},
    {'name': 'Gauge 2', 'prep_model': models.Gauge2Preprocessing, 'post_model': models.Gauge2Postprocessing, 'type': 'gauge'},
    {'name': 'Gauge 3', 'prep_model': models.Gauge3Preprocessing, 'post_model': models.Gauge3Postprocessing, 'type': 'gauge'},
    
    # Honing Machines
    {'name': 'Honing 1', 'prep_model': models.Honing1Preprocessing, 'post_model': models.Honing1Postprocessing, 'type': 'honing'},
    {'name': 'Honing 2', 'prep_model': models.Honing2Preprocessing, 'post_model': models.Honing2Postprocessing, 'type': 'honing'},
    
    # Processing Machines
    {'name': 'Deburring', 'prep_model': models.DeburringPreprocessing, 'post_model': models.DeburringPostprocessing, 'type': 'processing'},
    {'name': 'Pre-Washing', 'prep_model': models.PrewashingPreprocessing, 'post_model': models.PrewashingPostprocessing, 'type': 'processing'},
    {'name': 'Final Washing', 'prep_model': models.FinalWashingPreprocessing, 'post_model': models.FinalWashingPostprocessing, 'type': 'processing'},
    
    # Final Processes
    {'name': 'O-Ring & Leak Test', 'prep_model': models.OringLeakTestPreprocessing, 'post_model': models.OringLeakTestPostprocessing, 'type': 'final'},
    {'name': 'Painting', 'prep_model': models.PaintingPreprocessing, 'post_model': models.PaintingPostprocessing, 'type': 'final'},
    {'name': 'Lubrication', 'prep_model': models.LubricationPreprocessing, 'post_model': models.LubricationPostprocessing, 'type': 'final'},
]

# Assembly machines
ASSEMBLY_CONFIGS = [
    {'name': 'Assembly Machine 1', 'prep_model': models.AssemblyMachine1Preprocessing, 'post_model': models.AssemblyMachine1Postprocessing},
    {'name': 'Assembly Machine 2', 'prep_model': models.AssemblyMachine2Preprocessing, 'post_model': models.AssemblyMachine2Postprocessing},
    {'name': 'Assembly Machine 3', 'prep_model': models.AssemblyMachine3Preprocessing, 'post_model': models.AssemblyMachine3Postprocessing},
    {'name': 'Assembly Machine 4', 'prep_model': models.AssemblyMachine4Preprocessing, 'post_model': models.AssemblyMachine4Postprocessing},
]


def get_machine_data(prep_model, post_model, machine_type='standard'):
    """Aggregate preprocessing and postprocessing data"""
    records = []
    prep_records = prep_model.objects.all()[:100]
    
    for prep in prep_records:
        if machine_type in ['oring', 'painting', 'lubrication']:
            qr_value = prep.qr_code
            post = post_model.objects.filter(qr_code=qr_value).first()
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
            for i in range(1, 6):
                val = getattr(post, f'value{i}', None)
                if val is not None:
                    gauge_values[f'value{i}'] = val
        
        records.append({
            'prep_id': prep.id,
            'prep_timestamp': prep.timestamp,
            'prep_machine_name': prep.machine_name,
            'prep_status': 'OK',
            'qr_code': qr_value,
            'post_id': post_id,
            'post_timestamp': post_timestamp,
            'post_status': post_status,
            'overall_status': overall_status,
            'status_class': status_class,
            'gauge_values': gauge_values,
            'sort_priority': 1 if post else 2,
        })
    
    records.sort(key=lambda x: (x['sort_priority'], -x['prep_timestamp'].timestamp()))
    return records


def get_assembly_machine_data(prep_model, post_model):
    """Special handler for assembly machines"""
    records = []
    prep_records = prep_model.objects.all()[:100]
    
    for prep in prep_records:
        qr_internal = prep.qr_code_internal
        post = post_model.objects.filter(qr_code_internal=qr_internal).first()
        
        if post:
            overall_status = post.status
            status_class = 'completed-ok' if post.status == 'OK' else 'completed-ng'
            post_id = post.id
            qr_external = post.qr_code_external
            qr_housing = post.qr_code_housing
            post_timestamp = post.timestamp
            post_status = post.status
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
            'prep_timestamp': prep.timestamp,
            'prep_machine_name': prep.machine_name,
            'prep_status': 'OK',
            'qr_code': qr_internal,
            'qr_external': qr_external,
            'qr_housing': qr_housing,
            'post_id': post_id,
            'post_timestamp': post_timestamp,
            'post_status': post_status,
            'overall_status': overall_status,
            'status_class': status_class,
            'sort_priority': 1 if post else 2,
        })
    
    records.sort(key=lambda x: (x['sort_priority'], -x['prep_timestamp'].timestamp()))
    return records


def check_machine_status(prep_model):
    """Check if machine is active (data within last 5 minutes)"""
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    recent_count = prep_model.objects.filter(timestamp__gte=five_minutes_ago).count()
    return recent_count > 0


def get_latest_machine_record(prep_model, post_model, machine_type='standard'):
    """Get the latest record for a machine"""
    latest_prep = prep_model.objects.first()
    if not latest_prep:
        return None
    
    if machine_type in ['oring', 'painting', 'lubrication']:
        qr_value = latest_prep.qr_code
        post = post_model.objects.filter(qr_code=qr_value).first()
    else:
        qr_value = latest_prep.qr_data
        post = post_model.objects.filter(qr_data=qr_value).first()
    
    # Get gauge values if applicable
    gauge_values = {}
    if post and hasattr(post, 'value1'):
        for i in range(1, 6):
            val = getattr(post, f'value{i}', None)
            if val is not None:
                gauge_values[f'value{i}'] = val
    
    return {
        'qr_code': qr_value,
        'prep_timestamp': latest_prep.timestamp,
        'post_status': post.status if post else 'Pending',
        'has_post': post is not None,
        'gauge_values': gauge_values,
    }


def get_latest_assembly_record(prep_model, post_model):
    """Get the latest record for assembly machine"""
    latest_prep = prep_model.objects.first()
    if not latest_prep:
        return None
    
    qr_internal = latest_prep.qr_code_internal
    post = post_model.objects.filter(qr_code_internal=qr_internal).first()
    
    return {
        'qr_code': qr_internal,
        'qr_external': post.qr_code_external if post else '-',
        'qr_housing': post.qr_code_housing if post else '-',
        'prep_timestamp': latest_prep.timestamp,
        'post_status': post.status if post else 'Pending',
        'has_post': post is not None,
    }


def dashboard_view(request):
    """Main dashboard showing all machines"""
    machines_data = []
    
    for config in MACHINE_CONFIGS:
        is_active = check_machine_status(config['prep_model'])
        machine_type = 'standard'
        if config['name'].startswith('O-Ring'):
            machine_type = 'oring'
        elif config['name'] == 'Painting':
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
    
    return render(request, 'dashboard/dashboard.html', {'machines': machines_data})


def machine_detail_view(request, machine_name):
    """Detail view for specific machine"""
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    
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
    
    if not config:
        return render(request, 'dashboard/machine_detail.html', {'error': 'Machine not found'})
    
    if is_assembly:
        records = get_assembly_machine_data(config['prep_model'], config['post_model'])
    else:
        machine_type = 'standard'
        if config['name'].startswith('O-Ring'):
            machine_type = 'oring'
        elif config['name'] == 'Painting':
            machine_type = 'painting'
        elif config['name'] == 'Lubrication':
            machine_type = 'lubrication'
        records = get_machine_data(config['prep_model'], config['post_model'], machine_type)
    
    is_active = check_machine_status(config['prep_model'])
    
    # Convert datetime objects to strings for JSON
    records_json = []
    for record in records:
        record_copy = record.copy()
        record_copy['prep_timestamp'] = record['prep_timestamp'].isoformat()
        if record['post_timestamp']:
            record_copy['post_timestamp'] = record['post_timestamp'].isoformat()
        records_json.append(record_copy)
    
    context = {
        'machine_name': config['name'],
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
    
    if not config:
        return JsonResponse({'error': 'Machine not found'}, status=404)
    
    if is_assembly:
        records = get_assembly_machine_data(config['prep_model'], config['post_model'])
    else:
        machine_type = 'standard'
        if config['name'].startswith('O-Ring'):
            machine_type = 'oring'
        elif config['name'] == 'Painting':
            machine_type = 'painting'
        elif config['name'] == 'Lubrication':
            machine_type = 'lubrication'
        records = get_machine_data(config['prep_model'], config['post_model'], machine_type)
    
    is_active = check_machine_status(config['prep_model'])
    
    for record in records:
        record['prep_timestamp'] = record['prep_timestamp'].isoformat()
        if record['post_timestamp']:
            record['post_timestamp'] = record['post_timestamp'].isoformat()
    
    return JsonResponse({
        'machine_name': config['name'],
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
        if config['name'].startswith('O-Ring') or config['name'] in ['Painting', 'Lubrication']:
            prep_records = config['prep_model'].objects.filter(qr_code__icontains=qr_code)
            post_records = config['post_model'].objects.filter(qr_code__icontains=qr_code)
        else:
            prep_records = config['prep_model'].objects.filter(qr_data__icontains=qr_code)
            post_records = config['post_model'].objects.filter(qr_data__icontains=qr_code)
        
        if prep_records.exists() or post_records.exists():
            results.append({
                'machine': config['name'],
                'preprocessing_count': prep_records.count(),
                'postprocessing_count': post_records.count(),
            })
    
    for config in ASSEMBLY_CONFIGS:
        prep_records = config['prep_model'].objects.filter(qr_code_internal__icontains=qr_code)
        post_records = config['post_model'].objects.filter(
            Q(qr_code_internal__icontains=qr_code) |
            Q(qr_code_external__icontains=qr_code) |
            Q(qr_code_housing__icontains=qr_code)
        )
        
        if prep_records.exists() or post_records.exists():
            results.append({
                'machine': config['name'],
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
    
    if not config:
        return HttpResponse('Machine not found', status=404)
    
    if is_assembly:
        records = get_assembly_machine_data(config['prep_model'], config['post_model'])
    else:
        machine_type = 'standard'
        if config['name'].startswith('O-Ring'):
            machine_type = 'oring'
        elif config['name'] == 'Painting':
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










#  

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta, datetime
from . import models
import csv
from collections import defaultdict


# Import all machine configs from your existing views.py
MACHINE_CONFIGS = [
    # DMG MORI Machines
    {'name': 'DMG MORI 1', 'prep_model': models.DmgMori1Preprocessing, 'post_model': models.DmgMori1Postprocessing, 'type': 'dmg_mori'},
    {'name': 'DMG MORI 2', 'prep_model': models.DmgMori2Preprocessing, 'post_model': models.DmgMori2Postprocessing, 'type': 'dmg_mori'},
    {'name': 'DMG MORI 3', 'prep_model': models.DmgMori3Preprocessing, 'post_model': models.DmgMori3Postprocessing, 'type': 'dmg_mori'},
    {'name': 'DMG MORI 4', 'prep_model': models.DmgMori4Preprocessing, 'post_model': models.DmgMori4Postprocessing, 'type': 'dmg_mori'},
    {'name': 'DMG MORI 5', 'prep_model': models.DmgMori5Preprocessing, 'post_model': models.DmgMori5Postprocessing, 'type': 'dmg_mori'},
    {'name': 'DMG MORI 6', 'prep_model': models.DmgMori6Preprocessing, 'post_model': models.DmgMori6Postprocessing, 'type': 'dmg_mori'},
    
    # Gauge Machines
    {'name': 'Gauge 1', 'prep_model': models.Gauge1Preprocessing, 'post_model': models.Gauge1Postprocessing, 'type': 'gauge'},
    {'name': 'Gauge 2', 'prep_model': models.Gauge2Preprocessing, 'post_model': models.Gauge2Postprocessing, 'type': 'gauge'},
    {'name': 'Gauge 3', 'prep_model': models.Gauge3Preprocessing, 'post_model': models.Gauge3Postprocessing, 'type': 'gauge'},
    
    # Honing Machines
    {'name': 'Honing 1', 'prep_model': models.Honing1Preprocessing, 'post_model': models.Honing1Postprocessing, 'type': 'honing'},
    {'name': 'Honing 2', 'prep_model': models.Honing2Preprocessing, 'post_model': models.Honing2Postprocessing, 'type': 'honing'},
    
    # Processing Machines
    {'name': 'Deburring', 'prep_model': models.DeburringPreprocessing, 'post_model': models.DeburringPostprocessing, 'type': 'processing'},
    {'name': 'Pre-Washing', 'prep_model': models.PrewashingPreprocessing, 'post_model': models.PrewashingPostprocessing, 'type': 'processing'},
    {'name': 'Final Washing', 'prep_model': models.FinalWashingPreprocessing, 'post_model': models.FinalWashingPostprocessing, 'type': 'processing'},
    
    # Final Processes
    {'name': 'O-Ring & Leak Test', 'prep_model': models.OringLeakTestPreprocessing, 'post_model': models.OringLeakTestPostprocessing, 'type': 'final'},
    {'name': 'Painting', 'prep_model': models.PaintingPreprocessing, 'post_model': models.PaintingPostprocessing, 'type': 'final'},
    {'name': 'Lubrication', 'prep_model': models.LubricationPreprocessing, 'post_model': models.LubricationPostprocessing, 'type': 'final'},
]

ASSEMBLY_CONFIGS = [
    {'name': 'Assembly Machine 1', 'prep_model': models.AssemblyMachine1Preprocessing, 'post_model': models.AssemblyMachine1Postprocessing},
    {'name': 'Assembly Machine 2', 'prep_model': models.AssemblyMachine2Preprocessing, 'post_model': models.AssemblyMachine2Postprocessing},
    {'name': 'Assembly Machine 3', 'prep_model': models.AssemblyMachine3Preprocessing, 'post_model': models.AssemblyMachine3Postprocessing},
    {'name': 'Assembly Machine 4', 'prep_model': models.AssemblyMachine4Preprocessing, 'post_model': models.AssemblyMachine4Postprocessing},
]


def analytics_view(request):
    """Main analytics page"""
    return render(request, 'dashboard/analytics.html')


def get_date_range(start_date_str, end_date_str):
    """Parse date range from request parameters"""
    try:
        if start_date_str:
            # Parse date string and make it timezone-aware
            naive_start = datetime.strptime(start_date_str, '%Y-%m-%d')
            start_date = timezone.make_aware(naive_start)
        else:
            start_date = timezone.now() - timedelta(days=7)
        
        if end_date_str:
            # Parse date string and make it timezone-aware
            naive_end = datetime.strptime(end_date_str, '%Y-%m-%d')
            naive_end = naive_end.replace(hour=23, minute=59, second=59)
            end_date = timezone.make_aware(naive_end)
        else:
            end_date = timezone.now()
        
        return start_date, end_date
    except ValueError:
        # Default to last 7 days
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
    machine_data = {}
    
    # Determine which machines to query
    configs_to_query = []
    if machine_filter == 'all':
        configs_to_query = MACHINE_CONFIGS + ASSEMBLY_CONFIGS
    else:
        config = get_machine_config_by_id(machine_filter)
        if config:
            configs_to_query = [config]
    
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    
    # Collect data from each machine
    for config in configs_to_query:
        machine_name = config['name']
        is_assembly = 'Assembly' in machine_name
        
        # Check if machine is active
        recent_count = config['prep_model'].objects.filter(timestamp__gte=five_minutes_ago).count()
        if recent_count > 0:
            data['active_machines'] += 1
        
        # Get preprocessing records in date range
        prep_records = config['prep_model'].objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        machine_stats = {
            'machine': machine_name,
            'ok': 0,
            'ng': 0,
            'pending': 0
        }
        
        for prep in prep_records:
            # Get QR code
            if is_assembly:
                qr_value = prep.qr_code_internal
                post = config['post_model'].objects.filter(qr_code_internal=qr_value).first()
            elif machine_name.startswith('O-Ring') or machine_name in ['Painting', 'Lubrication']:
                qr_value = prep.qr_code
                post = config['post_model'].objects.filter(qr_code=qr_value).first()
            else:
                qr_value = prep.qr_data
                post = config['post_model'].objects.filter(qr_data=qr_value).first()
            
            # Determine status
            if post:
                status = post.status
            else:
                status = 'Pending'
            
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
            
            # Get gauge values if available
            gauge_values = {}
            if post and hasattr(post, 'value1'):
                for i in range(1, 6):
                    val = getattr(post, f'value{i}', None)
                    if val is not None:
                        gauge_values[f'value{i}'] = val
            
            # Store record for timeline
            all_records.append({
                'machine': machine_name,
                'qr_code': qr_value,
                'timestamp': prep.timestamp,
                'status': status,
                'gauge_values': gauge_values
            })
        
        if machine_stats['ok'] + machine_stats['ng'] + machine_stats['pending'] > 0:
            data['machine_stats'].append(machine_stats)
    
    # Sort records by timestamp
    all_records.sort(key=lambda x: x['timestamp'])
    
    # Generate timeline data (daily aggregation)
    daily_data = defaultdict(lambda: {'ok': 0, 'ng': 0})
    for record in all_records:
        date_key = record['timestamp'].strftime('%Y-%m-%d')
        if record['status'] == 'OK':
            daily_data[date_key]['ok'] += 1
        elif record['status'] == 'NG':
            daily_data[date_key]['ng'] += 1
    
    sorted_dates = sorted(daily_data.keys())
    data['timeline_data']['labels'] = sorted_dates
    data['timeline_data']['ok'] = [daily_data[date]['ok'] for date in sorted_dates]
    data['timeline_data']['ng'] = [daily_data[date]['ng'] for date in sorted_dates]
    
    # Generate hourly data
    hourly_data = defaultdict(int)
    for record in all_records:
        hour_key = record['timestamp'].strftime('%H:00')
        hourly_data[hour_key] += 1
    
    sorted_hours = sorted(hourly_data.keys())
    data['hourly_data']['labels'] = sorted_hours
    data['hourly_data']['values'] = [hourly_data[hour] for hour in sorted_hours]
    
    # Generate trend data (yield rate over time)
    trend_data = []
    for date in sorted_dates:
        ok = daily_data[date]['ok']
        ng = daily_data[date]['ng']
        total = ok + ng
        yield_rate = (ok / total * 100) if total > 0 else 0
        trend_data.append(yield_rate)
    
    data['trend_data']['labels'] = sorted_dates
    data['trend_data']['values'] = trend_data
    
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
        record['timestamp'] = record['timestamp'].isoformat()
    
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
    writer.writerow(['Machine', 'QR Code', 'Timestamp', 'Status', 'Gauge Values'])
    for record in data['detailed_data']:
        gauge_str = ''
        if record['gauge_values']:
            gauge_str = ', '.join([f"{k}:{v:.3f}" for k, v in record['gauge_values'].items()])
        
        writer.writerow([
            record['machine'],
            record['qr_code'],
            record['timestamp'] if isinstance(record['timestamp'], str) else record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            record['status'],
            gauge_str
        ])
    
    return response