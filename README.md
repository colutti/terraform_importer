# Terraform Azure Importer

Terraform Azure Importer is a small script to import existing Azure resources into Terraform's state when the resources were created outside of Terraform

## Installation

Just clone this repository or download it.

## Dependencies

```bash
pip3 install azure.mgmt.compute
pip3 install azure.identity
pip3 install chardet
```

## Usage

First you need to create a terraform plan in json:

```bash
terraform plan -out <plan_name>.tfplan
terraform show -json <plan_name>.tfplan > <plan_name>.json
```
After creating the plan, just call the script passing the json plan:

```bash
python3 import.py --plan <plan_name>.json --subscription <your_subscription_id>
```

Note: if you wish to execute the import automatically, you can use the parameter apply:

```bash
python3 import.py --plan <plan_name>.json --subscription <your_subscription_id> --apply
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](hts://choosealicense.com/licenses/mit/)
