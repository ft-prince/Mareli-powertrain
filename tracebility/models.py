from django.db import models


# ============================================================================
# CNC MACHINES (1-6) - Preprocessing & Postprocessing
# ============================================================================

class Cnc1Preprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    machine_name = models.CharField(max_length=50)
    qr_data = models.CharField(max_length=100)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'cnc1_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"CNC1 Pre - {self.qr_data}"


class Cnc1Postprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'cnc1_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"CNC1 Post - {self.qr_data} - {self.status}"


class Cnc2Preprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    machine_name = models.CharField(max_length=50)
    qr_data = models.CharField(max_length=100)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'cnc2_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"CNC2 Pre - {self.qr_data}"


class Cnc2Postprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'cnc2_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"CNC2 Post - {self.qr_data} - {self.status}"


class Cnc3Preprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    machine_name = models.CharField(max_length=50)
    qr_data = models.CharField(max_length=100)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'cnc3_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"CNC3 Pre - {self.qr_data}"


class Cnc3Postprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'cnc3_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"CNC3 Post - {self.qr_data} - {self.status}"


class Cnc4Preprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    machine_name = models.CharField(max_length=50)
    qr_data = models.CharField(max_length=100)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'cnc4_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"CNC4 Pre - {self.qr_data}"


class Cnc4Postprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'cnc4_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"CNC4 Post - {self.qr_data} - {self.status}"


class Cnc5Preprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    machine_name = models.CharField(max_length=50)
    qr_data = models.CharField(max_length=100)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'cnc5_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"CNC5 Pre - {self.qr_data}"


class Cnc5Postprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'cnc5_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"CNC5 Post - {self.qr_data} - {self.status}"


class Cnc6Preprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    machine_name = models.CharField(max_length=50)
    qr_data = models.CharField(max_length=100)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'cnc6_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"CNC6 Pre - {self.qr_data}"


class Cnc6Postprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'cnc6_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"CNC6 Post - {self.qr_data} - {self.status}"


# ============================================================================
# GAUGE MACHINES (1-3)
# ============================================================================

class Gauge1Preprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    previous_machine_status = models.CharField(max_length=10)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'gauge1_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Gauge1 Pre - {self.qr_data}"


class Gauge1Postprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    value1 = models.FloatField(blank=True, null=True)
    value2 = models.FloatField(blank=True, null=True)
    value3 = models.FloatField(blank=True, null=True)
    value4 = models.FloatField(blank=True, null=True)
    value5 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'gauge1_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Gauge1 Post - {self.qr_data} - {self.status}"


class Gauge2Preprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    previous_machine_status = models.CharField(max_length=10)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'gauge2_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Gauge2 Pre - {self.qr_data}"


class Gauge2Postprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    value1 = models.FloatField(blank=True, null=True)
    value2 = models.FloatField(blank=True, null=True)
    value3 = models.FloatField(blank=True, null=True)
    value4 = models.FloatField(blank=True, null=True)
    value5 = models.FloatField(blank=True, null=True)
    value6 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'gauge2_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Gauge2 Post - {self.qr_data} - {self.status}"


class Gauge3Preprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    previous_machine_status = models.CharField(max_length=10)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'gauge3_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Gauge3 Pre - {self.qr_data}"


class Gauge3Postprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    value1 = models.FloatField(blank=True, null=True)
    value2 = models.FloatField(blank=True, null=True)
    value3 = models.FloatField(blank=True, null=True)
    value4 = models.FloatField(blank=True, null=True)
    value5 = models.FloatField(blank=True, null=True)
    value6 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'gauge3_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Gauge3 Post - {self.qr_data} - {self.status}"


# ============================================================================
# HONING MACHINES (1-2)
# ============================================================================

class Honing1Preprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    previous_machine_status = models.CharField(max_length=10)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'honing1_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Honing1 Pre - {self.qr_data}"


class Honing1Postprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'honing1_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Honing1 Post - {self.qr_data} - {self.status}"


class Honing2Preprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    previous_machine_status = models.CharField(max_length=10)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'honing2_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Honing2 Pre - {self.qr_data}"


class Honing2Postprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'honing2_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Honing2 Post - {self.qr_data} - {self.status}"


# ============================================================================
# DEBURRING MACHINE
# ============================================================================

class DeburringPreprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    previous_machine_status = models.CharField(max_length=10)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'deburring_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Deburring Pre - {self.qr_data}"


class DeburringPostprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'deburring_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Deburring Post - {self.qr_data} - {self.status}"


# ============================================================================
# WASHING MACHINES (Pre-washing & Final-washing)
# ============================================================================

class PrewashingPreprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    previous_machine_status = models.CharField(max_length=10)
    status = models.CharField(max_length=10)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'prewashing_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Prewashing Pre - {self.qr_data}"


class PrewashingPostprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    previous_machine_status = models.CharField(max_length=10)
    status = models.CharField(max_length=10)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'prewashing_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Prewashing Post - {self.qr_data}"


class FinalwashingPreprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    previous_machine_status = models.CharField(max_length=10)
    status = models.CharField(max_length=10)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'finalwashing_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Finalwashing Pre - {self.qr_data}"


class FinalwashingPostprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data = models.CharField(max_length=100)
    previous_machine_status = models.CharField(max_length=10)
    status = models.CharField(max_length=10)
    model_name = models.CharField(max_length=20)  # ADDED

    class Meta:
        managed = True
        db_table = 'finalwashing_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Finalwashing Post - {self.qr_data}"


# ============================================================================
# ASSEMBLY MACHINES (OP40A, OP40B, OP40C, OP40D)
# ============================================================================

class Op40AProcessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp_internal = models.DateTimeField()
    qr_data_internal = models.CharField(unique=True, max_length=100)
    previous_machine_internal_status = models.CharField(max_length=10)
    model_name_internal = models.CharField(max_length=20)  # ADDED
    timestamp_external = models.DateTimeField(blank=True, null=True)
    qr_data_external = models.CharField(unique=True, max_length=100, blank=True, null=True)
    model_name_external = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    timestamp_housing = models.DateTimeField(blank=True, null=True)
    previous_machine_housing_status = models.CharField(max_length=10, blank=True, null=True)
    qr_data_housing = models.CharField(unique=True, max_length=100, blank=True, null=True)
    model_name_housing = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'op40a_processing'
        ordering = ['-id']

    def __str__(self):
        return f"OP40A - {self.qr_data_internal}"


class Op40BProcessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp_internal = models.DateTimeField()
    qr_data_internal = models.CharField(unique=True, max_length=100)
    previous_machine_internal_status = models.CharField(max_length=10)
    model_name_internal = models.CharField(max_length=20)  # ADDED
    timestamp_external = models.DateTimeField(blank=True, null=True)
    qr_data_external = models.CharField(unique=True, max_length=100, blank=True, null=True)
    model_name_external = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    timestamp_housing = models.DateTimeField(blank=True, null=True)
    previous_machine_housing_status = models.CharField(max_length=10, blank=True, null=True)
    qr_data_housing = models.CharField(unique=True, max_length=100, blank=True, null=True)
    model_name_housing = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'op40b_processing'
        ordering = ['-id']

    def __str__(self):
        return f"OP40B - {self.qr_data_internal}"


class Op40CProcessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp_internal = models.DateTimeField()
    qr_data_internal = models.CharField(unique=True, max_length=100)
    previous_machine_internal_status = models.CharField(max_length=10)
    model_name_internal = models.CharField(max_length=20)  # ADDED
    timestamp_external = models.DateTimeField(blank=True, null=True)
    qr_data_external = models.CharField(unique=True, max_length=100, blank=True, null=True)
    model_name_external = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    timestamp_housing = models.DateTimeField(blank=True, null=True)
    previous_machine_housing_status = models.CharField(max_length=10, blank=True, null=True)
    qr_data_housing = models.CharField(unique=True, max_length=100, blank=True, null=True)
    model_name_housing = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'op40c_processing'
        ordering = ['-id']

    def __str__(self):
        return f"OP40C - {self.qr_data_internal}"


class Op40DProcessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp_internal = models.DateTimeField()
    qr_data_internal = models.CharField(unique=True, max_length=100)
    previous_machine_internal_status = models.CharField(max_length=10)
    model_name_internal = models.CharField(max_length=20)  # ADDED
    timestamp_external = models.DateTimeField(blank=True, null=True)
    qr_data_external = models.CharField(unique=True, max_length=100, blank=True, null=True)
    model_name_external = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    timestamp_housing = models.DateTimeField(blank=True, null=True)
    previous_machine_housing_status = models.CharField(max_length=10, blank=True, null=True)
    qr_data_housing = models.CharField(unique=True, max_length=100, blank=True, null=True)
    model_name_housing = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'op40d_processing'
        ordering = ['-id']

    def __str__(self):
        return f"OP40D - {self.qr_data_internal}"


# ============================================================================
# OP80 - LEAK TEST & O-RING ASSEMBLY
# ============================================================================

class Op80Preprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data_piston = models.CharField(unique=True, max_length=100)
    model_name_internal = models.CharField(max_length=20)  # ADDED
    qr_data_housing = models.CharField(unique=True, max_length=100, blank=True, null=True)
    model_name_external = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    previous_machine_status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'op80_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"OP80 Pre - Piston: {self.qr_data_piston}"


class Op80Postprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data_housing_new = models.CharField(unique=True, max_length=100)
    qr_data_housing = models.CharField(unique=True, max_length=100, blank=True, null=True)
    match_status = models.CharField(max_length=10)
    status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'op80_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"OP80 Post - {self.qr_data_housing_new} - {self.status}"


# ============================================================================
# PAINTING MACHINE 
# ============================================================================

class PaintingPreprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data_housing = models.CharField(unique=True, max_length=100, blank=True, null=True)  # UPDATED: Made nullable
    model_name_housing = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    qr_data_piston = models.CharField(unique=True, max_length=100, blank=True, null=True)
    model_name_piston = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    previous_machine_status = models.CharField(max_length=10)
    pre_status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'painting_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Painting Pre - Housing: {self.qr_data_housing}"


class PaintingPostprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100, blank=True, null=True)  # ADDED (was missing)
    qr_data_piston = models.CharField(unique=True, max_length=100)  
    qr_data_housing = models.CharField(max_length=100, blank=True, null=True)  
    status = models.CharField(max_length=50, blank=True, null=True)  

    class Meta:
        managed = True
        db_table = 'painting_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Painting Post - {self.qr_data_piston} - {self.status}"


# ============================================================================
# LUBRICATION MACHINE (FINAL STEP)
# ============================================================================

class LubPreprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data_piston = models.CharField(unique=True, max_length=100)
    model_name_piston = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    qr_data_housing = models.CharField(max_length=100, blank=True, null=True)
    model_name_housing = models.CharField(max_length=20, blank=True, null=True)  # ADDED
    previous_machine_status = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'lub_preprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Lub Pre - Piston: {self.qr_data_piston}"


class LubPostprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.CharField(max_length=100)
    qr_data_piston = models.CharField(unique=True, max_length=100)
    status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'lub_postprocessing'
        ordering = ['-id']

    def __str__(self):
        return f"Lub Post - {self.qr_data_piston} - {self.status}"