from collections import defaultdict
from pathlib import Path
from warnings import warn

import pymbe.api as pm


PYMBE_ROOT = Path(pm.__file__).parent
FIXTURES = (PYMBE_ROOT / "../../tests/fixtures").resolve()


def get_latest_by_name(client: pm.SysML2ClientWidget):
    projects = defaultdict(list)

    for id_, data in client.projects.items():
        projects[data["name"]] += [id_]

    for project_name, project_ids in projects.items():
        if len(project_ids) == 1:
            projects[project_name] = project_ids[0]
            continue
        name = project_name
        created_map = [
            (client.projects[project_id]["created"], project_id) for project_id in project_ids
        ]
        projects[project_name] = sorted(created_map)[-1][1]
    return dict(projects)


def download_all_projects(url: str, port: int = 9000):
    client = pm.SysML2ClientWidget(host_url=url, host_port=port)

    for project_name, project_id in get_latest_by_name(client).items():
        print(f"Retrieving '{project_name}'")
        client.selected_project = project_id
        try:
            model = pm.Model.load(
                elements=client.self._retrieve_data(client.elements_url),
                name=project_name,
                source=client.elements_url,
            )
            print(f" > Saving {project_name}")
            model.save_to_file(FIXTURES / f"{project_name}.json")
            print(f" > Successfully Downloaded '{project_name}'")
        except Exception as exc:
            warn(f">>> Could not download '{project_name}'")


if __name__ == "__main__":
    download_all_projects(url="http://sysml2.intercax.com")
