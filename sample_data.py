#!/usr/bin/env python
"""
Clean and Generate Test Data - All in One
==========================================
This script:
1. Deletes ALL existing data from all machines
2. Generates fresh test data (50 records per machine)

Usage:
    python manage.py shell < clean_and_generate.py
"""

import random
from datetime import datetime, timedelta
from django.utils import timezone

# Import your models
from tracebility import models

print("=" * 70)
print("STEP 1: CLEANING EXISTING DATA")
print("=" * 70)

# Delete all existing data
print("\nDeleting existing data...")

# CNC Machines
for model_class in [
    models.Cnc1Preprocessing, models.Cnc1Postprocessing,
    models.Cnc2Preprocessing, models.Cnc2Postprocessing,
    models.Cnc3Preprocessing, models.Cnc3Postprocessing,
    models.Cnc4Preprocessing, models.Cnc4Postprocessing,
    models.Cnc5Preprocessing, models.Cnc5Postprocessing,
    models.Cnc6Preprocessing, models.Cnc6Postprocessing,
]:
    count = model_class.objects.count()
    if count > 0:
        model_class.objects.all().delete()
        print(f"  ✓ Deleted {count} records from {model_class.__name__}")

# Gauge Machines
for model_class in [
    models.Gauge1Preprocessing, models.Gauge1Postprocessing,
    models.Gauge2Preprocessing, models.Gauge2Postprocessing,
    models.Gauge3Preprocessing, models.Gauge3Postprocessing,
]:
    count = model_class.objects.count()
    if count > 0:
        model_class.objects.all().delete()
        print(f"  ✓ Deleted {count} records from {model_class.__name__}")

# Honing Machines
for model_class in [
    models.Honing1Preprocessing, models.Honing1Postprocessing,
    models.Honing2Preprocessing, models.Honing2Postprocessing,
]:
    count = model_class.objects.count()
    if count > 0:
        model_class.objects.all().delete()
        print(f"  ✓ Deleted {count} records from {model_class.__name__}")

# Deburring
for model_class in [models.DeburringPreprocessing, models.DeburringPostprocessing]:
    count = model_class.objects.count()
    if count > 0:
        model_class.objects.all().delete()
        print(f"  ✓ Deleted {count} records from {model_class.__name__}")

# Washing Machines
for model_class in [
    models.PrewashingPreprocessing, models.PrewashingPostprocessing,
    models.FinalwashingPreprocessing, models.FinalwashingPostprocessing,
]:
    count = model_class.objects.count()
    if count > 0:
        model_class.objects.all().delete()
        print(f"  ✓ Deleted {count} records from {model_class.__name__}")

# Assembly Machines
for model_class in [
    models.Op40AProcessing, models.Op40BProcessing,
    models.Op40CProcessing, models.Op40DProcessing,
]:
    count = model_class.objects.count()
    if count > 0:
        model_class.objects.all().delete()
        print(f"  ✓ Deleted {count} records from {model_class.__name__}")

# OP80
for model_class in [models.Op80Preprocessing, models.Op80Postprocessing]:
    count = model_class.objects.count()
    if count > 0:
        model_class.objects.all().delete()
        print(f"  ✓ Deleted {count} records from {model_class.__name__}")

# Painting
for model_class in [models.PaintingPreprocessing, models.PaintingPostprocessing]:
    count = model_class.objects.count()
    if count > 0:
        model_class.objects.all().delete()
        print(f"  ✓ Deleted {count} records from {model_class.__name__}")

# Lubrication
for model_class in [models.LubPreprocessing, models.LubPostprocessing]:
    count = model_class.objects.count()
    if count > 0:
        model_class.objects.all().delete()
        print(f"  ✓ Deleted {count} records from {model_class.__name__}")

print("\n✅ All existing data deleted!")

print("\n" + "=" * 70)
print("STEP 2: GENERATING FRESH TEST DATA")
print("=" * 70)

# Configuration
NUM_RECORDS_PER_MACHINE = 50
START_DATE = datetime.now() - timedelta(days=7)

# Status options
STATUSES = ['OK', 'NG']
STATUS_WEIGHTS = [0.95, 0.05]

print(f"Generating {NUM_RECORDS_PER_MACHINE} records per machine...")
print(f"Start date: {START_DATE}")
print()

def generate_qr_code(prefix, index):
    return f"{prefix}{str(index).zfill(6)}"

def generate_timestamp(base_time, offset_minutes):
    dt = base_time + timedelta(minutes=offset_minutes)
    return dt.strftime('%d/%m/%Y, %I:%M:%S %p')

def random_status():
    return random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]

generated_qrs = set()

def unique_qr(prefix, index):
    qr = generate_qr_code(prefix, index)
    while qr in generated_qrs:
        index += 1
        qr = generate_qr_code(prefix, index)
    generated_qrs.add(qr)
    return qr

# ============================================================================
# CNC MACHINES (1-6)
# ============================================================================
print("Generating CNC Machine Data...")

cnc_machines = [
    (models.Cnc1Preprocessing, models.Cnc1Postprocessing, "CNC1"),
    (models.Cnc2Preprocessing, models.Cnc2Postprocessing, "CNC2"),
    (models.Cnc3Preprocessing, models.Cnc3Postprocessing, "CNC3"),
    (models.Cnc4Preprocessing, models.Cnc4Postprocessing, "CNC4"),
    (models.Cnc5Preprocessing, models.Cnc5Postprocessing, "CNC5"),
    (models.Cnc6Preprocessing, models.Cnc6Postprocessing, "CNC6"),
]

for prep_model, post_model, prefix in cnc_machines:
    for i in range(1, NUM_RECORDS_PER_MACHINE + 1):
        qr = unique_qr(prefix, i)
        time_offset = i * 5
        
        prep_fields = {
            'timestamp': generate_timestamp(START_DATE, time_offset),
            'machine_name': f"{prefix} Machine",
            'qr_data': qr,
        }
        
        if hasattr(prep_model, 'model_name'):
            prep_fields['model_name'] = 'MODEL_A'
        
        prep = prep_model.objects.create(**prep_fields)
        
        if random.random() < 0.9:
            post_model.objects.create(
                timestamp=generate_timestamp(START_DATE, time_offset + 2),
                qr_data=qr,
                status=random_status()
            )
    
    print(f"  ✓ {prefix}: {NUM_RECORDS_PER_MACHINE} records created")

# ============================================================================
# GAUGE MACHINES (1-3)
# ============================================================================
print("\nGenerating Gauge Machine Data...")

gauge_machines = [
    (models.Gauge1Preprocessing, models.Gauge1Postprocessing, "GAUGE1", 5),
    (models.Gauge2Preprocessing, models.Gauge2Postprocessing, "GAUGE2", 6),
    (models.Gauge3Preprocessing, models.Gauge3Postprocessing, "GAUGE3", 6),
]

for prep_model, post_model, prefix, num_values in gauge_machines:
    for i in range(1, NUM_RECORDS_PER_MACHINE + 1):
        qr = unique_qr(prefix, i)
        time_offset = i * 5
        
        prep_fields = {
            'timestamp': generate_timestamp(START_DATE, time_offset),
            'qr_data': qr,
            'previous_machine_status': random_status(),
        }
        
        if hasattr(prep_model, 'model_name'):
            prep_fields['model_name'] = 'MODEL_A'
        
        prep = prep_model.objects.create(**prep_fields)
        
        if random.random() < 0.9:
            gauge_data = {
                'timestamp': generate_timestamp(START_DATE, time_offset + 2),
                'qr_data': qr,
                'status': random_status(),
            }
            
            for j in range(1, num_values + 1):
                gauge_data[f'value{j}'] = round(random.uniform(10.0, 50.0), 3)
            
            post_model.objects.create(**gauge_data)
    
    print(f"  ✓ {prefix}: {NUM_RECORDS_PER_MACHINE} records created")

# ============================================================================
# HONING MACHINES (1-2)
# ============================================================================
print("\nGenerating Honing Machine Data...")

honing_machines = [
    (models.Honing1Preprocessing, models.Honing1Postprocessing, "HONING1"),
    (models.Honing2Preprocessing, models.Honing2Postprocessing, "HONING2"),
]

for prep_model, post_model, prefix in honing_machines:
    for i in range(1, NUM_RECORDS_PER_MACHINE + 1):
        qr = unique_qr(prefix, i)
        time_offset = i * 5
        
        prep_fields = {
            'timestamp': generate_timestamp(START_DATE, time_offset),
            'qr_data': qr,
            'previous_machine_status': random_status(),
        }
        
        if hasattr(prep_model, 'model_name'):
            prep_fields['model_name'] = 'MODEL_A'
        
        prep = prep_model.objects.create(**prep_fields)
        
        if random.random() < 0.9:
            post_model.objects.create(
                timestamp=generate_timestamp(START_DATE, time_offset + 2),
                qr_data=qr,
                status=random_status()
            )
    
    print(f"  ✓ {prefix}: {NUM_RECORDS_PER_MACHINE} records created")

# ============================================================================
# DEBURRING MACHINE
# ============================================================================
print("\nGenerating Deburring Machine Data...")

for i in range(1, NUM_RECORDS_PER_MACHINE + 1):
    qr = unique_qr("DEBURR", i)
    time_offset = i * 5
    
    prep_fields = {
        'timestamp': generate_timestamp(START_DATE, time_offset),
        'qr_data': qr,
        'previous_machine_status': random_status(),
    }
    
    if hasattr(models.DeburringPreprocessing, 'model_name'):
        prep_fields['model_name'] = 'MODEL_A'
    
    models.DeburringPreprocessing.objects.create(**prep_fields)
    
    if random.random() < 0.9:
        models.DeburringPostprocessing.objects.create(
            timestamp=generate_timestamp(START_DATE, time_offset + 2),
            qr_data=qr,
            status=random_status()
        )

print(f"  ✓ DEBURRING: {NUM_RECORDS_PER_MACHINE} records created")

# ============================================================================
# WASHING MACHINES
# ============================================================================
print("\nGenerating Washing Machine Data...")

washing_machines = [
    (models.PrewashingPreprocessing, models.PrewashingPostprocessing, "PREWASH"),
    (models.FinalwashingPreprocessing, models.FinalwashingPostprocessing, "FINWASH"),
]

for prep_model, post_model, prefix in washing_machines:
    for i in range(1, NUM_RECORDS_PER_MACHINE + 1):
        qr = unique_qr(prefix, i)
        time_offset = i * 5
        prev_status = random_status()
        
        prep_fields = {
            'timestamp': generate_timestamp(START_DATE, time_offset),
            'qr_data': qr,
            'previous_machine_status': prev_status,
            'status': random_status(),
        }
        
        if hasattr(prep_model, 'model_name'):
            prep_fields['model_name'] = 'MODEL_A'
        
        prep = prep_model.objects.create(**prep_fields)
        
        if random.random() < 0.9:
            post_fields = {
                'timestamp': generate_timestamp(START_DATE, time_offset + 2),
                'qr_data': qr,
                'previous_machine_status': prev_status,
                'status': random_status(),
            }
            
            if hasattr(post_model, 'model_name'):
                post_fields['model_name'] = 'MODEL_A'
            
            post_model.objects.create(**post_fields)
    
    print(f"  ✓ {prefix}: {NUM_RECORDS_PER_MACHINE} records created")

# ============================================================================
# ASSEMBLY MACHINES (OP40 A/B/C/D)
# ============================================================================
print("\nGenerating Assembly Machine Data (OP40)...")

assembly_machines = [
    (models.Op40AProcessing, "OP40A"),
    (models.Op40BProcessing, "OP40B"),
    (models.Op40CProcessing, "OP40C"),
    (models.Op40DProcessing, "OP40D"),
]

for model_class, prefix in assembly_machines:
    for i in range(1, NUM_RECORDS_PER_MACHINE + 1):
        qr_internal = unique_qr(f"{prefix}INT", i)
        qr_external = unique_qr(f"{prefix}EXT", i)
        qr_housing = unique_qr(f"{prefix}HSG", i)
        time_offset = i * 5
        
        base_time = START_DATE + timedelta(minutes=time_offset)
        has_complete = random.random() < 0.8
        
        record_data = {
            'timestamp_internal': timezone.make_aware(base_time),
            'qr_data_internal': qr_internal,
            'previous_machine_internal_status': random_status(),
        }
        
        if hasattr(model_class, 'model_name_internal'):
            record_data['model_name_internal'] = 'MODEL_A'
        
        if has_complete:
            record_data.update({
                'timestamp_external': timezone.make_aware(base_time + timedelta(minutes=1)),
                'qr_data_external': qr_external,
                'timestamp_housing': timezone.make_aware(base_time + timedelta(minutes=2)),
                'previous_machine_housing_status': random_status(),
                'qr_data_housing': qr_housing,
                'status': random_status(),
                'created_at': timezone.make_aware(base_time + timedelta(minutes=3)),
            })
            
            if hasattr(model_class, 'model_name_external'):
                record_data['model_name_external'] = 'MODEL_B'
            if hasattr(model_class, 'model_name_housing'):
                record_data['model_name_housing'] = 'MODEL_C'
        
        model_class.objects.create(**record_data)
    
    print(f"  ✓ {prefix}: {NUM_RECORDS_PER_MACHINE} records created")

# ============================================================================
# OP80 - LEAK TEST
# ============================================================================
print("\nGenerating OP80 (Leak Test) Data...")

for i in range(1, NUM_RECORDS_PER_MACHINE + 1):
    qr_piston = unique_qr("OP80PST", i)
    qr_housing = unique_qr("OP80HSG", i)
    qr_housing_new = unique_qr("OP80NEW", i)
    time_offset = i * 5
    
    prep_fields = {
        'timestamp': generate_timestamp(START_DATE, time_offset),
        'qr_data_piston': qr_piston,
        'qr_data_housing': qr_housing,
        'previous_machine_status': random_status()
    }
    
    if hasattr(models.Op80Preprocessing, 'model_name_internal'):
        prep_fields['model_name_internal'] = 'MODEL_A'
    if hasattr(models.Op80Preprocessing, 'model_name_external'):
        prep_fields['model_name_external'] = 'MODEL_B'
    
    models.Op80Preprocessing.objects.create(**prep_fields)
    
    if random.random() < 0.85:
        match_status = 'TRUE' if random.random() < 0.95 else 'FALSE'
        
        models.Op80Postprocessing.objects.create(
            timestamp=generate_timestamp(START_DATE, time_offset + 2),
            qr_data_housing_new=qr_housing_new,
            qr_data_housing=qr_housing,
            match_status=match_status,
            status=random_status() if match_status == 'TRUE' else 'NG'
        )

print(f"  ✓ OP80: {NUM_RECORDS_PER_MACHINE} records created")

# ============================================================================
# PAINTING MACHINE
# ============================================================================
print("\nGenerating Painting Machine Data...")

for i in range(1, NUM_RECORDS_PER_MACHINE + 1):
    qr_housing = unique_qr("PAINTHS", i)
    qr_piston = unique_qr("PAINTPS", i)
    time_offset = i * 5
    prev_status = random_status()
    pre_status = random_status()
    
    prep_fields = {
        'timestamp': generate_timestamp(START_DATE, time_offset),
        'qr_data_housing': qr_housing,
        'qr_data_piston': qr_piston,
        'previous_machine_status': prev_status,
        'pre_status': pre_status
    }
    
    if hasattr(models.PaintingPreprocessing, 'model_name_housing'):
        prep_fields['model_name_housing'] = 'MODEL_A'
    if hasattr(models.PaintingPreprocessing, 'model_name_piston'):
        prep_fields['model_name_piston'] = 'MODEL_B'
    
    models.PaintingPreprocessing.objects.create(**prep_fields)
    
    if random.random() < 0.88:
        post_fields = {
            'qr_data_piston': qr_piston,
            'qr_data_housing': qr_housing,
            'status': random_status()
        }
        
        if hasattr(models.PaintingPostprocessing, 'timestamp'):
            post_fields['timestamp'] = generate_timestamp(START_DATE, time_offset + 3)
        
        models.PaintingPostprocessing.objects.create(**post_fields)

print(f"  ✓ PAINTING: {NUM_RECORDS_PER_MACHINE} records created")

# ============================================================================
# LUBRICATION MACHINE
# ============================================================================
print("\nGenerating Lubrication Machine Data...")

for i in range(1, NUM_RECORDS_PER_MACHINE + 1):
    qr_piston = unique_qr("LUBPST", i)
    qr_housing = unique_qr("LUBHSG", i)
    time_offset = i * 5
    
    prep_fields = {
        'timestamp': generate_timestamp(START_DATE, time_offset),
        'qr_data_piston': qr_piston,
        'qr_data_housing': qr_housing,
        'previous_machine_status': random_status()
    }
    
    if hasattr(models.LubPreprocessing, 'model_name_piston'):
        prep_fields['model_name_piston'] = 'MODEL_A'
    if hasattr(models.LubPreprocessing, 'model_name_housing'):
        prep_fields['model_name_housing'] = 'MODEL_B'
    
    models.LubPreprocessing.objects.create(**prep_fields)
    
    if random.random() < 0.9:
        models.LubPostprocessing.objects.create(
            timestamp=generate_timestamp(START_DATE, time_offset + 2),
            qr_data_piston=qr_piston,
            status=random_status()
        )

print(f"  ✓ LUBRICATION: {NUM_RECORDS_PER_MACHINE} records created")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("✅ COMPLETE - Data Cleaned and Regenerated!")
print("=" * 70)

total_records = 0
for model_class in [
    models.Cnc1Preprocessing, models.Cnc1Postprocessing,
    models.Cnc2Preprocessing, models.Cnc2Postprocessing,
    models.Gauge1Preprocessing, models.Gauge1Postprocessing,
    models.PaintingPreprocessing, models.PaintingPostprocessing,
    models.LubPreprocessing, models.LubPostprocessing,
    models.Op80Preprocessing, models.Op80Postprocessing,
    models.Op40AProcessing,
]:
    total_records += model_class.objects.count()

print(f"\nTotal records in database: ~{total_records}")
print("\n✅ Ready to test! Visit: http://localhost:8000/")
print("=" * 70)