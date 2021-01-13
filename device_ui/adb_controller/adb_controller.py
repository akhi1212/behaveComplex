from __future__ import annotations

import logging
import pprint
import subprocess as sp
from typing import Optional, List

from config.config import config


class AdbController:
    def __init__(self):
        self.logger = logging.getLogger(config.LOGGER_NAME + f".{self.__class__.__name__}")
        self.serial_number: str = self._get_sn()

    def _get_sn(self) -> str:
        serial_numbers = self.get_connected_devices_serial_numbers()
        assert len(serial_numbers) == 1, f"One device must be connected. Instead, got {len(serial_numbers)}"
        return serial_numbers[0]

    def execute(self, cmd: str, do_add_sn: bool = True) -> str:
        """
        Executes ADB commands. If the command's exit code is not 0 - raises subprocess.CalledProcessError
        :param cmd: command to be executed
        :param do_add_sn: adds the "-s <serial number>" to the command. Might be useful if we run on a machine
        with multiple devices connected.
        :return: the ADB output

            >>> adb = AdbController()
            >>> adb.execute("adb devices")
            List of devices attached
            <serial number>        device
        """
        assert cmd.startswith("adb ")
        if do_add_sn:
            cmd = self.__add_sn(cmd=cmd)
        self.logger.debug(cmd)
        exitcode, output = sp.getstatusoutput(cmd)
        if exitcode == 0:
            self.logger.debug(output)
        else:
            self.logger.exception(output)
            raise sp.CalledProcessError(cmd=cmd, returncode=exitcode)
        return output

    def __add_sn(self, cmd: str) -> str:
        if "-s" in cmd:
            return cmd
        cmd = cmd.split()
        self.logger.debug(f"Add s/n to command {cmd}")
        adb_index = cmd.index("adb")
        cmd = cmd[: adb_index + 1] + ["-s"] + [self.serial_number] + cmd[adb_index + 1:]
        self.logger.debug(f"Result: {cmd}")
        return " ".join(cmd)

    def get_device_info(self, serial_number: Optional[str] = None) -> DeviceInfo:
        serial_number = serial_number or self.serial_number
        device_info = DeviceInfo(adb=self, serial_number=serial_number)
        self.logger.debug(f"Device info for s/n {serial_number}: \n{device_info}")
        return device_info

    def get_connected_devices_serial_numbers(self) -> List[str]:
        output = self.execute("adb devices", do_add_sn=False)
        connected_devices = [
            line.strip().split("\t")[0].strip()
            for line in output.split("\n")[1:]
            if line.strip()
        ]
        self.logger.debug(f"Connected devices: {connected_devices}")
        return connected_devices

    def _get_imei(self) -> str:
        shell_cmd = r"service call iphonesubinfo 1 | " \
                  r"toybox cut -d \"'\" -f2 | " \
                  r"toybox grep -Eo '[0-9]' | " \
                  r"toybox xargs | " \
                  r"toybox sed 's/\ //g'"
        return self.execute(cmd=f'adb -s {self.serial_number} shell "{shell_cmd}"', do_add_sn=False)


class DeviceInfo:
    def __init__(self, adb: AdbController, serial_number: str):
        self.adb = adb
        self.serial_number: str = serial_number
        self.name: str = ""
        self.manufacturer: str = ""
        self.android_version: str = ""
        self.imei: str = self.adb._get_imei()
        self.set_properties()

    def __repr__(self):
        return pprint.pformat(self.__dict__, indent=4)

    def set_properties(self):
        cmd = f"adb -s {self.serial_number} shell getprop"
        output = self.adb.execute(cmd=cmd)

        properties_map = {
            "ro.config.marketing_name": "name",
            "ro.product.vendor.manufacturer": "manufacturer",
            "ro.build.version.release": "android_version",
        }
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            key, value = [ss.strip().strip("[]") for ss in line.split("]: [")]
            try:
                setattr(self, properties_map[key], value)
            except KeyError:
                pass
