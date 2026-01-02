import docker

from docker.errors import DockerException, APIError, NotFound
from typing import Optional, Dict, Any


class DockerService:
    
    _client = None
    
    @classmethod
    def _get_client(cls):
        if cls._client is None:
            try:
                cls._client = docker.from_env()
                cls._client.ping()
            except DockerException as e:
                print(f"Docker connection error: {e}")
                return None
        return cls._client
    
    @staticmethod
    def get_all_images() -> Dict[str, Any]:
        client = DockerService._get_client()
        if not client:
            return {"error": "Docker client not available. Please ensure Docker Desktop is running."}
        
        try:
            images = client.images.list(all=True)
            images_info = []
            
            for image in images:
                image_data = {
                    "id": image.short_id.replace('sha256:', ''),
                    "tags": image.tags if image.tags else ["<none>"],
                    "size_mb": round(image.attrs.get('Size', 0) / (1024 * 1024), 2),
                    "created": image.attrs.get('Created', '').split('T')[0] if image.attrs.get('Created') else ''
                }
                images_info.append(image_data)
            
            return {
                "total_images": len(images_info),
                "images": images_info
            }
            
        except APIError as e:
            return {"error": f"Docker API error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    @staticmethod
    def get_all_containers(show_all: bool = True) -> Dict[str, Any]:
        client = DockerService._get_client()
        if not client:
            return {"error": "Docker client not available. Please ensure Docker Desktop is running."}
        
        try:
            containers = client.containers.list(all=show_all)
            containers_info = []
            
            for container in containers:
                ports_list = []
                for port_key, port_bindings in (container.ports or {}).items():
                    if port_bindings:
                        for binding in port_bindings:
                            ports_list.append(f"{binding.get('HostPort', '')}→{port_key}")
                
                networks = list(container.attrs.get('NetworkSettings', {}).get('Networks', {}).keys())
                
                container_data = {
                    "id": container.short_id,
                    "name": container.name,
                    "status": container.status,
                    "image": container.image.tags[0] if container.image.tags else container.image.short_id,
                    "running": container.status == 'running',
                    "ports": ports_list if ports_list else [],
                    "networks": networks
                }
                containers_info.append(container_data)
            
            running_count = len([c for c in containers_info if c['running']])
            
            return {
                "total_containers": len(containers_info),
                "running_containers": running_count,
                "stopped_containers": len(containers_info) - running_count,
                "containers": containers_info
            }
            
        except APIError as e:
            return {"error": f"Docker API error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    @staticmethod
    def run_container(
        image: str,
        name: Optional[str] = None,
        command: Optional[str] = None,
        ports: Optional[Dict] = None,
        environment: Optional[Dict] = None,
        volumes: Optional[Dict] = None,
        detach: bool = True,
        remove: bool = False,
        network: Optional[str] = None
    ) -> Dict[str, Any]:
        client = DockerService._get_client()
        if not client:
            return {"error": "Docker client not available. Please ensure Docker Desktop is running."}
        
        try:
            run_kwargs = {
                'image': image,
                'detach': detach,
                'remove': remove
            }
            
            if name:
                run_kwargs['name'] = name
            if command:
                run_kwargs['command'] = command
            if ports:
                run_kwargs['ports'] = ports
            if environment:
                run_kwargs['environment'] = environment
            if volumes:
                run_kwargs['volumes'] = volumes
            if network:
                run_kwargs['network'] = network

            container = client.containers.run(**run_kwargs)
            container.reload()
            
            result = {
                "success": True,
                "message": f"Container started successfully",
                "container_id": container.short_id,
                "container_name": container.name,
                "status": container.status,
                "image": image
            }
            
            if detach:
                ports_list = []
                for port_key, port_bindings in (container.ports or {}).items():
                    if port_bindings:
                        for binding in port_bindings:
                            ports_list.append(f"{binding.get('HostPort', '')}→{port_key}")
                
                result["ports"] = ports_list
                result["ip_address"] = container.attrs.get('NetworkSettings', {}).get('IPAddress', '')
            else:
                result["logs"] = container.logs().decode('utf-8')
            
            return result
            
        except NotFound as e:
            return {"error": f"Image '{image}' not found. Please pull the image first."}
        except APIError as e:
            return {"error": f"Docker API error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    @staticmethod
    def start_container(container_id: str) -> Dict[str, Any]:
        client = DockerService._get_client()
        if not client:
            return {"error": "Docker client not available. Please ensure Docker Desktop is running."}
        
        try:
            container = client.containers.get(container_id)
            container.start()
            container.reload()
            
            return {
                "success": True,
                "message": f"Container '{container.name}' started successfully",
                "container_id": container.short_id,
                "container_name": container.name,
                "status": container.status
            }
            
        except NotFound:
            return {"error": f"Container '{container_id}' not found"}
        except APIError as e:
            return {"error": f"Docker API error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    @staticmethod
    def stop_container(container_id: str, timeout: int = 10) -> Dict[str, Any]:
        client = DockerService._get_client()
        if not client:
            return {"error": "Docker client not available. Please ensure Docker Desktop is running."}
        
        try:
            container = client.containers.get(container_id)
            container.stop(timeout=timeout)
            container.reload()
            
            return {
                "success": True,
                "message": f"Container '{container.name}' stopped successfully",
                "container_id": container.short_id,
                "container_name": container.name,
                "status": container.status
            }
            
        except NotFound:
            return {"error": f"Container '{container_id}' not found"}
        except APIError as e:
            return {"error": f"Docker API error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
        