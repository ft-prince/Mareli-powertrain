from django.contrib import admin
from django.utils.html import format_html
from . import models


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def colored_status(status):
    """Display status with color coding"""
    if status == 'OK':
        return format_html(
            '<span style="background: #e8f5e9; color: #00cc66; padding: 4px 12px; border-radius: 4px; font-weight: bold;">✓ OK</span>'
        )
    elif status == 'NG':
        return format_html(
            '<span style="background: #ffebee; color: #cc3333; padding: 4px 12px; border-radius: 4px; font-weight: bold;">✗ NG</span>'
        )
    else:
        return format_html(
            '<span style="background: #fff3e0; color: #ff9933; padding: 4px 12px; border-radius: 4px; font-weight: bold;">⏳ Pending</span>'
        )


# ============================================================================
# CNC MACHINES (1-6) - Preprocessing & Postprocessing
# ============================================================================

@admin.register(models.Cnc1Preprocessing)
class Cnc1PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'machine_name', 'qr_data', 'model_name')
    search_fields = ('qr_data', 'machine_name', 'model_name')
    list_filter = ('machine_name', 'model_name')
    readonly_fields = ('id',)


@admin.register(models.Cnc1Postprocessing)
class Cnc1PostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'status_display')
    search_fields = ('qr_data',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


@admin.register(models.Cnc2Preprocessing)
class Cnc2PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'machine_name', 'qr_data', 'model_name')
    search_fields = ('qr_data', 'machine_name', 'model_name')
    list_filter = ('machine_name', 'model_name')
    readonly_fields = ('id',)


@admin.register(models.Cnc2Postprocessing)
class Cnc2PostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'status_display')
    search_fields = ('qr_data',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


@admin.register(models.Cnc3Preprocessing)
class Cnc3PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'machine_name', 'qr_data', 'model_name')
    search_fields = ('qr_data', 'machine_name', 'model_name')
    list_filter = ('machine_name', 'model_name')
    readonly_fields = ('id',)


@admin.register(models.Cnc3Postprocessing)
class Cnc3PostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'status_display')
    search_fields = ('qr_data',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


@admin.register(models.Cnc4Preprocessing)
class Cnc4PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'machine_name', 'qr_data', 'model_name')
    search_fields = ('qr_data', 'machine_name', 'model_name')
    list_filter = ('machine_name', 'model_name')
    readonly_fields = ('id',)


@admin.register(models.Cnc4Postprocessing)
class Cnc4PostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'status_display')
    search_fields = ('qr_data',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


@admin.register(models.Cnc5Preprocessing)
class Cnc5PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'machine_name', 'qr_data', 'model_name')
    search_fields = ('qr_data', 'machine_name', 'model_name')
    list_filter = ('machine_name', 'model_name')
    readonly_fields = ('id',)


@admin.register(models.Cnc5Postprocessing)
class Cnc5PostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'status_display')
    search_fields = ('qr_data',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


@admin.register(models.Cnc6Preprocessing)
class Cnc6PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'machine_name', 'qr_data', 'model_name')
    search_fields = ('qr_data', 'machine_name', 'model_name')
    list_filter = ('machine_name', 'model_name')
    readonly_fields = ('id',)


@admin.register(models.Cnc6Postprocessing)
class Cnc6PostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'status_display')
    search_fields = ('qr_data',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


# ============================================================================
# GAUGE MACHINES (1-3)
# ============================================================================

@admin.register(models.Gauge1Preprocessing)
class Gauge1PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'model_name', 'previous_machine_status')
    search_fields = ('qr_data', 'model_name')
    list_filter = ('previous_machine_status', 'model_name')
    readonly_fields = ('id',)


@admin.register(models.Gauge1Postprocessing)
class Gauge1PostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'status_display', 'value1', 'value2', 'value3', 'value4', 'value5')
    search_fields = ('qr_data',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


@admin.register(models.Gauge2Preprocessing)
class Gauge2PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'model_name', 'previous_machine_status')
    search_fields = ('qr_data', 'model_name')
    list_filter = ('previous_machine_status', 'model_name')
    readonly_fields = ('id',)


@admin.register(models.Gauge2Postprocessing)
class Gauge2PostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'status_display', 'value1', 'value2', 'value3', 'value4', 'value5')
    search_fields = ('qr_data',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


@admin.register(models.Gauge3Preprocessing)
class Gauge3PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'model_name', 'previous_machine_status')
    search_fields = ('qr_data', 'model_name')
    list_filter = ('previous_machine_status', 'model_name')
    readonly_fields = ('id',)


@admin.register(models.Gauge3Postprocessing)
class Gauge3PostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'status_display', 'value1', 'value2', 'value3', 'value4', 'value5')
    search_fields = ('qr_data',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


# ============================================================================
# HONING MACHINES (1-2)
# ============================================================================

@admin.register(models.Honing1Preprocessing)
class Honing1PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'model_name', 'previous_machine_status')
    search_fields = ('qr_data', 'model_name')
    list_filter = ('previous_machine_status', 'model_name')
    readonly_fields = ('id',)


@admin.register(models.Honing1Postprocessing)
class Honing1PostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'status_display')
    search_fields = ('qr_data',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


@admin.register(models.Honing2Preprocessing)
class Honing2PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'model_name', 'previous_machine_status')
    search_fields = ('qr_data', 'model_name')
    list_filter = ('previous_machine_status', 'model_name')
    readonly_fields = ('id',)


@admin.register(models.Honing2Postprocessing)
class Honing2PostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'status_display')
    search_fields = ('qr_data',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


# ============================================================================
# DEBURRING MACHINE
# ============================================================================

@admin.register(models.DeburringPreprocessing)
class DeburringPreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'model_name', 'previous_machine_status')
    search_fields = ('qr_data', 'model_name')
    list_filter = ('previous_machine_status', 'model_name')
    readonly_fields = ('id',)


@admin.register(models.DeburringPostprocessing)
class DeburringPostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'status_display')
    search_fields = ('qr_data',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


# ============================================================================
# WASHING MACHINES (Pre-washing & Final-washing)
# ============================================================================

@admin.register(models.PrewashingPreprocessing)
class PrewashingPreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'model_name', 'previous_machine_status', 'status_display')
    search_fields = ('qr_data', 'model_name')
    list_filter = ('previous_machine_status', 'status', 'model_name')
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


@admin.register(models.PrewashingPostprocessing)
class PrewashingPostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'model_name', 'previous_machine_status', 'status_display')
    search_fields = ('qr_data', 'model_name')
    list_filter = ('previous_machine_status', 'status', 'model_name')
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


@admin.register(models.FinalwashingPreprocessing)
class FinalwashingPreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'model_name', 'previous_machine_status', 'status_display')
    search_fields = ('qr_data', 'model_name')
    list_filter = ('previous_machine_status', 'status', 'model_name')
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


@admin.register(models.FinalwashingPostprocessing)
class FinalwashingPostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data', 'model_name', 'previous_machine_status', 'status_display')
    search_fields = ('qr_data', 'model_name')
    list_filter = ('previous_machine_status', 'status', 'model_name')
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


# ============================================================================
# ASSEMBLY MACHINES (OP40A, OP40B, OP40C, OP40D)
# ============================================================================

@admin.register(models.Op40AProcessing)
class Op40AProcessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'qr_data_internal', 'qr_data_external', 'qr_data_housing', 
                    'model_name_internal', 'model_name_external', 'model_name_housing',
                    'previous_machine_internal_status', 'previous_machine_housing_status', 
                    'status_display', 'created_at')
    search_fields = ('qr_data_internal', 'qr_data_external', 'qr_data_housing',
                     'model_name_internal', 'model_name_external', 'model_name_housing')
    list_filter = ('status', 'previous_machine_internal_status', 
                   'previous_machine_housing_status', 'created_at')
    readonly_fields = ('id',)
    date_hierarchy = 'created_at'
    
    def status_display(self, obj):
        return colored_status(obj.status or 'Pending')
    status_display.short_description = 'Status'


@admin.register(models.Op40BProcessing)
class Op40BProcessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'qr_data_internal', 'qr_data_external', 'qr_data_housing', 
                    'model_name_internal', 'model_name_external', 'model_name_housing',
                    'previous_machine_internal_status', 'previous_machine_housing_status', 
                    'status_display', 'created_at')
    search_fields = ('qr_data_internal', 'qr_data_external', 'qr_data_housing',
                     'model_name_internal', 'model_name_external', 'model_name_housing')
    list_filter = ('status', 'previous_machine_internal_status', 
                   'previous_machine_housing_status', 'created_at')
    readonly_fields = ('id',)
    date_hierarchy = 'created_at'
    
    def status_display(self, obj):
        return colored_status(obj.status or 'Pending')
    status_display.short_description = 'Status'


@admin.register(models.Op40CProcessing)
class Op40CProcessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'qr_data_internal', 'qr_data_external', 'qr_data_housing', 
                    'model_name_internal', 'model_name_external', 'model_name_housing',
                    'previous_machine_internal_status', 'previous_machine_housing_status', 
                    'status_display', 'created_at')
    search_fields = ('qr_data_internal', 'qr_data_external', 'qr_data_housing',
                     'model_name_internal', 'model_name_external', 'model_name_housing')
    list_filter = ('status', 'previous_machine_internal_status', 
                   'previous_machine_housing_status', 'created_at')
    readonly_fields = ('id',)
    date_hierarchy = 'created_at'
    
    def status_display(self, obj):
        return colored_status(obj.status or 'Pending')
    status_display.short_description = 'Status'


@admin.register(models.Op40DProcessing)
class Op40DProcessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'qr_data_internal', 'qr_data_external', 'qr_data_housing', 
                    'model_name_internal', 'model_name_external', 'model_name_housing',
                    'previous_machine_internal_status', 'previous_machine_housing_status', 
                    'status_display', 'created_at')
    search_fields = ('qr_data_internal', 'qr_data_external', 'qr_data_housing',
                     'model_name_internal', 'model_name_external', 'model_name_housing')
    list_filter = ('status', 'previous_machine_internal_status', 
                   'previous_machine_housing_status', 'created_at')
    readonly_fields = ('id',)
    date_hierarchy = 'created_at'
    
    def status_display(self, obj):
        return colored_status(obj.status or 'Pending')
    status_display.short_description = 'Status'


# ============================================================================
# OP80 - LEAK TEST & O-RING ASSEMBLY
# ============================================================================

@admin.register(models.Op80Preprocessing)
class Op80PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data_piston', 'qr_data_housing', 
                    'model_name_internal', 'model_name_external', 'previous_machine_status')
    search_fields = ('qr_data_piston', 'qr_data_housing', 'model_name_internal', 'model_name_external')
    list_filter = ('previous_machine_status',)
    readonly_fields = ('id',)


@admin.register(models.Op80Postprocessing)
class Op80PostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data_housing_new', 'qr_data_housing', 
                    'match_status', 'status_display')
    search_fields = ('qr_data_housing_new', 'qr_data_housing')
    list_filter = ('match_status', 'status')
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


# ============================================================================
# PAINTING MACHINE
# ============================================================================

@admin.register(models.PaintingPreprocessing)
class PaintingPreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data_housing', 'qr_data_piston', 
                    'model_name_housing', 'model_name_piston',
                    'previous_machine_status', 'pre_status')
    search_fields = ('qr_data_housing', 'qr_data_piston', 'model_name_housing', 'model_name_piston')
    list_filter = ('previous_machine_status', 'pre_status')
    readonly_fields = ('id',)


@admin.register(models.PaintingPostprocessing)
class PaintingPostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data_piston', 'qr_data_housing', 'status_display')
    search_fields = ('qr_data_piston', 'qr_data_housing')
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'


# ============================================================================
# LUBRICATION MACHINE (FINAL STEP)
# ============================================================================

@admin.register(models.LubPreprocessing)
class LubPreprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data_piston', 'qr_data_housing', 
                    'model_name_piston', 'model_name_housing', 'previous_machine_status')
    search_fields = ('qr_data_piston', 'qr_data_housing', 'model_name_piston', 'model_name_housing')
    list_filter = ('previous_machine_status',)
    readonly_fields = ('id',)


@admin.register(models.LubPostprocessing)
class LubPostprocessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'qr_data_piston', 'status_display')
    search_fields = ('qr_data_piston',)
    list_filter = ('status',)
    readonly_fields = ('id',)
    
    def status_display(self, obj):
        return colored_status(obj.status)
    status_display.short_description = 'Status'