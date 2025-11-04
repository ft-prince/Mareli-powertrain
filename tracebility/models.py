from django.db import models
from django.utils import timezone


class MasterTraceability(models.Model):
    """Master traceability table for overall product tracking"""
    PRODUCT_TYPE_CHOICES = [
        ('PISTON', 'Piston'),
        ('HOUSING', 'Housing'),
    ]
    
    STATUS_CHOICES = [
        ('IN_PROCESS', 'In Process'),
        ('OK', 'OK'),
        ('NG', 'NG'),
        ('SCRAPPED', 'Scrapped'),
        ('COMPLETE', 'Complete'),
    ]
    
    qr_code = models.CharField(max_length=100, unique=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    current_machine = models.CharField(max_length=50, null=True, blank=True)
    start_timestamp = models.DateTimeField(default=timezone.now)
    last_update_timestamp = models.DateTimeField(default=timezone.now)
    
    # Machine status tracking
    dmg_mori_status = models.CharField(max_length=10, null=True, blank=True)
    dmg_mori_machine = models.CharField(max_length=50, null=True, blank=True)
    dmg_mori_timestamp = models.DateTimeField(null=True, blank=True)
    
    gauge_status = models.CharField(max_length=10, null=True, blank=True)
    gauge_machine = models.CharField(max_length=50, null=True, blank=True)
    gauge_timestamp = models.DateTimeField(null=True, blank=True)
    gauge_value1 = models.FloatField(null=True, blank=True)
    gauge_value2 = models.FloatField(null=True, blank=True)
    gauge_value3 = models.FloatField(null=True, blank=True)
    gauge_value4 = models.FloatField(null=True, blank=True)
    gauge_value5 = models.FloatField(null=True, blank=True)
    
    honing_status = models.CharField(max_length=10, null=True, blank=True)
    honing_machine = models.CharField(max_length=50, null=True, blank=True)
    honing_timestamp = models.DateTimeField(null=True, blank=True)
    
    deburring_status = models.CharField(max_length=10, null=True, blank=True)
    deburring_timestamp = models.DateTimeField(null=True, blank=True)
    
    prewashing_status = models.CharField(max_length=10, null=True, blank=True)
    prewashing_timestamp = models.DateTimeField(null=True, blank=True)
    
    final_washing_status = models.CharField(max_length=10, null=True, blank=True)
    final_washing_timestamp = models.DateTimeField(null=True, blank=True)
    
    assembly_status = models.CharField(max_length=10, null=True, blank=True)
    assembly_machine = models.CharField(max_length=50, null=True, blank=True)
    assembly_timestamp = models.DateTimeField(null=True, blank=True)
    assembly_internal_code = models.CharField(max_length=100, null=True, blank=True)
    assembly_external_code = models.CharField(max_length=100, null=True, blank=True)
    assembly_housing_code = models.CharField(max_length=100, null=True, blank=True)
    
    leak_test_status = models.CharField(max_length=10, null=True, blank=True)
    leak_test_timestamp = models.DateTimeField(null=True, blank=True)
    
    painting_status = models.CharField(max_length=10, null=True, blank=True)
    painting_timestamp = models.DateTimeField(null=True, blank=True)
    
    lubrication_status = models.CharField(max_length=10, null=True, blank=True)
    lubrication_timestamp = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'renata_traceability'
        ordering = ['-last_update_timestamp']
    
    def __str__(self):
        return f"{self.qr_code} - {self.product_type}"


# Base models for preprocessing/postprocessing
class BasePreprocessing(models.Model):
    """Abstract base model for preprocessing tables"""
    timestamp = models.DateTimeField(default=timezone.now)
    machine_name = models.CharField(max_length=50)
    qr_data = models.CharField(max_length=100)
    
    class Meta:
        abstract = True
        ordering = ['-timestamp']


class BasePostprocessing(models.Model):
    """Abstract base model for postprocessing tables"""
    timestamp = models.DateTimeField(default=timezone.now)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    
    class Meta:
        abstract = True
        ordering = ['-timestamp']


# DMG MORI Machines (1-6)
class DmgMori1Preprocessing(BasePreprocessing):
    class Meta:
        db_table = 'dmg_mori_1_preprocessing'

class DmgMori1Postprocessing(BasePostprocessing):
    class Meta:
        db_table = 'dmg_mori_1_postprocessing'


class DmgMori2Preprocessing(BasePreprocessing):
    class Meta:
        db_table = 'dmg_mori_2_preprocessing'

class DmgMori2Postprocessing(BasePostprocessing):
    class Meta:
        db_table = 'dmg_mori_2_postprocessing'


class DmgMori3Preprocessing(BasePreprocessing):
    class Meta:
        db_table = 'dmg_mori_3_preprocessing'

class DmgMori3Postprocessing(BasePostprocessing):
    class Meta:
        db_table = 'dmg_mori_3_postprocessing'


class DmgMori4Preprocessing(BasePreprocessing):
    class Meta:
        db_table = 'dmg_mori_4_preprocessing'

class DmgMori4Postprocessing(BasePostprocessing):
    class Meta:
        db_table = 'dmg_mori_4_postprocessing'


class DmgMori5Preprocessing(BasePreprocessing):
    class Meta:
        db_table = 'dmg_mori_5_preprocessing'

class DmgMori5Postprocessing(BasePostprocessing):
    class Meta:
        db_table = 'dmg_mori_5_postprocessing'


class DmgMori6Preprocessing(BasePreprocessing):
    class Meta:
        db_table = 'dmg_mori_6_preprocessing'

class DmgMori6Postprocessing(BasePostprocessing):
    class Meta:
        db_table = 'dmg_mori_6_postprocessing'


# Gauge Machines (1-3)
class Gauge1Preprocessing(BasePreprocessing):
    previous_machine_status = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'gauge_1_preprocessing'


class Gauge1Postprocessing(BasePostprocessing):
    value1 = models.FloatField(null=True, blank=True)
    value2 = models.FloatField(null=True, blank=True)
    value3 = models.FloatField(null=True, blank=True)
    value4 = models.FloatField(null=True, blank=True)
    value5 = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'gauge_1_postprocessing'


class Gauge2Preprocessing(BasePreprocessing):
    previous_machine_status = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'gauge_2_preprocessing'


class Gauge2Postprocessing(BasePostprocessing):
    value1 = models.FloatField(null=True, blank=True)
    value2 = models.FloatField(null=True, blank=True)
    value3 = models.FloatField(null=True, blank=True)
    value4 = models.FloatField(null=True, blank=True)
    value5 = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'gauge_2_postprocessing'


class Gauge3Preprocessing(BasePreprocessing):
    previous_machine_status = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'gauge_3_preprocessing'


class Gauge3Postprocessing(BasePostprocessing):
    value1 = models.FloatField(null=True, blank=True)
    value2 = models.FloatField(null=True, blank=True)
    value3 = models.FloatField(null=True, blank=True)
    value4 = models.FloatField(null=True, blank=True)
    value5 = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'gauge_3_postprocessing'


# Honing Machines (1-2)
class Honing1Preprocessing(BasePreprocessing):
    previous_gauge_status = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'honing_1_preprocessing'


class Honing1Postprocessing(BasePostprocessing):
    class Meta:
        db_table = 'honing_1_postprocessing'


class Honing2Preprocessing(BasePreprocessing):
    previous_gauge_status = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'honing_2_preprocessing'


class Honing2Postprocessing(BasePostprocessing):
    class Meta:
        db_table = 'honing_2_postprocessing'


# Deburring Machine
class DeburringPreprocessing(BasePreprocessing):
    previous_honing_status = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'deburring_preprocessing'


class DeburringPostprocessing(BasePostprocessing):
    class Meta:
        db_table = 'deburring_postprocessing'


# Washing Machines
class PrewashingPreprocessing(BasePreprocessing):
    previous_deburring_status = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'prewashing_preprocessing'


class PrewashingPostprocessing(BasePostprocessing):
    class Meta:
        db_table = 'prewashing_postprocessing'


class FinalWashingPreprocessing(BasePreprocessing):
    previous_prewashing_status = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'final_washing_preprocessing'


class FinalWashingPostprocessing(BasePostprocessing):
    class Meta:
        db_table = 'final_washing_postprocessing'


# Assembly Machines (1-4)
class AssemblyMachine1Preprocessing(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    machine_name = models.CharField(max_length=50, default='Assembly Machine 1')
    qr_code_internal = models.CharField(max_length=100)
    previous_piston_status = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'assembly_machine_1_preprocessing'
        ordering = ['-timestamp']


class AssemblyMachine1Postprocessing(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    qr_code_internal = models.CharField(max_length=100)
    qr_code_external = models.CharField(max_length=100)
    qr_code_housing = models.CharField(max_length=100)
    status = models.CharField(max_length=10, default='OK')
    
    class Meta:
        db_table = 'assembly_machine_1_postprocessing'
        ordering = ['-timestamp']


class AssemblyMachine2Preprocessing(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    machine_name = models.CharField(max_length=50, default='Assembly Machine 2')
    qr_code_internal = models.CharField(max_length=100)
    previous_piston_status = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'assembly_machine_2_preprocessing'
        ordering = ['-timestamp']


class AssemblyMachine2Postprocessing(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    qr_code_internal = models.CharField(max_length=100)
    qr_code_external = models.CharField(max_length=100)
    qr_code_housing = models.CharField(max_length=100)
    status = models.CharField(max_length=10, default='OK')
    
    class Meta:
        db_table = 'assembly_machine_2_postprocessing'
        ordering = ['-timestamp']


class AssemblyMachine3Preprocessing(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    machine_name = models.CharField(max_length=50, default='Assembly Machine 3')
    qr_code_internal = models.CharField(max_length=100)
    previous_piston_status = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'assembly_machine_3_preprocessing'
        ordering = ['-timestamp']


class AssemblyMachine3Postprocessing(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    qr_code_internal = models.CharField(max_length=100)
    qr_code_external = models.CharField(max_length=100)
    qr_code_housing = models.CharField(max_length=100)
    status = models.CharField(max_length=10, default='OK')
    
    class Meta:
        db_table = 'assembly_machine_3_postprocessing'
        ordering = ['-timestamp']


class AssemblyMachine4Preprocessing(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    machine_name = models.CharField(max_length=50, default='Assembly Machine 4')
    qr_code_internal = models.CharField(max_length=100)
    previous_piston_status = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        db_table = 'assembly_machine_4_preprocessing'
        ordering = ['-timestamp']


class AssemblyMachine4Postprocessing(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    qr_code_internal = models.CharField(max_length=100)
    qr_code_external = models.CharField(max_length=100)
    qr_code_housing = models.CharField(max_length=100)
    status = models.CharField(max_length=10, default='OK')
    
    class Meta:
        db_table = 'assembly_machine_4_postprocessing'
        ordering = ['-timestamp']


# O-Ring Assembly & Leak Test
class OringLeakTestPreprocessing(BasePreprocessing):
    previous_assembly_status = models.CharField(max_length=10, null=True, blank=True)
    qr_code = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'oring_leak_test_preprocessing'


class OringLeakTestPostprocessing(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    qr_code = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'oring_leak_test_postprocessing'
        ordering = ['-timestamp']


# Painting Machine
class PaintingPreprocessing(BasePreprocessing):
    previous_leak_test_status = models.CharField(max_length=10, null=True, blank=True)
    qr_code = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'painting_preprocessing'


class PaintingPostprocessing(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    qr_code = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'painting_postprocessing'
        ordering = ['-timestamp']


# Lubrication Machine (Final)
class LubricationPreprocessing(BasePreprocessing):
    previous_painting_status = models.CharField(max_length=10, null=True, blank=True)
    qr_code = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'lubrication_preprocessing'


class LubricationPostprocessing(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    qr_code = models.CharField(max_length=100)
    status = models.CharField(max_length=10, default='OK')
    
    class Meta:
        db_table = 'lubrication_postprocessing'
        ordering = ['-timestamp']