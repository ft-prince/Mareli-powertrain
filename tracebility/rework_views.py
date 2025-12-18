"""
Rework Page Views
Handles searching, filtering, and updating of production records
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from . import models

# Import existing configurations from views.py
from .views import (
    MACHINE_CONFIGS, 
    ASSEMBLY_CONFIGS, 
    OP80_CONFIG,
    parse_timestamp_to_datetime
)


def get_all_model_names():
    """Get distinct model names from all machines"""
    model_names = set()
    
    # Get from CNC machines
    for config in MACHINE_CONFIGS:
        if config['prep_model'] and hasattr(config['prep_model'], 'objects'):
            try:
                prep_models = config['prep_model'].objects.values_list('model_name', flat=True).distinct()
                model_names.update([m for m in prep_models if m])
            except:
                pass
    
    # Get from assembly machines
    for config in ASSEMBLY_CONFIGS:
        try:
            internal_models = config['prep_model'].objects.values_list('model_name_internal', flat=True).distinct()
            external_models = config['prep_model'].objects.values_list('model_name_external', flat=True).distinct()
            housing_models = config['prep_model'].objects.values_list('model_name_housing', flat=True).distinct()
            model_names.update([m for m in internal_models if m])
            model_names.update([m for m in external_models if m])
            model_names.update([m for m in housing_models if m])
        except:
            pass
    
    # Get from OP80
    try:
        op80_internal = OP80_CONFIG['prep_model'].objects.values_list('model_name_internal', flat=True).distinct()
        op80_external = OP80_CONFIG['prep_model'].objects.values_list('model_name_external', flat=True).distinct()
        model_names.update([m for m in op80_internal if m])
        model_names.update([m for m in op80_external if m])
    except:
        pass
    
    # Remove None and 'N/A'
    model_names.discard(None)
    model_names.discard('N/A')
    model_names.discard('')
    
    return sorted(list(model_names))


def get_machine_list():
    """Get list of all machines for dropdown"""
    machines = []
    
    for config in MACHINE_CONFIGS:
        machines.append({
            'id': config['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_'),
            'name': config['display_name'],
            'type': config['type']
        })
    
    for config in ASSEMBLY_CONFIGS:
        machines.append({
            'id': config['name'].lower().replace(' ', '_'),
            'name': config['display_name'],
            'type': 'assembly'
        })
    
    machines.append({
        'id': 'op80_leak_test',
        'name': OP80_CONFIG['display_name'],
        'type': 'op80'
    })
    
    return machines


def search_across_all_machines(filters):
    """
    Search across all machines based on filters
    Returns list of records with machine info
    """
    results = []
    
    # Extract filters
    qr_code = filters.get('qr_code', '').strip()
    model_name = filters.get('model_name', '')
    machine_id = filters.get('machine', '')
    start_date = filters.get('start_date', '')
    end_date = filters.get('end_date', '')
    status_filter = filters.get('status', '')
    
    # Parse dates
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        except:
            pass
    if end_date:
        try:
            end_dt = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
        except:
            pass
    
    # Determine which machines to search
    configs_to_search = []
    if machine_id and machine_id != 'all':
        # Search specific machine
        for config in MACHINE_CONFIGS:
            config_id = config['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
            if config_id == machine_id:
                configs_to_search.append(config)
                break
        
        if not configs_to_search:
            for config in ASSEMBLY_CONFIGS:
                config_id = config['name'].lower().replace(' ', '_')
                if config_id == machine_id:
                    configs_to_search.append(config)
                    break
        
        if not configs_to_search and machine_id == 'op80_leak_test':
            configs_to_search.append(OP80_CONFIG)
    else:
        # Search all machines
        configs_to_search = MACHINE_CONFIGS + ASSEMBLY_CONFIGS + [OP80_CONFIG]
    
    # Search each machine
    for config in configs_to_search:
        machine_name = config['name']
        display_name = config.get('display_name', machine_name)
        machine_type = config.get('type', 'standard')
        is_assembly = 'OP40' in machine_name
        
        if not config.get('prep_model'):
            continue
        
        # Build query for preprocessing
        query = Q()
        
        # QR Code filter
        if qr_code:
            if is_assembly:
                query &= (Q(qr_data_internal__icontains=qr_code) | 
                         Q(qr_data_external__icontains=qr_code) | 
                         Q(qr_data_housing__icontains=qr_code))
            elif 'Painting' in machine_name:
                query &= (Q(qr_data_housing__icontains=qr_code) | Q(qr_data_piston__icontains=qr_code))
            elif 'Lubrication' in machine_name:
                query &= (Q(qr_data_piston__icontains=qr_code) | Q(qr_data_housing__icontains=qr_code))
            elif 'Oring_leak' in machine_name:
                query &= (Q(qr_data_piston__icontains=qr_code) | Q(qr_data_housing__icontains=qr_code))
            else:
                query &= Q(qr_data__icontains=qr_code)
        
        # Model name filter
        if model_name and model_name != 'all':
            if is_assembly:
                query &= (Q(model_name_internal=model_name) | 
                         Q(model_name_external=model_name) | 
                         Q(model_name_housing=model_name))
            elif 'Painting' in machine_name:
                query &= (Q(model_name_housing=model_name) | Q(model_name_piston=model_name))
            elif 'Lubrication' in machine_name:
                query &= (Q(model_name_piston=model_name) | Q(model_name_housing=model_name))
            elif 'Oring_leak' in machine_name:
                query &= (Q(model_name_internal=model_name) | Q(model_name_external=model_name))
            else:
                query &= Q(model_name=model_name)
        
        # Get preprocessing records
        try:
            prep_records = config['prep_model'].objects.filter(query)[:500]  # Limit to 500 results
        except Exception as e:
            print(f"Error querying {machine_name}: {e}")
            continue
        
        # Process each record
        for prep in prep_records:
            # Get timestamp
            if is_assembly:
                timestamp = prep.timestamp_internal
            else:
                timestamp = prep.timestamp
            
            # Date filter
            if start_dt or end_dt:
                dt = parse_timestamp_to_datetime(timestamp)
                if dt:
                    if timezone.is_naive(dt):
                        dt = timezone.make_aware(dt)
                    
                    if start_dt and dt < start_dt:
                        continue
                    if end_dt and dt > end_dt:
                        continue
            
            # Get status and QR based on machine type
            if is_assembly:
                qr_value = prep.qr_data_internal
                qr_external = prep.qr_data_external or '-'
                qr_housing = prep.qr_data_housing or '-'
                status = prep.status if prep.qr_data_external and prep.qr_data_housing else 'Pending'
                model_value = getattr(prep, 'model_name_internal', 'N/A')
                
            elif 'Painting' in machine_name:
                qr_value = prep.qr_data_housing
                qr_external = prep.qr_data_piston
                qr_housing = '-'
                post = config['post_model'].objects.filter(qr_data_housing=qr_value).first()
                status = post.status if post else 'Pending'
                model_value = getattr(prep, 'model_name_housing', 'N/A')
                
            elif 'Lubrication' in machine_name:
                qr_value = prep.qr_data_piston
                qr_external = '-'
                qr_housing = prep.qr_data_housing
                post = config['post_model'].objects.filter(qr_data_piston=qr_value).first()
                status = post.status if post else 'Pending'
                model_value = getattr(prep, 'model_name_piston', 'N/A')
                
            elif 'Oring_leak' in machine_name:
                qr_value = prep.qr_data_piston
                qr_external = '-'
                qr_housing = prep.qr_data_housing
                post = config['post_model'].objects.filter(qr_data_housing_new=qr_housing).first()
                status = post.status if post else 'Pending'
                model_value = getattr(prep, 'model_name_internal', 'N/A')
                
            else:
                qr_value = prep.qr_data
                qr_external = '-'
                qr_housing = '-'
                post = config['post_model'].objects.filter(qr_data=qr_value).first() if config['post_model'] else None
                status = post.status if post else 'Pending'
                model_value = getattr(prep, 'model_name', 'N/A')
            
            # Status filter
            if status_filter and status_filter != 'all' and status != status_filter:
                continue
            
            # Format timestamp
            if hasattr(timestamp, 'isoformat'):
                timestamp_str = timestamp.isoformat()
            else:
                timestamp_str = str(timestamp)
            
            # Build record
            record = {
                'prep_id': prep.id,
                'post_id': post.id if 'post' in locals() and post else None,
                'machine_name': machine_name,
                'display_name': display_name,
                'machine_type': machine_type,
                'qr_code': qr_value,
                'qr_external': qr_external,
                'qr_housing': qr_housing,
                'model_name': model_value,
                'timestamp': timestamp_str,
                'status': status,
                'previous_machine_status': getattr(prep, 'previous_machine_status', '-'),
            }
            
            results.append(record)
    
    # Sort by timestamp (newest first)
    results.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return results


def rework_page(request):
    """Main rework page view"""
    model_names = get_all_model_names()
    machines = get_machine_list()
    
    context = {
        'model_names': model_names,
        'machines': machines,
    }
    
    return render(request, 'rework/rework.html', context)


@csrf_exempt
def rework_search_api(request):
    """API endpoint for searching records"""
    if request.method == 'GET':
        filters = {
            'qr_code': request.GET.get('qr_code', ''),
            'model_name': request.GET.get('model_name', ''),
            'machine': request.GET.get('machine', ''),
            'start_date': request.GET.get('start_date', ''),
            'end_date': request.GET.get('end_date', ''),
            'status': request.GET.get('status', ''),
        }
        
        results = search_across_all_machines(filters)
        
        return JsonResponse({
            'success': True,
            'count': len(results),
            'results': results
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@csrf_exempt
def rework_update_api(request):
    """API endpoint for updating record status"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        machine_name = data.get('machine_name')
        prep_id = data.get('prep_id')
        post_id = data.get('post_id')
        new_status = data.get('status')
        machine_type = data.get('machine_type')
        
        if not machine_name or not new_status:
            return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
        
        # Find machine config
        config = None
        for c in MACHINE_CONFIGS + ASSEMBLY_CONFIGS + [OP80_CONFIG]:
            if c['name'] == machine_name:
                config = c
                break
        
        if not config:
            return JsonResponse({'success': False, 'error': 'Machine not found'}, status=404)
        
        # Update the appropriate record
        updated = False
        
        # For most machines, update postprocessing
        if post_id and config.get('post_model'):
            try:
                post_record = config['post_model'].objects.get(id=post_id)
                post_record.status = new_status
                post_record.save()
                updated = True
            except config['post_model'].DoesNotExist:
                pass
        
        # For assembly machines, update preprocessing (since they use same model)
        if machine_type == 'assembly' and prep_id:
            try:
                prep_record = config['prep_model'].objects.get(id=prep_id)
                prep_record.status = new_status
                prep_record.save()
                updated = True
            except config['prep_model'].DoesNotExist:
                pass
        
        if updated:
            return JsonResponse({
                'success': True,
                'message': f'Status updated to {new_status}',
                'new_status': new_status
            })
        else:
            return JsonResponse({'success': False, 'error': 'Record not found or cannot be updated'}, status=404)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def rework_get_record_api(request, machine_name, prep_id):
    """API endpoint to get full record details for editing"""
    # Find machine config
    config = None
    for c in MACHINE_CONFIGS + ASSEMBLY_CONFIGS + [OP80_CONFIG]:
        config_id = c['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
        if config_id == machine_name:
            config = c
            break
    
    if not config:
        return JsonResponse({'success': False, 'error': 'Machine not found'}, status=404)
    
    try:
        prep_record = config['prep_model'].objects.get(id=prep_id)
        
        # Get machine type
        machine_type = config.get('type', 'standard')
        is_assembly = 'OP40' in config['name']
        
        # Build record details
        record = {
            'prep_id': prep_record.id,
            'machine_name': config['name'],
            'display_name': config.get('display_name', config['name']),
            'machine_type': machine_type,
        }
        
        # Get QR and status based on machine type
        if is_assembly:
            record['qr_code'] = prep_record.qr_data_internal
            record['qr_external'] = prep_record.qr_data_external or ''
            record['qr_housing'] = prep_record.qr_data_housing or ''
            record['status'] = prep_record.status or 'Pending'
            record['model_name_internal'] = getattr(prep_record, 'model_name_internal', 'N/A')
            record['model_name_external'] = getattr(prep_record, 'model_name_external', 'N/A')
            record['model_name_housing'] = getattr(prep_record, 'model_name_housing', 'N/A')
            record['timestamp'] = prep_record.timestamp_internal.isoformat() if hasattr(prep_record.timestamp_internal, 'isoformat') else str(prep_record.timestamp_internal)
            
        elif 'Painting' in config['name']:
            qr_value = prep_record.qr_data_housing
            post = config['post_model'].objects.filter(qr_data_housing=qr_value).first()
            record['qr_code'] = qr_value
            record['qr_piston'] = prep_record.qr_data_piston
            record['status'] = post.status if post else 'Pending'
            record['post_id'] = post.id if post else None
            record['model_name'] = getattr(prep_record, 'model_name_housing', 'N/A')
            record['timestamp'] = prep_record.timestamp
            
        elif 'Lubrication' in config['name']:
            qr_value = prep_record.qr_data_piston
            post = config['post_model'].objects.filter(qr_data_piston=qr_value).first()
            record['qr_code'] = qr_value
            record['qr_housing'] = prep_record.qr_data_housing
            record['status'] = post.status if post else 'Pending'
            record['post_id'] = post.id if post else None
            record['model_name'] = getattr(prep_record, 'model_name_piston', 'N/A')
            record['timestamp'] = prep_record.timestamp
            
        elif 'Oring_leak' in config['name']:
            qr_value = prep_record.qr_data_piston
            qr_housing = prep_record.qr_data_housing
            post = config['post_model'].objects.filter(qr_data_housing_new=qr_housing).first()
            record['qr_code'] = qr_value
            record['qr_housing'] = qr_housing
            record['status'] = post.status if post else 'Pending'
            record['post_id'] = post.id if post else None
            record['model_name'] = getattr(prep_record, 'model_name_internal', 'N/A')
            record['timestamp'] = prep_record.timestamp
            
        else:
            qr_value = prep_record.qr_data
            post = config['post_model'].objects.filter(qr_data=qr_value).first() if config['post_model'] else None
            record['qr_code'] = qr_value
            record['status'] = post.status if post else 'Pending'
            record['post_id'] = post.id if post else None
            record['model_name'] = getattr(prep_record, 'model_name', 'N/A')
            record['timestamp'] = prep_record.timestamp
        
        # Add previous machine status if available
        record['previous_machine_status'] = getattr(prep_record, 'previous_machine_status', '-')
        
        return JsonResponse({'success': True, 'record': record})
        
    except config['prep_model'].DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)