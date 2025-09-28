# CV Optimizer based on OpenAI

Welcome to the **CV Optimizer** project! This application provides a platform for optimizing CVs for a provided role description using OpenAI.

---

## **Getting Started**

Follow these steps to set up and run the project:

### **Prerequisites**

1. **Install Python**  
   Download and install the latest version of Python from [python.org](https://www.python.org/downloads/). Ensure it's properly added to your system PATH.

2. **Install Visual Studio Code**  
   Download and install [Visual Studio Code](https://code.visualstudio.com/).

3. **Open a New Folder**  
   In VSC, go to File → Open Folder.  
   Choose or create a new folder (e.g., cv-optimizer).

4. **Validate Python installed**  
   Open the terminal in VSC (Terminal → New Terminal).  
   Run the following command to confirm Python is installed:
      ```bash
      python --version
      ```
---

### **Installation Steps**

1. **Set up Python Environment**    
   - Create a Python environment by running:        
      ```bash
      python -m venv cvopt-env
      ```
   This creates a folder *cvopt-env* inside your project.

   - Activate the environment:
        - **Windows**: `cvopt-env\Scripts\activate`
        - **Mac/Linux**: `source cvopt-env/bin/activate`

   You’ll see *(cvopt-env)* in your terminal — that means it’s active.

2. **Navigate to Project Directory**  
   Move to the folder where `requirements.txt` is located:
   ```bash
   cd path/to/your/project
   ```

3. **Install Project Dependencies**  
   Use the following command to install all the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**  
   Start the Flask application by running:
   ```bash
   python app.py
   ```

5. **Open in Browser**  
   Open your web browser and navigate to:
   ```
   http://127.0.0.1:10000
   ```

---