README about resq_be andresq_ios(+connecting them)
resq_be (Django Backend):

"resq_be" is a Django-based backend for an emergency response application. It provides endpoints for starting an emergency call and sending "Yes" or "No" responses.

 Folder Structure

resq_be/
├── core/                    # Django app for core functionalities
│   ├── migrations/          # Database migration files
│   ├── templates/           # HTML templates
│   ├── static/              # Static files (e.g., CSS, JS)
│   ├── __init__.py          # Initializes the Django app
│   ├── admin.py             # Django admin configurations
│   ├── apps.py              # App configurations
│   ├── models.py            # Database models
│   ├── tests.py             # Test cases
│   ├── views.py             # View functions for handling requests
│   └── urls.py              # URL routing for the app
├── db.sqlite3               # SQLite database file
├── manage.py                # Django command-line utility
└── requirements.txt         # List of Python dependencies

![Uploading Screenshot 2024-10-09 at 8.15.47 PM.png…]()

 Prerequisites
- Python 3.x
- Django
- pip for Python package management

Setup Instructions
1. Clone the Repository:
  
   git clone <repository_url>
   cd resq_be
   

2. Create a Virtual Environment and Activate It

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate


3. Install Dependencies:

   pip install -r requirements.txt


4. Run Migrations:
   
   python manage.py migrate


5. Start the Development Server:
  
   python manage.py runserver


6. Access the Backend
   Open a web browser and go to  "http://127.0.0.1:8000"

 API Endpoints
- Start Emergency Call: "POST /start_call/"
- Send Yes/No Response:"POST /yes_no_response/<call_id>/"


Virtual environment:
venv/

Python cache files:
__pycache__/
Django database
db.sqlite3


 resq_ios (Xcode iOS App):

"resq_ios" is a Swift-based iOS app built with SwiftUI. It allows users to initiate emergency calls and send "Yes" or "No" responses. It integrates with the Django backend ("resq_be") to record and handle emergency situations.

 Folder Structure

resq_ios/
├── resq_ios/                # Main app folder
│   ├── ContentView.swift    # Main SwiftUI view for the app
│   ├── Assets/              # App assets (images, etc.)
│   ├── Info.plist           # App configuration file
│   └── resq_iosApp.swift    # App entry point
├── resq_iosTests/           # Unit test targets
├── resq_iosUITests/         # UI test targets
       
       
<img width="519" alt="Screenshot 2024-10-09 at 8 16 18 PM" src="https://github.com/user-attachments/assets/14929471-ac52-4819-8764-e5fb477b0a80">

Prerequisites:
- Xcode (latest version recommended)
- macOS

Setup Instructions:
1. Clone the Repository

   git clone <repository_url>
   cd resq_ios
   
2. Open the Project in Xcode:

   open resq_ios.xcodeproj
   
3. **Configure App Transport Security (if needed)**
   In Info.plist, add the following configuration if connecting to a non-secure backend:
xml
   <key>NSAppTransportSecurity</key>
   <dict>
       <key>NSAllowsArbitraryLoads</key>
       <true/>
   </dict>
   
4. Build and Run the App:
   - Choose a simulator or a connected device.
   - Click the "Run" button in Xcode or press "Cmd + R"

 Connecting resq_ios with resq_be
To connect the iOS app ("resq_ios") with the Django backend ("resq_be"):

1. Start the Django Server:
   Make sure "resq_be" is running on "http://127.0.0.1:8000"

2. Set Up the Base URL in the iOS App:
   In "NetworkManager.swift", ensure the "baseURL" points to the Django server:
swift
   private let baseURL = "http://127.0.0.1:8000"
   
3. Test API Calls:
   - Use the "Call 119" button to trigger the "startEmergencyCall" function.
   - Use the "Yes" and "No" buttons to trigger the "sendYesNoResponse" function.

!!!!Notes!!!!

- Ensure both the backend and iOS app are running simultaneously for testing.
- Use the correct IP address if testing on a physical device instead of the localhost.
