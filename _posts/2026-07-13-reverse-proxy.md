---
layout: post
title: "Reverse Proxy pt. 1"
date: 2026-07-13
filepath: "~/eric/writing/reverse-proxy-1"
---

Recently, I've been meaning to try and learn some new stuff, particularly
something related to networking and maybe some linux API specific stuff.
Following the age old advice that is always given when you're trying to come up
with a project idea: try and solve a problem you have in your life, an old
problem came to mind: making my home computer accessible while I'm not at home.

A few years ago, I randomly got into the idea of self hosting stuff and making a
little homelab at my house (I even got a little thinkcentre desktop computer).
The problem that I quickly ran into was that I could only access my "homelab"
from home, since I can't easily acquire my own static IP address allocation.

## Hole Punching

While randomly browsing through different project ideas I learned of the concept
of [hole-punching](https://en.wikipedia.org/wiki/Hole_punching_(networking))
which in fact solves the problem of making my home desktop publicly accessible.
The idea is relatively simple: Imagine you have a computer on a home network
that isn't accessible outside of your LAN (e.g. due to NAT, or firewall). We can
get a device running on a static IP address (in my case an AWS EC2 instance)
and have the computer on the local LAN initiate a connection with the computer
on the static IP address and then have it act as a proxy forwarding data from
that static IP address to the home network and then re forwarding the response
back.

![amazing diagram of the proxy design](/assets/posts/proxy-posts/proxy-diagram.png)

My initial plan was to send a simple handshake to kickoff the connection with
EC2 instance indicating the port mappings that should be made that map from the
EC2's ports to the computer on the home network.

## Design

The design of the server took some time for me to wrap my head around, but it's
approximately the following:

The server will bind to a listening port that will be connected to by the
client(s) (the computer behind NAT) when a connection is established the client
will send the port mappings in the following format:

```
| number of mappings (2 bytes) | from port (2 bytes) | to port (2 bytes) | ...
```

After this message is sent the server will open a new socket for each of from
ports in the mappings to listen for ingress connections.

when a connection arrives the server will then save the socket adresss along
with the associated file descriptor in a bidirectional map.

This server will use non-blocking sockets with EPOLL and thus some worker
threads will receive notifications for write operations on the ingress ports
then forward the message through a **singular** socket that is connected
to the destination client.

In this message we just have a simple header attached to the packet sent to
the EC2 including a socket fd (4 bytes), a data length (2 bytes), and the data.
On the reponse from the client it adds back the same header (albeit with a
different data payload but the same socket fd).

Then it gets forwarded out of the socket in the socket fd.

