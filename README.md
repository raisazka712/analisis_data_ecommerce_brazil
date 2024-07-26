## Setup Environment - Anaconda
conda create --name main-ds Python 3.11.5
conda activate main-ds
pip install -r requirements.txt

## Setup Environment - Shell/Terminal
mkdir submission_analisis_data
cd submission_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt

## Run steamlit app
streamlit run dashboard.py