#! /usr/bin/python3
# -*- encoding: utf-8 -*-

def get_appArmorProfile_securityContext(deploymentKind, containerName=None):
    if containerName == None:
        return deploymentKind['spec']['template']['spec']['securityContext']['appArmorProfile']
    else:
        if 'initContainers' in deploymentKind['spec']['template']['spec']:
            all_initcontainers = deploymentKind['spec']['template']['spec']['initContainers']
            for initcontainer in all_initcontainers:
                if not initcontainer['name'] == containerName: continue
                else:
                    return initcontainer['securityContext']['appArmorProfile']
        else:
            all_containers = deploymentKind['spec']['template']['spec']['containers']
            for container in all_containers:
                if not container['name'] == containerName: continue
                else:
                    return container['securityContext']['appArmorProfile']
    return None

def check_appArmorProfileAnnotation_existed(deploymentKind, containerName):
    appArmorAnnotation = 'container.apparmor.security.beta.kubernetes.io/' + containerName
    return appArmorAnnotation in deploymentKind['spec']['template']['metadata']['annotations']

def check_appArmorProfileSecurityContext_existed(deploymentKind, containerName=None):
    if containerName == None:
        return 'appArmorProfile' in deploymentKind['spec']['template']['spec']['securityContext']
    else:
        if 'initContainers' in deploymentKind['spec']['template']['spec']:
            all_initcontainers = deploymentKind['spec']['template']['spec']['initContainers']
            for initcontainer in all_initcontainers:
                if not initcontainer['name'] == containerName: continue
                return 'appArmorProfile' in initcontainer['securityContext']
        all_containers = deploymentKind['spec']['template']['spec']['containers']
        for container in all_containers:
            if not container['name'] == containerName: continue
            return 'appArmorProfile' in container['securityContext']
    return False        