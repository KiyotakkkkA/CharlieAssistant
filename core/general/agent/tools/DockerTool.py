from core.general.agent.ToolBuilder import ToolBuilder
from core.general.agent.services import DockerService
from core.interfaces import ITool
from core.types.ai import ToolClassSetupObject


class DockerTool(ITool):

    name = 'Docker Tools Pack'

    @staticmethod
    def setup_get_all_images_tool() -> ToolClassSetupObject:
        return {
            "name": "get_all_images_tool",
            "handler": DockerTool.get_all_images_handler,
            "tool": ToolBuilder()
                .set_name("get_all_images_tool")
                .set_description("Tool that retrieves information about all Docker images on the system | If Docker client is not available, try to open Docker Desktop app")
        }
    
    @staticmethod
    def get_all_images_handler(**kwargs):
        return DockerService.get_all_images()

    @staticmethod
    def setup_get_all_containers_tool() -> ToolClassSetupObject:
        return {
            "name": "get_all_containers_tool",
            "handler": DockerTool.get_all_containers_handler,
            "tool": ToolBuilder()
                .set_name("get_all_containers_tool")
                .set_description("Tool that retrieves information about all Docker containers (running and stopped) | If Docker client is not available, try to open Docker Desktop app")
                .add_property("show_all", "boolean", description="Show all containers including stopped ones (default: true)")
        }

    @staticmethod
    def get_all_containers_handler(show_all: bool = True, **kwargs):
        return DockerService.get_all_containers(show_all=show_all)

    @staticmethod
    def setup_run_container_tool() -> ToolClassSetupObject:
        return {
            "name": "run_container_tool",
            "handler": DockerTool.run_container_handler,
            "tool": ToolBuilder()
                .set_name("run_container_tool")
                .set_description("Tool that runs a Docker container from an image | If Docker client is not available, try to open Docker Desktop app")
                .add_property("image", "string", description="Docker image name or ID to run")
                .add_property("name", "string", description="Optional container name")
                .add_property("command", "string", description="Optional command to run in container")
                .add_property("ports", "object", description="Port mappings (e.g., {'80/tcp': 8080})")
                .add_property("environment", "object", description="Environment variables as key-value pairs")
                .add_property("volumes", "object", description="Volume mappings (e.g., {'/host/path': {'bind': '/container/path', 'mode': 'rw'}})")
                .add_property("detach", "boolean", description="Run container in background (default: true)")
                .add_property("remove", "boolean", description="Automatically remove container when it exits (default: false)")
                .add_property("network", "string", description="Network to connect the container to")
                .add_requirements(['image'])
        }

    @staticmethod
    def run_container_handler(image: str, name: str | None = None, command: str | None = None, 
                            ports: dict | None = None, environment: dict | None = None, volumes: dict | None = None,
                            detach: bool = True, remove: bool = False, network: str | None = None, **kwargs):
        return DockerService.run_container(
            image=image,
            name=name,
            command=command,
            ports=ports,
            environment=environment,
            volumes=volumes,
            detach=detach,
            remove=remove,
            network=network
        )

    @staticmethod
    def setup_start_container_tool() -> ToolClassSetupObject:
        return {
            "name": "start_container_tool",
            "handler": DockerTool.start_container_handler,
            "tool": ToolBuilder()
                .set_name("start_container_tool")
                .set_description("Tool that starts a stopped Docker container | If Docker client is not available, try to open Docker Desktop app")
                .add_property("container_id", "string", description="Container ID or name to start")
                .add_requirements(['container_id'])
        }

    @staticmethod
    def start_container_handler(container_id: str, **kwargs):
        return DockerService.start_container(container_id=container_id)

    @staticmethod
    def setup_stop_container_tool() -> ToolClassSetupObject:
        return {
            "name": "stop_container_tool",
            "handler": DockerTool.stop_container_handler,
            "tool": ToolBuilder()
                .set_name("stop_container_tool")
                .set_description("Tool that stops a running Docker container | If Docker client is not available, try to open Docker Desktop app")
                .add_property("container_id", "string", description="Container ID or name to stop")
                .add_property("timeout", "integer", description="Seconds to wait for stop before killing (default: 10)")
                .add_requirements(['container_id'])
        }

    @staticmethod
    def stop_container_handler(container_id: str, timeout: int = 10, **kwargs):
        return DockerService.stop_container(container_id=container_id, timeout=timeout)
    
DockerTool.commands = [
    DockerTool.setup_get_all_images_tool(),
    DockerTool.setup_get_all_containers_tool(),
    DockerTool.setup_run_container_tool(),
    DockerTool.setup_start_container_tool(),
    DockerTool.setup_stop_container_tool(),
]