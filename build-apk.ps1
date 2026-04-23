# Android APK Build Script - Windows PowerShell
# Usage: .\build-apk.ps1 [-BuildType debug|release] [-Interactive]

param(
    [ValidateSet("debug", "release")]
    [string]$BuildType = "",
    [switch]$Interactive,
    [string]$VersionName = "",
    [int]$VersionCode = 0,
    [string]$JavaHome = "",
    [string]$AndroidHome = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AndroidDir = Join-Path $ScriptDir "android"
$OutputDir = $ScriptDir

# Default values
$DefaultBuildType = "debug"
$DefaultVersionName = "1.0.0"
$DefaultVersionCode = 1

function Get-AutoDetectJavaHome {
    $paths = @(
        "C:\Program Files\Android\Android Studio\jbr",
        "C:\Program Files\Java\jdk-17",
        "C:\Program Files\Java\jdk-11",
        "C:\Program Files\Eclipse Adoptium\jdk-17",
        "$env:JAVA_HOME"
    )
    foreach ($path in $paths) {
        if ($path -and (Test-Path $path)) {
            return $path
        }
    }
    return ""
}

function Get-AutoDetectAndroidHome {
    $paths = @(
        "$env:LOCALAPPDATA\Android\Sdk",
        "$env:ANDROID_HOME",
        "C:\Android\Sdk"
    )
    foreach ($path in $paths) {
        if ($path -and (Test-Path $path)) {
            return $path
        }
    }
    return ""
}

function Update-ReadHost {
    param(
        [string]$Prompt,
        [string]$Default
    )
    if ($Default) {
        $input = Read-Host "$Prompt (default: $Default)"
        if ([string]::IsNullOrWhiteSpace($input)) {
            return $Default
        }
        return $input
    }
    return Read-Host $Prompt
}

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Android APK Build Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Auto-detect defaults
$DetectedJavaHome = Get-AutoDetectJavaHome
$DetectedAndroidHome = Get-AutoDetectAndroidHome

# Interactive mode or use defaults
if ($Interactive) {
    Write-Host "Interactive Configuration Mode" -ForegroundColor Yellow
    Write-Host "-----------------------------------------"
    Write-Host ""
    
    # Build type
    if ([string]::IsNullOrWhiteSpace($BuildType)) {
        $input = Update-ReadHost "Build type [debug/release]" $DefaultBuildType
        $BuildType = if ($input -in @("debug", "release")) { $input } else { $DefaultBuildType }
    }
    
    # Version name
    if ([string]::IsNullOrWhiteSpace($VersionName)) {
        $VersionName = Update-ReadHost "Version name" $DefaultVersionName
    }
    
    # Version code
    if ($VersionCode -eq 0) {
        $input = Update-ReadHost "Version code" $DefaultVersionCode
        $VersionCode = if ($input -as [int]) { [int]$input } else { $DefaultVersionCode }
    }
    
    # JAVA_HOME
    if ([string]::IsNullOrWhiteSpace($JavaHome)) {
        $JavaHome = Update-ReadHost "JAVA_HOME path" $DetectedJavaHome
    }
    
    # ANDROID_HOME
    if ([string]::IsNullOrWhiteSpace($AndroidHome)) {
        $AndroidHome = Update-ReadHost "ANDROID_HOME path" $DetectedAndroidHome
    }
    
    Write-Host ""
} else {
    # Use defaults or provided parameters
    if ([string]::IsNullOrWhiteSpace($BuildType)) { $BuildType = $DefaultBuildType }
    if ([string]::IsNullOrWhiteSpace($VersionName)) { $VersionName = $DefaultVersionName }
    if ($VersionCode -eq 0) { $VersionCode = $DefaultVersionCode }
    if ([string]::IsNullOrWhiteSpace($JavaHome)) { $JavaHome = $DetectedJavaHome }
    if ([string]::IsNullOrWhiteSpace($AndroidHome)) { $AndroidHome = $DetectedAndroidHome }
}

# Set environment variables
$env:JAVA_HOME = $JavaHome
$env:ANDROID_HOME = $AndroidHome
$env:ANDROID_SDK_ROOT = $AndroidHome

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Build Type: $BuildType"
Write-Host "  Version Name: $VersionName"
Write-Host "  Version Code: $VersionCode"
Write-Host "  JAVA_HOME: $JavaHome"
Write-Host "  ANDROID_HOME: $AndroidHome"
Write-Host ""

# Update version in build.gradle.kts
$BuildGradle = Join-Path $AndroidDir "app\build.gradle.kts"
if (Test-Path $BuildGradle) {
    $content = Get-Content $BuildGradle -Raw
    $content = $content -replace 'versionCode = \d+', "versionCode = $VersionCode"
    $content = $content -replace 'versionName = "[^"]*"', "versionName = `"$VersionName`""
    Set-Content $BuildGradle $content -NoNewline
    Write-Host "Updated version in build.gradle.kts" -ForegroundColor Green
}

# Check if gradlew exists
$GradlewPath = Join-Path $AndroidDir "gradlew.bat"
if (-not (Test-Path $GradlewPath)) {
    Write-Host "Error: gradlew.bat not found in $AndroidDir" -ForegroundColor Red
    exit 1
}

Set-Location $AndroidDir

# Build APK
Write-Host "Building APK..." -ForegroundColor Green
$BuildTask = "assemble$($BuildType.Substring(0,1).ToUpper())$($BuildType.Substring(1))"
& $GradlewPath $BuildTask --no-daemon 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Find and copy APK
$ApkSource = Join-Path $AndroidDir "app\build\outputs\apk\$BuildType\app-$BuildType.apk"
$ApkDest = Join-Path $OutputDir "accounting-app-v$VersionName-$BuildType.apk"
$ApkLatest = Join-Path $OutputDir "accounting-app-$BuildType.apk"

if (Test-Path $ApkSource) {
    Copy-Item $ApkSource $ApkDest -Force
    Copy-Item $ApkSource $ApkLatest -Force
    $ApkSize = (Get-Item $ApkDest).Length / 1MB
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "  Build Successful!" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "  Version: $VersionName ($VersionCode)" -ForegroundColor Yellow
    Write-Host "  APK: $ApkDest" -ForegroundColor Yellow
    Write-Host "  Size: $([math]::Round($ApkSize, 2)) MB" -ForegroundColor Yellow
} else {
    Write-Host "Error: APK not found at $ApkSource" -ForegroundColor Red
    exit 1
}
