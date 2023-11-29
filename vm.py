from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
import os



print(f"Provisioning a VM")


# Creating Azure CLI Credential
credential = AzureCliCredential()

subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"] = "4da68ba2-d985-4c44-ae01-da75defd25f0"

resource_client = ResourceManagementClient(credential, subscription_id)

RESOURCE_GROUP_NAME = "python-azure-vm-lab5b"
LOCATION = "westeurope"

# Create the resource group.
rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
    {
        "location": LOCATION
    }
)

print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")

VNET_NAME = "python-azure-vm-example-vnet1b"
SUBNET_NAME = "python-azure-vm-example-subnet"
IP_NAME = "python-azure-vm-example-ip"
IP_CONFIG_NAME = "python-azure-vm-example-ip-config"
NIC_NAME = "python-azure-vm-example-nic"

network_client = NetworkManagementClient(credential, subscription_id)

# Create the virtual network
poller = network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": LOCATION,
        "address_space": {
            "address_prefixes": ["10.0.0.0/16"]
        }
    }
)

vnet_result = poller.result()

print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")

poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME,
    VNET_NAME, SUBNET_NAME,
    { "address_prefix": "10.0.0.0/24" }
)
subnet_result = poller.result()

print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")

poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
    IP_NAME,
    {
        "location": LOCATION,
        "sku": { "name": "Standard" },  # Corrected SKU to "Standard"
        "public_ip_allocation_method": "Static",
        "public_ip_address_version" : "IPV4"
    }
)

ip_address_result = poller.result()

print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
    NIC_NAME,
    {
        "location": LOCATION,
        "ip_configurations": [ {
            "name": IP_CONFIG_NAME,
            "subnet": { "id": subnet_result.id },
            "public_ip_address": {"id": ip_address_result.id }
        }]
    }
)

nic_result = poller.result()

print(f"Provisioned network interface client {nic_result.name}")

compute_client = ComputeManagementClient(credential, subscription_id)

VM_NAME = "PythonAzureVM"
USERNAME = "pythonazureuser"
PASSWORD = "Adolphus~777"

print(f"Provisioning virtual machine {VM_NAME}; this operation might take a few minutes.")

poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
    {
        "location": LOCATION,
        "storage_profile": {
            "image_reference": {
                "publisher": 'Canonical',
                "offer": "UbuntuServer",
                "sku": "18.04-LTS",  # Updated SKU to "18.04-LTS"
                "version": "latest"
            }
        },
        "hardware_profile": {
            "vm_size": "Standard_D2s_v3"  # Check if this size is available in the specified region
        },
        "os_profile": {
            "computer_name": VM_NAME,
            "admin_username": USERNAME,
            "admin_password": PASSWORD
        },
        "network_profile": {
            "network_interfaces": [{
                "id": nic_result.id,
            }]
        }
    }
)

vm_result = poller.result()

print(f"Provisioned virtual machine {vm_result.name}")
