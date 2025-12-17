from django import template

register = template.Library()

@register.filter(name='get_machine_group')
def get_machine_group(machine_id):
    """Determine which group a machine belongs to based on its ID"""
    machine_id = str(machine_id).lower()
    
    if 'dmg_mori' in machine_id:
        return 'dmg_mori'
    elif 'gauge' in machine_id:
        return 'gauge'
    elif 'honing' in machine_id:
        return 'honing'
    elif 'prewashing' in machine_id or 'finalwashing' in machine_id or 'finlwashing' in machine_id:
        return 'washing'
    elif 'deburring' in machine_id:
        return 'processing'
    elif 'op40' in machine_id:
        return 'assembly'
    elif 'op80' in machine_id or 'painting' in machine_id or 'lubrication' in machine_id:
        return 'special'
    else:
        return 'other'








