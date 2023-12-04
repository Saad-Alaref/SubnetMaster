import ipaddress
import math

def read_input():
    try:
        # User inputs the base network address
        ip_input = input("Enter main network's IP Address (e.g., 192.168.1.0): ")
        # User inputs the network size (CIDR notation)
        network_size = input("Enter the network size (CIDR notation, e.g., 24 for /24): ")
        # Form the base network in CIDR format
        base_network = f"{ip_input}/{network_size}"

        # Validate the base network
        ipaddress.ip_network(base_network, strict=False)

        num_subnets = int(input("Enter the number of subnets: "))
        if num_subnets <= 0:
            raise ValueError("Number of subnets must be a positive integer.")

        subnets_information = {}

        for i in range(num_subnets):
            subnet_name = input(f"Enter the name for subnet {i+1}: ")
            subnet_hosts = int(input(f"Enter the number of hosts for '{subnet_name}': "))
            if subnet_hosts < 0:
                raise ValueError("Number of hosts must be a non-negative integer.")
            subnets_information[subnet_name] = subnet_hosts

        return base_network, subnets_information

    except ValueError as e:
        print(f"Invalid input: {e}")
        return None, None
    except ipaddress.AddressValueError:
        print("Invalid IP address. Please enter a valid IP address.")
        return None, None

def calculate_subnet_mask(hosts):
    host_bits = math.ceil(math.log2(hosts + 2))  # +2 for network and broadcast addresses
    subnet_mask = 32 - host_bits
    return subnet_mask

def vlsm_subnet_calculator_advanced(base_network, subnets_info):
    """
    base_network: The base network in CIDR notation (e.g., '192.168.1.0/24').
    subnets_info: A dictionary with subnet names as keys and the number of required hosts as values.
    return: A dictionary with subnet details or an error message if subnetting cannot be completed.
    """
    base_net = ipaddress.ip_network(base_network, strict=False)
    sorted_subnets = sorted(subnets_info.items(), key=lambda x: x[1], reverse=True)

    results = {}
    next_subnet_start = base_net.network_address

    # Check if the total number of hosts can fit within the base network
    total_hosts_required = sum(hosts + 2 for _, hosts in sorted_subnets)  # Add 2 for network and broadcast addresses
    if total_hosts_required > base_net.num_addresses:
        return "The total number of hosts exceeds the capacity of the base network."

    for subnet_name, required_hosts in sorted_subnets:
        # Find the smallest subnet that can fit the required hosts
        subnet_bits = 32 - (required_hosts + 2).bit_length()
        subnet_mask = 32 if subnet_bits > 32 else subnet_bits
        new_subnet = ipaddress.ip_network(f"{next_subnet_start}/{subnet_mask}", strict=False)

        # Check if the new subnet is within the base network
        if base_net.overlaps(new_subnet) and new_subnet.subnet_of(base_net):
            # Calculate network details
            results[subnet_name] = {
                "Network IP": str(new_subnet.network_address),
                "Subnet Mask": str(new_subnet.netmask),
                "Number of IPs": new_subnet.num_addresses,
                "Used Hosts": required_hosts,
                "Host IP Range": f"{new_subnet.network_address + 1} - {new_subnet.broadcast_address - 1}",
                "Broadcast Address": str(new_subnet.broadcast_address),
                "Remaining Hosts": new_subnet.num_addresses - 2 - required_hosts,
                "Network Capacity": f"{round((required_hosts / (new_subnet.num_addresses - 2)) * 100, 2)}%",
                "CIDR Notation": f"{new_subnet.network_address}/{new_subnet.prefixlen}"
            }
            next_subnet_start = new_subnet.broadcast_address + 1
        else:
            results[subnet_name] = "Cannot fit within the base network"

    return results


def print_table(subnet_details):
    # Add 'Subnet Name' to the headers list
    headers = ["Subnet Name", "CIDR Notation", "Number of IPs", "Used Hosts",
               "Host IP Range", "Broadcast Address", "Remaining Hosts", "Network Capacity"]

    # Calculate column widths
    col_widths = [max(len(subnet_name) if col == "Subnet Name" else len(str(details.get(col, '')))
                   for subnet_name, details in subnet_details.items()) for col in headers]

    # Print the header
    header_row = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))

    # Print each row
    for subnet_name, details in subnet_details.items():
        row_data = [subnet_name] + [str(details.get(col, '')) for col in headers[1:]]  # Combine subnet name and other details
        row = " | ".join(data.ljust(col_widths[i]) for i, data in enumerate(row_data))
        print(row)


base_network, subnets_info = read_input()

print("\n")

if subnets_info is not None:
    subnet_details = vlsm_subnet_calculator_advanced(base_network, subnets_info)
    if isinstance(subnet_details, dict):
        print_table(subnet_details)
    else:
        print("Subnet calculation error:", subnet_details)
