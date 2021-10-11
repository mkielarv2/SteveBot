from dataclasses import dataclass


@dataclass
class VmState:
    """Simplified model of the Azure virtual machine state"""
    hardware: str
    state: str
    location: str
    public_ip: str