from blessed import Terminal

term = Terminal()
# This was generated using toilet
def show_header(sub_header=None):
    print(term.clear())
    header = """
      ▄▄▄▄    ▄                         ▀▀█           ▄▄▄▄▄▄       
     █▀   ▀   █     ▄▄▄▄  ▄ ▄▄    ▄▄▄     █    ▄   ▄      █▀  ▄▄▄  
     ▀█▄▄▄    █    █▀ ▀█  █▀  █  ▀   █    █    ▀▄ ▄▀    ▄█   █▀  █ 
         ▀█   ▀    █   █  █   █  ▄▀▀▀█    █     █▄█    ▄▀    █▀▀▀▀ 
     ▀▄▄▄█▀   █    ▀█▄▀█  █   █  ▀▄▄▀█    ▀▄▄   ▀█    ██▄▄▄▄ ▀█▄▄▀ 
                    ▄  █                        ▄▀                 
                     ▀▀                        ▀▀                  
                     ▀▀                        ▀▀
        Copyrights 2019 BisonCorps\n
        https://github.com/bisoncorps/signalum\n\n
        """
    
    if sub_header:
        header += f"""

        TABLE: {sub_header}
        """
    print(header)
                

def get_logo():
    return ("""
  ▄▄▄▄    ▄                         ▀▀█           ▄▄▄▄▄▄       
 █▀   ▀   █     ▄▄▄▄  ▄ ▄▄    ▄▄▄     █    ▄   ▄      █▀  ▄▄▄  
 ▀█▄▄▄    █    █▀ ▀█  █▀  █  ▀   █    █    ▀▄ ▄▀    ▄█   █▀  █ 
     ▀█   ▀    █   █  █   █  ▄▀▀▀█    █     █▄█    ▄▀    █▀▀▀▀ 
 ▀▄▄▄█▀   █    ▀█▄▀█  █   █  ▀▄▄▀█    ▀▄▄   ▀█    ██▄▄▄▄ ▀█▄▄▀ 
                ▄  █                        ▄▀                 
                 ▀▀                        ▀▀                  
                 ▀▀                        ▀▀
    Copyrights 2019 BisonCorps\n
    https://github.com/bisoncorps/signalum\n\n
    """)

MAJOR_CLASSES = {
    "00000": "Miscellanous",
    "00001": "Computer",
    "00010": "Phone",
    "00011": "LAN/Network Access Point",
    "00100": "Audio/Video",
    "00101": "Peripheral",
    "00110": "Imaging",
    "00111": "Wearable",
    "01000": "Toy",
    "01001": "Health",
    "11111": "Device code not specified",
    
}

MINOR_CLASSES = {

    "Computer": {
        "000000": "Uncategorized",
        "000001": "Desktop Workstation",
        "000010": "Server-class computer",
        "000011": "Laptop",
        "000100": "Handheld PC/PDA",
        "000101": "Palm-size PC/PDA",
        "000110": "Wearable computer (watch size)",
        "000111": "Tablet",
    },

    "Phone": {
        "000000": "Uncategorized",
        "000001": "Cellular",
        "000010": "Cordless",
        "000011": "Smartphone",
        "000100": "Wired modem or voice gateway",
        "000101": "Common ISDN access",
    },

    "LAN/Network Access Point": {
        "000": "Fully Available",
        "001": "1 to 17% utilized",
        "010": "17 to 33% utilized",
        "011": "33 to 50% utilized",
        "100": "50 to 67% utilized",
        "101": "67 to 83% utilized",
        "110": "83 to 99% utilized",
        "111": "No service available",
    },

    "Audio/Video": {
        "000000": "Uncategorized",
        "000001": "Wearable Headset Device",
        "000010": "Hands-free device",
        "000011": "(reserved)",
        "000100": "Microphone",
        "000101": "Loudspeaker",
        "000110": "Headphones",
        "000111": "Portable Audio",  
        "001000": "Car Audio",  
        "001001": "Set-top box",  
        "001010": "Hifi Audio Device",  
        "001011": "VCR",  
        "001100": "Video camera",
        "001101": "Camcoder",  
        "001110": "Video Monitor",  
        "001111": "Video Display and Loudspeaker",  
        "010000": "Video Conferencing",  
        "010001": "(reserved)",  
        "010010": "Gaming/Toy",  
    },

    "Peripheral": {
        "00": "Not Keyboard/Pointing Device",        
        "01": "Keyboard",        
        "10": "Pointing Device",        
        "11": "Combo keyboard/pointing device",        
    },

    "Imaging": {
        "0001": "Display",        
        "0010": "Camera",        
        "0100": "Scanner",        
        "1000": "Printer",        
    },

    "Wearable": {
        "000001": "Wristwatch",
        "000010": "Pager",
        "000011": "Jacket",
        "000100": "Helmet",
        "000101": "Glasses",  
    },

    "Toy": {
        "000001": "Robot",
        "000010": "Vehicle",
        "000011": "Doll/Action Figure",
        "000100": "Controller",
        "000101": "Game",  
    },

    "Health": {
        "000000": "Uncategorized",
        "000001": "Blood Pressure Meter",
        "000010": "Thermometer",
        "000011": "Weighing scale",
        "000100": "Glucose meter",
        "000101": "Pulse Oximeter",
        "000110": "Heart/Pulse rate monitor",
        "000111": "Health Data display",  
        "001000": "Step counter",  
        "001001": "Body Composition Analyzer",  
        "001010": "Peak Flow monitor",  
        "001011": "Medication monitor",  
        "001100": "Knee Prosthesis",
        "001101": "Ankle Prosthesis",  
        "001110": "Generic Health Manager",  
        "001111": "Personal Mobility device",  
    }, 

    "XXXX": {},          
}

SERVICES = {
 '13': "Limited Discoverable Mode",
 '16': "Positioning",   
 '17': "Networking",   
 '18': "Rendering",   
 '19': "Capturing",   
 '20': "Object Transfer",   
 '21': "Audio",   
 '22': "Telephony",   
 '23': "Information",   
}
