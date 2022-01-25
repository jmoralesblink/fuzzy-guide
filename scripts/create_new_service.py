import os
import file_utils
import sys

# get service name
if len(sys.argv) == 2:
    service_name = sys.argv[1]
else:
    parent_folder = os.path.basename(os.getcwd())
    service_name = input(f"What is the name of the service? Leave empty for {parent_folder}: ") or parent_folder
service_name_dash = service_name.replace(" ", "-").replace("_", "-").lower()

# setup string replacements
service_name_under = service_name_dash.replace("-", "_")
service_name_title = service_name_dash.replace("-", " ").title()
service_output_path = f"../{service_name_dash}"
replacements = {
    "django-service-bootstrap": service_name_dash,
    "django_service_bootstrap": service_name_under,
    "DJANGO_SERVICE_BOOTSTRAP": service_name_under.upper(),
    "Django Service Bootstrap": service_name_title
}

# copy files
file_utils.copy_and_update_dir("service", f"../{service_name_dash}", replacements)
file_utils.copy_and_update_dir(".github", f"../{service_name_dash}/.github", replacements)
file_utils.copy_and_update_dir("k8s", f"../{service_name_dash}/k8s", replacements)

# update file permissions
file_utils.make_file_executable(f"../{service_name_dash}/bin/docker-entrypoint.sh")


# remove folders that should not be in the final service
file_utils.delete_folder(f"../{service_name_dash}/scripts")
file_utils.delete_folder(f"../{service_name_dash}/service")

# print follow-up instructions for the new service
print("\n")
print(f"Your service has been created at {os.path.abspath(service_output_path)}")
print("Follow Up Steps:")
print("  * Ensure these changes are on a branch called init, based off of origin/init")
print("  * Commit these changes, push, and create a PR, which will auto-provision the dev environment")
print("  * Once provisioned, add the deploy-to-dev label to the PR to deploy to the dev environment")
# etc...
