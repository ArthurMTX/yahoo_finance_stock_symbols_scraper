# Yahoo Finance Symbols Retriever

This script retrieves all the ticker symbols available on Yahoo Finance and stores them in a file for further processing. Currently, only the ticker symbols are retrieved. The approach is brute force and may take several hours to complete although it is optimized to run concurrently (took 20mins on my machine).

## Features

- **Comprehensive Retrieval:** Uses multiple search queries to cover all possible symbols.
- **Brute Force Approach:** Iterates through combinations of letters and numbers to retrieve symbols.
- **Logging:** Provides detailed logs of the script's progress and any errors encountered.
- **Output File:** Stores the retrieved symbols in a file for subsequent processing.

## Requirements

- **Python 3.x**
- **Libraries:** 
  - `requests`
  - Standard libraries: `logging`, `time`, `threading`, `concurrent.futures`

If you encounter an error due to missing libraries, install them using pip. For example:

```bash
pip install requests
```

## Running the Script

To execute the script, simply run:

```bash
python yh_get_all_sym.py
```
Ensure you run this command in the same directory where the script is located.

## Output

- Symbols File: The ticker symbols are stored in a file named `yh_all_symbols.txt`.
    - The file contains the symbols in the form of a Python set (e.g., 
    ```json
    {
        "AA": "Alcoa Corporation",
        "AAPL": "Apple Inc.",
        "AAL": "American Airlines Group, Inc.",
        "AAOI": "Applied Optoelectronics, Inc.",
        "AABB": "Asia Broadband, Inc.",
    }
    ```
    - It is located in the same folder from which the script is executed.
    - The output file size is approximately 27 MB.
- Console Messages: Real-time progress is shown in the console during script execution.
- Log File: A log file (``yh_get_all_sym.log``) is generated containing detailed information and console messages.

