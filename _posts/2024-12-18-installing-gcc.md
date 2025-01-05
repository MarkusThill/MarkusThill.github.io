---
layout: post
title: "Short Notes: Installing GCC 13 on Debian and Ubuntu"
modified:
categories: 
tags: [c++, c, debian, ubuntu]
description: "Learn how to install and configure the latest GNU GCC/G++ compiler on Debian and Ubuntu systems. This step-by-step guide covers updating packages, adding the Toolchain Test PPA, installing GCC 13, verifying the installation, and setting it as the default compiler."
thumbnail: 
giscus_comments: true
featured: False
share:
toc:
  beginning: true
date: 2024-12-19 12:16:00
---

# Installing GCC 13.3.0 on Ubuntu

To install GCC 13.3.0 on your Ubuntu system, you can use the `ubuntu-toolchain-r/test` PPA, which provides newer versions of GCC.

## Steps to Install GCC 13

### 1. Update Your Package List and Install Prerequisites
Run the following commands:
```
sudo apt update
sudo apt install -y software-properties-common
```

### 2. Add the Toolchain Test PPA
Use the following commands to add the PPA:
```
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt update
```

### 3. Install GCC 13
Run the command:
```
sudo apt install -y gcc-13 g++-13
```

### 4. Verify the Installation
Check the installed GCC version:
```
gcc-13 --version
```

This should display the installed version of GCC 13.

### 5. Set GCC 13 as the Default Compiler (Optional)
If you have multiple versions of GCC installed and want to set GCC 13 as the default, use the `update-alternatives` tool:

```
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 11
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 11
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-13 13
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-13 13
```

Follow the on-screen instructions to select GCC 13 as the default compiler:

```
sudo update-alternatives --config gcc
sudo update-alternatives --config g++
```

Check the currently configured version, for example, with:

```
gcc --version
cc --version
g++ --version
c++ --version
```

---

## Notes
1. The `ubuntu-toolchain-r/test` PPA provides the latest GCC versions, but the exact subversion (e.g., 13.3.0) may vary.
2. As of now (Dec 2024), GCC 13.3.0 is not available in the PPA; the latest version provided is GCC 13.2.0.
3. If you specifically require GCC 13.3.0, you may need to build it from source. For most purposes, the version available in the PPA should suffice.

---

## Additional Resources
For more detailed instructions and additional methods to install GCC on Ubuntu, refer to the following resources:

- Install GCC 13 on Ubuntu 22.04 - Lindevs: https://lindevs.com/install-gcc-on-ubuntu/
- Installing GCC13 on Ubuntu 22.04 | DeveloperNote.com: https://developernote.com/2023/08/installing-gcc13-on-ubuntu-22-04/
- How to Install the Latest Version of GCC on Ubuntu | Baeldung on Linux: https://www.baeldung.com/linux/gnu-compiler-collection-ubuntu-installation

These guides provide comprehensive steps and additional context for installing GCC on Ubuntu systems.
