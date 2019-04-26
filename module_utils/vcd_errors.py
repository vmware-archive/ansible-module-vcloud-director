# Copyright © 2018 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause OR GPL-3.0-only


class VCDVappCreationError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VCDLoginError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VDCNotFoundError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, " VDCNotFoundError [" + msg + "]")


class ItemFoundError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, " ItemFoundError [" + msg + "]")


class VCDDiskCreationError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VCDDiskDeletionError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VCDOrgCreationError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VCDOrgDeleteError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class APINotImplement(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VCDVdcDeleteError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VCDVdcCreateError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmCreateError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmDeleteError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmReloadError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmModifyCPUError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmModifyMemoryError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmUnDeployError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmPowerOnError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmPowerOffError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappNetworkCreateError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappUpdateError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
