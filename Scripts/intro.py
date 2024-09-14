## tool
██████╗  ██████╗ ██████╗ ███╗   ██╗████████╗
██╔══██╗██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝
██████╔╝██║     ██║   ██║██╔██╗ ██║   ██║   
██╔═══╝ ██║     ██║   ██║██║╚██╗██║   ██║   
██║     ╚██████╗╚██████╔╝██║ ╚████║   ██║   
╚═╝      ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   
                                            
                                            
                                            
                                            
                                            
                                            
                                            

####



   ___                                 ___         __                     __    _                  ______             __
  / _ \  ____ ___  __ __  __ __       / _ | __ __ / /_ ___   __ _  ___ _ / /_  (_) ___   ___      /_  __/ ___  ___   / /
 / ___/ / __// _ \ \ \ / / // /      / __ |/ // // __// _ \ /  ' \/ _ `// __/ / / / _ \ / _ \      / /   / _ \/ _ \ / / 
/_/    /_/   \___//_\_\  \_, /      /_/ |_|\_,_/ \__/ \___//_/_/_/\_,_/ \__/ /_/  \___//_//_/     /_/    \___/\___//_/  
                        /___/                                                                                           


###

   ___           ___   _  ______  ___  ___   __ _____  ___ ___
  / _ )__ __    / _ | / |/ / __ \/ _ \/ _ | / //_/ _ \/ _ <  /
 / _  / // /   / __ |/    / /_/ / , _/ __ |/ ,< / // / // / / 
/____/\_, /   /_/ |_/_/|_/\____/_/|_/_/ |_/_/|_|\___/\___/_/  
     /___/                                                    ###



###


import pyfiglet

def print_art():
    # Define the text for each section
    tool_text = "PConT"
    header_text = "Proxy Automation Tool"
    footer_text = "By Anorak"

    # Create ASCII art using the specified fonts
    tool_art = pyfiglet.figlet_format(tool_text, font="3d")
    header_art = pyfiglet.figlet_format(header_text, font="slant")
    footer_art = pyfiglet.figlet_format(footer_text, font="slant")

    # Print the ASCII art
    print(tool_art)
    print(header_art)
    print(footer_art)

# Call the function to print the art
print_art()


###
