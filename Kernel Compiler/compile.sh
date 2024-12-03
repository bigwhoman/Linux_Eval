#!/bin/bash

# Configuration
KERNEL_BASE_URL="https://cdn.kernel.org/pub/linux/kernel/v6.x"
WORK_DIR="./"

# Function to get latest versions for each kernel series
get_latest_versions() {
    # Create a temporary file to store the index
    wget -q $KERNEL_BASE_URL/ -O - | \
    grep -o 'linux-6\.[0-9]\+\.[0-9]\+\.tar\.xz' | \
    sort -V | \
    awk -F'[-.]' '
    {
        major=$2
        minor=$3
        patch=$4
        if (!max[major"."minor] || patch > maxpatch[major"."minor]) {
            max[major"."minor]=$0
            maxpatch[major"."minor]=patch
        }
    }
    END {
        for (ver in max) {
            print max[ver]
        }
    }' | sort -V
}

# Function to compile and install a kernel version
compile_kernel() {
    local kernel_archive=$1
    local kernel_version=${kernel_archive%.tar.xz}
    
    echo "Processing $kernel_version..."
    
    # Extract the kernel
    tar xf "$kernel_archive"
    cd "$kernel_version"
    
    # Copy current kernel config as base
    cp -v /boot/config-$(uname -r) .config
    
    # Run menuconfig in automated mode (saves and exits)
    yes "" | make oldconfig
    
    # Disable trusted keys
    ./scripts/config --disable SYSTEM_TRUSTED_KEYS
    ./scripts/config --disable SYSTEM_REVOCATION_KEYS
    
    # Compile kernel (sending two newlines as input)
    printf "\n\n" | make -j$(nproc)
    
    # Install modules and kernel (using expect-like behavior for sudo password)
    echo "$SUDO_PASSWORD" | sudo -S make modules_install -j$(nproc)
    echo "$SUDO_PASSWORD" | sudo -S make install -j$(nproc)
    
    cd ..
}

# Main script
main() {
    # Create and enter work directory
    mkdir -p "$WORK_DIR"
    cd "$WORK_DIR"
    
    # Get list of latest kernel versions
    echo "Getting latest kernel versions..."
    get_latest_versions > versions.txt
    cat versions.txt 
    # Process each kernel version
    while read -r version; do
        # Download kernel
        echo "Downloading $version..."
        wget "$KERNEL_BASE_URL/$version"
        
        # Compile and install
        compile_kernel "$version"
#        
#        # Cleanup
#        rm -rf "${version%.tar.xz}" "$version"
    done < versions.txt
    
    echo "All kernel versions have been processed!"
}

# Check if script is run as root
#if [ "$EUID" -ne 0 ]; then 
#    echo "Please run as root or with sudo privileges"
#    exit 1
#fi

# Execute main function
main
