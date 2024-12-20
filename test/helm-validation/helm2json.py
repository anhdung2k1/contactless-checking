#! /usr/bin/python3
# -*- encoding: utf-8 -*-

import yaml
import argparse
import json
from basiclib import *

class Validator(object):
    """
    General validation for helm charts
    """
    file_index = 0
    file_location = os.path.abspath(__file__)
    root_directory = os.path.dirname(file_location)
    helm_set = []
    helm_set_string = []
    
    def __init__(self, helmchart=None, stderr=False):
        self.namespace = "helm-testing"
        self.stderr = stderr
        self.helm_bin = None
        self.helmchart = helmchart
        self.kubeversion = None
        
    def getopts(self):
        parser = argparse.ArgumentParser(description="Helm chart validation tool")
        parser.add_argument("--helmchart", nargs='?', helm="helm chart to be parsed")
        parser.add_argument("--set", action="append", help="helm chart's set parameters")
        parser.add_argument("--kind", nargs='?', help="K8s kind to be validated (\"all\" for all them)")
        parser.add_argument("--kubeversion", nargs='?', help="k8s version to be validated")
        args = parser.parse_args()
        if args.helmchart:
            self.helmchart = args.helmchart
            logdebug(f"helm chart: {self.helmchart}")
        if args.set:
            self.helm_set = args.set
        if args.kind:
            self.helm_kind = args.kind
        if args.kubeversion:
            self.kubeversion = args.kubeversion
    
    def validate(self, kind=None):
        """
        Check helm chart parameter and do validation
        """
        if self.helm_bin is None:
            try:
                subprocess.check_call(["helm3", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.helm_bin = "helm3"
            except FileNotFoundError:
                try:
                    subprocess.check_call(["helm", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.helm_bin = "helm"
                except FileNotFoundError:
                    raise Exception("helm installation not found")

        set_values = ""
        if len(self.helm_set) > 0:
            set_values = " --set=".join(self.helm_set)
            set_values = " --set=" + set_values

        for str_value in self.helm_set_string:
            set_values += " --set-string " + str_value

        if kind:
            self.helm_kind = kind

        if self.kubeversion:
            set_values += " --kube-version=" + self.kubeversion

        # Run the helm template command, capturing stdout and stderr separately
        cmd = f"{self.helm_bin} template {self.helmchart} --namespace={self.namespace} {set_values}"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Handle stderr (warnings) separately to avoid parsing issues
        if result.stderr:
            logerror(result.stderr)
        
        data_array = self.parse_helm(result.stdout, self.helm_kind)
        return data_array

    def parse_helm(self, text: str, kind: str) -> str:
        """
        It returns the yaml block regarding certain k8s kind
        """
        result = []
        for block in text.split("\n---\n"):
            if len(block) < 1:
                continue
            try:
                y = yaml.safe_load(block)
            except yaml.YAMLError as e:
                logerror(f"Error parsing YAML block: {e}")
                continue
            if y.get("kind", "").lower() == kind.lower() or kind.lower() == "all":
                result.append(y)
        return result

def jsonbeautifier(jsonStruct):
    if jsonStruct is None:
        return "null"
    return json.dumps(jsonStruct, indent=4)

def jsonprettyprint(jsonStruct):
    loginfo(jsonbeautifier(jsonStruct))

def get_chart_version(target_helm):
    target_yaml_path = os.path.join(target_helm, "Chart.yaml")
    
    if not os.path.exists(target_yaml_path):
        logerror(f"Error: File not found - {target_yaml_path}")
        return None
    
    try:
        with open(target_yaml_path, "r") as f:
            chart_data = yaml.safe_load(f)
    except Exception as e:
        logerror(f"Error reading YAML file: {e}")
        return None
    
    if not isinstance(chart_data, dict):
        logerror("Error: Invalid YAML format, Expected a dictionary.")
        return None
    return chart_data.get("version", None)