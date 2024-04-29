# gtmeav
BIG-IP EAV monitor to test for status of virtual server within GTM GSLB configuration.

To run from the cli (credentials provided in program

./gtmeavprobe.py 1.2.3.4 443 -g 192.168.0.2 -v vip1 -b BIG-IPVE16-A.local

EAV configuration
-----------------

# Arguments section

-g 192.168.0.2 -v vip1 -b BIG-IPVE16-A.local

Note: This really shouldn't be run frequently as it's generally a heavy lift compared to a tcp-half-open monitor. imo. Minimum rate should be 10/31 vs default 5/16
