

# Ciena SAOS 6 Collection

The Ansible Ciena SAOS collection includes a variety of Ansible content to help automate the management of Ciena SAOS 6.x network appliances.

This collection has been tested against Ciena 6.20

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.9.10,<2.11**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

### Supported connections
The Ciena SAOS 6 collection supports ``network_cli``  connections.

## Included content

<!--start collection content-->
### Cliconf plugins
Name | Description
--- | ---
[ciena.saos6.saos6](https://github.com/ciena/ciena.saos6/blob/main/docs/ciena.saos6.saos6_cliconf.rst)|Use saos cliconf to run command on Ciena SAOS 6 platform

### Modules
Name | Description
--- | ---
[ciena.saos6.saos6_command](https://github.com/ciena/ciena.saos6/blob/main/docs/ciena.saos6.saos6_command_module.rst)|Run commands on remote devices running Ciena SAOS 6
[ciena.saos6.saos6_facts](https://github.com/ciena/ciena.saos6/blob/main/docs/ciena.saos6.saos6_facts_module.rst)|Collect facts from remote devices running Ciena SAOS 6

<!--end collection content-->
## Installing this collection

You can install the Ciena SAOS 6 collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install ciena.saos6

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: ciena.saos6
```

## Using this collection

This collection includes [network resource modules](https://docs.ansible.com/ansible/latest/network/user_guide/network_resource_modules.html).

### Using modules from the Ciena SAOS 6 collection in your playbooks

You can call modules by their Fully Qualified Collection Namespace (FQCN), such as `ciena.saos6.saos6_command`.
The following example task replaces configuration changes in the existing configuration on a Ciena SAOS 6 network device, using the FQCN:

```yaml
---
  - name: Execute SAOS 6 commands
    ciena.saos6.saos6_command:
      commands:
      - port set port 2 description foo
      - port set port 3 description bar
      - config save
```

**NOTE**: For Ansible 2.9, you may not see deprecation warnings when you run your playbooks with this collection. Use this documentation to track when a module is deprecated.

## Contributing to this collection

We welcome community contributions to this collection. If you find problems, please open an issue or create a PR against the [Ciena SAOS 6 collection repository](https://github.com/ciena/ciena.saos6).

## Changelogs

[CHANGELOG](CHANGELOG.rst)

## Roadmap

<!-- Optional. Include the roadmap for this collection, and the proposed release/versioning strategy so users can anticipate the upgrade/update cycle. -->

## More information

- [Ansible network resources](https://docs.ansible.com/ansible/latest/network/getting_started/network_resources.html)
- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

Apache License Version 2.0

See [LICENSE](LICENSE) to see the full text.
