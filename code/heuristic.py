import os
def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes
def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where
    allowed template fields - follow python string module:
    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """
    t1w = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-00{item:01d}_T1w') # MPRAGE
    func = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_run-00{item:01d}_func')
    fmap_mag =  create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_magnitude')
    fmap_phase = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_phasediff')
    dwi = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_run-00{item:01d}_dwi') # diffusion weighted imaging == DTI == HARDI == DSI
    t1_map = create_key('sub-{subject}/{session}/t1_map/sub-{subject}_{session}_run-00{item:01d}_t1_map')
    t1 = create_key('sub-{subject}/{session}/t1/sub-{subject}_{session}_run-00{item:01d}_t1')
    t2 = create_key('sub-{subject}/{session}/t2/sub-{subject}_{session}_run-00{item:01d}_t2')
    t2_map = create_key('sub-{subject}/{session}/t2_map/sub-{subject}_{session}_run-00{item:01d}_t2_map')
    other = create_key('sub-{subject}/{session}/other/sub-{subject}_{session}_run-00{item:01d}_other')
    # ADD FLAIR


    info = {t1w: [], func: [],  t1_map : [], t2_map : [] , fmap_phase: [], dwi: [], t1 : [], t2:[], other : []}
    
    for idx, s in enumerate(seqinfo):
        
        # check DWI - maybe seq name starts with ep_ ? Ask Yasser

        if "DTI" in s.series_description or (and not ('DEV' in s.image_type) and not ('TIV' in s.image_type) and not ('LABELS' in s.image_type)):
            info[t1w].append(s.series_id)
        
        if (s.sequence_name == '*ep_b0') and not s.is_derived and (s.dim4 > 40) : 
            info[dwi].append(s.series_id)
        
        if (s.dim3 == 64) and (s.dim4 == 1) and ('gre_field_mapping' in s.protocol_name):
            info[fmap_mag].append(s.series_id)
        
        if (s.dim3 == 32) and (s.dim4 == 1) and ('gre_field_mapping' in s.protocol_name):
            info[fmap_phase].append(s.series_id)
        
        if ("T1 MAP" in s.image_type) or ("T1_MAP" in s.image_type) : 
            info[t1_map].append(s.series_id)

        if ("T2 MAP" in s.image_type) or ("T2_MAP" in s.image_type) : 
            info[t2_map].append(s.series_id)

        if s.sequence_name == "*epfid2d1_60" :
            info[func].append(s.series_id)

        if "t1" in s.protocol_name.lower() : 
            info[t1].append(s.series_id)

        if "t2" in s.protocol_name.lower() : 
            info[t2].append(s.series_id)
        else : 
            info[other].append(s.series_id)
        
    return info