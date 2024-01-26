# EngageTrack backend

Backend of prototype tool to analyze student engagement and predict student results using OULAD dataset(Kuzilek J., Hlosta M., Zdrahal Z. Open University Learning Analytics dataset Sci. Data 4:170171 doi: 10.1038/sdata.2017.171 (2017)).
Frontend available here: https://github.com/Timorun/EngFrontend/

## Getting Started

To get a local copy up and running follow these simple steps in combination with the frontend.

### Prerequisites

1. Install the necessary software to use:

[//]: # (- python 3.11.x)
- python 3.11.x
  https://www.python.org/downloads/release/python-3117/
  check version
  ```sh
    python --version
  ```

### Installation

1. Clone the repo
   ```sh
   git clone git@github.com:Timorun/EngBackend.git
   ```
   And visit the created directory
   ```sh
   cd .\EngBackend\
   ```
2. Create a virtual environment
   ```sh
   python -m venv env
   ```
   And activate the virtual environment
   - Windows:
    ```sh
    .\env\Scripts\activate
    ```
   - macOS/Linux:
    ```sh
    source env/bin/activate
    ```
3. Install Python packages
   ```sh
   pip install -r requirements.txt
   ```

### Running

1. Make sure you are in the virtual environment (env). Otherwise, activate the virtual environment
   - Windows:
    ```sh
    .\env\Scripts\activate
    ```
   - macOS/Linux:
    ```sh
    source env/bin/activate
    ```
2. Set the FLASK_APP environment variable
    - Windows:
    ```sh
    set FLASK_APP=engagetrack.py
    ```
    - macOS/Linux:
    ```sh
    export FLASK_APP=engagetrack.py
    ```
3. Run the application
    ```sh
   flask run
   ```

## License
This project is licensed under the MIT License - see the LICENSE.txt file for details.