---
layout: post
title: "Short Notes: Installing the Latest CMake on Debian and Ubuntu"
modified:
categories: 
tags: [cmake, debian, ubuntu]
description: "Learn how to install the latest version of CMake on Debian-based systems. This guide covers prerequisites, removing older versions, compiling from source, and verifying the installation."
thumbnail: 
giscus_comments: true
featured: False
share:
toc:
  beginning: true
date: 2024-12-18 12:16:00
---

This guide provides step-by-step instructions for installing the latest version of CMake on Debian-based systems, including Debian and Ubuntu. You'll learn how to remove an existing version, meet prerequisites, compile from source, and verify the installation.

---

## Step 1: Remove Old Versions of CMake

If you already have an older version of CMake installed, it's a good idea to remove it to avoid conflicts. Run the following command:

```bash
sudo apt remove --purge --auto-remove cmake
```

---

## Step 2: Install Required Dependencies

Before compiling CMake from source, ensure you have the necessary libraries installed. The `libssl-dev` package is particularly important to avoid compilation errors:

```bash
sudo apt install libssl-dev
```

---

## Step 3: Download and Compile the Latest CMake Version

Now, download and compile the latest version of CMake. Replace the `version` and `build` variables with the desired CMake version numbers.
Check [https://cmake.org/files/](https://cmake.org/files/), for the latest versions.

```bash
# Adjust the version and build as needed
version=3.29
build=9

# Create a temporary directory for the build process
mkdir ~/temp
cd ~/temp

# Download the source tarball
wget https://cmake.org/files/v$version/cmake-$version.$build.tar.gz

# Extract the tarball
tar -xzvf cmake-$version.$build.tar.gz
cd cmake-$version.$build/

# Configure and build CMake
./bootstrap
make -j$(nproc)  # Utilize all available CPU cores for faster compilation
sudo make install
```

This process might take some time depending on your system's resources.

---

## Step 4: Verify the Installation

After the installation is complete, verify that CMake is correctly installed:

```bash
cmake --version
```

If you encounter an error at this step but the `which cmake` command still shows the binary path, you may need to reset the shell's command hash table:

```bash
hash -r
```

---

## Optional: Cleanup Temporary Files

After the installation is complete, you can remove the temporary directory to free up space:

```bash
rm -rf ~/temp
```

---

## Notes

1. **Updating CMake**: If a new version of CMake is released, repeat the process with updated `version` and `build` variables.
2. **Additional Libraries**: If your project requires other dependencies, ensure they are installed before building CMake.
3. **Alternative Installation**: If you prefer not to compile from source, consider installing CMake from a precompiled binary or a PPA (for Ubuntu users).

By following these steps, you'll have the latest version of CMake installed and ready to use!

