param name string
param location string = resourceGroup().location
param tags object = {}

// Virtual Network configuration
param vnetAddressPrefix string = '10.0.0.0/16'
param defaultSubnetPrefix string = '10.0.1.0/24'
// Changed from /24 to /23 to provide at least 512 IP addresses
param acaSubnetPrefix string = '10.0.2.0/23'

// Create Network Security Group for "default" subnet
resource nsgDefault 'Microsoft.Network/networkSecurityGroups@2021-05-01' = {
  name: 'nsg-${name}-default'
  location: location
  properties: {
    securityRules: [
      // ...add security rules as needed...
    ]
  }
}

resource nsgAca 'Microsoft.Network/networkSecurityGroups@2021-05-01' = {
  name: 'nsg-${name}-aca'
  location: location
  properties: {
    securityRules: [
      {
        name: 'Allow-Internet-HTTPS'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: 'Internet'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
      // ...add additional security rules as needed...
    ]
  }
}

// Add Virtual Network with two subnets: default and aca
resource vnet 'Microsoft.Network/virtualNetworks@2021-05-01' = {
  name: 'vnet-${name}'
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressPrefix
      ]
    }
    subnets: [
      {
        name: 'default'
        properties: {
          addressPrefix: defaultSubnetPrefix
          networkSecurityGroup: {
            id: nsgDefault.id
          }
        }
      }
      {
        name: 'aca'
        properties: {
          addressPrefix: acaSubnetPrefix
          networkSecurityGroup: {
            id: nsgAca.id
          }
        }
      }
    ]
  }
}

output vnetId string = vnet.id
output vnetName string = vnet.name
output defaultSubnetId string = '${vnet.id}/subnets/default'
output acaSubnetId string = '${vnet.id}/subnets/aca'
