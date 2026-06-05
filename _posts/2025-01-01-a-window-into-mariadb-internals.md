---
layout: post
title: "A window into MariaDB internals"
date: 2025-01-01
filepath: "~/eric/writing/mariadb-internals"
---

I've been looking to take a deeper dive into some of the areas that I make PRs in. Admittedly, most of the stuff that I have worked on has been on a smaller part of the code base where I didn't necessarily need to know that much about the system that I was adding code to.

So recently, after being interested in maybe participating in [GSoC](https://summerofcode.withgoogle.com/) I got interested in contributing to [MariaDB](https://github.com/MariaDB/server/). Particularly I wanted to pick a system inside of the database and really hone in on it. Somewhat arbitrarily, I chose the optimizer since it seems to be one of the more difficult (and hopefully interesting? TBD) areas of development and with the introduction of SQL window functions I figured there was some areas for me to make some contributions.

Long story short, I came across a pretty simple feature/request, for building a simple optimization for window functions in the case that the window is always empty (I'll get into what a window is next). And so I decided I'll make a write-up of the process and the internals I'm touching, since I've been hearing more and more how important of a skill writing is.

> If you think you know something but don't write it down, you will only think you know it.
> — Leslie Lamport

## SQL window functions

Window functions can use all aggregate functions (and some extras).

## MariaDB's window function execution

*(work in progress)*
