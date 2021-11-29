PACSMAN is a batch query/retrieve interface for the CareStream PACS at Lausanne University Hospital.

It is implemented as a Python application running on Ubuntu Linux, relying on the DCMTK suite of tools. A Docker image is available.


NOTE: This readme has not been updated in a little while. It's mostly correct but win7 is not supported anymore since too painful to install. Linux is recommended.

# Building and testing


## Building the pacsman Docker image from the repo

    cd /path/to/PACSMAN/; docker build --network=host -t pacsman .

## Running the test suite 

    cd /path/to/PACSMAN/; docker build --network=host -t pacsman .


# Deployment

## From a Docker image

### Deploying from the gitlab Docker registry

Login to the registry with `docker login registry.gitlab.com`

Pull and run the image with `docker run registry.gitlab.com/jonasrichiardi/pacsman/pacsman`

You should see the help message from PACSMAN.

### Deploying from a local image

First load the docker image (`pacsman.tar`) from the distribution server or storage media where it's located into the local docker install on your computer.

#### Linux

    docker load -i /path/to/image/pacsman.tar

#### Windows 10

TODO

#### Windows 7 (Deprecated)

Start the `Docker Quickstart Terminal`, then `cd /path/to/image/`, then `docker load -i pacsman.tar`




## From source (deprecated)

### Ubuntu Linux

1. Install dcmtk `sudo apt-get install -y dcmtk`
2. Download and install miniconda: `wget -c http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh`, then `chmod +x Miniconda-latest-Linux-x86_64.sh`
3. Download the code using command `git clone https://gitlab.com/jonasrichiardi/PACSMAN`
4. Setup the environment and install heudiconv by running `bash ./utils/create_miniconda3_environment.sh` and then `bash ./utils/installation_python_modules.sh` .
5. Create the configuration file as described below.
6. Verify the installation works by running this test: `XXX_TEST_WITH_EXAMPLE_CSV_HERE`

FIXME: environment spec file is not the same on linux as on Windows.
FIXME: update doc to use conda env

### Windows 7 (deprecated)

#### Installation

Requirements: 
- git <https://git-scm.com/download/win>
- Chocolatey <https://chocolatey.org/>
- Miniconda <https://conda.io>
- Powershell (installed by default since win7 SP1)

This is more annoying than the Linux install.

1. Download and install the chocolatey package manager <https://chocolatey.org/>
2. Take a new `command prompt in admin mode and install dcmtk: `choco install dcmtk`
3. Check installation succeeded by taking a new command prompt and typing `echoscu`
4. Download and install miniconda from <https://conda.io>
5. Download the pacsman code using command `git clone https://gitlab.com/jonasrichiardi/PACSMAN`
6. Using `cmd.exe` in admin mode: Setup the python environment 
	- Run a command prompt as admin (start menu - right click on Command Prompt - Run as administrator)
	- Activate the base conda environment: `D:\path\to\miniconda\Scripts\activate.bat d:\path\to\miniconda`
	- Create the environment: `conda env create -n pacsman_minimal -f /path/to/PACSMAN/deployment/utils/environment_minimal.yml`
	- Note: This is messy but using `Anaconda Prompt` may get you a `NotWriteableError: The current user does not have write
permissions to a required path`,
7. Using `Anaconda prompt`: install support to run conda in PowerShell (<https://github.com/BCSharp/PSCondaEnvs>), because that's where chocolatey makes dcmtk available
	- Running `Anaconda Prompt`: `conda install -n root -c pscondaenvs pscondaenvs`. This will create scripts `activate.ps1` and `deactivate.ps1` in `D:\path\to\miniconda\Scripts\`
	- There are other options which we have not tested, see e.g. 
		- <https://github.com/pldmgg/misc-powershell/tree/master/MyModules/AnacondaEnv> and <https://gist.github.com/pldmgg/c84e802bcecd6e4c962f65be5b5d316d>
		- <https://github.com/Liquidmantis/PSCondaEnvs>
8. Using `Powershell` in admin mode we enable these cmdlets:
	- Run `Powershell` as admin (right-click - run as admin) and `Set-ExecutionPolicy RemoteSigned`
9. Create the PACS client/server configuration file as described below.  




# Usage

## Using Docker

To keep things simple, chose a directory (e.g. `my_dir`) that will store the query file (e.g. `my_query.csv`) and configuration file (e.g. `my_config.json`). Create a sub-directory (say `my_output_dir`) to store the DICOM files into.

To make this directory accessible within the Docker container, you need to `bind mount` it as a docker volume to a specific location in the container by using the `-v` flag. In the examples below, we bind mount the host computer's directory into the `/base` volume within Docker. Then within the PACSMAN options (which runs *within* the container), paths for the config file and query files will be relative to that docker volume.

This docker image's entrypoint is `pacsman.py`.

### Linux 

    docker run --net=host -it --rm -v ~/my_dir/.:/base registry.gitlab.com/jonasrichiardi/pacsman/pacsman --save --info  --queryfile /base/my_query.csv --config /base/my_config.json --out_directory /base/my_output_dir

### Windows 10 
	
You need to give Docker permission to access your chosen directory `my_dir`. To do this, right-click onto Docker in your taskbar > Settings > File sharing.
Then add permission for `my_dir`. 

    docker run -p my_move_port -it --rm -v c:\Users\my_user\my_dir:/base registry.gitlab.com/jonasrichiardi/pacsman/pacsman --save --info  --queryfile /base/my_query.csv --config /base/my_config.json --out_directory /base/my_output_dir

Where `my_move_port` should be replaced by the same value as you have in the config file `move_port`.


## From source

### Windows 7 (deprecated)

1. Using `Powershell` in normal mode we can now run pacsman
	- Run `Powershell`, cd to `D:\path\to\miniconda\Scripts\`, then `.\activate pacsman_minimal`. We can probably to better in terms of adding the cmdlet to the path.
2. Verify the installation works by running this test: (TODO `XXX_TEST_WITH_EXAMPLE_CSV_HERE`)

### Windows 10 (deprecated)

TODO

### Linux 

Activate your conda environment. 

TODO syntax

See the section `Running queries`

# Running queries 

## Command line

	python pacsman.py --info --save --queryfile path_to_queryfile --config path_to_config_file --out_directory path_to_out_directory

 - The --info or -i option allows you to dump the information in the retrieved series (`findscu` output) into csv files.
 - The --save or -s option allows you to save the queryed dicom images to disk. Cannot be used with --move.
 - The --move or -m option allows you to C-MOVE the queryed dicom images to another DICOM node specified in the config file. Cannot be used with --save.
 - The --queryfile or -q path_to_queryfile option is mandatory and specifies which queryfile to use to query/retrieve.
 - The --config or -c path_to_config_file option is mandatory and specifies the config file to use for the query/retrieve.
 - The --out_directory or -d path_to_out_directory is optional and specifies the path to the folder where the info dumps and the dicom images will be stored.

Note : you can download the images without the --info option or only dump the info if --save option is not included.


 - Running the command above will download the dicom images by default into data folder of the project folder. 
 - You can specify the output directory by adding the option --out_directory or -d path_to_output_directory.
 - You can also specify a different config file by adding the option --config or -c path_to_config_file.


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
- `server_ip`: PACS server IP address
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

	StudyDate,patientID
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

### Command line 
	python get_pseudonyms.py --config my_config_deid.json --queryfile my_query.csv --project_name my_project_name --out_directory ./

 - `my_config_deid.json` is the configuration file for the de-ID API, containing token and service URL.
 - `my_query.csv` is the PACSMAN query file, listing all PatientIDs to pseudonymise
 - `my_project_name` Corresponds both to the project name on GPCR and may correspond to the album name on Kheops where the study will be pushed

After running, the output directory will contain a file `new_ids_[my_project_name].json` which can be used directly with
anonymisation process below

### Docker command-line (Windows)

	docker run -it --rm -v c:\Users\my_user\my_dir:/base --entrypoint "conda" registry.gitlab.com/jonasrichiardi/pacsman/pacsman run -n pacsman_minimal python get_pseudonyms.py ...

## Anonymizing directly with PACSMAN

### Command line 
	python anonymize_Dicoms.py --in_folder files-directory --out_folder anonymized-files-directory --new_ids my_new_ids.json --delete_identifiable --fuzz_acq_dates
 
 - `files-directory` is the path to the folder that contains all the dicom images.
 - `anonymized-files-directory` is the path to the directory where the anonymized dicom images will be saved.
 - `my_new_ids.json` maps on-disk real patient IDs to a chosen anonymisation code. Example contents: `{'sub-1234':'P0001', 'sub-87262':'P0002'}`
 - `--delete_identifiable` - remove identifiable files (see below)
 - `--fuzz_acq_dates` - shifts acquisition dates by a random amount, synchronised with birth date fuzzing. Returns a file 'date_offsets.csv'.

### Docker command-line (Windows)
	docker run -it --rm -v c:\Users\my_user\my_dir:/base --entrypoint "conda" registry.gitlab.com/jonasrichiardi/pacsman/pacsman run -n pacsman_minimal python anonymize_Dicoms.py ...

where `...` refers to the same argument as above

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
	python anonymize_Dicoms.py --in_folder ~/data --out_folder ~/anonymized_data

 Running this command will anonymize the dicom files within the data folder and save them into anonymized_data folder.

#### Example 2 
	python anonymize_Dicoms.py --in_folder ~/data --out_folder ~/data 

Runnning the command above will replace all the images within data folder with anonymized ones.

#### Example 3 
	python anonymize_Dicoms.py --in_folder ~/data --out_folder ~/anonymized_data --delete_identifiable 

 Running this command will anonymize the dicom files within the data folder and save them into anonymized_data folder, and delete any identifiable images.

## Anonymizing via the Karnak gateway

### Docker command-line (Windows)
	docker run -it --rm -v c:\Users\my_user\my_dir:/base --entrypoint "conda" registry.gitlab.com/jonasrichiardi/pacsman/pacsman run -n pacsman_minimal python add_Karnak_tags.py --new_ids my_new_ids.json --album_name my_album_name

 - `my_new_ids.json` maps on-disk real patient IDs to a chosen anonymisation code, same syntax as for direct PACSMAN anonymisation. Example contents: `{'sub-1234':'P0001', 'sub-87262':'P0002'}`
 - `my_album_name` must match a Kheops album name



# Converting to NIFTI 

## Command line

	python convert.py path_to_data_folder 

path_to_data_folder is the path to the data to be converted to nifti format. The structure of the data should be exactly the same way as for the anonymization.


# Move dumps 

If pacsman is called with the option --info or -i it will store csv files containing information about each series. <br> Move dumps is useful for moving these csv files into a new folder for complete anonymization of the data folder content.

## Command line

	python move_dumps.py --data_folder ~/path-to-folder-containing-dicom-files --info_folder ~/path-to-new-folder

- data_folder takes the path to the dicom folder. 
- info_folder takes the path to the folder where the csv files will be moved.
## Notes : 
 - The path passed to --info_folder must exist, otherwise the program will crash.
 - If the csv files are not at the same level as the series folders, the script won't have any effect.


# Create DICOMDIR 

The create_DICOMDIR script creates a copy of the dicom directory passed as parameter changing the names of folders and images to 8 character alpha numeric names and creates a DICOMDIR file of this newly created directory.

## Command line

	python create_DICOMDIR.py --in_folder ~/path-to-dicom-folder --out_folder ~/out-path

- in_folder takes the path to the dicom folder.
- out_folder takes the path where the renamed dicoms and the DICOMDIR will be stored.

## Notes 

- The path passed to out_folder must exist.
- Make sure to have enough storage space for the new dicom directory.
