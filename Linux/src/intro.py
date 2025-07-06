def print_art():
    # Define the color codes
    hacker_green = "\033[92m"  # Bright green
    reset_color = "\033[0m"    # Reset to default color

    tool_art = f"""
{hacker_green}██████╗  ██████╗ ██████╗ ███╗   ██╗████████╗
██╔══██╗██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝
██████╔╝██║     ██║   ██║██╔██╗ ██║   ██║   
██╔═══╝ ██║     ██║   ██║██║╚██╗██║   ██║   
██║     ╚██████╗╚██████╔╝██║ ╚████║   ██║   
╚═╝      ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   
{reset_color}
"""


    # Print the ASCII art
    print(tool_art)
    

# Call the function to print the art
print_art()


def print_bold_text():
    # Define the color codes and formatting
    hacker_green = "\033[92m"  # Bright green
    bold_text = "\033[1m"     # Bold text
    reset_color = "\033[0m"   # Reset to default color

    # Define the text for each section
   
    header_text = "Proxy Automation Tool"
    footer_text = "By Anorak001"

    # Print the bold text with color
    
    print(f"{hacker_green}{bold_text}{header_text}{reset_color}")
    print(f"{hacker_green}{bold_text}{footer_text}{reset_color}")

# Call the function to print the text
print_bold_text()

