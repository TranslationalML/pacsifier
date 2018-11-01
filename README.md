PACSMAN is a batch query/retrieve interface for the CareStream PACS at Lausanne University Hospital.

# Deployment

PACSMAN is a Python application running on Ubuntu Linux, relying on the DCMTK suite of tools.

## From source

### Ubuntu Linux

1. Install dcmtk `sudo apt-get install -y dcmtk`
2. Download and install miniconda: `wget -c http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh`, then `chmod +x Miniconda-latest-Linux-x86_64.sh`
3. Download the code using command `git clone https://gitlab.com/jonasrichiardi/PACSMAN`
4. Setup the environment and install heudiconv by running `bash ./utils/create_miniconda3_environment.sh` and then `bash ./utils/installation_python_modules.sh` .
5. Create the configuration file as described below.
6. Verify the installation works by running this test: `XXX_TEST_WITH_EXAMPLE_CSV_HERE`

### Windows 7

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
	- Create the environment: `conda env create -n pacsman_minimal -f /path/to/PACSMAN/files/environment_minimal.yml`
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


#### Usage

1. Using `Powershell` in normal mode we can now run pacsman
	- Run `Powershell`, cd to `D:\path\to\miniconda\Scripts\`, then `.\activate pacsman_minimal`. We can probably to better in terms of adding the cmdlet to the path.
2. Verify the installation works by running this test: `XXX_TEST_WITH_EXAMPLE_CSV_HERE`

## Using Docker

    docker run --net=host -it --rm -v  ~/.:/base pacsmanlite:latest --save save --info info --queryfile /base/my_query.csv --config /base/my_config.json --out_directory /base/my_output_dir

### Building the pacsman image

    cd /path/to/PACSMAN/; docker build --network=host -t pacsmanlite .

### Deploying from a local image

First load the docker image into the local docker install.

#### Linux

    docker load -i /path/to/image/pacsmanlite.tar

#### Windows 7

Start the `Docker Quickstart Terminal`, then `cd /path/to/image/`, then `docker load -i pacsmanlite.tar`

### Deploying from dockerhub

An image is also on the dockerhub at  `benothma/pacsman:latest`

## Config file 

The config file is a json file that should include the keys : 
- `server_ip`: PACS server IP address
- `port`: PACS server port number 
- `server_AET`: PACS server application entity title
- `AET`: current station application entity title
- `move_port`: port number to use on the current station to receive images (C-MOVE destination)

The AET and corresponding IP of the workstation should be declared on Carestream, including the storeable attribute.

# Running queries 

## Command line

	python pacsman.py --info --save --queryfile path_to_queryfile

 - The --info option allows you to dump the information in the retrieved series into csv files.
 - The --save option allows you to save the queryed dicom images.
 - The --queryfile path_to_queryfile option is mandatory and specifies which queryfile to use to query/retrieve.

Note : you can download the images without the --info option or only dump the info if --save option is not included.

 - Running the command above will download the dicom images by default into data folder of the project folder. 
 - You can specify the output directory by adding the option --out_directory path_to_output_directory.
 - You can also specify a different config file by adding the option --config path_to_config_file.


## Query file: 

The query file is a `.csv` file that should include one or many of these column names : 
- StudyDate : The study dates of this column should be in the format YYYYMMDD (e.g 19900912 which indicates the 12th of September 1990). <br> Note : Querying on a date range is supported. (e.g 20150201-20160201 will query on studies between 01/02/2015 and 01/02/2016 ) 
- StudyTime : The study time should be in the format HHMMSS (e.g 140500 which means 14:05:00)
⁻ SeriesDecription : The series description.
- PatientID :  The patient ID 
- ProtocolName : The protocol names.
- StudyInstanceUID : The Study Instance UID.
- PatientName : The patient name. (It is not recommanded to use this filter since there is no clear norm on how the patient names were stored on the pacs server)
- PatientBirthDate : Similarily to the StudyDate the date should be in format YYYYMMDD. Querying on date range is not supported for patient birth date.
- SeriesInstanceUID : The Series Instance UID
- ImageType : The image type as stored in the pacs server. (Note : using this filter significantly slows down the querying process. Use it only if absolutely necessary.)
- Modality : The modality.

The query file can be built in Excel and exported to comma-separated values `.csv` format.


Notes : 
- The query file could include one or many of the columns mentioned above. 
- If a line in a csv file contains an empty string on a particular columns, then, the query will not include the attribute corresponding to the column in question.
- The querying does not accept the value `*` alone on any attribute. However it can be used as a wildcard 
if other characters are provided, e.g. `ProtocolName` could be set to `BEAT_SelfNav*`
- the Series folders are named after the Series Description of its images. However, it may happen that a dicom image has no SeriesDescription stored. In that case, the image will be stored within a folder called No_series_description.

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
	BEAT_SelfNav\*,CT,19920611

This csv file will retrieve all the images with ProtocolName starting with BEAT_SelfNav, Modality CT and of Patients whose birthdays are on  11th of June 1992.

# Anonymization 
## Command line 
	python anonymize.py files-directory anonymized-files-directory
 - files-directory is the path to the folder that contains all the dicom images.
 - anonymized-files-directory is the path to the directory where the anonymized dicom images will be saved.

## Important Notes 
 - If the anonymized-files-directory is the same as the files-directory the raw dicom images will be deleted and replaced by the anonymized ones (This proved useful when there was no more storage space left for additional images ).
 - The files-directory must contain the following structure : 
 	- The files-directory must contain subject folders with names that start with sub- (e.g. sub-123456). In any other case, the script will run but won't affect the data in any way.
 	- A subject folder must contain session folders with names that start with ses- (e.g. ses-20150423110533). In any other case, the script will run but won't have any effect on the dicom images.
 	- A session folder must contain other folders which contain only the dicom images to be anonymized. If the folders within the session folder contain another kind of file the program will crash. The session folder however, can contain any other files (not folders) and it won't affect the program.

 - The anonymized-files-directory must exist on the computer.

## Examples

### Example 1  
 	python anonymize.py ~/data ~/anonymized_data

 Running this command will anonymize the dicom files within the data folder and save them into anonymized_data folder.

### Example 2 
	python anonymize.py ~/data ~/data 

Runnning the command above will replace all the images within data folder with anonymized ones.

# Converting to NIFTI 

## Command line

	python converter.py path_to_data_folder 

path_to_data_folder is the path to the data to be converted to nifti format. The structure of the data should be exactly the same way as for the anonymization.
