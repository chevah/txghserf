#!/usr/bin/python
# Copyright (c) 2007 Brandon Sterne
# Licensed under the MIT license.
# http://brandon.sternefamily.net/files/mit-license.txt
# CIDR Block Converter - 2007
import re


# convert an IP address from its dotted-quad format to its
# 32 binary digit representation
def ip2bin(ip):
    b = ""
    inQuads = ip.split(".")
    outQuads = 4
    for q in inQuads:
        if q != "":
            b += dec2bin(int(q), 8)
            outQuads -= 1
    while outQuads > 0:
        b += "00000000"
        outQuads -= 1
    return b


# convert a decimal number to binary representation
# if d is specified, left-pad the binary number with 0s to that length
def dec2bin(n, d=None):
    s = ""
    while n > 0:
        if n & 1:
            s = "1" + s
        else:
            s = "0" + s
        n >>= 1
    if d is not None:
        while len(s) < d:
            s = "0" + s
    if s == "":
        s = "0"
    return s


# convert a binary string into an IP address
def bin2ip(b):
    ip = ""
    for i in range(0, len(b), 8):
        ip += str(int(b[i:i + 8], 2)) + "."
    return ip[:-1]


# input validation routine for the CIDR block specified
def validateCIDRBlock(b):
    # appropriate format for CIDR block ($prefix/$subnet)
    p = re.compile("^([0-9]{1,3}\.){0,3}[0-9]{1,3}(/[0-9]{1,2}){1}$")
    if not p.match(b):
        print "Error: Invalid CIDR format!"
        return False
    # extract prefix and subnet size
    prefix, subnet = b.split("/")
    # each quad has an appropriate value (1-255)
    quads = prefix.split(".")
    for q in quads:
        if (int(q) < 0) or (int(q) > 255):
            print "Error: quad " + str(q) + " wrong size."
            return False
    # subnet is an appropriate value (1-32)
    if (int(subnet) < 1) or (int(subnet) > 32):
        print "Error: subnet " + str(subnet) + " wrong size."
        return False
    # passed all checks -> return True
    return True


def get_IP_list(block):
    """
    Return IP list address from block.
    """
    parts = block.split("/")
    base_ip = ip2bin(parts[0])
    subnet = int(parts[1])

    # If a subnet of 32 was specified simply return the single IP.
    if subnet == 32:
        return [bin2ip(base_ip)]

    result = []
    net = (32 - subnet)
    ip_prefix = base_ip[:-net]
    for i in range(2 ** net):
        ip = bin2ip(ip_prefix + dec2bin(i, net))
        result.append(ip)
    return result


def is_IP_in_block(ip, block):
    """
    Return True if IP belongs to CIDR block.
    """
    for member_ip in get_IP_list(block):
        if member_ip == ip:
            return True
    return False
