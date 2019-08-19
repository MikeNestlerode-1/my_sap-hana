


# Azure Pipeline Test
This is Azure pipeline test created for deploy/v2

## Table of contents
- [Supported Scenarios](#supported-scenarios)
- [Design](#design)
- [Add new scenario](#add-new-scenario)

## Supported Scenarios

1. **allNew**: create all resources from scratch
2. **reuseRG**: use existing resource group (generated inside the job)
3. **reuseVNET**: use existing vnet (management generated from [allNew](#allNew))
4. **reuseNSG**: use existing NSG (nsg geneareted from  [allNew](#allNew))

## Design
- All PRs against master and include code change in deploy/v2 will trigger this pipeline test.
- Each scenario will create a testcase with name that contains name of the testcase and buildId, eg. v2-allNew-289.
- Each testcase will create resources under it's own resource group, which has the same name as the testcase, eg. resource group v2-allNew-289.
- Terraform will run with varible file generated during the test, which has name as the testcase as well, eg. v2-allNew-289.json
- After the deployment is done (successful/fail), cleanup job will delete the resource group
## Add New Scenario
### 1. Maintain custom JSON

- create a custom json under `templates/tempGen/<scenario>.json`
  - the json need to include key(s) that will be customized for this scenario
  - for values that requires to be replaced, please put a different placeholder for each one:
    - for name of resource group, replace with `var-rg-name`
    - for arm id of the reuse reousrce, replace with `<reuse resource name>-arm-id`
    - sample:
    ```json
    {
      "infrastructure" : {
              "resource_group" : {
                      "is_existing" : "true",
                      "name" : "var-rg-name",
                      "arm_id" : "rg-arm-id"
              }
      }
    }
    ```
### 2. Maintain `azure-pipelines-v2.yaml`
  - create a new job under `stage: CreatingResources`
  - define the scenario by setting variable `scenario`
  - in `script` section, add necessary step(s) to retrieve the value(s) for placeholder(s) (eg. using az cli)
  - use `templates/update-place-holder.yaml` as many times as needed to replace the above values into `templates/tempGen/<scenario>.json`
  - sample:
    ```yaml
    - job: reuseRG
      variables:
        scenario: v2-reuseRG
        testcase: $(scenario)-$(Build.BuildId)
      steps:
      - script: |
          az login --service-principal --user $(hana-pipeline-spn-id) --password  $(hana-pipeline-spn-pw) --tenant $(landscape-tenant) --output none
          az group create --location westus2 -n $(testcase)
          echo '##vso[task.setvariable variable=arm_id]$(az group show --name $(testcase) --query id --output tsv)'
      - template: templates/update-place-holder.yaml
        parameters:
          scenario: $(scenario)
          testCaseName: $(testcase)
          placeHolder: var-rg-name
          value: $(testcase)
      - template: templates/update-place-holder.yaml
        parameters:
          scenario: $(scenario)
          testCaseName: $(testcase)
          placeHolder: rg-arm-id
          value: $(arm_id)
      - template: templates/terraform-deployment-steps.yaml
        parameters:
          testCaseName: $(testcase)
    ```
  - add the new scenario to `stage: DestroyingResources` -> `job: cleanUp` -> varible `rg_list` with naming `<scenario>-$(Build.BuildId)`.