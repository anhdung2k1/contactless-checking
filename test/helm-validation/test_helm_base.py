#! /usr/bin/python3
# -*- encoding: utf-8 -*-
from basiclib import *
import helm2json
import unittest
import commonlib
import os
import inspect

class TestHelmBase(unittest.TestCase):
    '''
    Verify general helm chart options for Emotional Music
    '''
    
    target_helm_dir = os.environ.get("HELMDIR")
    version = helm2json.get_chart_version(target_helm_dir)
    
    h2j = helm2json.Validator()
    h2j.helmchart = target_helm_dir
    
    # @unittest.skip
    def test_setting_appArmor_values(self):
        """Setting appArmor values on container level."""
        self.h2j.kubeversion = "1.29.0"
        loginfo("TEST:" + inspect.currentframe().f_code.co_name + " rendering annotations with kubeversion: " + self.h2j.kubeversion)
 
        self.h2j.helm_set = [
            "appArmorProfile.type=runtime/default",
            "appArmorProfile.face-client.type=unconfined",
            "appArmorProfile.face-model.type=RuntimeDefault",
            "appArmorProfile.authentication.type=Localhost",
            "appArmorProfile.authentication.localhostProfile=profiles.json"
        ]
        self.h2j.helm_kind = "Deployment"
        deployment = self.h2j.validate()
 
        for dp in deployment:
            self.assertEqual(dp['spec']['template']['metadata']['annotations']['container.apparmor.security.beta.kubernetes.io/face-client'], 'unconfined')
            self.assertEqual(dp['spec']['template']['metadata']['annotations']['container.apparmor.security.beta.kubernetes.io/face-model'], 'runtime/default')
            self.assertEqual(dp['spec']['template']['metadata']['annotations']['container.apparmor.security.beta.kubernetes.io/authentication'], 'localhost/profiles.json')
 
            self.assertFalse(commonlib.check_appArmorProfileSecurityContext_existed(dp, 'face-model'))
            self.assertFalse(commonlib.check_appArmorProfileSecurityContext_existed(dp, 'face-client'))
            self.assertFalse(commonlib.check_appArmorProfileSecurityContext_existed(dp, 'authentication'))
 
        self.h2j.kubeversion = "1.30.0"
        loginfo("TEST:" + inspect.currentframe().f_code.co_name + " rendering appArmorProfile securityContext with kubeversion: " + self.h2j.kubeversion)
        self.h2j.helm_kind = "Deployment"
        deployment = self.h2j.validate()

        for dp in deployment:
            self.assertEqual(commonlib.get_appArmorProfile_securityContext(dp)['type'], 'RuntimeDefault')
            if dp == 'face-client':
                self.assertEqual(commonlib.get_appArmorProfile_securityContext(dp, 'face-client')['type'], 'Unconfined')
            elif dp == 'face-model':
                self.assertEqual(commonlib.get_appArmorProfile_securityContext(dp, 'face-model')['type'], 'RuntimeDefault')
            elif dp == 'authentication':
                self.assertEqual(commonlib.get_appArmorProfile_securityContext(dp, 'authentication')['type'], 'Localhost')
                self.assertEqual(commonlib.get_appArmorProfile_securityContext(dp, 'authentication')['localhostProfile'], 'profiles.json')
            self.assertFalse(commonlib.check_appArmorProfileAnnotation_existed(dp, 'face-client'))
            self.assertFalse(commonlib.check_appArmorProfileAnnotation_existed(dp, 'face-model'))
            self.assertFalse(commonlib.check_appArmorProfileAnnotation_existed(dp, 'authentication'))

        loginfo("TEST:" + inspect.currentframe().f_code.co_name + ":OK")