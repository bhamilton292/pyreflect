# pyreflect

Very simple program to listen for packets on one multicast IP and port, read the payload, and immediately republish the payload to a different multicast IP and port.

Multicast groups are hard-coded to 2x link-local multicast IPs.  I discovered that my ISP leased router blocks non-link-local multicast groups on WiFi, which is why I chose link-local groups.

Additional programs to 1) send multicast packets and 2) receive multicast packets and print payload to stdout are included in /testing-helpers for ease of validating the repub function.

Run on python 3.9.18.
