# Copyright (C) Edward Jones

from .blender_available import blender_available
from .lazy_import import LazyImport
from .util import dict_union
from math import log
if blender_available():
    from bpy import types
    data = LazyImport('bpy', 'data')

from .log import printi, printw


def shrink_wrap_glyphs_to_keys(glyph_names: [str], keycap_model_name: str,
                               cap_unit_length: float,
                               shrink_wrap_offset: float, subsurf_params:dict, scaling:float) -> None:
    if keycap_model_name is None:
        printw('Shrink-wrapping was aborted as no models were successfully imported into blender')
        return

    glyphs:[dict] = map(lambda gn: { 'obj': data.objects[gn] }, glyph_names)
    min_log_max_dim:float = 0.0
    max_log_max_dim:float = 0.0
    if subsurf_params['adaptive-subsurf']:
        glyphs = list(map(lambda g: dict_union(g, { 'log-max-dim': log(max(g['obj'].dimensions)) }), glyphs))
        if len(glyphs) != 0:
            min_log_max_dim = min(map(lambda g: g['log-max-dim'], glyphs))
            max_log_max_dim = max(map(lambda g: g['log-max-dim'], glyphs))
        else:
            min_log_max_dim = 0.0
            max_log_max_dim = 1.0
    print(min_log_max_dim, max_log_max_dim)

    # Shrink-wrap glyphs onto the keycaps
    for glyph in glyphs:
        # Translate to favourable position (assuming no 3u tall keycaps)
        obj:Obj = glyph['obj']
        obj.location.z += 3.0 * cap_unit_length * scaling

        # Apply subdivision surface to glyph
        printi('A%spplying subdivision surface to "%s"' %('daptively a' if subsurf_params['adaptive-subsurf'] else '', obj.name))
        subsurfModName: str = 'subsurf_' + obj.name
        subsurfMod: SubsurfModifier = obj.modifiers.new(name=subsurfModName, type='SUBSURF')
        subsurfMod.quality = subsurf_params['quality']
        subsurfMod.subdivision_type = 'SIMPLE'
        if subsurf_params['adaptive-subsurf']:
            subsurfMod.levels = round((glyph['log-max-dim'] - min_log_max_dim) / (max_log_max_dim - min_log_max_dim) * subsurf_params['viewport-levels'])
            subsurfMod.render_levels = round((glyph['log-max-dim'] - min_log_max_dim) / (max_log_max_dim - min_log_max_dim) * subsurf_params['render-levels'])
            #  subsurfMod.levels = subsurf_params['viewport-levels']
            #  subsurfMod.render_levels = subsurf_params['render-levels']
        else:
            subsurfMod.levels = subsurf_params['viewport-levels']
            subsurfMod.render_levels = subsurf_params['render-levels']

        # Shrink wrap glyph onto keycaps
        printi('Shrink-wrapping glyph-part "%s" onto "%s"' %(obj.name, keycap_model_name))
        shrinkWrapModName: str = 'shrink_wrap_' + obj.name
        shrinkWrapMod: ShrinkWrapModifier = obj.modifiers.new(
            name=shrinkWrapModName, type='SHRINKWRAP')
        shrinkWrapMod.target = data.objects[keycap_model_name]
        shrinkWrapMod.wrap_method = 'PROJECT'
        shrinkWrapMod.use_project_z = True
        shrinkWrapMod.use_negative_direction = True
        shrinkWrapMod.offset = shrink_wrap_offset
