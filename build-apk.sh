#!/usr/bin/env bash
# Android APK Build Script - Cross Platform (Linux/Windows with Git Bash/WSL)
# Usage: ./build-apk.sh [debug|release] [--interactive]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANDROID_DIR="$SCRIPT_DIR/android"
OUTPUT_DIR="$SCRIPT_DIR"

# Default values
DEFAULT_BUILD_TYPE="debug"
DEFAULT_VERSION_NAME="1.0.0"
DEFAULT_VERSION_CODE="1"
DEFAULT_JAVA_HOME=""
DEFAULT_ANDROID_HOME=""

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "windows"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "linux"
    fi
}

# Auto-detect JAVA_HOME
auto_detect_java_home() {
    local os=$(detect_os)
    if [[ "$os" == "windows" ]]; then
        if [[ -d "/c/Program Files/Android/Android Studio/jbr" ]]; then
            echo "/c/Program Files/Android/Android Studio/jbr"
        elif [[ -d "/c/Program Files/Java/jdk-17" ]]; then
            echo "/c/Program Files/Java/jdk-17"
        elif [[ -d "/c/Program Files/Java/jdk-11" ]]; then
            echo "/c/Program Files/Java/jdk-11"
        fi
    elif [[ "$os" == "macos" ]]; then
        if [[ -d "/Applications/Android Studio.app/Contents/jbr/Contents/Home" ]]; then
            echo "/Applications/Android Studio.app/Contents/jbr/Contents/Home"
        elif [[ -d "/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home" ]]; then
            echo "/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home"
        fi
    else
        if [[ -d "/opt/android-studio/jbr" ]]; then
            echo "/opt/android-studio/jbr"
        elif [[ -d "/usr/lib/jvm/java-17-openjdk" ]]; then
            echo "/usr/lib/jvm/java-17-openjdk"
        elif command -v java &> /dev/null; then
            dirname $(dirname $(readlink -f $(which java) 2>/dev/null || echo $(which java)))
        fi
    fi
}

# Auto-detect ANDROID_HOME
auto_detect_android_home() {
    local os=$(detect_os)
    if [[ "$os" == "windows" ]]; then
        echo "${LOCALAPPDATA:-$HOME/AppData/Local}/Android/Sdk"
    elif [[ "$os" == "macos" ]]; then
        echo "$HOME/Library/Android/sdk"
    else
        echo "${ANDROID_HOME:-$HOME/Android/Sdk}"
    fi
}

# Parse arguments
BUILD_TYPE=""
INTERACTIVE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        debug|release)
            BUILD_TYPE="$1"
            shift
            ;;
        -i|--interactive)
            INTERACTIVE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [debug|release] [--interactive]"
            echo ""
            echo "Options:"
            echo "  debug|release   Build type (default: debug)"
            echo "  -i, --interactive  Interactive mode for configuration"
            echo "  -h, --help      Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set defaults
BUILD_TYPE="${BUILD_TYPE:-$DEFAULT_BUILD_TYPE}"
DETECTED_JAVA_HOME=$(auto_detect_java_home)
DETECTED_ANDROID_HOME=$(auto_detect_android_home)

echo "========================================="
echo "  Android APK Build Script"
echo "========================================="
echo ""

# Interactive mode
if [[ "$INTERACTIVE" == "true" ]]; then
    echo "Interactive Configuration Mode"
    echo "-----------------------------------------"
    echo ""
    
    # Build type
    read -p "Build type [debug/release] (default: $BUILD_TYPE): " INPUT_BUILD_TYPE
    BUILD_TYPE="${INPUT_BUILD_TYPE:-$BUILD_TYPE}"
    
    # Version name
    read -p "Version name (default: $DEFAULT_VERSION_NAME): " INPUT_VERSION_NAME
    VERSION_NAME="${INPUT_VERSION_NAME:-$DEFAULT_VERSION_NAME}"
    
    # Version code
    read -p "Version code (default: $DEFAULT_VERSION_CODE): " INPUT_VERSION_CODE
    VERSION_CODE="${INPUT_VERSION_CODE:-$DEFAULT_VERSION_CODE}"
    
    # JAVA_HOME
    read -p "JAVA_HOME path (default: $DETECTED_JAVA_HOME): " INPUT_JAVA_HOME
    JAVA_HOME_PATH="${INPUT_JAVA_HOME:-$DETECTED_JAVA_HOME}"
    
    # ANDROID_HOME
    read -p "ANDROID_HOME path (default: $DETECTED_ANDROID_HOME): " INPUT_ANDROID_HOME
    ANDROID_HOME_PATH="${INPUT_ANDROID_HOME:-$DETECTED_ANDROID_HOME}"
    
    echo ""
else
    VERSION_NAME="$DEFAULT_VERSION_NAME"
    VERSION_CODE="$DEFAULT_VERSION_CODE"
    JAVA_HOME_PATH="$DETECTED_JAVA_HOME"
    ANDROID_HOME_PATH="$DETECTED_ANDROID_HOME"
fi

# Set environment variables
export JAVA_HOME="$JAVA_HOME_PATH"
export ANDROID_HOME="$ANDROID_HOME_PATH"
export ANDROID_SDK_ROOT="$ANDROID_HOME"

echo "Configuration:"
echo "  Build Type: $BUILD_TYPE"
echo "  Version Name: $VERSION_NAME"
echo "  Version Code: $VERSION_CODE"
echo "  JAVA_HOME: ${JAVA_HOME:-Not Set}"
echo "  ANDROID_HOME: ${ANDROID_HOME:-Not Set}"
echo ""

# Update version in build.gradle.kts if version changed
if [[ "$VERSION_NAME" != "$DEFAULT_VERSION_NAME" || "$VERSION_CODE" != "$DEFAULT_VERSION_CODE" ]]; then
    BUILD_GRADLE="$ANDROID_DIR/app/build.gradle.kts"
    if [[ -f "$BUILD_GRADLE" ]]; then
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            sed -i "s/versionCode = .*/versionCode = $VERSION_CODE/" "$BUILD_GRADLE"
            sed -i "s/versionName = \".*\"/versionName = \"$VERSION_NAME\"/" "$BUILD_GRADLE"
        else
            sed -i '' "s/versionCode = .*/versionCode = $VERSION_CODE/" "$BUILD_GRADLE" 2>/dev/null || \
            sed -i "s/versionCode = .*/versionCode = $VERSION_CODE/" "$BUILD_GRADLE"
            sed -i '' "s/versionName = \".*\"/versionName = \"$VERSION_NAME\"/" "$BUILD_GRADLE" 2>/dev/null || \
            sed -i "s/versionName = \".*\"/versionName = \"$VERSION_NAME\"/" "$BUILD_GRADLE"
        fi
        echo "Updated version in build.gradle.kts"
    fi
fi

# Check if gradlew exists
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    GRADLEW="$ANDROID_DIR/gradlew.bat"
else
    GRADLEW="$ANDROID_DIR/gradlew"
fi

if [[ ! -f "$GRADLEW" ]]; then
    echo "Error: gradlew not found in $ANDROID_DIR"
    exit 1
fi

# Set executable permission
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    chmod +x "$GRADLEW" 2>/dev/null || true
fi

cd "$ANDROID_DIR"

# Build APK
echo "Building APK..."
BUILD_TASK="assemble$(echo ${BUILD_TYPE:0:1} | tr '[:lower:]' '[:upper:]')${BUILD_TYPE:1}"
"$GRADLEW" $BUILD_TASK --no-daemon

# Find and copy APK
APK_NAME="app-${BUILD_TYPE}.apk"
APK_SOURCE="$ANDROID_DIR/app/build/outputs/apk/${BUILD_TYPE}/${APK_NAME}"
APK_DEST="$OUTPUT_DIR/accounting-app-v${VERSION_NAME}-${BUILD_TYPE}.apk"

if [[ -f "$APK_SOURCE" ]]; then
    cp "$APK_SOURCE" "$APK_DEST"
    # Also copy as latest
    cp "$APK_SOURCE" "$OUTPUT_DIR/accounting-app-${BUILD_TYPE}.apk"
    echo ""
    echo "========================================="
    echo "  Build Successful!"
    echo "========================================="
    echo "  Version: $VERSION_NAME ($VERSION_CODE)"
    echo "  APK: $APK_DEST"
    ls -lh "$APK_DEST" 2>/dev/null || stat "$APK_DEST"
else
    echo "Error: APK not found at $APK_SOURCE"
    exit 1
fi
