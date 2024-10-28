PACSIFIER is a batch query/retrieve interface for the CareStream PACS at Lausanne University Hospital.

It is implemented as a Python application running on Ubuntu Linux, relying on the DCMTK suite of tools. A Docker image is available.


NOTE: For Windows users, we strongly recommend using WSL to run PACSIFIER, or alternatively, Anaconda can be used, though it's less preferred. Linux is the recommended environment.

# Prerequisites

## 1. Docker

Ensure that Docker is installed on your system. Docker allows PACSIFIER to run in a containerized environment, simplifying the setup and deployment. Follow the appropriate installation guide for your operating system:

- **Linux:** Follow the [official Docker installation guide](https://docs.docker.com/engine/install/ubuntu/).
- **Windows (Recommended: WSL):** Install Docker Desktop for Windows and enable WSL 2 integration. Follow the [Docker Desktop installation guide](https://docs.docker.com/desktop/install/windows-install/). Make sure to enable the "Use the WSL 2 based engine" option during installation.
- **macOS:** Follow the [Docker Desktop installation guide](https://docs.docker.com/desktop/install/mac-install/).

After installation, verify that Docker is correctly installed by running:
```bash
docker --version
```
## 2. DCMTK Tools

DCMTK (DICOM Toolkit) is required for interacting with DICOM servers. You can install it as follows:
- **Linux(Ubuntu-based systems):** :
	```bash
	sudo apt install dcmtk
	```

- **Windows (With WSL):**: Follow the same instructions as above within your WSL environment.

For more details about the DCMTK toolkit and available tools, refer to the [DCMTK tools documentation](https://dicom.offis.de/en/dcmtk/dcmtk-tools/).

# Building and testing


## Building the pacsifier Docker image from the repo

    cd /path/to/PACSIFIER/; docker build --network=host -t pacsifier .

## Running the test suite 

    cd /path/to/PACSIFIER/; docker build --network=host -t pacsifier .

# Installation

## Step 1: Clone the Repository

Begin by cloning the PACSIFIER repository and navigating into the project directory:

```bash
git clone https://github.com/TranslationalML/pacsifier.git
cd pacsifier
```
## Step 2: Choose an Installation Method

You can either use Docker for a quick and straightforward setup or install PACSIFIER from source, which is recommended for developers who need to modify or extend the code.

## Installation via Docker (Recommended)

For a simple and consistent setup, you can use Docker. This approach ensures that all dependencies are correctly installed and configured.

1. **Build the Docker Image:**

   At the root of the repository, run the following command:

   ```bash
   make build-docker
   ```

   This will build the PACSIFIER Docker image using the provided Dockerfile.

2. **Running PACSIFIER:**

   Once the Docker image is built, you can run PACSIFIER by using:

   ```bash
   docker run --rm --net=host -v /path/to/config.json:/config.json -v /path/to/query.csv:/query.csv -v /path/to/output/directory:/output pacsifier:1.0.0 pacsifier -c /config.json -i -q /query.csv -d /output
   ```

3. **Testing via Docker:**

   To run tests using Docker, use the command:

   ```bash
   make test
   ```

## Installation from Source (For Developers)

If you need to develop or customize PACSIFIER, you can install it from source:

1. **Create a Python Environment:**

   Use Miniconda or another virtual environment manager to create a clean Python environment:

   conda create -n pacsifier_minimal python=3.10  
   conda activate pacsifier_minimal

2. **Install PACSIFIER:**

   With the environment activated, run:
	```bash
   pip install -e .
   ```

   This will install PACSIFIER in editable mode, allowing you to make and test changes easily.

3. **Optional: Install Additional Development Tools**

   If you plan to work on documentation or run tests, you may want to install additional dependencies:
	```bash
   pip install ".[dev,docs,test]"
   ```

4. **Verify the Installation:**

   To ensure everything is set up correctly, you can run:
	```bash
	pacsifier --help
	````

   This should display the help message for PACSIFIER, confirming the installation was successful.

## Installation for Legacy Windows Versions

The following instructions are provided for older versions of Windows (e.g., Windows 7). While not recommended for new setups, they are maintained here for users who need to install PACSIFIER on legacy systems. For a smoother installation, consider using WSL or upgrading to a more recent setup.

### Requirements:
- [Git](https://git-scm.com/download/win)
- [Chocolatey](https://chocolatey.org/)
- [Miniconda](https://conda.io)
- Powershell (installed by default since Windows 7 SP1)

This installation process is more cumbersome than the Linux setup.

1. Download and install the Chocolatey package manager:  
   [https://chocolatey.org/](https://chocolatey.org/)

2. Open a command prompt in admin mode and install DCMTK:  
   `choco install dcmtk`

3. Verify the installation by running a command prompt and typing:  
   `echoscu`

4. Download and install Miniconda from:  
   [https://conda.io](https://conda.io)

5. Clone the PACSIFIER repository using:  
   `git clone https://github.com/TranslationalML/pacsifier`

6. Set up the Python environment using `cmd.exe` in admin mode:
   - Run a command prompt as admin (Start menu > right-click on Command Prompt > Run as Administrator)
   - Activate the base conda environment:  
     `D:\path\to\miniconda\Scripts\activate.bat d:\path\to\miniconda`
   - Create the environment:  
     `conda env create -n pacsifier_minimal -f /path/to/pacsifier/deployment/utils/environment_minimal.yml`
   - Note: Using `Anaconda Prompt` might result in a `NotWriteableError: The current user does not have write permissions to a required path`.

7. Install support to run conda in PowerShell using `Anaconda Prompt` ([PSCondaEnvs](https://github.com/BCSharp/PSCondaEnvs)), as Chocolatey makes DCMTK available through PowerShell:
   - In `Anaconda Prompt`:  
     `conda install -n root -c pscondaenvs pscondaenvs`
   - This will create scripts `activate.ps1` and `deactivate.ps1` in `D:\path\to\miniconda\Scripts\`.
   - Other options, not extensively tested, include:  
     - [https://github.com/pldmgg/misc-powershell/tree/master/MyModules/AnacondaEnv](https://github.com/pldmgg/misc-powershell/tree/master/MyModules/AnacondaEnv)  
     - [https://gist.github.com/pldmgg/c84e802bcecd6e4c962f65be5b5d316d](https://gist.github.com/pldmgg/c84e802bcecd6e4c962f65be5b5d316d)  
     - [https://github.com/Liquidmantis/PSCondaEnvs](https://github.com/Liquidmantis/PSCondaEnvs)

8. Enable these cmdlets using Powershell in admin mode:
   - Run Powershell as admin (right-click > Run as Admin) and execute:  
     `Set-ExecutionPolicy RemoteSigned`

9. Create the PACS client/server configuration file as described in the documentation.

# Usage

## Using Docker

To keep things simple, choose a directory (e.g., `my_dir`) that will store the query file (e.g., `my_query.csv`) and configuration file (e.g., `my_config.json`). Create a sub-directory (e.g., `my_output_dir`) to store the DICOM files.

To make this directory accessible within the Docker container, you need to bind mount it as a Docker volume to a specific location in the container using the `-v` flag. In the examples below, we bind mount the host computer's directory into the `/base` volume within Docker. Paths for the config file and query files will be relative to that Docker volume.

This Docker image's entrypoint is `pacsifier.py`.

### Running on Linux or WSL

Build the Docker image if you haven't already:
```bash
make build-docker
```

Run PACSIFIER with Docker:
```bash
docker run --rm --net=host -v /path/to/my_dir:/base pacsifier:1.0.0 pacsifier --save --info --queryfile /base/my_query.csv --config /base/my_config.json --out_directory /base/my_output_dir
```

Replace /path/to/my_dir with the actual path on your system where the configuration and query files are stored. The output files will be saved to my_output_dir within the same mounted directory.

## From Source

### Running on Linux or WSL

1. **Activate your conda environment:**
```bash
conda activate pacsifier_minimal
```

2. **Run PACSIFIER:**
See the section `Running Queries`.

# Running Queries

## Command Line

To run PACSIFIER from the command line, use the following format:

   python pacsifier.py --info --save --queryfile /path/to/queryfile --config /path/to/config_file --out_directory /path/to/output_directory

### Options:
- `--info` or `-i`: Dumps information from the retrieved series (`findscu` output) into CSV files.
- `--save` or `-s`: Saves the queried DICOM images to disk. Cannot be used with `--move`.
- `--move` or `-m`: Moves the queried DICOM images to another DICOM node specified in the config file. Cannot be used with `--save`.
- `--queryfile` or `-q`: Specifies the path to the query file (mandatory for `--save` or `--move`).
- `--config` or `-c`: Specifies the path to the configuration file (mandatory for query/retrieve operations).
- `--out_directory` or `-d`: Optional. Specifies the directory where the information dumps and DICOM images will be saved.

### Additional Notes:
- The command will download DICOM images by default to the directory specified with `--out_directory`. If not provided, it defaults to a `data` folder within the project.
- You can choose to download images without using the `--info` option or only dump the information without using the `--save` option.
- `--move` cannot be used simultaneously with `--save` or `--upload`.

## Example Commands:
1. To query and save images:
   ```bash
   python pacsifier.py --save --info --queryfile /path/to/my_query.csv --config /path/to/my_config.json --out_directory /path/to/my_output_dir
   ```

2. To query and move images to a remote DICOM node:
   ```bash
   python pacsifier.py --move --queryfile /path/to/my_query.csv --config /path/to/my_config.json
   ```

3. To upload DICOM images to a PACS server:
   ```bash
   python pacsifier.py --move --queryfile /path/to/my_query.csv --config /path/to/my_config.json
   ```

## Query file

The query file is a `.csv` file that should include one or many of these column names : 
- StudyDate : The study dates of this column should be in the format YYYYMMDD (e.g 19900912 which indicates the 12th of September 1990). <br> Note : Querying on a date range is supported. (e.g 20150201-20160201 will query on studies between 01/02/2015 and 01/02/2016 ) 
- StudyTime : The study time should be in the format HHMMSS (e.g 140500 which means 14:05:00)
⁻ SeriesDecription : The series description.
- PatientID :  The patient ID. 
- ProtocolName : The protocol names.
- StudyInstanceUID : The Study Instance UID.
- PatientName : The patient name. (It is not recommanded to use this filter since there is no clear norm on how the patient names were stored on the pacs server)
- PatientBirthDate : Similarily to the StudyDate the date should be in format YYYYMMDD. Querying on date range is not supported for patient birth date.
- SeriesInstanceUID : The Series Instance UID
- ImageType : The image type as stored in the pacs server. (Note : using this filter significantly slows down the querying process. Use it only if absolutely necessary.) 
- AcquisitionDate : The acquisition date.
- SeriesNumber : The series number.
- StudyDescription : The study description.
- AccessionNumber : The Accession number.
- Modality : The modality.

The query file can be built in Excel and exported to comma-separated values `.csv` format.


Notes : 
- The query file could include one or many of the columns mentioned above. 
- If a line in a csv file contains an empty string on a particular columns, then, the query will not include the attribute corresponding to the column in question.
- The querying does not accept the value `*` alone on any attribute. However it can be used as a wildcard if other characters are provided, e.g. `ProtocolName` could be set to `BEAT_SelfNav*`
- the Series folders are named after the Series Description of its images. However, it may happen that a dicom image has no SeriesDescription stored. In that case, the image will be stored within a folder called No_series_description.

## Config file 

The config file is a json file that must include exactly these keys: 
- `server_address`: PACS server IP / URL address
- `port`: PACS server port number 
- `server_AET`: PACS server application entity title
- `AET`: current station application entity title
- `move_AET`: the AET of the remote move destination
- `move_port`: port number to use on the move destination (local) to receive images (C-MOVE destination)
- `batch_size` : The number of series to be downloaded before sleeping for a while.
- `batch_wait_time` : sleep time after each batch_size number of series is downloaded.

The AET and corresponding IP of the workstation should be declared on Carestream, including the storeable attribute.



### Examples

#### Example 1 

	StudyDate,PatientID
	20150512,123421
	,45322
	20180102,

A csv file like the one written above will retrieve:
- Images correspoding to study done on 12/05/2015 and for patient with patientID 123421.
- Images of patient with patient ID 45322.
- Images of studies done the 02/01/2018.

#### Example 2 

	StudyDate,PatientID
	20150512,123421

The query for the csv file described above will fail since the column name patientID does not correspond to any allowed column mentioned above. (patientID should be PatientID)

#### Example 3 

	StudyDate,PatientID
	20150512,*

The query for this csv file will fail because querying with values * is not allowed.

#### Example 4 

	StudyDate,PatientID
	20150512-20150612,124588

Using this csv file, the query will retrieve images of the patient with patient ID 124588 and Study date between 12/05/2015 and 12/06/2015.

#### Example 5

	ProtocolName,Modality,PatientBirthDate
	BEAT_SelfNav*,CT,19920611

This csv file will retrieve all the images with ProtocolName starting with BEAT_SelfNav, Modality CT and of Patients whose birthdays are on  11th of June 1992.

# Anonymization

## Getting pseudonyms from the De-ID API at CHUV (GPCR)

For patients that have a study declared in the Horus system, you can get consistent pseudonyms using the De-ID API.

### Command Line
   python get_pseudonyms.py --config my_config_deid.json --queryfile my_query.csv --project_name my_project_name --out_directory ./

- `my_config_deid.json` is the configuration file for the De-ID API, containing the token and service URL.
- `my_query.csv` is the PACSIFIER query file, listing all PatientIDs to pseudonymize.
- `my_project_name` corresponds to the project name on GPCR and may also correspond to the album name on Kheops where the study will be pushed.

After running, the output directory will contain two files: `new_ids_[my_project_name].json` and `day_shift_[my_project_name].json`, which can be used directly with the anonymization process below.

### Docker Command-Line

   docker run -it --rm -v c:\Users\my_user\my_dir:/base --entrypoint "conda" pacsifier:1.0.0 run -n pacsifier_minimal python get_pseudonyms.py ...

## Anonymizing Directly with PACSIFIER

### Command Line
   python anonymize_Dicoms.py --in_folder files-directory --out_folder anonymized-files-directory --new_ids my_new_ids.json --delete_identifiable --fuzz_acq_dates --remove_private_tags --keep_patient_dir_names

- `files-directory`: Path to the folder containing the DICOM images.
- `anonymized-files-directory`: Path where the anonymized DICOM images will be saved.
- `my_new_ids.json`: Maps real patient IDs on disk to anonymized codes (e.g., `{"sub-1234":"P0001", "sub-87262":"P0002"}`).
- `--delete_identifiable`: Removes identifiable files such as screen saves with embedded patient information.
- `--fuzz_acq_dates`: Randomly shifts acquisition-related dates for further anonymization.
- `--remove_private_tags`: Strips private DICOM tags that may contain identifiable information.
- `--keep_patient_dir_names`: Retains the original patient directory names instead of renaming them based on new IDs.

### Docker Command-Line
   ```bash
  docker run -it --rm -v /home/my_user/my_dir:/base --entrypoint "conda" pacsifier:1.0.0 run -n pacsifier_minimal python anonymize_Dicoms.py --in_folder /base/files-directory --out_folder /base/anonymized-files-directory --new_ids /base/my_new_ids.json --delete_identifiable --fuzz_acq_dates
   ```

Replace `...` with the same arguments as above.

### Important Notes
- If `anonymized-files-directory` is the same as `files-directory`, the original DICOM images will be replaced with anonymized versions (useful when storage space is limited).
- The `files-directory` must follow this structure:
  - **Subject Folders:** Names starting with `sub-` (e.g., `sub-123456`). The script will not work if folders do not follow this pattern.
  - **Session Folders:** Each subject folder should contain sessions starting with `ses-` (e.g., `ses-202201010101`). Files within sessions are anonymized.
  - **Anonymization Options:**
    - `--delete_identifiable` helps remove DICOM images with identifiable data embedded in image data (e.g., screen saves from certain CT machines).
    - `--fuzz_acq_dates` shifts acquisition dates randomly by ±30 days.
    - `--remove_private_tags` removes all private tags from DICOM images for extra security.

### Examples

#### Example 1
   ```bash
   python anonymize_Dicoms.py --in_folder ~/data --out_folder ~/anonymized_data --fuzz_acq_dates --remove_private_tags
   ```

This command anonymizes DICOM files from the `data` folder and saves them into `anonymized_data`, applying date fuzzing and removing private tags.

#### Example 2
   ```bash
   python anonymize_Dicoms.py --in_folder ~/data --out_folder ~/data --delete_identifiable
   ```

This will replace the images within the `data` folder with anonymized versions, removing identifiable images.

#### Example 3
   ```bash
   python anonymize_Dicoms.py --in_folder ~/data --out_folder ~/anonymized_data --keep_patient_dir_names --new_ids my_new_ids.json
   ```

Running this command will anonymize the DICOM files, retain original patient directory names, and use the new IDs provided in `my_new_ids.json`.

## Anonymizing via the Karnak Gateway

### Docker Command-Line
   ```bash
   docker run -it --rm -v /home/my_user/my_dir:/base --entrypoint "conda" pacsifier:1.0.0 run -n pacsifier_minimal python add_Karnak_tags.py --new_ids /base/my_new_ids.json --day_shift /base/day_shift.json --album_name my_album_name
   ```

- `my_new_ids.json`: Maps real patient IDs to anonymized codes, using the same format as direct anonymization.
- `day_shift.json`: Maps patient IDs to a chosen day shift. Optional (e.g., `{"sub-1234":"-1", "sub-87262":"35"}`).
- `my_album_name`: Should match a Kheops album name.

### Important Notes 
 - If the anonymized-files-directory is the same as the files-directory the raw dicom images will be deleted and replaced by the anonymized ones (This proved useful when there was no more storage space left for additional images ).
 - The files-directory must contain the following structure : 
 	- The files-directory must contain subject folders with names that start with sub- (e.g. sub-123456). In any other case, the script will run but won't affect the data in any way.
 	- A subject folder must contain session folders with names that start with ses- (e.g. ses-20150423110533). In any other case, the script will run but won't have any effect on the dicom images.
 	- A session folder must contain other folders which contain only the dicom images to be anonymized. If the folders within the session folder contain another kind of file the program will crash. The session folder however, can contain any other files (not folders) and it won't affect the program.
 - The anonymized-files-directory must exist on the computer.
 - The `--delete_identifiable` or `-i` option will *delete* files that have patient identifiers embedded in image data. This is the case for example for screen saves coming from the GE Revolution CT machine, which have the patient name embedded.  This uses the `ImageType` attribute and looks for 'SCREEN SAVE'.

### Examples

#### Example 1 
   ```bash
	python anonymize_Dicoms.py --in_folder ~/data --out_folder ~/anonymized_data
   ```

 Running this command will anonymize the dicom files within the data folder and save them into anonymized_data folder.

#### Example 2
   ```bash
	python anonymize_Dicoms.py --in_folder ~/data --out_folder ~/data
   ```

Runnning the command above will replace all the images within data folder with anonymized ones.

#### Example 3
   ```bash 
	python anonymize_Dicoms.py --in_folder ~/data --out_folder ~/anonymized_data --delete_identifiable
   ```

 Running this command will anonymize the dicom files within the data folder and save them into anonymized_data folder, and delete any identifiable images.

## Anonymizing via the Karnak gateway

```bash
docker run -it --rm -v /home/my_user/my_dir:/base --entrypoint "conda" pacsifier:1.0.0 run -n pacsifier_minimal python add_Karnak_tags.py --new_ids /base/my_new_ids.json --day_shift /base/day_shift.json --album_name my_album_name
  ```

 - `my_new_ids.json` maps on-disk real patient IDs to a chosen anonymisation code, same syntax as for direct PACSIFIER anonymisation. Example contents: `{'sub-1234':'P0001', 'sub-87262':'P0002'}`
 - `day_shift.json` maps on-disk real patient IDs to a chosen day shift, similar syntax as for direct PACSIFIER anonymisation. It is an optional parameter. Example contents: `{'sub-1234':'-1', 'sub-87262':'35'}`
 - `my_album_name` must match a Kheops album name

# Move dumps 

If pacsifier is called with the option --info or -i it will store csv files containing information about each series. <br> Move dumps is useful for moving these csv files into a new folder for complete anonymization of the data folder content.

## Command line
```bash
python move_dumps.py --data_folder ~/path-to-folder-containing-dicom-files --info_folder ~/path-to-new-folder
```

- data_folder takes the path to the dicom folder. 
- info_folder takes the path to the folder where the csv files will be moved.

## Notes : 
 - The path passed to --info_folder must exist, otherwise the program will crash.
 - If the csv files are not at the same level as the series folders, the script won't have any effect.


# Create DICOMDIR 

The create_DICOMDIR script creates a copy of the dicom directory passed as parameter changing the names of folders and images to 8 character alpha numeric names and creates a DICOMDIR file of this newly created directory.

## Command line
```bash
python create_DICOMDIR.py --in_folder ~/path-to-dicom-folder --out_folder ~/out-path
```

- in_folder takes the path to the dicom folder.
- out_folder takes the path where the renamed dicoms and the DICOMDIR will be stored.

## Notes 

- The path passed to out_folder must exist.
- Make sure to have enough storage space for the new dicom directory.
