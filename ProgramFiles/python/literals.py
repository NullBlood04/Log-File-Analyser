application_list = [
    ".NET Runtime",
    ".NET Runtime Optimization Service",
    "Application Error",
    "Application Hang",
    "brave",
    "Brave-Browser",
    "bravem",
    "CertEnroll",
    "Edge",
    "edgeupdate",
    "ESENT",
    "EventSystem",
    "igcc",
    "IntelDalJhi",
    "Microsoft-Windows-AppModel-State",
    "Microsoft-Windows-AppXDeploymentServer/Operational",
    "Microsoft-Windows-CAPI2",
    "Microsoft-Windows-Defrag",
    "Microsoft-Windows-Perflib",
    "Microsoft-Windows-RestartManager",
    "Microsoft-Windows-User Profiles Service",
    "Microsoft-Windows-WMI",
    "MSI Service",
    "MsiInstaller",
    "NortonSecurity",
    "NVIDIA app SelfUpdate Source",
    "OneDriveUpdaterService",
    "ProtonVPNService",
    "RtkAudioUniversalService",
    "SecurityCenter",
    "Service1",
    "Software Protection Platform Service",
    "VSS",
    "Windows Error Reporting",
    "Windows Search Service",
    "Wlclntfy",
    "WMIRegistrationService"
]


markdown_css = """
<style>
    .title {
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        color: #BB86FC;
        margin-bottom: 1em;
    }

    div[data-baseweb="select"] {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
        border-radius: 10px;
    }

    div[data-baseweb="popover"] {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
    }

    div[data-baseweb="option"] {
        color: white !important;
        background-color: #2d2d2d !important;
    }

    div[data-baseweb="option"]:hover {
        background-color: #4a4a4a !important;
        color: #00ffcc !important;
    }

    .card {
        background-color: #090214;
        padding: 1.5em;
        height: 10em;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(0,0,0,0.3);
        border: 1px solid #2C2C2C;
        transition: all 0.3s ease-in-out;
    }
    
    .result-content {
        width: 360px;
        height: 390px;
        padding: 1em;
        overflow-y: auto;
        background-color: #090214;
        color: #cccccc;
        border-radius: 10px;
        border: 1px solid #333;
    }
                
    .card:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(186, 144, 252, 0.2);
    }
    .card-title {
        font-size: 1.5em;
        font-weight: 600;
        color: #BB86FC;
        margin-bottom: 0.5em;
    }
    .card-body {
        font-size: 1em;
        color: #c7c7c7;
        margin-bottom: 1em;
        width: inherit;
        height: 6em;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .stButton>button {
        width: 100%;
        background-color: #BB86FC;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6em 1em;
        font-size: 0.95em;
        transition: 0.2s ease;
        margin-top: -1em;
    }
    .stButton>button:hover {
        background-color: #a878e3;
    }
</style>
"""