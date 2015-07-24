Title: OpenWRT upload quota and bandwidth limiting
Date: 2015-07-23 21:20:00
Modified: 2015-07-24 01:33:00
Category: OpenWRT, Networking, Linux

Suppose your ISP is traffic shaping your connection when you exceed a certain upload quota,
and some rogue user in your network is constantly uploading data.

To avoid getting hit by traffic management, you want to limit the amount of data the user is able to upload
per day, and limit their upload speed significantly when the quota has been reached.

We can accomplish both with Linux traffic shaping (`tc`) and `iptables` rules.

This setup assumes and requires:

* OpenWRT Barrier Breaker 14.07.
* [sqm-scripts](http://wiki.openwrt.org/doc/howto/sqm) enabled and configured.
* Your outgoing interface is `eth1`.

## Why SQM?

I've been playing with different traffic shaping scripts and none gave satisfactory results as SQM. One could write the `tc` rules manually and spend a lot of time studying the documentation but the most recent algorithms, such as `hfsc`, are notoriously complicated and underdocumented.

SQM gives us a modern QoS infrastructure for people that don't have time to read papers and navigate through the source code. Please refer to the [OpenWRT wiki page for SQM](http://wiki.openwrt.org/doc/howto/sqm) for installation instructions. This guide assumes the default SQM configuration is in place and running.

## Configuring the bandwidth limiter

First, we need to modify the default sqm configuration (`/usr/lib/sqm/simple.qos`) and add a new `tc` class to limit upload speed to
our rogue user. 

You'll find the patch at [https://gist.github.com/1player/fba5775fe0780af310a3](https://gist.github.com/1player/fba5775fe0780af310a3)

Also, make sure to create a help file for it, or the `luci` module for SQM won't be able to find it. Assuming you've called the new script `simple-bwlimit.qos`:

    cp /usr/lib/sqm/simple.qos /usr/lib/sqm/simple-bwlimit.qos
    # edit as needed

This new QoS script creates a new class, with mark 4, with a maximum bandwidth of a 100th of the total upload bandwidth, as defined in the `$BL_RATE` variable, which in my case resolves to 50kbps.

We need to make sure SQM is using this new configuration: open the SQM luci module, and in the `Queue Disciplice` tab select the new script, then load in the new rules.

    /etc/init.d/sqm restart

To make sure the changes have been applied, `tc class show` should list your new class.

    tc -s class show dev eth1 | grep 1:14
    # class htb 1:14 parent 1:1 leaf 140: prio 4 rate 50Kbit ceil 50Kbit burst 1600b cburst 1600b 

## Setting up the iptables rules and quota

The traffic shaping class is set up, but no MAC address is being filtered yet, nor we're not doing any kind of quota management. We'll be using iptables and specifically the `quota` module to do that.

The iptables `quota` module isn't loaded or installed by default, install it with:

    opkg update
    opkg install iptables-mod-extra
    modprobe xt_quota

Now, we just need to set up the filtering logic:

    iptables -t mangle -A FORWARD -o eth1 -m mac --mac-source ro:gu:e0:00:us:er -m quota --quota 157286400 -j RETURN
    iptables -t mangle -A FORWARD -o eth1 -m mac --mac-source ro:gu:e0:00:us:er -j MARK --set-mark 4

These rules, in the `mangle FORWARD` chain, are processed when forwarding the packets from an interface to the other. With the `-o eth1` option we want to match the packets going out to the internet. Also, the rule are applied only to the MAC address `ro:gu:e0:00:us:er`: you can specify an IP address instead of a MAC, but these rules won't work anymore if the DHCP client decides to give the rogue user a different address.

The first line lets the outgoing packets pass unscathed if the quota, expressed in bytes (here 150 MB) has not been reached.
The second line will take effect when the quota is reached, marking the packets which will then be shaped by the `tc` class we've defined previously. The bandwidth limited class from my QoS script has been given the mark number 4.

This is what your iptables configuration should now look like:

    iptables -t mangle -vL FORWARD
    # Chain FORWARD (policy ACCEPT 40050 packets, 28M bytes)
    #  pkts bytes target  prot opt in   out  source   destination  
    # 67883   44M mssfix  all  --  any  any  anywhere anywhere     
    # 23356   26M RETURN  all  --  any  eth1 anywhere anywhere    MAC ro:gu:e0:00:us:er quota: 157286400 bytes
    #     0     0 MARK    all  --  any  eth1 anywhere anywhere    MAC ro:gu:e0:00:us:er MARK set 0x4

We're almost done, there's one last problem: the quota, represented by the "bytes" column, doesn't reset by itself.
The easiest way to reset it is to add a new crontab rule:

    0 * * * * iptables -t mangle -Z FORWARD 2

The `iptables -t mangle -Z FORWARD 2` command will be executed every day at midnight, and reset the stats of the second rule, which in my case corresponds to the quota rule as listed from `iptables -t mangle -vL FORWARD`

To test if it works, just set the mac-source to your PC and try to upload some data somewhere: after reaching the limit you should see your speed decreasing significantly.