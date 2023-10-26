"""Custom heuristic file for Heudiconv DICOM to BIDS converter.

Link
----

*  https://github.com/nipy/heudiconv
"""

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
    func = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_run-00{item:01d}_task-rest_bold')
    fmap = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_run-00{item:01d}_fmap')

    dwi_dti = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-DTI_run-00{item:01d}_dwi') # diffusion weighted imaging == DTI == HARDI == DSI
    dwi_dsi = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-DSI_run-00{item:01d}_dwi')
    hardi = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-HARDI_run-00{item:01d}_dwi')
    
    t1_map = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-00{item:01d}_T1map')
    t2_map = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-00{item:01d}_T2map')
    flair = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-00{item:01d}_FLAIR')
    mt_on = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_acq-mton_run-00{item:01d}_mt')
    mt_off = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_acq-mtoff_run-00{item:01d}_mt')

    other = create_key('sub-{subject}/{session}/other/sub-{subject}_{session}_run-00{item:01d}_other')


    info = {t1w: [], func: [],  t1_map : [], t2_map : [] , fmap: [], dwi_dti: [], dwi_dsi: [], hardi : [] , mt_on : [], mt_off:[], other : []}
    
    for idx, s in enumerate(seqinfo):
        
        #########################################DWI##############################################

        if "dti" in s.series_description.lower() and not "_colfa" in s. series_description.lower() and not "adc" in s. series_description.lower() and not "tensor" in s.series_description.lower() and not "trace" in s.series_description.lower() and not "_fa" in s.series_description.lower():
            info[dwi_dti].append(s.series_id)

        if "dsi" in s.series_description.lower() and not "_colfa" in s. series_description.lower() and not "adc" in s. series_description.lower() and not "tensor" in s.series_description.lower() and not "trace" in s.series_description.lower() and not "_fa" in s.series_description.lower():
            info[dwi_dsi].append(s.series_id)

        if "hardi" in s.series_description.lower() and not "_colfa" in s. series_description.lower() and not "adc" in s. series_description.lower() and not "tensor" in s.series_description.lower() and not "trace" in s.series_description.lower() and not "_fa" in s.series_description.lower():
            info[hardi].append(s.series_id)

        #########################################func##############################################
        if ('resting' in  s.series_description.lower()) or "rsfmri" in s.series_description.lower(): 
            info[func].append(s.series_id)

        if 'spcir' in s.sequence_name.lower() or 'spc3d' in s.sequence_name.lower() : 
            info[flair].append(s.series_id)

        if "mprage-p3" in s.series_description.replace("_","-").lower():
            info[t1w].append(s.series_id)

        if ("t1map" in s.series_description.lower()) or ("t1-grep" in s.series_description.replace("_","-").lower()) or "t1-images" in s.series_description.replace("_","-").lower() : 
            info[t1_map].append(s.series_id)

        if ("t2map" in s.series_description.lower()) or ("t2-tse" in s.series_description.replace("_","-").lower()) or "t2-images" in s.series_description.replace("_","-").lower() : 
            info[t2_map].append(s.series_id)

        if ("mt" in s.series_description.lower()) and not("nomt" in s.series_description.lower()) : 
            info[mt_on].append(s.series_id)

        if ("nomt" in s.series_description.lower()): 
            info[mt_off].append(s.series_id)

        if "gre-field-mapping" in s.series_description.replace("_","-").lower() :
            info[fmap].append(s.series_id)

        else :
            info[other].append(s.series_id)

    return info

"""
idsDTIs       = {'-ep2d-diff-dti';'-dti-std-p3';};
idsT1s        = {'mprage-p3.nii.gz';'t1.nii.gz';'mprage_wip542d.nii.gz'};
idsDSIs       = {'dsi-603-q4-half-tra-strict.nii.gz';'dwidsi.nii.gz';'dsi-603-q4-half-tra-strict-strict.nii.gz';'dsi-466-q4-half-tra-strict.nii.gz'};
idsrsFMRIs    = {'ep2d-bold-resting-state';'t1.nii.gz';'mprage_wip542d.nii.gz';'rsfmri'};
idsT1Maps     = {'t1map.nii.gz';'t1-gre';'t1gre';'t1-images'};
idsT2Maps     = {'t2map.nii.gz';'t2-tse';'t2tse';'-t2';'-t2-images'};
idsFMaps      = {'gre-field-mapping'};
idsMTons      = {'mt-3-3d'};
idsMToffs     = {'mt-3-nomt-3d'};

"""


"""

modName = 'dwi'; % Modality for DSI
runNumb = num2str(contDSI);
acqName = ['dsiNdir' num2str(length(bvals))]; % Acquisition number. One study could contain more than one DWI
nnamenii = [Id '_' sesId '_acq-' acqName '_run-' runNumb '_' modName];

"""

"""        
                if (s.dim3 == 64) and (s.dim4 == 1) and ('gre_field_mapping' in s.protocol_name):
                    info[fmap_mag].append(s.series_id)
                
                if (s.dim3 == 32) and (s.dim4 == 1) and ('gre_field_mapping' in s.protocol_name):
                    info[fmap_phase].append(s.series_id)
"""        
"""
    fmap_mag =  create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_magnitude')
    fmap_phase = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_phasediff')
    
"""