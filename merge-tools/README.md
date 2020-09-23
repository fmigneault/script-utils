# Merging CWL Application Package and OGC-API Process Deploy Payload

To help in the update procedure of `Application Package` and the corresponding deployment JSON
payload that contains it, you can use the provided [merge script](./merge_cwl_app_deploy) that will keep
them in sync by updating the payload with new CWL modifications contained within the process definition.

Example:
    
    merge_cwl_app_deploy <path-to-app-package> <path-to-process-deploy>


It is recommended to add this location to your path so that the script becomes easily accessible from 
within any other directory.
