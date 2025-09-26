#!/usr/bin/env python3
# Copyright 2018-2024 Lausanne University Hospital and University of Lausanne,
# Switzerland & Contributors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Shared pynetdicom Storage SCP listener functionality."""

import os
import sys
from datetime import datetime
from pynetdicom import AE, StoragePresentationContexts
from pynetdicom.sop_class import CTImageStorage, MRImageStorage, SecondaryCaptureImageStorage


def handle_store(event, output_dir):
    """Handle incoming C-STORE requests."""
    # Get the dataset from the event
    dataset = event.dataset

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename based on SOP Instance UID
    sop_instance_uid = dataset.SOPInstanceUID
    filename = f"{sop_instance_uid}.dcm"
    filepath = os.path.join(output_dir, filename)

    # Save the dataset
    dataset.save_as(filepath)

    print(f"Received and saved: {filepath}")
    print(f"Patient ID: {dataset.get('PatientID', 'Unknown')}")
    print(f"Study Date: {dataset.get('StudyDate', 'Unknown')}")
    print(f"Series Description: {dataset.get('SeriesDescription', 'Unknown')}")
    print("-" * 50)

    # Return success status
    return 0x0000


def create_ae():
    """Create and configure Application Entity for pynetdicom listener."""
    ae = AE()
    
    # Add essential supported presentation contexts
    ae.add_supported_context(CTImageStorage)
    ae.add_supported_context(MRImageStorage)
    ae.add_supported_context(SecondaryCaptureImageStorage)
    
    # Add common DICOM storage SOP classes that are most likely to be used
    from pynetdicom.sop_class import (
        ComputedRadiographyImageStorage,
        DigitalXRayImageStorageForPresentation,
        DigitalXRayImageStorageForProcessing,
        UltrasoundImageStorage,
        NuclearMedicineImageStorage,
        PositronEmissionTomographyImageStorage,
        RTImageStorage,
        RTDoseStorage,
        RTStructureSetStorage,
        RTPlanStorage,
        BasicTextSRStorage,
        EnhancedSRStorage,
        ComprehensiveSRStorage,
        EncapsulatedPDFStorage,
        PatientRootQueryRetrieveInformationModelMove,
    )
    
    # Add the SOP classes
    sop_classes = [
        ComputedRadiographyImageStorage,
        DigitalXRayImageStorageForPresentation,
        DigitalXRayImageStorageForProcessing,
        UltrasoundImageStorage,
        NuclearMedicineImageStorage,
        PositronEmissionTomographyImageStorage,
        RTImageStorage,
        RTDoseStorage,
        RTStructureSetStorage,
        RTPlanStorage,
        BasicTextSRStorage,
        EnhancedSRStorage,
        ComprehensiveSRStorage,
        EncapsulatedPDFStorage,
        PatientRootQueryRetrieveInformationModelMove,
    ]
    
    for sop_class in sop_classes:
        ae.add_supported_context(sop_class)
    
    return ae


def start_listener(address, port, aet, output_dir):
    """Start the pynetdicom listener server."""
    # Create Application Entity
    ae = create_ae()
    
    # Start the SCP
    print("Starting pynetdicom listener...")
    print(f"Address: {address}")
    print(f"Port: {port}")
    print(f"AET: {aet}")
    print(f"Output directory: {output_dir}")
    print(f"Started at: {datetime.now()}")
    print("-" * 50)
    
    try:
        ae.start_server(
            (address, port),
            ae_title=aet,
            evt_handlers=[(0x0001, lambda event: handle_store(event, output_dir))]
        )
    except KeyboardInterrupt:
        print("\nShutting down listener...")
        ae.shutdown()
    except Exception as e:
        print(f"Error starting listener: {e}")
        sys.exit(1)
