import subprocess
import os
import yaml

# Define the base path for Ansible playbooks and configuration files
ANSIBLE_PLAYBOOKS_PATH = os.getenv('ANSIBLE_PLAYBOOKS_PATH', '/Users/pawansi/workspace/CatC_Configs/dnac_ansible_workflows/workflows/')
CONFIG_FILES_BASE_PATH = os.getenv('CONFIG_FILES_BASE_PATH', '/Users/pawansi/workspace/CatC_Configs/CatalystCenter_Configurations/catc_configs/')
ANSIBLE_HOSTS_INVENTORY = os.getenv('ANSIBLE_HOSTS_INVENTORY', '/Users/pawansi/workspace/CatC_Configs/CatalystCenter_Configurations/ansible_inventory/catalystcenter_inventory_10.195.243.53')
ANSIBLE_LOG_DIR_PATH = os.getenv('ANSIBLE_LOG_DIR_PATH', '/Users/pawansi/workspace/CatC_Configs/ansible_logs/')
# Function to read usecase data from a YAML file
def read_usecase_data(yaml_file):
    """Reads use case data from the specified YAML file."""
    try:
        with open(yaml_file, 'r') as f:
            usecase_data = yaml.safe_load(f)
        return usecase_data
    except FileNotFoundError:
        print(f"Error: YAML file not found: {yaml_file}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None

def validate_schema(usecase_name, usecase_data):
    """Validates the data file against the schema for the given use case."""
    config_file = os.path.join(ANSIBLE_PLAYBOOKS_PATH, usecase_data[usecase_name]["schema_file"])
    data_file = os.path.join(CONFIG_FILES_BASE_PATH, usecase_data[usecase_name]["data_file"])
    
    try:
        subprocess.run(["yamale", "-s", config_file, data_file], check=True)
        print(f"Schema validation successful for {usecase_name}")
    except subprocess.CalledProcessError as e:
        print(f"Schema validation failed for {usecase_name}: {e}")

def execute_playbook(usecase_name, usecase_data):
    """Executes the Ansible playbook for the given use case."""
    playbook = os.path.join(ANSIBLE_PLAYBOOKS_PATH, usecase_data[usecase_name]["playbook"])
    data_file = os.path.join(CONFIG_FILES_BASE_PATH, usecase_data[usecase_name]["data_file"])
    ansible_log_path = os.path.join(ANSIBLE_LOG_DIR_PATH, f"{usecase_name}_ansible.log")

    try:
        cmd = [
            "ansible-playbook",
            "-i", ANSIBLE_HOSTS_INVENTORY,
            playbook,
            "--e", f"VARS_FILE_PATH={data_file}",
            "-vvvv"
        ]
        with open(ansible_log_path, 'w') as log_file:
            subprocess.run(cmd, check=True, stdout=log_file, stderr=subprocess.STDOUT)
        print(f"Playbook execution successful for {usecase_name}")
    except subprocess.CalledProcessError as e:
        print(f"Playbook execution failed for {usecase_name}: {e}")

def main():
    """Main function to handle user input and execute actions."""
    # Get the YAML file path from the user
    usecase_maps_dir = "usecase_maps"  # Replace with the actual directory path
    yaml_files = [f for f in os.listdir(usecase_maps_dir) if f.endswith(".yml")]
    if not yaml_files:
        print(f"No YAML files found in {usecase_maps_dir}")
        return

    print("\nAvailable use case data files:")
    for i, file in enumerate(yaml_files):
        print(f"{i+1}. {file}")

    while True:
        try:
            choice = int(input("\nSelect a file by entering its number: "))
            if 1 <= choice <= len(yaml_files):
                yaml_file = os.path.join(usecase_maps_dir, yaml_files[choice - 1])
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    if not yaml_files:
        print(f"No YAML files found in {usecase_maps_dir}")
        yaml_file = input("Enter the path to the YAML file containing use case data: ")
    print(f"Reading use case data from {yaml_file}...")
    usecase_data = read_usecase_data(yaml_file)

    if usecase_data is None:
        return  # Exit if there was an error reading the YAML file

    while True:
        print("\nSelect an option to run:")
        print("1. Validate")
        print("2. Execute")
        print("3. Validate and Execute")
        print("4. Exit")
        option = input("Enter your choice: ")

        if option == "4":
            print("Exiting...")
            break

        print("\nSelect a use case to run:")
        for i, usecase_name in enumerate(usecase_data.keys()):
            print(f"{i+1}. {usecase_name}")
        print(f"{len(usecase_data.keys()) + 1}. Exit")
        choice = input("Enter your choice: ")

        try:
            choice = int(choice)
            if choice == len(usecase_data.keys()) + 1:
                print("Exiting...")
                break
            elif 1 <= choice <= len(usecase_data.keys()):
                usecase_name = list(usecase_data.keys())[choice - 1]
                if option == "1":
                    validate_schema(usecase_name, usecase_data)
                elif option == "2":
                    execute_playbook(usecase_name, usecase_data)
                elif option == "3":
                    validate_schema(usecase_name, usecase_data)
                    execute_playbook(usecase_name, usecase_data)
                else:
                    print("Invalid option. Please try again.")
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()